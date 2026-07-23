# AI.Web Slice 46 — GP-014 Equivalence and Regression Proof

This slice adds a proof harness and evidence scripts only. The accepted parent
is `00df51e4b2fe14e437291c5228159820dd1cf139` with tree
`987c08cc797ebe721dc28ab7d03b69a6b1b61f8f`.

The real test must be run by Nic on `/home/nic/forge`. External package checks
prove only archive integrity, syntax, exact file identity, correction
apply/rollback containment and isolated construction behavior.

The corrected result collector runs:

1. exact applied-state and payload-hash preflight;
2. an exact backup of all sixteen untracked Slice 46 files;
3. temporary removal of only those sixteen files so the accepted Slice 45
   predecessor is clean at the required live path `/home/nic/forge`;
4. Slice 24 full acceptance and Slice 25 committed hygiene checks on that live
   clean predecessor;
5. unconditional restoration of the exact corrected Slice 46 payload;
6. Slice 46 behavior and independent verifier, including the inherited Slice 45
   verifier chain through the accepted language-core predecessors;
7. an exact disposable apply/rollback rehearsal;
8. result-packet and checksum creation.

The temporary predecessor-acceptance transition is fail-closed, exact-path,
hash-checked, backed up before removal and restored in a `finally` boundary.
It never touches tracked predecessor files, the Git index or HEAD.

No staging or commit is performed by the package or collector.

## Inherited virtual-environment path correction

The first acceptance-context correction correctly created a disposable
interpreter bridge in the inherited Slice 45 checkout, but it resolved the live
virtual-environment interpreter symlink before writing that bridge. On Ubuntu,
resolving `/home/nic/forge/.venv/bin/python3` produces the system interpreter
path (for example `/usr/bin/python3.x`). That discards the virtual-environment
dependency context and caused the inherited GP-014 tests to fail with
`ModuleNotFoundError: lark`.

The verifier now preserves the exact accepted invocation path
`/home/nic/forge/.venv/bin/python3` when creating the disposable bridge. It does
not copy or modify the virtual environment, and it does not alter Slice 45,
GP-014, the Slice 46 runtime proof modules, tracked predecessors, routes, UI,
memory, tools, actions, resources, or delivery authority.
