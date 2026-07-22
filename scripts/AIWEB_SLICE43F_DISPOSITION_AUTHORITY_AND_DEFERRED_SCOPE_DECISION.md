# AI.Web Slice 43F Disposition Authority and Deferred Scope Decision

## Ruling

Slice 43F is authorized only to consume a validated Slice 43E drift and
materiality result and create one deterministic Echo disposition:
`PASSED`, `REJECTED` or `CONTAINED`.

## Admitted input

The only admitted input is a valid Slice 43E result whose request, package,
drift-finding, materiality, comparison, source-admission and predecessor
identities validate under the committed Slice 43E law.

Raw text, free-form interpretation, recomputed or fabricated identities,
unsupported versions, missing packages and inconsistent ancestry are held
without creating a disposition.

## Deterministic disposition law

1. `CONTAINED` applies when any admitted finding has `unsupported`,
   `conflicted` or `indeterminate` materiality. Incomplete authority prevents
   lawful progression.
2. Otherwise, `REJECTED` applies when any admitted material finding contains an
   exact deterministic Echo-law violation.
3. Otherwise, `PASSED` applies because all material preservation obligations
   pass and no incomplete authority blocks progression.

Incomplete authority takes precedence over rejection when both are present.
The material violation and incomplete-authority findings remain retained in
the containment record; neither is erased or downgraded.

## Rejection and containment custody

A rejection record is created only with `REJECTED`. It identifies the exact
material violation findings, admitted drift kinds and deterministic rejection
law references.

A containment record is created only with `CONTAINED`. It identifies the exact
blocking findings, incomplete-authority states, any coexisting material
violations and the applied precedence law.

Every result retains every Slice 43E finding and its Slice 43D, Slice 43C and
Slice 42 ancestry regardless of disposition.

## Permanent non-authority boundary

Slice 43F does not:

- rewrite the candidate or automatically repair wording;
- remove, weaken, downgrade or suppress drift;
- authorize or perform delivery;
- call EchoForge or delegate validation to it;
- call an LLM or use embeddings, vectors, RAG, similarity, neural parsing or a
  hidden classifier;
- create route, API, network, filesystem, memory-write, tool or action
  authority;
- determine truth, evidence validity, permission or execution;
- modify or integrate MSM-v1;
- supersede GP-014.

## Deferred scope

- MSM-v1 validation-link custody: Slice 43G.
- Disabled bootstrap integration and Slice 43 closeout: Slice 43H.
- GP-014 integration and protection: Slices 44-47.
