# Patch 102 Engine Review Evidence Cross-Check

Engine: `tier_enforcer`
Status: `EVIDENCE_CROSSCHECK_READY_NO_AUTHORITY`
Evidence ID: `EEB-2dcdd27009bc29cd`
Candidate path: `/home/nic/aiweb/engines/tier_enforcer`

## LLM Invocation
- Called: `True`
- Provider: `ollama`
- Model: `qwen3:8b`
- Status: `OLLAMA_VISIBLE_REVIEW_READY`
- Hidden reasoning stored: `False`

## Local LLM Visible Review

Plain-English Purpose:  
Enforces separation between Tier 1 (human-facing) and Tier 2 (system-level) outputs to prevent interface drift and maintain runtime coherence across AI.Web systems.  

Likely System Role:  
A runtime validation enforcer that classifies output, logs cross-tier violations, and tags content with tier headers. Used for system-level output sanitization and compliance checks.  

Evidence Used:  
- `run.py`: Implements classification (`classify_output`), enforcement (`enforce_tier`), and logging functions.  
- `tier_rules.json`: Defines keyword lists for Tier 1 and Tier 2 classification.  
- Test scripts and logs (`test_log.txt`, `tier_violation_log.json`) demonstrate enforcement actions and violation detection.  

Risks / Uncertainties:  
- Reliance on static keyword lists may miss nuanced tier classifications.  
- No evidence of dynamic rule updates or fallback mechanisms for missing rules.  
- Log files are stored as JSON; potential single-point failure if corrupted.  

Recommendation Draft:  
Approve with caveats: Ensure keyword lists are regularly audited for completeness. Implement safeguards for missing rules (e.g., default classification). Monitor log file integrity.  

Suggested Nic Action:  
Approve review, but request confirmation that keyword coverage is sufficient and that log management processes are in place.

## Bound Evidence Files

### `run.py`
- Path: `/home/nic/aiweb/engines/tier_enforcer/run.py`
- SHA-256: `8be3d8ddd0dfaf71f1f52ba493b8a20ac4c06df096d9aa123ec935357120f083`
- Lines: `73`
- Imports sample: `import json, from datetime import datetime, from pathlib import Path`
- Functions sample: `load_rules, _log_event, log_violation, classify_output, enforce_tier`

```text
# run.py – AI.Web Tier Enforcer
# Enforces Tier 1 (human-facing) and Tier 2 (system-level) output separation

import json
from datetime import datetime
from pathlib import Path

# File paths
RULES_FILE = Path(__file__).parent / "tier_rules.json"
VIOLATION_LOG = Path(__file__).parent / "tier_violation_log.json"
TEST_LOG = Path(__file__).parent / "test_log.txt"

# Load rules from tier_rules.json
def load_rules():
    if not RULES_FILE.exists():
        raise FileNotFoundError("tier_rules.json not found.")
    return json.loads(RULES_FILE.read_text())

# Basic logger
def _log_event(msg):
    with open(TEST_LOG, "a") as f:
        f.write(f"[{datetime.now().isoformat()}] {msg}\n")

# Log a violation
def log_violation(content, reason, detected_tier):
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "reason": reason,
        "tier_detected": detected_tier,
        "content": content
    }

    # Append to log
    if VIOLATION_LOG.exists():
        log = json.loads(VIOLATION_LOG.read_text())
    else:
        log = []

    log.append(log_entry)
    VIOLATION_LOG.write_text(json.dumps(log, indent=2))

# Classify input as Tier 1, Tier 2, or MIXED
def classify_output(text):
    rules = load_rules()
    tier1_hits = sum(1 for word in rules["tier1_keywords"] if word in text.lower())
    tier2_hits = sum(1 for word in rules["tier2_keywords"] if word in text.lower())

    if tier1_hits > 0 and tier2_hits > 0:
        return "MIXED"
    elif tier2_hits > tier1_hits:
        return "TIER 2"
    elif tier1_hits > 0:
        return "TIER 1"
    else:
        return "UNCLASSIFIED"

# Enforce tier protocol
def enforce_tier(text):
    result = classify_output(text)
    _log_event(f"Checked content: classified as {result}")

    if result == "MIXED":
        log_violation(text, "Cross-tier contamination", result)
        return "[TIER VIOLATION] Output rejected due to mixed content."
    elif result == "TIER 1":
        return f"[TIER 1] {text}"
    elif result == "TIER 2":
        return f"[TIER 2] {text}"
    else:
        log_violation(text, "Unclassified content", result)
        return "[UNCLASSIFIED] Output does not match Tier 1 or Tier 2."
```

### `README.md`
- Path: `/home/nic/aiweb/engines/tier_enforcer/README.md`
- SHA-256: `32a9a95d1451e727dc3ba35efa60bf5eb235dad7200f76c52497ba3e132b1313`
- Lines: `12`
- Functions sample: `tier_enforcer, This, engine, enforces, the, Web, Tiered, Communication, Framework, analyzes, output, and, Classifies, Tier, Mixed, Logs, violations, tier_violation_log, json, Tags, clean, content, with, TIER, headers`

```text
# tier_enforcer

This engine enforces the AI.Web Tiered Communication Framework.

It analyzes output and:
- Classifies it as Tier 1, Tier 2, or Mixed
- Logs violations to `tier_violation_log.json`
- Tags clean content with `[TIER 1]` or `[TIER 2]` headers
- Blocks mixed or unclassified output to prevent interface drift

This engine ensures runtime voice coherence across all LLMs and agents.
```

