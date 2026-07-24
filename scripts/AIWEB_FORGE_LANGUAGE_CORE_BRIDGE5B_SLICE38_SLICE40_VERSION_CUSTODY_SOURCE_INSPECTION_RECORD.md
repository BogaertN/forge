# Bridge 5B Source Inspection Record

## Accepted source identity

- Repository: `/home/nic/forge`
- Branch: `main`
- HEAD: `35b3fc1de6fe52788ec0a2465e73b1448ad6fc04`
- Parent: `492d85032342aabbcf328b15110bc34b19ec8ca2`
- Tree: `9a5f697685f3e65fe4e61b101fd9a784f28a075c`
- Subject: `Forge language bridge 5A lineage compatibility correction`

## Source evidence

- Post-Bridge-5A eligibility seam packet: `6eef64608ce15304ee2d6b9ed5d4158ee39ff2d29fb05eff1434b2b07968910c`
- Gate-authority construction supplement: `d1d16bc627e66d54205ab60f971a22897371a4a2ee12834a7a005f1c59832dad`
- Supplement files captured: 548
- Supplement construction-reference records: 451
- Supplement warnings: 0

## Findings

1. Slice 38C's current admitted predicates are version `v1.3.0`.
2. Slice 38E's current admitted predicate frames are version `v1.1.0`.
3. Slice 38G preserves those exact IDs and versions in predicate and role-layout candidates.
4. Slice 40C through Slice 40F hard-code predicate and frame version `v1.0.0` in family record and evaluation-input validation.
5. The captured source contains no admitted adapter authorizing relabeling current registry records as `v1.0.0`.
6. Existing Slice 40 tests use frozen `v1.0.0` fixture IDs, so their compatibility must remain intact.
7. The correction therefore adds exact registry custody without weakening the legacy path or accepting arbitrary versions.

## Tested result

The new regression constructs a real Slice 37-to-38 inspect branch,
preserves its exact predicate and frame identities, validates all four
Slice 40 family inputs, and obtains four `INDETERMINATE` family results
under absent authority. It does not perform Slice 40G composition, Slice
40H custody, Slice 41C eligibility, or selected-meaning construction.
