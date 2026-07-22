# AI.Web Slice 43B Deterministic Validation, Identity, Versioning, and Lifecycle Runtime Specification

## Status

Additive validation-and-custody increment beneath:

`aiweb_language_core_bootstrap.rmc_echo_runtime.governed_lifecycle`

No accepted Slice 43A file is modified.

## Accepted parent

- Repository: `/home/nic/forge`
- Branch: `main`
- HEAD: `32719319e3df8dcde42f3ececcb14863d2c541b8`
- Parent: `ebe931909b59a40ac4ef202b89d8f4f2702104a3`
- Tree: `d84b9a8e9f612d1ed461bb3785aef52d2acabbef`
- Subject: `Slice 43A RMC Echo core schema and authority boundary`

## Purpose

Slice 43B supplies deterministic structural governance for the immutable Slice
43A RMC Echo schema:

1. canonical UTF-8 JSON serialization with exact dataclass field order;
2. deterministic SHA-256 record and governance-bundle identities;
3. supported Slice 43A schema, specification, and Slice 43B profile versions;
4. exact accepted-parent and predecessor-reference custody;
5. immutable validation and lifecycle successor records;
6. a closed explicit lifecycle transition law;
7. malformed-record, unknown-version, duplicate-record, identity-collision, and
   inconsistent-reference rejection;
8. fail-closed cross-record consistency checks.

## Canonical identity law

Canonical records use:

- admitted dataclass field order;
- enum values rather than implementation representations;
- tuples represented as ordered arrays;
- string-key mappings sorted lexicographically;
- UTF-8 JSON;
- no insignificant separator whitespace;
- SHA-256 only;
- no timestamps, randomness, process identity, filesystem state, environment
  state, or hash-table iteration order.

The identity field itself is excluded from each record digest. Bundle ID and
bundle digest are excluded from the governance-bundle digest. All other fields
remain identity-bearing.

## Exact record custody

Slice 43B governs all twelve Slice 43A record types plus:

- `RmcEchoVersionCustody`;
- `RmcEchoLifecycleRecord`;
- `RmcEchoLifecycleTransitionRecord`;
- `RmcEchoGovernanceBundle`.

## Cross-record consistency

Validation requires the exact internal custody chain:

authorized-meaning reference + proposed-expression reference
→ validation-input boundary
→ one requirement for each of the 22 preservation dimensions
→ one validation-finding boundary per dimension
→ one drift-finding boundary per dimension
→ disposition boundary
→ rejection and containment boundaries
→ trace boundary
→ receipt boundary
→ aggregate RMC Echo schema record.

It also requires exact shared lineage, Slice 42G integration references,
successor-manifest reference, governed-outward-meaning reference,
expression-plan reference, preservation-obligation reference, finding and drift
reference sets, trace ancestry, receipt ancestry, schema versions, and
predecessor custody.

## Lifecycle law

Successful validation stages are:

`schema_declared → version_bound → predecessors_bound →
cross_record_validated → record_validated → record_sealed`.

Every transition is explicit. Automatic progression is prohibited. Incomplete,
unknown-version, malformed, invalid-predecessor, duplicate-record, and
identity-collision outcomes are separate blocked states. Resumption begins a
new immutable successor chain and preserves the blocked predecessor identity.

## Authority-zero law

A structurally valid, canonically serialized, identity-valid, lifecycle-sealed
record is not an Echo decision and is not source admission.

Slice 43B does not:

- admit any Slice 42 source record;
- compare authorized meaning with proposed expression;
- create semantic validation findings;
- classify drift or decide materiality;
- decide `PASSED`, `REJECTED`, or `CONTAINED`;
- issue rejection or containment;
- repair or rewrite selected meaning or expression text;
- create or integrate an MSM-v1 validation link;
- modify or migrate MSM-v1;
- enable bootstrap integration;
- deliver output;
- determine truth, validate evidence, grant permission, or authorize execution;
- create routes or APIs, invoke tools, perform actions, access or write memory,
  touch the filesystem or network, or load external resources;
- use an LLM, EchoForge, embedding, vector, RAG, similarity engine, neural
  parser, hidden classifier, confidence score, probability rank, or nearest
  known substitution;
- supersede GP-014.

## Deferred work

- 43C: exact accepted Slice 42 authorized-meaning and expression admission;
- 43D: deterministic meaning-preservation comparison and findings;
- 43E: drift type and materiality classification;
- 43F: Echo disposition, rejection, and containment issuance;
- 43G: additive MSM-v1 validation-link custody;
- 43H: disabled bootstrap integration and Slice 43 closeout.
