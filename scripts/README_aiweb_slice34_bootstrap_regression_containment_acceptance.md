# AI.Web Slice 34 — Bootstrap Regression and Containment Acceptance

Slice 34 closes Phase B without beginning the general bidirectional Language
Core. It proves the exact Slice 31–33 bootstrap flows remain deterministic,
fixture-only, offline, read-only, and consequence-free, while the external
installer/verifier proves the inherited regression matrix and one-command
rollback.

## Exact scope

Slice 34 adds an isolated `regression_containment` subpackage and three proof
scripts. It modifies no existing Forge source file and does not connect the
subpackage from `aiweb_language_core_bootstrap/__init__.py`.

The in-memory evaluator checks the exact five accepted Slice 33 flows in order.
It is disabled by default and requires:

`--enable-offline-containment-evaluation`

Without that flag it returns:

`refused_bootstrap_containment_evaluation_disabled`

## What the runtime evaluator does not do

The evaluator does not run subprocesses, the inherited 45-command matrix, the
eight Slice 30–33 preservation commands, or rollback. It records those as
mandatory external proof duties and keeps technical acceptance false.

It does not use network access, write files, write runtime memory, mutate
evidence, ingest resources, invoke component behavior or component verifiers,
call GP-014, deliver, route tools, execute actions, register routes/APIs/UI, use
LLM/vector/embedding/RAG/Chroma/Qwen/Ollama authority, claim general language,
or claim release or production readiness.

## Required external proof

The hardened Slice 34 installer must prove, before and after the local commit:

- all 45 inherited Slice 0B–24 acceptance commands pass;
- the Slice 30 behavior and committed verifier pass;
- the Slice 31 behavior and committed verifier pass;
- the Slice 32 R1 behavior and committed verifier pass;
- the Slice 33 behavior and committed verifier pass;
- the Slice 34 behavior and repository verifier pass;
- exact protected hashes remain unchanged;
- source-tree Python caches remain absent;
- the repository remains clean;
- a generated one-command rollback artifact is tested in a disposable clone;
- the live rollback artifact is generated and verify-only checked;
- no push occurs and Slice 35 is not begun.

## Developer commands

List requirements:

```text
python3 -B scripts/aiweb_slice34_bootstrap_regression_containment_acceptance.py \
  --list-requirements
```

Prove disabled default:

```text
python3 -B scripts/aiweb_slice34_bootstrap_regression_containment_acceptance.py
```

Run explicit in-memory containment evaluation:

```text
python3 -B scripts/aiweb_slice34_bootstrap_regression_containment_acceptance.py \
  --enable-offline-containment-evaluation
```

Behavior and adversarial proof:

```text
python3 -B scripts/test_aiweb_slice34_bootstrap_regression_containment_acceptance.py
```

Repository verifier before staging:

```text
python3 -B scripts/aiweb_slice34_bootstrap_regression_containment_acceptance_verify.py \
  /home/nic/forge --mode precommit
```

Repository verifier after commit:

```text
python3 -B scripts/aiweb_slice34_bootstrap_regression_containment_acceptance_verify.py \
  /home/nic/forge --mode committed
```

## Acceptance boundary

A passing runtime evaluation is not technical acceptance. A passing installer is
not whole-product production readiness. Slice 34 accepts only the exact Phase B
bootstrap containment and regression scope proved by its reviewed operation
packet and separate Decision Owner technical acceptance record.
