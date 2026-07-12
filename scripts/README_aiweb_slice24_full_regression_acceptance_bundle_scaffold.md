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
