# GP-007 — Strict Typed AST and Safe Solver Adapter Boundary

## Purpose

GP-007 migrates only the existing `linear_equation_one_unknown` capability onto
an explicit syntax-and-execution boundary:

```text
question
→ AI.Web-owned strict token/grammar parser
→ canonical typed AST
→ AST hash binding in the service request
→ Forge-owned exact-Fraction safe solver adapter
→ adapter execution receipt
→ existing governed gate
→ RMC meaning manifest
→ renderer
→ Echo approval
```

## Why this build exists

GP-006 recorded future parser/solver dependencies as review-only candidates.
GP-007 does not promote any of them. Instead, it establishes the production
contract that any later Lark or SymPy-backed implementation would have to
satisfy: complete input consumption, typed syntax, hash-bound adapter inputs,
no raw expression evaluation, independent verification, and no downstream
authority bypass.

## New protection

The previously supported linear equation family remains supported. These forms
are now explicitly refused by the strict typed-AST boundary:

- `x + y = 10`
- `2(x + 3) = 14`
- `x^2 = 9`
- `sin(x) = 1`
- `solve 3x + 5 = 20 for y`
- `3x + 5 = 20 and then graph it`
- decimal/coefficient or zero-coefficient forms outside the current contract

## Scope boundaries

GP-007 adds no new problem domain, no third-party dependency, no corpus
ingestion, no route or UI, no MEA modification, no persistent memory write, no
Identity Vault write, no Contribution Economy write, no ledger entry, and no
CT mint.
