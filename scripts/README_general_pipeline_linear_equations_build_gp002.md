# GP-002 — One-Unknown Linear Equations

**Build ID:** `GENERAL-LEARNING-TO-ANSWER-PIPELINE-LINEAR-EQUATIONS-BUILD-GP-002`
**Schema:** `general_pipeline_v1_build_gp002`

## What this build adds

A second learned math domain on top of GP-001, with **no GP-001 file modified**:

- `linear_equation_one_unknown` — solves `a*x + b = c` (and `a*x - b = c`,
  `x +/- b = c`, `a*x = c`) for the single unknown, using exact fractions, and
  verifies by substitution. Any single-letter variable works (x, y, ...).

Examples it now answers (from instructional algebra source text):

```
solve 3x + 5 = 20 for x   -> x = 5
2y - 4 = 10               -> y = 7
4x = 28                   -> x = 7
solve 2x + 3 = 8 for x    -> x = 5/2
5x + 10 = 0               -> x = -2
```

Sample generated answer (composed from the manifest, not a template):

> The answer is 5. Start from 3x + 5 = 20. Subtract 5 from both sides: 3x = 15.
> Divide both sides by 3: x = 15 ÷ 3 = 5. Check: substituting x = 5 gives
> 3 × 5 + 5 = 20, which matches 20. This answer is verified by exact arithmetic.

## How it stays clean

- **GP-001 is byte-for-byte untouched.** GP-002 ships two new modules
  (`domains_equations.py`, `gp002_linear_equations.py`) and wires itself in via
  `gp002_linear_equations.activate()` — an idempotent hook that registers the
  new domain and teaches the source compiler to authorise algebra sources.
- **Same guarantees as GP-001:** unlearned questions are refused (no guessing),
  the governed gate still requires positive information gain + passed exact
  verification before sealing, and Echo still approves only faithful renderings.
- **Boundaries:** in-memory only. No route, UI, LLM, file I/O, memory write,
  Chroma, Identity Vault, or CT/ledger activity.

## Files installed

```
rmc_engine_v1/general_pipeline/domains_equations.py
rmc_engine_v1/general_pipeline/gp002_linear_equations.py
scripts/test_general_pipeline_linear_equations_build_gp002.py
scripts/general_pipeline_linear_equations_build_gp002_verify.py
scripts/README_general_pipeline_linear_equations_build_gp002.md
scripts/SHA256SUMS_general_pipeline_linear_equations_build_gp002.txt
scripts/MEA_GENERAL_PIPELINE_BUILD_GP002_DELIVERY_MANIFEST.json
```

## Verify after install

```
.venv/bin/python scripts/test_general_pipeline_linear_equations_build_gp002.py --forge-root "$HOME/forge"
.venv/bin/python scripts/general_pipeline_linear_equations_build_gp002_verify.py --forge-root "$HOME/forge"
```

Expected:

```
RESULT: GENERAL-LEARNING-TO-ANSWER-PIPELINE-LINEAR-EQUATIONS-BUILD-GP-002_BEHAVIOR PASS  Total:30 Passed:30 Failed:0
RESULT: GENERAL-PIPELINE-LINEAR-EQUATIONS-BUILD-GP-002_VERIFY PASS  Total:26 Passed:26 Failed:0
```

GP-001 must still pass unchanged (35/35 and 23/23).

## To use it

```python
from rmc_engine_v1.general_pipeline import gp002_linear_equations as gp2
gp2.activate()                      # idempotent; do this once per process
from rmc_engine_v1.general_pipeline import learn_and_answer
book = "algebra equation solve unknown variable both sides isolate"
print(learn_and_answer(book, "algebra_book", "solve 3x + 5 = 20 for x").answer_text)
```

## Roadmap (set by this build)

- **GP-003:** multi-step arithmetic word problems ("had 12, bought 8, gave away 5").
- **GP-004:** elementary language — spelling/pluralization rules (first non-math
  domain, still exactly verifiable).
- then toward riddles/word-search once the language footing is real.
