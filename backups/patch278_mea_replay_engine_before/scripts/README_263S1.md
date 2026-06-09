# Patch 263S1 — Lifecycle Boundary Proof Correction

Patch 263S1 fixes a proof-surface inconsistency in Patch 263S.

Patch 263S correctly enforced confirmation tokens on restart, shutdown, and exit-window confirmation routes. However, the shared boundary object rendered by `/api/aiweb-os/lifecycle-manifest`, `/api/aiweb-os/status`, and `/api/aiweb-os/logs` reported:

- `requires_preview_before_confirm: false`
- `requires_exact_confirmation_token: false`

That was misleading for a final product surface because the lifecycle system as a whole is preview-first and exact-token gated for mutating actions.

This patch changes the boundary payload so the global lifecycle safety contract reports:

- `preview_before_confirm_required_for_confirming_actions: true`
- `exact_confirmation_token_required_for_confirming_actions: true`
- `requires_preview_before_confirm: true`
- `requires_exact_confirmation_token: true`

It also adds per-action fields so read-only endpoints remain semantically clear:

- `this_action_requires_preview_before_confirm`
- `this_action_requires_exact_confirmation_token`

No frontend behavior changes are required. No shell route, arbitrary command route, RMC memory write, Identity Vault write, Chroma write, or LLM call is added.
