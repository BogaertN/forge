# AI.Web Slice 43A RMC Echo Core Schema and Authority Boundary Specification

## Status

Schema-only increment. No validator, comparator, drift classifier, materiality
engine, disposition engine, rejection issuer, containment issuer, repair engine,
MSM adapter, delivery gate, or bootstrap integration is installed.

## Accepted parent

- Repository: `/home/nic/forge`
- Branch: `main`
- HEAD: `ebe931909b59a40ac4ef202b89d8f4f2702104a3`
- Tree: `efab06b171dfd5a34b56c0cff81026788e40a1e0`
- Subject: `Slice 42H disabled bootstrap integration and Slice 42 closeout`

## Package

`aiweb_language_core_bootstrap.rmc_echo_runtime`

## Purpose

Define immutable typed custody contracts for the exact future relationship
between an authorized Slice 42 meaning chain and its proposed unvalidated
expression while preventing schema existence from becoming Echo authority.

## Admitted schema types

1. `AuthorizedMeaningReferenceRecord`
2. `ProposedExpressionReferenceRecord`
3. `EchoValidationInputBoundaryRecord`
4. `PreservationDimensionRequirementRecord`
5. `ValidationFindingBoundaryRecord`
6. `DriftFindingBoundaryRecord`
7. `EchoDispositionBoundaryRecord`
8. `EchoRejectionBoundaryRecord`
9. `EchoContainmentBoundaryRecord`
10. `EchoTraceBoundaryRecord`
11. `EchoReceiptBoundaryRecord`
12. `RmcEchoRuntimeSchemaRecord`

Schema-only enums:

1. `EchoValidationInputCustodyState`
2. `ValidationFindingCustodyState`
3. `DriftFindingCustodyState`
4. `EchoDisposition`
5. `EchoDispositionCustodyState`
6. `RejectionCustodyState`
7. `ContainmentCustodyState`
8. `PreservationDimension`

## Preservation dimensions

The schema carries separate dimensions for selected identity and lineage, active
scope, negation, modifiers, certainty and claim strength, modality and
conditional scope, time and operational status, evidence boundary, inherited
limitations, qualifications, caveats, refusal/containment, unresolved
ambiguity, unsupported state, action/proposal/simulation/observation,
permission versus request, privacy/identity, memory, external-resource status,
delivery authority, economic/ledger boundary, and non-LLM provenance.

## Exact custody chain

`AuthorizedMeaningReferenceRecord`
+ `ProposedExpressionReferenceRecord`
→ `EchoValidationInputBoundaryRecord`
→ `PreservationDimensionRequirementRecord`
→ validation-finding boundary
→ drift-finding boundary
→ disposition boundary
→ rejection/containment boundaries
→ trace and receipt boundaries.

This chain is schema custody only. No transition or decision in the chain occurs
in Slice 43A.

## MSM-v1 decision

Decision value:

`deferred_to_slice43g_exact_additive_adapter`

The existing dormant `ValidationLinkRecord` is protected. Slice 43A does not
instantiate it or modify MSM-v1.

## Historical Echo decision

The Slice 19 scaffold and legacy `rmc_engine_v1` Echo files remain protected
historical evidence. The new package imports or calls none of them.

## Hard boundary

Slice 43A does not admit, compare, validate, classify, decide, reject, contain,
repair, approve, integrate, deliver, execute, route, read or write memory, read
or write the filesystem, access a network, load an external resource, call a
model, or alter GP-014.

## Deferred work

- 43B: deterministic validation, identity, versioning, serialization, lifecycle;
- 43C: exact authorized-meaning and proposed-expression admission;
- 43D: meaning-preservation comparison and validation findings;
- 43E: drift classification and materiality;
- 43F: Echo disposition, rejection, and containment issuance;
- 43G: additive MSM-v1 validation-link custody;
- 43H: disabled bootstrap integration and Slice 43 closeout;
- all delivery, tool, action, memory-write, public-route, and product authority.