### `test_tier_enforcer.py`
- Path: `/home/nic/aiweb/engines/tier_enforcer/test_tier_enforcer.py`
- SHA-256: `43dfaf56cf055d46c66006175a6cbeca225cbb17458873183ff6728e1faceae6`
- Lines: `14`
- Imports sample: `from run import enforce_tier`

```text
from run import enforce_tier

print("🔹 TEST 1: Tier 1 (human)")
text1 = "This tool helps you stay calm, organize your thoughts, and journal clearly."
print(enforce_tier(text1))

print("\n🔹 TEST 2: Tier 2 (system)")
text2 = "The phase engine triggers χ(t) when symbolic recursion breaks coherence."
print(enforce_tier(text2))

print("\n🔹 TEST 3: Mixed content (violation)")
text3 = "This gentle app keeps you calm while monitoring ψ and memory stack integrity."
print(enforce_tier(text3))
```

### `test_log.txt`
- Path: `/home/nic/aiweb/engines/tier_enforcer/test_log.txt`
- SHA-256: `2e7d2ac6c77a2acb6ed2aa123e94dedf2425515a94103b7d03a1d5b4c8d05731`
- Lines: `4`
- Functions sample: `Checked, content, classified, TIER, MIXED`

```text
[2025-04-22T20:55:01.950567] Checked content: classified as TIER 1
[2025-04-22T20:55:01.950669] Checked content: classified as TIER 2
[2025-04-22T20:55:01.950747] Checked content: classified as MIXED
```

### `tier_violation_log.json`
- Path: `/home/nic/aiweb/engines/tier_enforcer/tier_violation_log.json`
- SHA-256: `9e0ac6996a0ba4585b446a0c049924a9e3bd08cad7c011007d097dd382892b9c`
- Lines: `8`
- Functions sample: `timestamp, reason, Cross, tier, contamination, tier_detected, MIXED, content, This, gentle, app, keeps, you, calm, while, monitoring, u03c8, and, memory, stack, integrity`

```text
[
  {
    "timestamp": "2025-04-22T20:55:01.950757",
    "reason": "Cross-tier contamination",
    "tier_detected": "MIXED",
    "content": "This gentle app keeps you calm while monitoring \u03c8 and memory stack integrity."
  }
]
```

### `tier_rules.json`
- Path: `/home/nic/aiweb/engines/tier_enforcer/tier_rules.json`
- SHA-256: `f29a905ecbe6ea968b0431a40870d2bbb7de32423ea8ab0d56bb699ad8365dc0`
- Lines: `49`
- Functions sample: `tier1_keywords, stress, calm, journal, family, clear, thinking, mental, health, easy, use, everyday, life, simple, feeling, off, spiral, organize, friendly, helpful, decision, making, support, real, gentle`

```text
{
  "tier1_keywords": [
    "stress",
    "calm",
    "journal",
    "family",
    "clear thinking",
    "mental health",
    "easy to use",
    "everyday life",
    "simple",
    "feeling off",
    "spiral",
    "organize",
    "friendly",
    "helpful",
    "decision-making",
    "support",
    "real life",
    "gentle",
    "accessible",
    "anyone can use this",
    "what you’re going through"
  ],
  "tier2_keywords": [
    "symbolic recursion",
    "ψ",
    "χ(t)",
    "Christ Function",
    "echo",
    "drift",
    "resonance",
    "loop closure",
    "agent",
    "runtime stack",
    "phase engine",
    "memory state",
    "cold archive",
    "naming vector",
    "FBSC",
    "phase 6",
    "projection",
    "entropy score",
    "recursive overlay",
    "system logic",
    "drift firewall"
  ]
}
```

### `engine_manifest.json`
- Path: `/home/nic/aiweb/engines/tier_enforcer/engine_manifest.json`
- SHA-256: `5a08ed7936afb286f07a9438267c76380e29858d82f87c310f0fd00ef5f8e45e`
- Lines: `9`
- Functions sample: `name, tier_enforcer, version, status, stable, locked, true, last_verified, description, Web, Tier, Enforcement, Engine, Classifies, content, human, facing, system, Detects, and, blocks, cross, tier, contamination, Logs`

```text
{
  "name": "tier_enforcer",
  "version": "1.0.0",
  "status": "stable",
  "locked": true,
  "last_verified": "2025-04-22",
  "description": "AI.Web Tier Enforcement Engine. Classifies content as Tier 1 (human-facing) or Tier 2 (system-facing). Detects and blocks cross-tier contamination. Logs violations and tags all output with correct tier for runtime trust and clarity."
}
```

## Simple Keyword Overlap
- functions_mentioned: `classify_output, enforce_tier, enforces, Web, output, and, Classifies, Tier, Logs, violations, tier_violation_log, json, Tags, content, with, TIER, headers, Cross, tier, app, integrity, use, Enforcement, human, facing, system, cross`
- imports_mentioned: `import json, from run import enforce_tier`
- classes_mentioned: `none`
- file_names_mentioned: `run.py, test_log.txt, tier_violation_log.json, tier_rules.json`
- evidence_terms_present: `none`

## Warnings
- LLM role wording does not explicitly repeat deterministic role label.

## Authority
This report is for human verification only. It does not approve, reject, mutate the ledger, edit engine files, or create lockfile authority.
