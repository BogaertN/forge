# AI.Web Slice 24 — Full Regression and Acceptance Bundle Scaffold

Slice 24 is a proof-and-acceptance scaffold, not a feature slice.

## Purpose

Run and prove the accepted scope from Slice 1 through Slice 23 together by
using the active current verifier/test/context/source-guard matrix.

## Hard Boundary

Only exact passed scope is accepted. No broad general-language claim is allowed
unless the full required proof set passes in the recorded local context.

Slice 24 does not make live runtime authority. It does not write memory, promote
external resources, deliver output, execute actions, register routes, modify
configuration, or grant UI authority.

## Why There Are Two Modes

During patch application and staging, the repository is intentionally not clean
because the Slice 24 files are untracked or staged. In those phases the verifier
performs structural/source-behavior proof only.

After Slice 24 is committed and the Forge working tree is clean, the verifier can
be run with `--run-acceptance` to execute the full active command matrix and
produce the final acceptance result packet.

## Main Commands

Structural verification:

```bash
/usr/bin/python3 scripts/aiweb_slice24_full_regression_acceptance_bundle_verify.py /home/nic/forge
```

Full acceptance run after clean commit:

```bash
/usr/bin/python3 scripts/aiweb_slice24_full_regression_acceptance_bundle_verify.py /home/nic/forge --run-acceptance --result-dir /home/nic/Downloads/AIWEB_SLICE24_ACCEPTANCE_RESULTS_<STAMP>
```

The full acceptance result writes `slice24_acceptance_result.json` plus command
stdout/stderr records into the chosen result directory.

## Python Cache Acceptance Policy

The final acceptance context distinguishes managed-environment bytecode from
source-tree bytecode:

- `.venv/` and `venv/` are managed Python environments. Their ignored bytecode
  does not make the Forge source tree dirty and is excluded from the cache scan.
- `__pycache__/`, `*.pyc`, and `*.pyo` inside the active source tree remain
  acceptance blockers.
- The scanner is read-only. It does not remove caches.
- Acceptance commands run with bytecode writing disabled or redirected outside
  the repository so the proof run does not create source-tree caches.

Git cleanliness and source-tree cache cleanliness are separate requirements. A
cache may be ignored by Git and still be prohibited inside active source paths.

## Structural Probe Isolation

The structural verifier writes its dry acceptance result only inside a temporary
directory outside the Forge repository. It must not create or retain
`.slice24_structural_probe` in the live source tree. The behavior test asserts
that no live structural-probe residue exists before or after verification.
