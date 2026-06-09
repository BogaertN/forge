# MATH-001R1 / GP-012R1 — Symbolic Mathematics Computation Kernel Governance Correction

## Purpose

This build replaces the rejected pre-install MATH-001 / GP-012R package. It retains the typed mathematical manifest, allowlisted recursive AST, isolated SymPy worker, resource limits, and twenty-six symbolic operation families. It removes the rejected parallel delivery-authority behavior.

## Correct production route

`typed SymbolicMathOperationManifest -> allowlisted recursive AST -> isolated SymPy worker -> verified execution receipt -> pending-governance receipt`

A successful computation is marked `COMPUTED_VERIFIED_PENDING_DOWNSTREAM_GOVERNANCE`. It is not rendered and is not delivered by this kernel. Any future user-facing delivery must pass through the existing Forge governance spine: `Manifest Contract v2 -> actual Echo validation -> DeliveryAuthorizationReceiptV2`.

## Preserved capability scope

The computation kernel supports twenty-six typed operation families: exact evaluation, simplification, expansion, factoring, trigonometric simplification and expansion, equation and system solving, inequality solving, differentiation, integration, limits, series expansion, summation, products, matrix determinant, inverse, RREF and eigen analysis, Euclidean distance, Pythagorean reasoning, geometry intersection, ordinary differential equation solving, commutators, tensor products, and substitution verification.

## Hard boundaries

This build adds no natural-language compiler, no raw mathematical source input, no arbitrary callable execution, no direct answer route, no new user question domain, no substitute Echo authority, no persistent memory write, no Identity Vault write, no Contribution Economy action, no CT mint, no ledger write, and no corpus ingestion. It installs no new dependencies; it binds only the already-authorized `sympy==1.14.0` and `mpmath==1.3.0` runtime support.
