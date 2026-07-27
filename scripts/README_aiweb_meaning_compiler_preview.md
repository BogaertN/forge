# Ask Forge Meaning Compiler Preview

This increment gives Ask Forge a bounded, deterministic preview of the
Language Core design. Human words remain the input. The runtime preserves the
exact Unicode source, derives candidate symbolic meaning structures from
controlled grammar and concept laws, may consult an explicitly supplied
read-only RMC snapshot, produces bounded wording, and checks that wording
against the source meaning with Echo.

The preview is not an LLM and does not create an LLM-style token stream. It
does not use token IDs, BPE, embeddings, vectors, nearest-neighbour retrieval,
semantic-similarity fallback, next-token prediction, or a model call. Lexical
occurrences and grammar constituents retain exact source spans; they are
symbolic records, not model tokens.

Registry matching derives an ASCII case key so `Forge` and `forge` can address
the same provisional entry. That key never replaces, normalizes, or hashes over
the exact source text retained in custody.

## Bounded flow

```text
exact Unicode source
  -> source custody and exact span projection
  -> controlled lexical/concept candidates
  -> deterministic predicate, role, negation, and scope derivation
  -> zero/one/many candidate meaning structures
  -> optional exact-relation RMC context (read-only)
  -> PREVIEW_READY or HELD
  -> deterministic reverse wording
  -> Echo meaning-preservation comparison
```

`PREVIEW_READY` means that one bounded meaning preview and its Echo-checked
wording are available for inspection. It is not permission, truth, evidence,
an executable plan, a tool route, or delivery authority. `HELD` is a valid
result for ambiguity, unknown words, unsupported structure, invalid or
tampered context, incomplete source coverage, or Echo drift. A held result
must preserve alternatives and exact unknown spans instead of guessing.

## Symbolic laws in v0

The runtime treats a candidate meaning as a discrete relation structure, not
as a point in an embedding space:

```text
M = Predicate(p) + Σ Bind(roleᵢ, senseᵢ) + Polarity + Purport
G(M) = Expectancy ∧ Congruity ∧ Connectedness ∧ Purport
ρ(M, R) = |exact concepts| + |exact relations| + |exact ancestry|
Select(M) only when G(M) is true and the lawful result is unique,
or when one lawful candidate has the unique nonzero maximum ρ.
Echo passes only when Signature(reparse(reverse(M))) = Signature(M).
```

These are exact set, relation, and Boolean operations. RMC cannot make an
incompatible candidate lawful, and a resonance tie cannot select a meaning.

The v0 Forge-owned seed registry is intentionally small: 20 provisional
concepts/senses, 11 predicates, and 7 participant roles. It is a working
foundation, not a claim of full English coverage. Unknown forms and structures
are held so future lexicon and grammar growth can be reviewed explicitly.

## RMC boundary

The preview accepts only a canonical immutable snapshot made from structured
RMC memory records. A record can support a candidate only through an admitted
exact relation and traceable record identity. Input order must not affect the
snapshot or result. Invalid identities, unsupported reference namespaces,
ineligible lifecycle states, contradictory metadata, changed records, and
resonance ties are held. Phase, correction, and Echo-control references remain
closed in v0. The preview neither searches nor writes the live memory tree.

The installed default snapshot reports `CONNECTED_EMPTY`, zero records, and
`no_eligible_structured_language_records`. Existing RMC files were not silently
reclassified because they do not yet carry validated language concept,
relation, and ancestry records. A future `rmc_language_context_v1` store should
use a content-hash and previous-entry hash chain before it becomes eligible.

The existing filesystem memory recaller is intentionally outside this
increment because its legacy word-overlap scoring is not the token-free exact
relation contract required here.

## Ask Forge surface

The adapter exposes:

```text
POST /api/operator/ask-forge/language-core-preview
```

The request is a JSON object accepted by
`rmc_engine_v1.meaning_compiler_preview.build_language_core_preview_response`.
The public HTTP request accepts exactly `source_text`; it cannot inject an RMC
snapshot. Structured snapshot injection exists only on the trusted Python
compiler interface until a verified Forge-owned RMC language store exists.
The response always includes the endpoint, a typed status/reason, exact source
custody, candidate or hold information, and the zero-authority boundary. The
existing `/api/operator/ask-forge/math-trace` lane remains separate and
unchanged.

## Acceptance checks

Run from `/home/nic/forge`:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/home/nic/forge \
  .venv/bin/python3 -B scripts/test_aiweb_meaning_compiler_preview.py /home/nic/forge

PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/home/nic/forge \
  .venv/bin/python3 -B scripts/test_aiweb_ask_forge_language_core_preview_route.py /home/nic/forge

PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/home/nic/forge \
  .venv/bin/python3 -B scripts/aiweb_meaning_compiler_preview_verify.py \
  --repo /home/nic/forge
```

The tests cover exact custody and replay, ambiguity, explicit unknown and
misspelled words, negation, structured read-only RMC context, reverse wording
and Echo drift, request validation, route preservation, and zero model,
embedding, vector, filesystem-write, network, tool, action, permission, and
delivery authority.
