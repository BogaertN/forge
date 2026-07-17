# AI.Web Slice 38F — Capability-Family Reference and Effect-Boundary Decision

## Decision status

Architecture implementation decision for the bounded Slice 38F runtime registry.

## Accepted parent

- Repository: `/home/nic/forge`
- Branch: `main`
- Parent HEAD: `93e0fcf5322f8beae9fe8ed7e0d57805f2c63674`
- Parent tree: `c2b2ae647a1ca45cf83927b9ccef39941e85067e`
- Parent subject: `Slice 38E predicate-frame constraints and role compatibility`

## Governing purpose

Slice 38F permits an admitted predicate frame to carry an immutable, non-operational reference indicating that a controlled capability family may become relevant to later governed processing. It also gives every admitted frame an explicit effect-boundary classification.

A reference is architecture metadata. It is not a wire, route, callable, tool registration, availability proof, argument bundle, permission record, execution plan, execution receipt, result proof, memory operation, delivery operation, resource-admission decision, or implementation action.

## Binding separation law

- capability reference is not capability availability;
- capability availability is not a route;
- a route is not an invocation;
- an invocation proposal is not authorization;
- an invocation proposal is not execution;
- frame completion is not permission;
- effect classification is not permission;
- capability-effect compatibility is not capability availability;
- relevance is not argument construction;
- occurrence is not proof.

## Admitted effect boundaries

The closed Slice 38F effect-boundary set is:

1. `no_action`
2. `read_only`
3. `communicative_only`
4. `verification_review_only`
5. `simulation_only`
6. `protected_mathematical_output_only`

These classifications describe only the maximum kind of consequence a meaning could later be considered for after separate authority, availability, route, permission, execution, and proof layers exist and pass.

## Admitted capability families

The closed Slice 38F capability-family set is:

1. `read_only_inspection`
2. `source_comparison`
3. `draft_preparation`
4. `verification_review`
5. `non_live_simulation`
6. `protected_mathematical_operation`

## Deferred candidates

The following roadmap candidates remain intentionally unadmitted:

1. `memory_request`
2. `software_change_proposal`
3. `delivery_request`

They are deferred because each crosses a later authority boundary involving memory access, code change, or delivery. Naming them in the roadmap does not create a registry identity.

## Exact admitted frame references

### Frame effect boundaries

- `inspect_read_only` → `read_only`
- `report_attributed_content` → `communicative_only`
- `request_non_authorizing` → `no_action`
- `verify_bounded_review` → `verification_review_only`
- `simulate_non_live` → `simulation_only`

### Frame capability-family relevance

- `inspect_read_only` → `read_only_inspection`
- `inspect_read_only` → `source_comparison`
- `report_attributed_content` → `draft_preparation`
- `verify_bounded_review` → `verification_review`
- `simulate_non_live` → `non_live_simulation`

`request_non_authorizing` intentionally carries no capability-family reference. A request remains a request and does not silently become a route or action proposal.

`protected_mathematical_operation` is admitted as a controlled family identity but remains unbound to the five Slice 38E frames. This preserves the GP-014 mathematical-output boundary without converting it into general-language capability authority.

## Lifecycle and provenance

Every admitted effect boundary, capability family, frame effect reference, frame capability reference, and compatibility record has:

- deterministic identity;
- stable lineage identity;
- candidate ancestry;
- architecture-admitted current version;
- explicit provenance;
- scope and non-scope;
- authority dependencies;
- unknown-state policy;
- immutable transition evidence.

The registry contains 28 candidate-to-architecture-admitted transitions. Every transition requires human approval, preserves the prior record, prohibits in-place mutation, and creates no availability, route, invocation, permission, execution, or result proof.

## Explicitly absent

Slice 38F installs none of the following:

- source-term lookup;
- occurrence-level frame selection;
- occurrence-level role assignment;
- candidate-meaning creation;
- selected meaning;
- gate outcome;
- capability availability registry;
- route registry;
- invocation registry;
- argument builder;
- tool activation;
- action execution;
- evidence validation;
- memory access;
- rendering;
- delivery;
- external-resource loading or admission;
- implementation authority;
- default capability references;
- nearest-known substitution;
- semantic-similarity authority;
- LLM authority.

## Acceptance boundary

Passing Slice 38F tests proves only that this exact closed, deterministic, architecture-only reference and effect-boundary registry behaves as specified. It does not prove general predicate understanding, capability availability, live routing, tool use, action execution, complete RMC, complete Forge, release readiness, or production readiness.
