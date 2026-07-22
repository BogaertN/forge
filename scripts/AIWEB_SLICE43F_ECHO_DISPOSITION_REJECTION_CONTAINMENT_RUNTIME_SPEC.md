# AI.Web Slice 43F Echo Disposition, Rejection and Containment Runtime Specification

## Status

External additive implementation for the exact accepted Slice 43E parent.

## Exact parent

- Branch: `main`
- HEAD: `2192c7ffc6df7f936ead4760f25a0f027dcffad7`
- Tree: `93ed56e1db485d611c0a434387eacec81a0149aa`
- Subject: `Slice 43E drift finding materiality and classification`

## Purpose

Slice 43F consumes only validated Slice 43E drift-classification and
materiality findings. It creates one immutable disposition package containing
one disposition record and, when applicable, one rejection or containment
record.

The closed disposition registry is exactly:

1. `PASSED`;
2. `REJECTED`;
3. `CONTAINED`.

## Precedence and decision law

The runtime evaluates the complete admitted Slice 43E package without deleting
or collapsing findings.

1. If one or more findings have `unsupported`, `conflicted` or `indeterminate`
   materiality, the disposition is `CONTAINED`.
2. If no incomplete-authority finding exists and one or more material findings
   contain an admitted deterministic Echo-law violation, the disposition is
   `REJECTED`.
3. If no incomplete-authority finding and no material Echo-law violation exist,
   the disposition is `PASSED`.

When incomplete authority and a material violation coexist, containment takes
precedence while both finding sets remain present in the containment and
summary records.

## Deterministic Echo-law violation registry

The following Slice 43E drift kinds are exact material violations when their
materiality is `material`:

1. omitted meaning;
2. claim strengthening;
3. scope expansion;
4. certainty upgrade;
5. evidence-status upgrade;
6. caveat omission;
7. refusal softening;
8. ambiguity erasure;
9. unresolved-state erasure;
10. invented fact;
11. invented evidence;
12. authority escalation;
13. action-status distortion;
14. memory-status distortion;
15. delivery-status distortion;
16. ancestry mismatch.

`unsupported_surface_addition` is not silently promoted into rejection.
Controlled formatting-only additions remain non-material and may pass. An
addition whose materiality cannot be lawfully determined remains indeterminate
and is contained.

## Required custody

Every successful disposition package preserves:

- the exact Slice 43F request identity;
- the exact Slice 43E result and package identities;
- all 13 Slice 43E drift-finding identities;
- no-drift, non-material, material-violation and incomplete-authority finding
  references;
- unsupported, conflicted and indeterminate finding references;
- all retained drift kinds;
- every comparison, evidence, trace, snapshot and ancestry reference inherited
  through Slice 43E;
- exact disposition, rejection, containment, precedence and retention-law
  references;
- deterministic canonical identities and digests.

Held invalid inputs create no disposition, rejection or containment package.

## Permanent boundaries

Slice 43F does not:

- rewrite, repair or replace the candidate;
- remove, downgrade or suppress drift;
- authorize or perform delivery;
- call EchoForge;
- use an LLM, embeddings, vectors, RAG, similarity, neural parsing or hidden
  classifiers;
- modify or integrate MSM-v1;
- create route, API, network, filesystem, memory-write, tool or action
  authority;
- determine truth, evidence validity, permission or execution;
- supersede GP-014.

MSM-v1 validation-link integration belongs to Slice 43G. Disabled integration
and Slice 43 closeout belong to Slice 43H.
