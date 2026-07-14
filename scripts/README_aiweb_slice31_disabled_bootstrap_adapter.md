# AI.Web Slice 31 — Disabled-by-Default Bootstrap Adapter

## Accepted purpose

Slice 31 adds one deterministic orchestrator adapter inside the isolated
`aiweb_language_core_bootstrap` package.

The adapter is:

- disabled by default;
- available only through two exact governed synthetic fixtures;
- explicitly enabled only for one in-memory offline fixture process;
- deterministic and standard-library-only;
- unable to accept arbitrary text or external files;
- unable to load any of the 15 registered boundary components;
- unable to connect to `main.py`, a route, UI, network, memory, evidence,
  delivery, tool, action, GP-014, release, or production path.

## Exact behavior

The disabled-default fixture proves refusal while the adapter is disabled.

The explicit-offline fixture observes only the already accepted Slice 30
bootstrap boundary identifiers and inert status. It does not interpret human
language, construct meaning, load a component, assemble the later Slice 33
trace or receipt, or create a public capability.

## Offline developer command

List fixtures:

```bash
/usr/bin/python3 -B scripts/aiweb_slice31_disabled_bootstrap_adapter.py \
  --list-fixtures
```

Prove the disabled default:

```bash
/usr/bin/python3 -B scripts/aiweb_slice31_disabled_bootstrap_adapter.py \
  --fixture slice31-disabled-default-probe-v1
```

Run the explicit in-memory offline inspection:

```bash
/usr/bin/python3 -B scripts/aiweb_slice31_disabled_bootstrap_adapter.py \
  --fixture slice31-explicit-offline-boundary-inspection-v1 \
  --enable-offline-fixture-adapter
```

The command accepts no free-form language, file path, corpus, evidence,
resource, memory, destination, tool, or action parameter.

## Explicit exclusions

Slice 31 does not begin Slice 32 component loading.

It does not establish a live language kernel, general-language interpretation,
Ask Forge route, API, UI, persistent trace, receipt assembly, memory write,
external-resource ingestion, delivery, tool invocation, state-changing action,
GP-014 integration, release, or production readiness.
