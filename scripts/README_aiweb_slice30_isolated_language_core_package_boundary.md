# AI.Web Slice 30 — Isolated Language-Core Package Boundary

## Scope

Slice 30 creates an isolated, standard-library-only package boundary at:

`aiweb_language_core_bootstrap/`

It creates exactly ten new files and modifies no existing file.

## What exists after Slice 30

- immutable authority-state records;
- a static registry of 15 accepted package identities;
- a closed import policy;
- an isolated package-boundary record;
- deterministic builders and validators;
- behavior tests;
- a repository verifier.

## What does not exist after Slice 30

- component loading;
- natural-language interpretation;
- rendering;
- `main.py` integration;
- routes;
- UI integration;
- network access;
- filesystem writes;
- environment-selected backends;
- external-resource admission;
- persistent memory;
- evidence mutation;
- delivery;
- tools;
- actions;
- GP-014 import, call, wrapper, promotion or supersession;
- release;
- production readiness.

## Behavior test

```text
/usr/bin/python3 -B scripts/test_aiweb_slice30_isolated_language_core_package_boundary.py
```

## Repository verifier

Before commit:

```text
/usr/bin/python3 -B scripts/aiweb_slice30_isolated_language_core_package_boundary_verify.py /home/nic/forge --mode precommit
```

After commit:

```text
/usr/bin/python3 -B scripts/aiweb_slice30_isolated_language_core_package_boundary_verify.py /home/nic/forge --mode committed
```

## Inherited regression

After the Slice 30 commit is clean:

```text
/usr/bin/python3 -B scripts/aiweb_slice24_full_regression_acceptance_bundle_verify.py /home/nic/forge --run-acceptance --result-dir <external-result-directory>
```

Acceptance requires:

- Slice 30 behavior test: PASS;
- Slice 30 verifier: PASS;
- inherited matrix: 45 executed, 45 passed, 0 failed, 0 skipped;
- clean worktree;
- exact local commit;
- no push.

## Rollback

Before commit, move only the ten new files into a timestamped quarantine under
`/home/nic/Downloads`, preserve hashes and logs, remove only newly empty
directories, and verify the original accepted HEAD remains clean.

After commit, do not rewrite history automatically. Preserve failure evidence,
do not push, and require a separately authorized recovery decision.
