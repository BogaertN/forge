# AI.Web Slice 38E — Predicate-Frame Constraints and Role Compatibility Runtime Specification

Slice 38E adds a closed, immutable, read-only predicate-frame registry anchored only to the five action roots admitted by Slice 38C and using only the eleven participant-role identities admitted by Slice 38D.

The registry contains five architecture-admitted frames:

1. `inspect_read_only`
2. `report_attributed_content`
3. `request_non_authorizing`
4. `verify_bounded_review`
5. `simulate_non_live`

Each frame declares exact linked action-root and predicate identities, required, optional, prohibited and conditional roles, cardinality, co-requirements, conflicts, role-to-concept compatibility policy, speech-act contexts, scope constraints, effect classification, authority dependencies, structural-state policies, version, provenance, and lifecycle ancestry.

Role-to-concept compatibility is intentionally fail-closed. Semantic-class references are review filters only. Semantic-class membership is not sufficient. Exact concept allowlists remain empty, exact admitted concept support is required later, and absent exact support remains unknown. This prevents the limited Slice 37 concept registry from being silently broadened into general semantic authority.

A structurally complete frame is not selected meaning, gate passage, permission, capability availability, route, invocation, execution, proof, memory authority, rendering authority, or delivery authority.

Slice 38E installs no source-term lookup, occurrence interpretation, frame selection, occurrence role assignment, CandidateMeaning construction, gate outcome, capability reference, route, tool, action, evidence validation, memory access, rendering, delivery, LLM authority, similarity fallback, or nearest-known-frame substitution.
