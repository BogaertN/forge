# LC-RMC-001 deterministic inward interpreter

LC-RMC-001 replaces the heuristic language-understanding responsibility behind
`rmc_engine_v1.phase_parser.parse_phase()` with a bounded deterministic
Language Core interpreter. The public RMC entrypoint and the existing
`memory_recaller.build_trace_spine()` call chain remain in place.

The initial operational profile derives these action roots directly from
source text:

- `inspect`
- `report`
- `request`
- `verify`
- `simulate`

It supports direct and polite imperatives, modal requests, simple active
declaratives, explicit negation, declared verb inflections, and bounded Forge
object phrases. Every consumed token retains exact source offsets. A declared
`with` attachment produces two unselected candidates rather than choosing by
order.

The closed grammar requires base action forms after modals, `do` auxiliaries,
and in imperatives; enforces declared subject/verb and subject/auxiliary
agreement; and rejects misplaced determiners or post-concept modifiers.

Unsupported predicates, terms, Unicode, control characters, incomplete
coverage, oversized input, source-embedded candidate identifiers, and
conflicting semantic metadata fail closed with stable refusal codes. There is
no LLM, embedding, vector, RAG, learned classifier, semantic-similarity,
spelling repair, synonym expansion, or legacy heuristic fallback.

Interpretation is not permission. The runtime and adapter do not route tools,
invoke capabilities, execute actions, render or deliver output, read or write
memory, or select an ambiguous meaning.

## RMC admission boundary

RMC proceeds only when Language Core returns exactly one complete,
non-negated `INTERPRETED` candidate with a valid governed phase. The trace
spine preserves that candidate identifier, semantic signature, action root,
predicate/frame identities, speech act, and negation state.

Candidate generation requires those custody fields to match exactly across
the phase report, admission record, and symbolic trace. Missing Language Core
custody or a changed phase, candidate ID, signature, action root, predicate,
frame, speech act, or negation state blocks candidate generation.

The candidate boundary deterministically replays the source interpretation
and requires the complete envelope to match, including coverage, source spans,
metadata-authority state, candidate signatures, and all no-authority flags.
The admitted phase path is exactly the profile-bound phase for this slice.
Candidate branches never inspect raw source keywords.

The following inputs stop before memory recall, drift analysis, and candidate
generation:

- refused or unsupported language;
- ambiguous language with more than one meaning candidate;
- negated actions, until RMC has an explicit negative-constraint contract.

A held trace has status `BLOCKED`, performs no fallback, creates an empty
candidate set, and has no selected candidate preview. The Forge phase-parser
API propagates the Language Core status and reason code instead of replacing a
refusal with `OK`. The Forge candidate-conclusion API likewise reports
`BLOCKED` and an empty `C_t` for a held trace.

This first profile is deliberately narrow. Language outside the five action
roots listed above remains unsupported until a later governed vocabulary and
phase-mapping slice expands it.

## Live verification

Run from the Forge repository root:

```bash
/home/nic/forge/.venv/bin/python3 \
  scripts/test_aiweb_lc_rmc_001_inward_interpreter.py \
  --mode live

/home/nic/forge/.venv/bin/python3 \
  scripts/aiweb_lc_rmc_001_inward_interpreter_verify.py \
  --repo /home/nic/forge \
  --mode live
```

Expected markers:

```text
LC_RMC_001_TEST_SUMMARY=... "successful": true
AIWEB_LC_RMC_001_INWARD_INTERPRETER_VERIFY=PASS
```

Stop if either command returns nonzero or the PASS marker is absent. A passing
test or verifier does not authorize staging, commit, push, output delivery,
memory mutation, or the next LC-RMC slice.

## Rollback boundary

Rollback must restore the predecessor phase parser plus the bounded Language
Core admission edits in `memory_recaller.py`, `candidate_generator.py`, and the
thin phase-parser API section of `main.py`; it must then remove only the new
LC-RMC runtime, adapter, verifier, test, and documentation paths. Unrelated
`main.py` or Forge work must remain untouched. No database migration, service
change, dependency installation, or memory restoration is involved.
