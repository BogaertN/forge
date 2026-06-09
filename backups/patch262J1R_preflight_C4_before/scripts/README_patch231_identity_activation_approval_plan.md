# Patch 231 — Identity Activation Approval Plan

Purpose: create a Forge-owned activation approval plan only, before adding any preflight or activation mutation commands.

New Forge commands:

- `forge-agent-activation-plan`
- `forge-agent-activation-plan-report`

Boundary:

- This patch does not install an activation command.
- This patch does not install the preflight command yet.
- This patch does not activate Gilligan, Athena, Neo, or any other agent.
- This patch does not write live RMC memory.
- This patch does not mutate Identity Vault.
- This patch writes only a Forge-owned planning report under `/home/nic/forge/memory/aiweb_patch231_identity_activation_approval_plan_v1/`.

The plan defines:

- who/what may authorize activation,
- future command names,
- required preflight checks,
- hard blockers,
- allowed activation fields,
- fields that must never change automatically,
- rollback policy,
- expected Patch 231A preflight result language.

Expected runtime verdict:

`IDENTITY_ACTIVATION_APPROVAL_PLAN_WRITTEN`

That verdict is not activation. It is only a written control plan for future activation gates.
