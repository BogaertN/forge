# General Pipeline Capability Service Contracts — Build GP-005

## Build identity

- Build ID: `GENERAL-PIPELINE-CAPABILITY-SERVICE-CONTRACTS-BUILD-GP-005`
- Schema: `general_pipeline_capability_services_v1_build_gp005`
- Depends on sealed baseline: `GENERAL-PIPELINE-PRODUCTION-REGROUND-BUILD-GP-004`

## Purpose

GP-004 made installed capabilities explicit and prevented instructional source text
from creating executable authority. GP-005 creates the execution boundary those
capabilities must pass through when the answering pipeline uses them.

A capability is not an agent and does not receive independent authority. In
GP-005 every runtime computation used by `answer_question()` is bound to:

1. an immutable Forge-owned `CapabilityServiceContract`,
2. a canonical `CapabilityInvocationRequest`,
3. a hash-bound `CapabilityExecutionReceipt`,
4. the existing governed gate,
5. the existing RMC meaning compiler,
6. the existing renderer and Echo approval.

## What this adds

- `capability_services.py`: typed service contracts, request envelopes, execution
  receipts, tamper rejection, and service-bound execution dispatcher.
- `gp005_capability_services.py`: GP-005 activation/status surface.
- Pipeline trace fields for service contract, request, and receipt hashes.
- MEA open-manifest facts identifying the Forge service boundary and its
  invocation authority policy.
- GP-005 behavior and static/live verification suites.

## What this changes

- `pipeline.py` no longer invokes `domain.execute(parsed)` directly. It routes
  the already-parsed question through `execute_registered_capability(parsed)`.
- `manifest_builder.py` records the selected service identity and invocation
  policy in the open MEA manifest.
- `__init__.py` exports the service-contract trace types and status helpers.

## Explicit non-scope

This build does not add:

- new reasoning or language domains,
- third-party dependencies,
- corpus ingestion or indexing,
- PDF extraction,
- source-provenance records,
- routes or UI,
- persistence or memory writes,
- Identity Vault writes,
- Contribution Economy writes,
- CT minting,
- ledger activity.

## Authority boundary

A GP-005 service may execute bounded computation in memory and emit a receipt.
It cannot seal the MEA manifest, compile meaning, render language, approve
Echo, write memory, modify identity state, or mint credit.
