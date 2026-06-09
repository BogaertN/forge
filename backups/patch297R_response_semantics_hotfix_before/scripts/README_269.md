# Patch 269 — ChristPing 7-Gate Resurrection Engine Preview

## Module
`forge/rmc_engine_v1/resurrection_engine.py`

## Endpoint
`/api/rmc/resurrection-preview`

## Seven gates
| Gate | Name | Failure outcome |
|---|---|---|
| 1 | SPC_TIER_WARM | no_resurrection_path |
| 2 | RESURRECTION_LIMIT | deep_archive_seal |
| 3 | PHI9_ELIGIBILITY | defer_until_next_phi9 |
| 4 | INVARIANT_CORE_PRESENT | defer |
| 5 | DRIFT_SIGNATURE_VALID | defer or deep_archive_seal if breach |
| 6 | RESONANCE_COMPARATOR | defer (MISMATCH is not deletion) |
| 7 | SYSTEM_CAPACITY | ghost_loop_containment_required |

## Decisions
- All 7 pass + Gate 6 MATCH → `resurrection_candidate`
- Gate 7 fails → `ghost_loop_containment_required`
- Limit exceeded / breach → `deep_archive_seal`
- COLD/DEEP tier → `no_resurrection_path_tier_not_warm`
- Normal gate fail → `defer_until_next_phi9_window`

## Boundary
Read-only. No writes, no SPC mutation, no runtime re-entry, no projection.
ψ′ is not restoration — it is a transformed identity constituted by collapse history.
Requires operator approval to activate (future patch).

## Tests: 78/78 pass. Verifier: 23/23.

## Install
```bash
tar -xzf ~/patch269_resurrection_engine_preview.tar.gz
python3 forge/scripts/patch269_verify.py
```
