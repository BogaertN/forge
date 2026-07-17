# AI.Web Slice 38B Runtime Specification

## Identity

**Slice:** 38B — Deterministic Validation, Identity, Versioning, and Lifecycle
**Accepted parent HEAD:** `2809966f62d172cf8660f9acb343a92813e87d2b`
**Accepted parent tree:** `b02d41d21c72e7eae3c39ce04e71286b1b5bcbb0`
**Accepted parent subject:** `Slice 38A action-root and predicate-identity core schema`

## Purpose

Slice 38B adds pure, fail-closed governance machinery around the immutable
Slice 38A namespace, action-root, predicate-identity, and provenance records.
It supplies deterministic validation, stable lineage identity, strict version
compatibility, explicit lifecycle-transition law, duplicate refusal, mutation
refusal, reference integrity, and collection-level ancestry checks.

Slice 38B does not populate the registry and does not interpret language.

## Accepted resource boundary

The governed resource families are exactly:

- `PredicateNamespaceIdentity`
- `ActionRootIdentity`
- `PredicateIdentity`

`PredicateProvenanceReference` remains a separate custody record and is
required by every governed resource and every lifecycle-authority record.

The accepted Slice 38A source files remain unchanged. Slice 38B is isolated in:

```text
aiweb_language_core_bootstrap/
  predicate_role_frame_registry/
    governed_lifecycle/
```

The parent package does not auto-import this subpackage.

## Stable identity

Each immutable version record retains the Slice 38A canonical record ID. Slice
38B adds a distinct stable lineage ID:

- namespace lineage: resource kind + exact namespace key;
- action-root lineage: resource kind + exact namespace ID + exact action-root key;
- predicate lineage: resource kind + exact namespace ID + exact action-root ID + exact predicate key.

A lifecycle transition must preserve the same exact resource type, resource
kind, and stable lineage. A different key, namespace, action-root dependency,
or resource family is not a correction. It is a different lineage and the
transition fails closed.

## Version law

Versions must use canonical `vN`, `vN.N`, or `vN.N.N` form without leading
zeros. Every lifecycle transition must:

1. create a new immutable target record;
2. strictly advance the source version;
3. remain inside the same major version;
4. preserve the prior record;
5. identify source and target record IDs exactly;
6. preserve transition ancestry.

A same-version body change is refused as mutation. A breaking major-version
change is incompatible in Slice 38B and requires later separately governed
authority.

## Scope and non-scope law

Every governed record requires explicit non-empty scope and non-scope with no
overlap. A lifecycle transition may narrow scope, but it may not broaden scope.
It may add non-scope and prohibited-use boundaries, but it may not remove
predecessor non-scope or prohibited-use boundaries. It may not add a permitted
use inside an existing lineage. A materially broader permitted-use profile
requires separately governed authority and cannot enter through correction.

## Lifecycle law

The accepted Slice 38A enum remains unchanged. The `candidate` state is the
accepted record token for proposed material; Slice 38B does not mutate the
accepted predecessor enum merely to rename it `proposed`.

The lifecycle matrix explicitly governs:

- observed;
- candidate/proposed;
- reviewed;
- admitted;
- architecture-admitted;
- implementation-deferred;
- unknown;
- unresolved;
- ambiguous;
- unsupported;
- conflicted;
- quarantined;
- deprecated;
- superseded;
- rejected;
- withdrawn.

No state promotes automatically. Admission requires reviewed ancestry. Unknown,
unsupported, unresolved, or ambiguous material cannot transition directly to
admitted state. It must return through the same canonical lineage to candidate
review, then reviewed state, then a separate explicit admission decision.

Withdrawal is limited to candidate or reviewed material. It cannot erase or
withdraw an admitted resource. Admitted resources must use deprecation,
supersession, quarantine, or rejection under explicit authority.

Quarantine requires exact causes and release requirements. Release returns only
to reviewed state. Rejection requires blocked re-entry keys. Supersession
requires a distinct explicit successor and preserved predecessor ancestry.
Reopening rejected or withdrawn material requires a reference to the exact
accepted transition that created the rejected or withdrawn source record. A
non-empty but missing, unrelated, or rejected transition reference fails closed.

Quarantine release requires accepted quarantine ancestry for the exact source
record, exact resolution of every current quarantine-cause reference, and
exact custody of every current release requirement. An unrelated cause,
missing requirement, partial requirement set, or substituted requirement
cannot release the record.

Reopening rejected or withdrawn material requires a distinct new authority
record. The authority record that created the negative disposition cannot also
serve as the authority that reopens it.

Rejection must include the exact canonical lineage ID among its blocked
re-entry keys. An arbitrary alias alone is insufficient negative authority.

## Unknown and unsupported law

Unknown remains unknown. Unsupported remains unsupported.

The following are prohibited:

- nearest-known action-root substitution;
- nearest-known predicate substitution;
- semantic-similarity authority;
- embedding or vector fallback;
- capability availability as meaning authority;
- route or tool names as predicate identity;
- inferred intent as lifecycle authority;
- direct unknown-to-admitted promotion;
- direct unsupported-to-admitted promotion.

The transition and authority records carry explicit permanent false fields for
nearest-known substitution and similarity authority. The lifecycle evaluator
also requires source and target to preserve the same stable lineage.

## Duplicate and mutation refusal

The batch validator rejects:

- duplicate provenance IDs;
- duplicate authority IDs;
- duplicate transition IDs;
- duplicate resource IDs;
- exact duplicate records;
- two different records at the same lineage and version;
- orphan non-initial versions;
- multiple incoming transitions;
- multiple outgoing transitions;
- multiple terminal versions in one lineage;
- admission without admission ancestry;
- broken or cross-namespace references;
- admitted predicate dependencies that are not admitted;
- active resources that reference a historical non-current dependency version;
- deprecated or terminally unavailable dependency references;
- unsafe supersession references.

Every boolean in a lifecycle-authority record is validated as an exact Python
`bool`. Integers, strings, null values, and other truthy or falsey substitutes
cannot satisfy review, approval, or non-authority gates.

Public validation boundaries are malformed-input fail-closed. Exact record
objects carrying wrongly typed, unhashable, or non-serializable field values
return deterministic validation issues rather than leaking Python exceptions.
The behavior suite exercises 5,688 deterministic malformed-field cases across
provenance, resources, authority records, transitions, batches, and transition
evaluation.

## Authority boundary

Lifecycle authority is explicit, human-approved, scoped, provenance-bound,
version-reviewed, scope-reviewed, lifecycle-reviewed, non-LLM, and
non-executing.

It does not authorize:

- registry population;
- surface-term matching;
- action-root lookup;
- predicate selection;
- participant-role assignment;
- frame completion;
- candidate or selected meaning;
- capability routing;
- tool activation;
- action execution;
- evidence validation;
- memory read or write;
- rendering;
- delivery;
- release;
- production readiness.

## Determinism and effects

All records are frozen dataclasses. All public operations are pure in-memory
construction, identity calculation, validation, or assertion. Importing the
subpackage performs no work. The implementation uses the Python standard
library only and performs no filesystem, network, subprocess, database, model,
vector, embedding, routing, memory, rendering, or delivery operation.

## Expected zero-effect result

```text
admitted action-root population = 0
admitted predicate population = 0
participant-role registry population = 0
predicate-frame registry population = 0
capability routes = 0
runtime invocations = 0
actions = 0
memory writes = 0
rendering = 0
delivery = 0
```
