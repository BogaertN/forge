# General Learning-to-Answer Pipeline — Build GP-001

**Build ID:** `GENERAL-LEARNING-TO-ANSWER-PIPELINE-FOUNDATION-BUILD-GP-001`
**Schema:** `general_pipeline_v1_build_gp001`

## What this build is

The first real, non-fixture vertical slice of the full architecture. It runs the
complete designed motion for the domains the system has actually learned:

```
instructional source text
  -> compile governed semantic source
user question
  -> match a learned domain
  -> parse into typed exact quantities
  -> build a real MEA ProblemManifest (the engine's own dataclass)
  -> execute exact arithmetic and verify it
  -> governed gate decides whether it may seal
  -> seal manifest to RESOLVED_MANIFEST / RENDER_ALLOWED
  -> compile a separate RMC meaning manifest
  -> generatively render natural language from meaning fields
  -> Echo approves the faithful rendering
  -> return the approved answer
```

It ships **two learned domains** at the beginning of math:

- `whole_number_arithmetic` — "what is A plus/minus/times/divided by B"
- `fraction_change_capacity` — "X was a/b full; after N removed it was c/d full;
  what is the full capacity?" (the Build 011 family)

## What is honest about it

- **It refuses what it has not learned.** A question no domain recognises returns
  `REFUSED_UNLEARNED` — it never guesses. That refusal is the feature that keeps
  the system from confabulating.
- **The renderer is generative, not canned.** Sentences are assembled from this
  problem's meaning fields (object, operation, operands, the actual computed
  reasoning steps, the exact answer, the verification). Different problems produce
  different sentences. There is no fixed answer string and no 144 Hz fixture in it.
- **Echo is the approval gate.** A faithful rendering of a resolved manifest is
  approved for delivery; Echo still does not certify external truth, write memory,
  mint CT, or open any route.
- **The math governs what can be said.** An exact answer does not auto-seal; it
  must pass the governed gate (positive information gain + passed exact
  verification + domain authorised by the source) before any language is produced.

## How capability grows

Add a new `Domain` in `rmc_engine_v1/general_pipeline/domains.py` (a matcher, a
parser, an exact executor, and a relation string), plus tests. The engine never
changes; only the library grows. This is how the system reaches more of an
elementary book over time — one verified domain at a time.

## Boundaries (Build GP-001)

In-memory only. No route, no UI, no LLM, no file I/O, no memory write, no Chroma,
no Identity Vault, no CT/ledger activity. **No existing Build 005–010 file is
modified.** This build adds new files only.

## Files installed

```
rmc_engine_v1/general_pipeline/__init__.py
rmc_engine_v1/general_pipeline/contracts.py
rmc_engine_v1/general_pipeline/domains.py
rmc_engine_v1/general_pipeline/source_compiler.py
rmc_engine_v1/general_pipeline/manifest_builder.py
rmc_engine_v1/general_pipeline/governed_gate.py
rmc_engine_v1/general_pipeline/meaning_and_renderer.py
rmc_engine_v1/general_pipeline/echo_approval.py
rmc_engine_v1/general_pipeline/pipeline.py
scripts/test_general_pipeline_foundation_build_gp001.py
scripts/general_pipeline_foundation_build_gp001_verify.py
scripts/README_general_pipeline_foundation_build_gp001.md
scripts/SHA256SUMS_general_pipeline_foundation_build_gp001.txt
```

## Verify after install

```
.venv/bin/python scripts/test_general_pipeline_foundation_build_gp001.py --forge-root "$HOME/forge"
.venv/bin/python scripts/general_pipeline_foundation_build_gp001_verify.py --forge-root "$HOME/forge"
```

Expected:

```
RESULT: GENERAL-LEARNING-TO-ANSWER-PIPELINE-FOUNDATION-BUILD-GP-001_BEHAVIOR PASS  Total:35 Passed:35 Failed:0
RESULT: GENERAL-PIPELINE-FOUNDATION-BUILD-GP-001_VERIFY PASS  Total:23 Passed:23 Failed:0
```
