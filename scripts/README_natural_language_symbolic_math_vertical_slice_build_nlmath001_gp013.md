# NL-MATH-001 / GP-013 — Natural-Language Symbolic Expression-to-Echo Vertical Slice

## Purpose

This patch completes the first lawful user-facing vertical slice on top of the installed
MATH-001R1 / GP-012R1 computation-only symbolic mathematics kernel.

The accepted route is:

`bounded natural-language mathematical request`
`-> AI.Web-owned full-input compiler`
`-> typed SymbolicMathOperationManifest`
`-> installed MATH-001R1 isolated SymPy computation`
`-> verified tool-evidence binding`
`-> real MEA ProblemManifest seal`
`-> separate RMC meaning manifest`
`-> deterministic mathematical semantic lexicon renderer`
`-> existing Manifest Contract v2`
`-> actual existing Echo validation`
`-> DeliveryAuthorizationReceiptV2`
`-> human-text answer`

This patch extends the already live General Pipeline delivery spine. It does **not**
promote the historical `rmc_engine_v1/renderer/*` hypothesis-preview lane into
delivery authority.

## Honest Scope of This First Complete Slice

The installed MATH-001R1 kernel remains capable of 26 typed symbolic operation
families. This patch opens natural-language-to-delivery support for the first coherent
eight-family expression/calculus slice:

- simplification
- expansion
- factoring
- trigonometric simplification
- trigonometric expansion
- differentiation
- integration
- limits

Example supported requests:

```text
Differentiate x^3 + 4*x with respect to x.
Find the derivative of x cubed plus 4 x with respect to x.
Integrate 3*x^2 + 4 with respect to x.
Expand (x + 1)^3.
Factor x^2 - 9.
Simplify (x^2 - 1)/(x - 1).
Trigonometric simplify sin(x)^2 + cos(x)^2.
Find the limit of (x^2 - 1)/(x - 1) as x approaches 1.
```

Other MATH-001R1 operation families remain available as typed computation-only
capabilities; their natural-language compilation and Echo delivery paths are not claimed
by this patch and must be built through later governed slices.

## Hard Boundaries

- No raw user expression is passed to SymPy.
- No `eval`, `exec`, `sympify`, or `parse_expr`.
- No natural-language guessing or partial trailing-instruction execution.
- First-slice expression symbols are restricted to the bounded vocabulary: x, y, z, t, n, i, a, b, c, u, v.
- No corpus ingestion or corpus-grounded teaching.
- No LLM authority.
- No new external dependency installation.
- No memory promotion or persistent memory write.
- No Identity Vault write.
- No Contribution Economy action.
- No CT mint.
- No ledger write.
- No route, UI, or `main.py` integration.
- No change to the existing four-domain legacy General Pipeline router.
- Computation evidence cannot itself authorize delivery.
- Delivery is authorized only after actual existing Echo succeeds through `DeliveryAuthorizationReceiptV2`.

## Files Installed

Modified existing files:

```text
rmc_engine_v1/general_pipeline/__init__.py
rmc_engine_v1/general_pipeline/manifest_contract_v2.py
```

New production files:

```text
rmc_engine_v1/general_pipeline/symbolic_math_language_compiler.py
rmc_engine_v1/general_pipeline/symbolic_math_mea_evidence_bridge.py
rmc_engine_v1/general_pipeline/symbolic_math_rmc_delivery.py
rmc_engine_v1/general_pipeline/symbolic_math_language_vertical_slice.py
rmc_engine_v1/general_pipeline/gp013_natural_language_symbolic_math_vertical_slice.py
```

New verification/documentation files:

```text
scripts/test_natural_language_symbolic_math_vertical_slice_build_nlmath001_gp013.py
scripts/natural_language_symbolic_math_vertical_slice_build_nlmath001_gp013_verify.py
scripts/README_natural_language_symbolic_math_vertical_slice_build_nlmath001_gp013.md
scripts/MEA_NATURAL_LANGUAGE_SYMBOLIC_MATH_VERTICAL_SLICE_BUILD_NLMATH001_GP013_DELIVERY_MANIFEST.json
```

## Install Workflow

Run preflight before install. Stop if it reports any changed baseline file,
unexpected existing new file, symbolic link, payload hash mismatch, or dependency
mismatch.

After installation, run the complete verification packager. The live Proto-forge
verification is the authority for inherited GP-001 through MATH-001R1 and this new
vertical slice.

## Rollback

The installer creates an exact backup of modified existing files and records which
new files were added. If final post-install verification fails, use the printed backup
folder with `--rollback` to return exactly to the accepted MATH-001R1 baseline.


Runtime control note: This language slice uses a governed 15-second wall-time / 12-second CPU default for its isolated SymPy invocation to cover worker startup and bounded symbolic execution. These values remain within the existing MATH-001R1 resource-policy limits.
