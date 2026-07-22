# AI.Web Slice 43E Drift Finding, Materiality and Classification Runtime Specification

## Status

External additive implementation for the exact accepted Slice 43D parent.

## Exact parent

- Branch: `main`
- HEAD: `26e8c30724dde17709203411a95f63dcf65a380b`
- Tree: `785690cd3fe8b3437fce226edac5472659db3f7c`
- Subject: `Slice 43D meaning-preservation comparison`

## Purpose

Slice 43E consumes only validated Slice 43D comparison findings bound to the
accepted Slice 43C and Slice 42 ancestry. It creates one immutable Slice 43E
classification record for every Slice 43D dimension finding.

The accepted drift-kind registry contains exactly:

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
16. ancestry mismatch;
17. unsupported surface addition.

## Materiality law

Materiality is recorded separately from Echo disposition.

- `not_applicable`: the Slice 43D finding is exactly preserved and no custody
  mismatch exists.
- `material`: at least one admitted material drift kind is present.
- `non_material`: the only drift is an unsupported surface addition and every
  addition belongs to the controlled formatting, punctuation or whitespace
  surface prefixes.
- `unsupported`: Slice 43D reported an unsupported comparison state.
- `conflicted`: Slice 43D reported a conflicted comparison state.
- `indeterminate`: Slice 43D reported an indeterminate state or the exact
  available custody cannot lawfully determine materiality.

Unknown additions are not guessed into non-material status.

## Required custody

Every classification record preserves:

- the exact Slice 43D comparison result and package identities;
- the exact Slice 43D finding identity;
- the exact dimension and comparison outcome;
- source and proposed snapshot identities;
- source and proposed values;
- source and proposed field paths;
- evidence and trace references;
- classification-rule references;
- materiality-rule references and grounds;
- ancestry-mismatch references where present.

## Permanent boundaries

Slice 43E does not:

- decide `PASSED`, `REJECTED` or `CONTAINED`;
- issue rejection or containment;
- repair, rewrite or replace text;
- modify or integrate MSM-v1;
- authorize delivery, routes, APIs, network, filesystem, memory writes, tools
  or actions;
- determine truth, evidence validity, permission or execution;
- use an LLM, EchoForge, embeddings, vectors, RAG, similarity, neural parsing
  or hidden classifiers;
- supersede GP-014.

Echo disposition belongs to Slice 43F. MSM-v1 validation-link integration
belongs to Slice 43G. Disabled integration and Slice 43 closeout belong to
Slice 43H.
