# CE-INTEGRATED-MULTIUSER-CORE-BUILD-002

## Purpose

This build upgrades the installed Contribution Economy from a founder bootstrap into a connected multi-user production spine. It integrates the canonical Identity Vault database, opaque contributor principal resolution, append-only consent/status lifecycle capability, Contribution Event proof compilation, Memory Capsule candidate composition, executable validation, empty core storage, and deny-by-default economic gates.

## Live writes allowed during installation

- Install reviewed Python modules and service/schema contract files.
- Add empty append-only v2 Identity Vault lifecycle tables and triggers; no contributor or consent row is inserted.
- Create an empty Contribution Economy core SQLite store and metadata manifest; all event/capsule/validation/finalization/mint/nullification tables remain empty.
- Replace the Build 001 ledger append entry points with a hard deny gate until later controlled activation.

## Live writes forbidden during installation

- No fake contributor enrollment.
- No new real contributor enrollment.
- No Contribution Event persistence.
- No persistent Memory Capsule candidate.
- No validation record persistence.
- No finalization, CT mint, Influence Ledger append, Investment Ledger append, nullification, public attribution, MEA mutation, RMC output-memory write, Chroma write, LLM call, network action, or API route exposure.

## Important preservation rule

The existing `ivp_nic_bogaert_contribution_owner_v1` Build 001 record remains the first lawful contributor principal and is resolved through a compatibility fallback. It is not rewritten, duplicated, or promoted into economic permission.

## Classification evidence rule

A typed contribution-event request may assert `CRT`, `CPT`, `BLD`, difficulty, and influence type, but Build 002 validation does not treat those assertions as proven. Candidate validation blocks advancement unless evidence confirmation is provided in a controlled verification context. This prevents claimed classification from becoming economic truth by assertion alone.
