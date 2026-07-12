# AI.Web Slice 25 — Repository Hygiene Scaffold v2

Slice 25 resolves one exact historical planning record, one exact test-generated
structural probe, and one exact source-tree Python-cache condition. It does not
begin the language-core bootstrap.

## Accepted design scope

Slice 25 may:

- preserve the exact historical JSON in a verified quarantine;
- remove that exact JSON from its active legacy memory path after preservation;
- preserve the exact Slice 24 dry structural probe and remove it from the live
  repository after preservation;
- isolate future Slice 24 dry structural probes in temporary directories outside
  the repository;
- preserve and remove only `agents/__pycache__` and
  `agents/forge/__pycache__`;
- exclude `.venv` and `venv` from the Slice 24 source-tree cache scan;
- keep source-tree `__pycache__`, `*.pyc`, and `*.pyo` as acceptance blockers;
- add read-only tests and verifiers for the repository-hygiene boundary.

## Managed environments

Managed virtual environments normally contain Python bytecode. Their ignored
bytecode is not active Forge source and is excluded from source-tree acceptance
scanning. The scanner remains read-only.

## Preserved evidence

Historical JSON:

`memory/forge_build_sequence_v1/20260712_054028_forge_build_sequence_v1.json`

Classification: preserved historical planning evidence; noncanonical; nonpatch;
nonexecution; nonruntime authority.

Structural probe:

`.slice24_structural_probe/slice24_acceptance_result.json`

Classification: preserved test-generated dry structural evidence; nonaccepted;
nonruntime authority.

## Protected paths

Slice 25 does not modify `main.py`, `.gitignore`, `.venv`, `venv`, GP-014
behavior, or the separate `/home/nic/aiweb` repository.

## Hard boundary

Slice 25 creates no language runtime, route, memory, evidence mutation, external
resource admission, delivery, tool routing, action execution, GP-014
supersession, release, production-readiness claim, or GitHub push.

## Verification

Applied pre-commit state:

```bash
/usr/bin/python3 -B scripts/test_aiweb_slice25_repository_hygiene_scaffold.py /home/nic/forge --state applied
/usr/bin/python3 -B scripts/aiweb_slice25_repository_hygiene_verify.py /home/nic/forge --state applied
```

Committed state:

```bash
/usr/bin/python3 -B scripts/test_aiweb_slice25_repository_hygiene_scaffold.py /home/nic/forge --state committed
/usr/bin/python3 -B scripts/aiweb_slice25_repository_hygiene_verify.py /home/nic/forge --state committed
```

A passing test or verifier is not acceptance by itself. Slice 25 still requires
a result packet, full clean post-commit acceptance, and a Decision Record.
