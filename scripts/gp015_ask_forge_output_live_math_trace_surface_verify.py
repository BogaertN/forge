#!/usr/bin/env python3
"""GP-015 structural/governance verification for backend and Operator Console source."""
from __future__ import annotations
import sys
from pathlib import Path

FORGE = Path(__file__).resolve().parents[1]
UI = Path("/home/nic/aiweb/apps/forge-operator-console")
if str(FORGE) not in sys.path:
    sys.path.insert(0, str(FORGE))

from rmc_engine_v1.general_pipeline.gp015_ask_forge_trace_surface import gp015_surface_boundary

checks=[]
def check(name, condition):
    checks.append((name, bool(condition)))
    if not condition:
        print(f"FAIL: {name}")

required_backend=(
    "rmc_engine_v1/general_pipeline/gp015_ask_forge_trace_surface.py",
    "scripts/test_gp015_ask_forge_output_live_math_trace_surface.py",
    "scripts/gp015_ask_forge_output_live_math_trace_surface_verify.py",
    "scripts/README_gp015_ask_forge_output_live_math_trace_surface.md",
    "scripts/MEA_GP015_ASK_FORGE_OUTPUT_LIVE_MATH_TRACE_SURFACE_DELIVERY_MANIFEST.json",
)
for rel in required_backend:
    check(f"required backend payload installed: {rel}", (FORGE/rel).is_file())
required_ui=(
    "src/forge/VerifiedMathConversation.tsx",
    "src/tabs/ForgeOutputTab.tsx",
    "src/api/forgeClient.ts",
    "src/api/types.ts",
    "src/styles/theme.css",
)
for rel in required_ui:
    check(f"required Operator Console source installed: {rel}", (UI/rel).is_file())

boundary=gp015_surface_boundary()
check("visible center conversation surface declared", boundary["central_conversation_surface"] is True)
check("existing tools retained", boundary["retains_existing_operator_tools"] is True)
check("GP-014 actual Echo route reused", boundary["uses_installed_gp014_expression_realizer"] is True and boundary["uses_actual_echo_delivery"] is True)
check("UI does not claim authority", boundary["ui_is_authority"] is False and boundary["forge_governs"] is True)
check("no LLM corpus shell or persistence authority", not any(boundary[k] for k in ("calls_llm", "uses_corpus", "executes_shell", "writes_files", "writes_memory", "writes_identity_vault", "writes_contribution_economy", "mints_ct", "writes_ledgers")))

main=(FORGE/"main.py").read_text(encoding="utf-8")
module=(FORGE/"rmc_engine_v1/general_pipeline/gp015_ask_forge_trace_surface.py").read_text(encoding="utf-8")
forge_output=(UI/"src/tabs/ForgeOutputTab.tsx").read_text(encoding="utf-8")
conversation=(UI/"src/forge/VerifiedMathConversation.tsx").read_text(encoding="utf-8")
client=(UI/"src/api/forgeClient.ts").read_text(encoding="utf-8")
types=(UI/"src/api/types.ts").read_text(encoding="utf-8")
css=(UI/"src/styles/theme.css").read_text(encoding="utf-8")
check("main API contract exposes GP-015 route", '"/api/operator/ask-forge/math-trace"' in main and 'gp015_governed_symbolic_math_echo_trace_surface' in main)
check("main POST handler invokes GP-015 bounded adapter", 'elif self.path == "/api/operator/ask-forge/math-trace"' in main and '_gp015_ask_forge_math_trace_surface_v1(question)' in main)
check("route error response does not expose raw backend exception text", '"error": str(e)[:240]' not in main and '"error": "governed_math_trace_request_failed"' in main)
check("backend uses accepted math vertical slice", "answer_symbolic_math_language_request" in module)
check("backend exposes trace rather than direct new delivery", "delivery_authorization_v2" in module and "uses_actual_echo_delivery" in module)
check("backend discloses professional review boundary", "professional_decisions_require_human_review" in module)
check("central chat component calls only governed math endpoint", "askForgeGovernedMathTrace" in conversation and "/api/operator/llm-request" not in conversation)
check("composer sits in primary conversation component", "gp015-composer" in conversation and "Ask Forge question" in conversation)
check("candidate and stage traces are visibly inspectable", "Verification trace" in conversation and "Operator-guided language expressions" in conversation and "Governed transaction stages" in conversation)
check("Forge Output promotes center surface", "<VerifiedMathConversation />" in forge_output and "Verified conversation first" in forge_output)
check("legacy operator functions remain retained below", all(token in forge_output for token in ("<SafeCommandRunner", "<AskForgeRequest", "<PageCapturePanel", "<PatchWorkflowPanel", "<AuditReceiptPanel")))
check("rails are not replaced by GP-015 source", "LeftRail" not in forge_output and "RightAuditRail" not in forge_output)
check("API client targets bounded route", "askForgeGovernedMathTrace" in client and "'/api/operator/ask-forge/math-trace'" in client)
check("TypeScript contract includes trace stages and candidates", "GovernedMathTraceResponse" in types and "GovernedMathTraceStage" in types and "GovernedMathExpressionCandidate" in types)
check("dark center-piece styling exists", ".gp015-conversation-frame" in css and ".gp015-composer" in css and ".gp015-chat-stream" in css)
check("bottom composer uses sticky controlled presentation", "position: sticky" in css and "bottom: 0" in css)

combined="\n".join((module, conversation, forge_output, client))
for token in ("eval(", "exec(", "sympify", "parse_expr", "requests.post", "sqlite3.connect", "chromadb", "ECHO_STYLE_SYMBOLIC_DELIVERY_AUTHORIZED"):
    check(f"GP-015 source excludes prohibited token {token!r}", token not in combined)

passed=sum(1 for _, ok in checks if ok)
print(f"RESULT: GP-015-ASK-FORGE-OUTPUT-LIVE-MATH-TRACE-SURFACE_VERIFY {'PASS' if passed==len(checks) else 'FAIL'}  Total:{len(checks)} Passed:{passed} Failed:{len(checks)-passed}")
raise SystemExit(0 if passed==len(checks) else 1)
