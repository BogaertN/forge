# General Pipeline Dependency and License Registry — Build GP-006

## Build identity

- Build ID: `GENERAL-PIPELINE-DEPENDENCY-LICENSE-REGISTRY-BUILD-GP-006`
- Schema: `general_pipeline_dependency_license_registry_v1_build_gp006`
- Depends on sealed baseline: `GENERAL-PIPELINE-CAPABILITY-SERVICE-CONTRACTS-BUILD-GP-005`

## Purpose

GP-005 established bounded Forge-owned capability service execution. GP-006
adds the dependency and licensing authority boundary that must exist before a
third-party parser, solver, unit library, document extractor, corpus indexer,
testing framework, or language checker may be introduced into that service
spine.

This build does **not** install those tools. It records their intended role and
observed upstream license posture as review-only governance candidates while
binding the current execution services only to:

1. AI.Web-owned General Pipeline internal executor source; and
2. the preexisting Python standard-library runtime already used by Forge.

## What this adds

- `dependency_registry.py`: immutable dependency/license records, deterministic
  registry hashing, active-runtime binding validation, candidate review records,
  and a hard license hold record for PyMuPDF.
- `gp006_dependency_license_registry.py`: GP-006 activation/status surface.
- Pipeline trace fields containing the active dependency registry hash, boundary
  record, and the two dependency records actually used by the current execution
  path.
- MEA open-manifest facts identifying dependency policy, registry hash, and the
  active runtime dependency records.
- GP-006 behavior and static/live verification suites.

## Current active execution dependencies

Current GP-001 through GP-005 capabilities remain attached only to:

- `dep.aiweb.general_pipeline.internal_executor.v1`
- `dep.python.standard_library.runtime.v1`

The Python record describes an already-present Forge runtime; GP-006 does not
install Python or alter the virtual environment.

## Review-only future candidates

GP-006 records these tools as future candidates only. They may not execute,
install, or bind to capability services through this build:

- Lark — future formal grammar parsing boundary; upstream repository identifies
  the main library as MIT and notes its standalone tool is MPL-2.0.
- SymPy — future typed-AST-fed symbolic algebra solver; upstream project states
  BSD licensing. Raw user strings must never be passed directly to its parsing
  boundary.
- Pint — future physical quantity and unit conversion service; upstream project
  states BSD licensing.
- SQLite FTS5 — future local deterministic full-text corpus index; SQLite states
  its source code is in the public domain.
- pypdf — future approved-source PDF extraction candidate; upstream license file
  contains BSD-3-Clause terms.
- pdfplumber — future layout-sensitive PDF extraction candidate; upstream
  license file contains MIT terms and transitive dependencies still require
  review.
- Hypothesis — future property/adversarial test harness; upstream source carries
  Mozilla Public License 2.0 notices.
- Z3 — future constraint/consistency service; upstream repository identifies MIT
  licensing.
- LanguageTool — future spelling/grammar candidate generator; upstream records
  identify LGPL licensing and language/resource components still require
  separate review.

## Explicit hold

- PyMuPDF is recorded as `HOLD_LICENSE_BOUNDARY`, not as an install candidate.
  Official project material states AGPL obligations or commercial licensing
  apply. AI.Web must make an explicit licensing decision before any production
  use.

## Evidence boundary

The license observations in this build are governance metadata captured from
upstream/official project materials on `2026-05-31`. They are not legal advice.
Every candidate must be refreshed, version-pinned, dependency-tree-reviewed,
and separately approved before it can be installed or bound to a production
capability.

## Explicit non-scope

This build does not add:

- a new reasoning or language domain,
- any third-party import or package installation,
- a parser, solver, unit service, PDF extractor, corpus database, or spellchecker,
- source provenance holding records for authors or institutions,
- corpus ingestion or indexing,
- routes or UI,
- persistence or memory writes,
- Identity Vault writes,
- Contribution Economy writes,
- CT minting,
- ledger activity.

## Authority boundary

A current capability service may execute only while its contract binds the
approved active dependency records and the current dependency registry hash.
A review-only or held dependency cannot be substituted into an invocation
request; construction or execution fails before the tool can run.
