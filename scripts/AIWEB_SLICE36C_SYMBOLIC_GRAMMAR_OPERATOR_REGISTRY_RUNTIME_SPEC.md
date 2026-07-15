# AI.Web Slice 36C — Symbolic Grammar-Operator Registry Runtime Specification

## Status

Bounded implementation specification for the additive Slice 36C package.

## Purpose

Slice 36C defines a closed, versioned, inspectable registry of symbolic
grammar-operator responsibilities that may participate in later bounded
input-structure analysis.

It does not recognize words, match phrases, create proposals, bind operators,
apply operators, assign phases, create meaning, infer permission, select
capabilities, route tools, write memory, or execute actions.

## Governing architecture

FBSC Volume II section 5.3 defines symbolic grammar operators as phase-intent bindings rather than conventional parts of speech. The eight canonical FBSC
grammar operators are preserved as inert registry definitions:

1. Initiator `⊕` — advisory affinity `Φ1`
2. Desire Vector `⇋` — advisory affinity `Φ3`
3. Structural Binding `⚯` — advisory affinity `Φ4`
4. Decay Mark `↧` — advisory affinity `Φ5`
5. Grace Override `†` — advisory affinity `Φ6`
6. Name Declaration `✎` — advisory affinity `Φ7`
7. Projection `↠` — advisory affinity `Φ8`
8. Loop Seal `⟲` — advisory affinity `Φ9`

These affinities are source-authority metadata only. Slice 36C performs no
phase assignment.

The registry also defines seventeen bounded language-core extension
responsibilities required by the accepted Slice 36 roadmap:

- continuation
- relation
- boundary
- recursion
- negation
- prohibition
- condition
- modality
- quotation containment
- exception
- uncertainty
- reference
- attachment
- conjunction
- separation
- suspension
- containment

The extension responsibilities have no invented glyph and no invented phase
affinity.

## Exact registry

The v1 registry contains exactly 25 operator definitions:

- 8 FBSC Volume II canonical definitions
- 17 bounded language-core extension definitions
- 20 required roadmap families represented
- 0 proposal rules
- 0 source bindings
- 0 operator applications
- 0 direct RSOC mappings

The registry is closed-world, deterministic and disabled by default.

## Definition contract

Every operator definition preserves:

- stable definition identity
- stable operator key
- semantic version
- canonical name
- operator family
- source origin
- optional authoritative glyph
- exact domain schema
- exact range schema
- permitted source-field prerequisites
- prohibited prerequisites
- required companion operator keys
- compatible operator keys
- incompatible operator keys
- compatibility-table status
- commutation status and restriction codes
- exact source-span requirements
- exact ancestry requirements
- uncertainty behavior
- malformed-input behavior
- unsupported-input behavior
- phase-affinity status
- phase-affinity values when explicitly authorized
- entropy-effect status
- drift-effect status
- permitted responsibility classes
- proposal-rule identities
- RSOC mapping identities
- runtime and authority flags
- source-authority references

## Domain and range

All definitions use:

```text
domain = aiweb-source-preserving-resonant-language-field-v1
range  = aiweb-symbolic-grammar-operator-proposal-candidate-v1
```

The range is a future contract identity only. Slice 36C does not create a
candidate.

## Proposal-rule law

Every future operator proposal must cite an exact, versioned rule. A lawful
proposal record must preserve:

- exact source span or spans
- observable source conditions
- proposal-rule identity and version
- registry identity and version
- candidate operator identity
- supporting conditions
- missing conditions
- conflicting conditions

Slice 36C installs zero proposal rules. Therefore every proposal request is
refused with a typed decision. No source form receives an operator because it
resembles a familiar word or phrase.

## Compatibility and commutation

No compatibility table, incompatibility table or commutation relation is
installed in Slice 36C. Empty compatible and incompatible sets do not mean that
all operators are compatible. They mean no relationship has yet been
authorized.

## Phase, entropy and drift

The eight canonical FBSC phase affinities are preserved as advisory authority
metadata only.

No phase trail is created.

No numeric entropy effect, entropy threshold, drift threshold or automatic
correction trigger is installed.

Documented FBSC drift relationships are preserved only as advisory codes where
the source explicitly describes them.

## Permanent prohibitions

Slice 36C must not use:

There is no lexeme-to-operator table in this implementation.


- an NLP tokenizer
- a word-class tagger
- a vocabulary lookup
- a lexeme-to-operator table
- phrase similarity
- embeddings
- statistical confidence
- a learned parser
- an LLM
- a vector store
- RAG
- memory search
- file search
- web search
- the legacy phase parser
- the legacy resonance lexicon
- MEA as a substitute language operator engine
- hidden fallback logic

## Authority boundaries

```text
registered operator ≠ runtime occurrence
runtime occurrence ≠ selected meaning
selected meaning ≠ permission
permission ≠ action route
FBSC grammar glyph ≠ RSOC core operator
phase affinity metadata ≠ phase assignment
empty compatibility set ≠ universal compatibility
```

## No automatic activation

Importing the package performs no registry build.

Building the registry performs no proposal.

Looking up an operator performs no proposal.

Evaluating a proposal request returns a typed refusal because no exact proposal
rule is installed.

## Accepted progression

Slice 36D may later install exact proposal rules and create source-bound
operator candidates, but only after a separate source-authority packet, design
ruling, tests, verification, backup and Decision Owner authorization.
