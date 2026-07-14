# AI.Web Slice 33 — Deterministic Trace and Receipt Assembly

Slice 33 creates an isolated, disabled-by-default, offline, fixture-only,
read-only trace and receipt assembler for the accepted Slice 31 and hardened
Slice 32 fixture flows.

## Purpose

For each exact accepted fixture flow, Slice 33 can produce an immutable
in-memory derivation trace and an immutable in-memory receipt. The trace shows
which accepted fixture, state, result, boundary, registry, observation, and
component identities were verified. The receipt binds that trace to the exact
accepted source versions and negative-authority state.

Slice 33 does not persist either record.

## Exact accepted flows

1. `slice31-disabled-default-probe-trace-v1`
2. `slice31-explicit-inspection-disabled-trace-v1`
3. `slice31-explicit-inspection-enabled-trace-v1`
4. `slice32-static-loading-disabled-trace-v1`
5. `slice32-static-loading-enabled-trace-v1`

The two disabled outcomes are not treated as failures. They produce lawful
refusal receipts when the Slice 33 assembler itself is explicitly enabled.

## Default behavior

The Slice 33 assembler is disabled by default. A trace or receipt is assembled
only when the offline developer command receives:

`--enable-offline-trace-receipt`

Without that flag the command returns:

`refused_trace_receipt_assembly_disabled`

and creates no trace or receipt.

## Developer command

List exact flows:

```text
python3 -B scripts/aiweb_slice33_deterministic_trace_receipt_assembly.py --list-flows
```

Prove the assembler remains disabled:

```text
python3 -B scripts/aiweb_slice33_deterministic_trace_receipt_assembly.py \
  --flow slice31-disabled-default-probe-trace-v1
```

Assemble one explicit offline trace and receipt:

```text
python3 -B scripts/aiweb_slice33_deterministic_trace_receipt_assembly.py \
  --flow slice32-static-loading-enabled-trace-v1 \
  --enable-offline-trace-receipt
```

The command writes compact JSON to standard output only. It accepts no file,
URL, corpus, evidence, memory, recipient, destination, tool, action, model, or
free-form language input.

## Strict identity boundary

Every completed trace and receipt is bound to the exact accepted identities for:

- the Architecture Alignment Lock;
- Slice 30 bootstrap boundary;
- Slice 31 adapter and fixture results;
- Slice 32 component-loading fixture results;
- Slice 32 R1 strict identity hardening;
- fixture IDs;
- source state IDs;
- result IDs;
- observation, authority, import-policy, boundary, and registry IDs;
- the exact 15 loaded package names and loaded-component IDs in exact order;
- trace step IDs and their ordered digest;
- lawful refusal or successful read-only outcome.

A record is not accepted merely because its hash matches its supplied body.
Fabricated or altered traces and receipts remain invalid after all nested IDs
are recomputed.

## Authority boundary

Slice 33 does not:

- modify `main.py`;
- connect Ask Forge;
- register a route, API, service, or UI;
- persist a trace or receipt;
- write memory;
- mutate evidence;
- admit or fetch external resources;
- use the network;
- read caller-supplied external files;
- invoke a component function;
- invoke a component verifier;
- deliver output;
- route a tool;
- execute an action;
- import or call GP-014;
- grant runtime authority;
- widen acceptance;
- begin Slice 34;
- establish release or whole-product production readiness.

## Proof commands

Behavior and adversarial proof:

```text
python3 -B scripts/test_aiweb_slice33_deterministic_trace_receipt_assembly.py
```

Repository verifier before staging:

```text
python3 -B scripts/aiweb_slice33_deterministic_trace_receipt_assembly_verify.py \
  /home/nic/forge --mode precommit
```

Repository verifier after commit:

```text
python3 -B scripts/aiweb_slice33_deterministic_trace_receipt_assembly_verify.py \
  /home/nic/forge --mode committed
```

The behavior suite includes 227 checks and proves that a fully fabricated,
self-consistent trace/receipt/result chain is rejected after all deterministic
identifiers are recomputed.
