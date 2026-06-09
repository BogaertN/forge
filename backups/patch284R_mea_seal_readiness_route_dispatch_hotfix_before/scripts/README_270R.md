# Patch 270R — Deep Pipeline Preflight Boundary Verification Repair

This patch repairs Patch 270's live preflight inconsistency where `activation_ready` could be `true` while `boundary_verifications` contained a failed containment-router check.

## Fix

Patch 270 incorrectly looked for `containment_router.boundary().projection_allowed == False`. The containment router correctly exposes this safety law under `routing_law.sealed_routes_cannot_project == True` and `routing_law.only_active_stack_may_reach_manifest == True`.

Patch 270R updates `deep_pipeline_preflight.py` to:

- support nested boundary flag paths such as `routing_law.sealed_routes_cannot_project`;
- verify containment router against its actual boundary contract;
- report `boundary_verifications_passed`;
- report `boundary_verification_failures`;
- force `activation_ready = false` if any installed boundary verification fails.

No live pipeline activation is performed. This remains read-only preflight.
