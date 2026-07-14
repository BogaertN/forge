# AI.Web Slice 32 — Accepted Boundary Component Loading

This slice adds the first explicit loading of accepted language-core boundary
packages. It remains disabled by default, fixture-only, offline, and
unconnected to `main.py` or any public surface.

## Exact behavior

- one static synthetic fixture;
- one disabled-default refusal path;
- one explicit developer enable flag;
- 15 direct source-declared package imports in registry order;
- exact package identity and `__all__` interface verification;
- no importlib, plugin discovery, entry-point lookup, package scanning,
  environment-selected backend, or hidden fallback;
- no component function or verifier invocation;
- no persistent side effect.

## Developer command

List the fixture:

```bash
/usr/bin/python3 -B scripts/aiweb_slice32_accepted_boundary_component_loading.py --list-fixtures
```

Prove disabled refusal:

```bash
/usr/bin/python3 -B scripts/aiweb_slice32_accepted_boundary_component_loading.py --fixture slice32-explicit-static-component-loading-v1
```

Run the explicit offline fixture:

```bash
/usr/bin/python3 -B scripts/aiweb_slice32_accepted_boundary_component_loading.py --fixture slice32-explicit-static-component-loading-v1 --enable-offline-component-loading
```

## Non-authority boundary

This slice does not interpret language, produce selected meaning, render output,
create a trace or receipt, connect runtime routes, read external data, write
memory, mutate evidence, deliver output, invoke tools, perform actions, or use
GP-014. Slice 33 remains separate.
