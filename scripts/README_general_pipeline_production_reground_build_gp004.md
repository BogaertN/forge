# General Pipeline Production Reground — Build GP-004

## Purpose

GP-004 hardens the already-built General Pipeline without adding a new domain. It replaces mutable domain-list/compiler-wrapper activation with a centralized bounded capability registry and closes the verified partial-match parsing defect in the linear-equation path.

## Installed capabilities after activation

- `cap.math.fraction_change_capacity.v1`
- `cap.math.whole_number_arithmetic.v1`
- `cap.math.linear_equation_one_unknown.v1`
- `cap.math.multi_step_count_change.v1`

## Enforced boundaries

- Capabilities are computation-only; they cannot render final output directly.
- Source text may support an installed capability but cannot install or register a capability.
- Every capability contract forbids persistent memory writes, Identity Vault writes, Contribution Economy writes, and CT minting.
- No corpus ingestion, no routes, no UI changes, no new language/spelling domain, and no third-party dependency are included in GP-004.

## Parser hardening included

- Equations require a complete supported expression; `x + y = 10`, parentheses, powers, mismatched requested variables, and trailing unsupported content refuse.
- Direct arithmetic refuses ignored leading or trailing content.
- Capacity problems refuse extra trailing instructions.
- Multi-step count-change narratives require every event clause in the supported narrative form to be recognized; unparsed numeric events refuse.

## Required tests after installation

Run the six existing GP-001 through GP-003 checks, then:

```bash
cd ~/forge
source .venv/bin/activate
python scripts/test_general_pipeline_production_reground_build_gp004.py --forge-root "$HOME/forge"
python scripts/general_pipeline_production_reground_build_gp004_verify.py --forge-root "$HOME/forge"
```

The delivered packet also includes a results-bundle helper so all eight receipts can be packaged for audit.
