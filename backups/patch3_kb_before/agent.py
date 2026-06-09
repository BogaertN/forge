"""
Forge agent.py
The main agent loop.

Flow per query:
  1. Build system prompt + user context
  2. Send to qwen3:8b via Ollama with tool definitions
  3. If model returns a tool_call: execute tool, log to audit, append result, repeat
  4. When model returns a text response: format and display it
  5. Write session end to audit log
"""

import re
import json
import requests
import datetime
from typing import Optional

from .context_builder import build_system_prompt, build_user_context
from .tools import TOOL_DEFINITIONS, dispatch
from .memory import (
    SessionMemory,
    write_audit_entry,
    write_error_log,
)
from .permissions import is_tool_allowed

def _strip_think_blocks(text: str) -> str:
    """
    Remove <think>...</think> scratchpad blocks from model output.
    These are qwen3's internal reasoning and must never be shown to the user.
    Handles multiline blocks and strips leading/trailing whitespace after removal.
    """
    cleaned = re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL)
    return cleaned.strip()


OLLAMA_URL   = "http://127.0.0.1:11434/api/chat"
MODEL        = "qwen3:8b"
MAX_TOOL_LOOPS = 10  # maximum tool calls per query before forcing a response


class ForgeAgent:
    """
    The Forge agent. Manages one session.
    """

    def __init__(self, session_id: str, session_memory: SessionMemory):
        self.session_id    = session_id
        self.memory        = session_memory
        self.system_prompt = build_system_prompt(session_id, session_memory)
        self.conversation: list[dict] = []  # grows across turns in a session

    def _call_ollama(self, messages: list[dict], use_tools: bool = True) -> dict:
        """
        Send a request to the Ollama API.
        Returns the parsed response dict.
        Raises requests.RequestException on network/server error.
        """
        payload = {
            "model": MODEL,
            "messages": [{"role": "system", "content": self.system_prompt}] + messages,
            "stream": False,
            "options": {
                "think": False,        # disable qwen3 thinking mode for speed
                "temperature": 0.1,    # low temperature for deterministic tool use
                "num_ctx": 8192,       # context window
            }
        }
        if use_tools:
            payload["tools"] = TOOL_DEFINITIONS

        response = requests.post(OLLAMA_URL, json=payload, timeout=120)
        response.raise_for_status()
        return response.json()

    def _execute_tool_call(self, tool_name: str, tool_args: dict) -> str:
        """
        Execute a tool call, enforce permissions, log to audit.
        Returns the result as a string for the LLM.
        """
        # Check tool is allowed at current trust level
        allowed, reason = is_tool_allowed(tool_name)
        if not allowed:
            result_str = f"ERROR: {reason}"
            write_audit_entry(
                session_id=self.session_id,
                tool=tool_name,
                path=str(tool_args),
                lines="-",
                reason="PERMISSION_DENIED",
                extra=reason
            )
            return result_str

        # Execute the tool
        result = dispatch(tool_name, tool_args)

        # Determine path for audit log
        audit_path = tool_args.get("path", "-")
        audit_lines = f"{tool_args.get('start_line', '-')}-{tool_args.get('end_line', '-')}"
        audit_reason = tool_args.get("query", "agent_tool_call")

        if result["ok"]:
            result_str = result["data"]
            audit_extra = "OK"
        else:
            result_str = f"ERROR: {result['error']}"
            audit_extra = f"ERROR: {result['error'][:80]}"

        audit_hash = write_audit_entry(
            session_id=self.session_id,
            tool=tool_name,
            path=audit_path,
            lines=audit_lines,
            reason=audit_reason,
            extra=audit_extra
        )

        # Record in session memory
        self.memory.record_tool_call(
            tool=tool_name,
            args=tool_args,
            result=result_str,
            audit_hash=audit_hash
        )

        return result_str

    def ask(self, question: str) -> str:
        """
        Process one user question through the full agent loop.
        Returns the final formatted response string.
        """
        # Build the message list for this turn
        user_messages = build_user_context(question, self.memory)

        # Append to conversation history
        self.conversation.extend(user_messages)

        tool_loop_count = 0
        messages_for_api = list(self.conversation)

        while tool_loop_count < MAX_TOOL_LOOPS:
            try:
                response = self._call_ollama(messages_for_api)
            except requests.exceptions.ConnectionError:
                return (
                    "\n[FORGE ERROR] Cannot reach Ollama at http://127.0.0.1:11434\n"
                    "Make sure Ollama is running: systemctl status ollama\n"
                )
            except requests.exceptions.Timeout:
                return "\n[FORGE ERROR] Ollama request timed out. The model may be loading.\n"
            except requests.exceptions.RequestException as e:
                write_error_log(self.session_id, str(e))
                return f"\n[FORGE ERROR] Ollama API error: {e}\n"

            message = response.get("message", {})
            role    = message.get("role", "assistant")
            content = message.get("content", "")
            tool_calls = message.get("tool_calls", [])

            # If there are tool calls, execute them
            if tool_calls:
                tool_loop_count += 1

                # Add assistant message with tool calls to history
                messages_for_api.append({
                    "role": "assistant",
                    "content": content or "",
                    "tool_calls": tool_calls
                })

                # Execute each tool call and collect results
                for tc in tool_calls:
                    fn   = tc.get("function", {})
                    name = fn.get("name", "")
                    args = fn.get("arguments", {})

                    # Ollama sometimes returns args as a string
                    if isinstance(args, str):
                        try:
                            args = json.loads(args)
                        except json.JSONDecodeError:
                            args = {}

                    result_str = self._execute_tool_call(name, args)

                    # Add tool result to messages
                    messages_for_api.append({
                        "role": "tool",
                        "content": result_str
                    })

                # Continue the loop — send results back to model
                continue

            # No tool calls — this is the final text response
            if not content:
                content = "[Forge returned an empty response. This is unexpected.]"

            content = _strip_think_blocks(content)

            # Store assistant response in conversation history
            self.conversation.append({
                "role": "assistant",
                "content": content
            })

            return content

        # Exceeded MAX_TOOL_LOOPS — force a text response
        write_error_log(
            self.session_id,
            f"Exceeded MAX_TOOL_LOOPS ({MAX_TOOL_LOOPS}) on question: {question[:80]}"
        )
        try:
            # One final call without tools to get a text response
            messages_for_api.append({
                "role": "user",
                "content": (
                    "You have used the maximum number of tool calls. "
                    "Summarize what you found so far and answer the question with what you have."
                )
            })
            response = self._call_ollama(messages_for_api, use_tools=False)
            return _strip_think_blocks(
                response.get("message", {}).get("content", "[No response from model]")
            )
        except Exception as e:
            return f"[FORGE ERROR] Tool loop exceeded and fallback failed: {e}"
