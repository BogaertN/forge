# AI.Web Forge Bridge 5B Decision

## Decision

Do not build the full Bridge 5 gate-composition and eligibility route yet.
The accepted post-Bridge-5A source proves a narrower compatibility defect
between the real Slice 38 registry versions and the Slice 40C through 40F
gate-family validators.

The current admitted Slice 38 predicate identity is version `v1.3.0` and
the linked current predicate-frame identity is version `v1.1.0`. The four
Slice 40 family validators accept only the earlier `v1.0.0` fixture pair.
Consequently, exact current Slice 38 ancestry cannot enter those validators
without either being rejected or being falsely relabeled as `v1.0.0`.

Bridge 5B preserves the existing frozen `v1.0.0` path and adds one exact
current-registry path. A non-legacy pair is accepted only when:

1. the predicate ID resolves in the admitted built-in predicate registry;
2. the supplied predicate version exactly equals that admitted record;
3. the frame ID resolves in the admitted predicate-frame registry;
4. the supplied frame version exactly equals that admitted frame record;
5. the frame's linked predicate ID exactly equals the supplied predicate ID.

Arbitrary semantic versions, unknown IDs, mixed legacy/current pairs, and
cross-predicate frame pairs remain rejected.

## Authority boundary

This is a compatibility correction only. It does not construct production
gate authority, compose gate results, create Slice 40H custody, evaluate
Slice 41C selection eligibility, construct selected meaning, route a tool,
execute an action, write memory, invoke an LLM, or run a simulation.

## Required predecessor

- HEAD: `35b3fc1de6fe52788ec0a2465e73b1448ad6fc04`
- Parent: `492d85032342aabbcf328b15110bc34b19ec8ca2`
- Tree: `9a5f697685f3e65fe4e61b101fd9a784f28a075c`
- Subject: `Forge language bridge 5A lineage compatibility correction`
- Post-Bridge-5A source packet SHA-256: `6eef64608ce15304ee2d6b9ed5d4158ee39ff2d29fb05eff1434b2b07968910c`
- Gate-authority supplement SHA-256: `d1d16bc627e66d54205ab60f971a22897371a4a2ee12834a7a005f1c59832dad`
