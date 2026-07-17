# AI.Web Slice 38F Runtime Specification

## Component

`aiweb_language_core_bootstrap.predicate_role_frame_registry.capability_family_reference_registry`

## Runtime character

The component is an immutable, deterministic, read-only registry. It carries controlled identities and exact references only. It performs no I/O, network access, subprocess execution, resource loading, route lookup, tool lookup, memory access, delivery, or implementation.

## Public record families

- provenance references;
- namespace identity;
- effect-boundary identities;
- capability-family identities;
- frame-to-effect references;
- frame-to-capability-family references;
- capability/effect compatibility records;
- lifecycle authority record;
- lifecycle transitions;
- registry manifest.

## Exact lookup surface

The public lookup surface accepts exact Forge-owned IDs or exact `(namespace_id, key)` pairs only. It performs no case folding, whitespace repair, stemming, synonym expansion, nearest-known substitution, semantic similarity, model inference, dictionary fallback, or default reference insertion.

Unknown or malformed lookup values return `None` or an empty tuple. They never select a nearby identity.

## Validation law

All public validators are total and fail closed. Malformed values, invalid enums, unhashable values, wrong record kinds, invalid IDs, broken lineage, missing provenance, incorrect cross-references, authority-bearing booleans, fabricated routes, fabricated invocation IDs, fabricated argument bundles, fabricated permissions, fabricated execution receipts, and altered manifests must produce unsuccessful validation reports rather than escaping as uncaught exceptions.

## Controlled counts

- effect boundaries: 6
- capability families: 6
- frame effect references: 5
- frame capability references: 5
- capability/effect compatibility records: 6
- provenance records: 4
- lifecycle authority records: 1
- lifecycle transition rules: 19
- lifecycle transitions: 28
- active corrections: 0
- active conflicts: 0

## Non-operational reference fields

Each frame capability-family reference records:

- exact frame identity and version;
- exact capability-family identity and version;
- exact frame-effect reference;
- exact effect-boundary identity;
- relevance mode;
- availability status fixed to `not_proven`;
- relevance basis;
- authority dependencies;
- scope and non-scope;
- unknown-state policy;
- version, lifecycle state, and provenance.

The same record requires the following operational fields to remain absent or false:

- `capability_available = false`
- `route_identity = None`
- `route_available = false`
- `invocation_identity = None`
- `invocation_proposed = false`
- `invocation_authorized = false`
- `argument_bundle_id = None`
- `arguments_constructed = false`
- `permission_id = None`
- `permission_granted = false`
- `execution_receipt_id = None`
- `execution_performed = false`
- `result_verified = false`
- `tool_bound = false`
- `memory_operation_performed = false`
- `delivery_performed = false`
- `external_resource_admitted = false`
- `implementation_performed = false`

## Effect-boundary law

An effect boundary classifies the maximum architecture-level consequence category that could be relevant later. It does not satisfy permission, prove availability, resolve a route, invoke a capability, perform execution, validate evidence, grant memory authority, authorize delivery, admit external resources, or implement code.

## Closed-set law

The current admitted sets are exact. Deferred family names remain outside the registry. `request_non_authorizing` receives no capability-family reference. `protected_mathematical_operation` remains unbound to current general-language frames.

## Verification modes

The Slice 38F verifier supports:

- `source-only`: external construction inspection;
- `applied`: exact untracked application on the accepted parent;
- `precommit`: exact additions-only staged index;
- `committed`: exact parent, subject, path set, and clean repository.

The live application run uses `applied` mode and executes one Slice 38F behavior test followed by all 32 inherited language-core tests sequentially with output visible in the operator terminal.
