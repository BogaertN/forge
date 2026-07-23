# Slice 46 — GP-014 Equivalence and Regression Proof Runtime Specification

Slice 46 proves equivalence; it does not modify the mathematical lane.

For each accepted positive fixture, the proof executes the direct GP-014 source
path twice and the explicitly enabled Slice 45 adapter path twice. It compares
question bytes, source status, source result hash, compiler and operation
manifest hashes, operation family, kernel and solution content, meaning and
contract hashes, rendered expression, selected candidate, candidate set, Echo
hash and DeliveryAuthorizationReceiptV2 hash.

For each accepted negative fixture, the proof requires the direct source and
the adapter-exposed source result to preserve the same refusal status, reasons,
non-delivery receipt, lack of expression receipt, lack of Echo approval and
lack of delivery authorization.

The proof separately injects three adapter-boundary failures: unavailable exact
binding, unexpected source exception and structurally invalid source result.
Every injected marker must remain absent from the outward record.

The package is inert on import, unregistered, local, deterministic and
in-memory. It adds no general-language, truth, evidence, permission, memory,
resource, route, UI, delivery, tool, action, production or release authority.
