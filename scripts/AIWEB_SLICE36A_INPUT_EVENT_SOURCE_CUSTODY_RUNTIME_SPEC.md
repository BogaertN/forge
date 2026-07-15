# AI.Web Slice 36A Runtime Specification

## Deterministic Input Event and Source Custody

**Decision owner:** Nicholas Jacob Bogaert / AI.Web  
**Repository:** `/home/nic/forge`  
**Parent acceptance:** Slice 35E at `6089037388680c144ff666cd3737a03e1ff34ef5`  
**Specification identity:** `aiweb-input-event-source-custody-v1`

## 1. Purpose

Slice 36A establishes exactly what source text Forge received before tokenization, structural analysis, derivation, concept lookup, reference resolution, interpretation, gate evaluation, routing, or action. The implementation creates immutable in-memory custody records only.

An input-event record proves that a bounded source event was supplied to this custody function. It does not prove that the source is true, trustworthy, authorized, safe, meaningful, or executable.

## 2. Accepted input surface

The public capture function accepts one exact Python `str` plus explicit custody metadata:

- `source_id`;
- `channel_id`;
- a nonnegative `sequence_number`, a `correlation_id`, or both;
- an immutable declared-limits record.

Source and channel identities use a closed ASCII identifier profile. The received source text is not restricted to ASCII. Valid Unicode scalar text is encoded with strict UTF-8 and preserved byte-for-byte.

## 3. Exact preservation

The custody record preserves:

- the exact received text;
- UTF-8 byte length;
- Unicode code-point length;
- SHA-256 of the exact strict UTF-8 bytes;
- a complete code-point-to-byte boundary table;
- a deterministic root source span;
- deterministic input-event, span, condition, limits, and result identities;
- the Unicode Character Database version used for unsupported-code-point classification.

No lowercasing, Unicode normalization, whitespace collapse, spelling correction, paraphrase, hidden-character deletion, replacement-character insertion, or intent inference is permitted.

## 4. Bounded limits

Default limits are smaller than immutable hard ceilings. A caller may declare lower limits but may not exceed the hard ceilings.

- Default UTF-8 bytes: 262,144
- Hard UTF-8 bytes: 1,048,576
- Default code points: 131,072
- Hard code points: 262,144
- Default recorded conditions: 256
- Hard recorded conditions: 4,096

Code-point limits are checked before UTF-8 allocation. UTF-8 byte limits are checked immediately after strict encoding. Over-limit input returns a typed malformed result and does not create an event record.

## 5. Malformed input

Malformed input is rejected with typed condition records. This includes:

- non-string source values;
- lone surrogate code points that cannot be strictly encoded as UTF-8;
- invalid source or channel identifiers;
- invalid sequence or correlation metadata;
- absence of both sequence and correlation identity;
- empty input when the declared limits disallow it;
- invalid, forged, or out-of-range limits;
- code-point or byte limit violations.

The public capture path converts these caller errors into deterministic result records. It does not leak raw type, value, or Unicode exceptions.

## 6. Unsupported but preserved input

Valid Unicode may be preserved while remaining unsupported for structural progression. The v1 unsupported profile includes:

- prohibited control characters other than TAB, LF, and CR;
- Unicode format-control characters;
- private-use characters;
- unassigned characters under the recorded Unicode database version;
- Unicode noncharacters.

Unsupported characters remain in the exact source text. Each recorded condition carries exact code-point and UTF-8 byte offsets. Condition recording is bounded; when the detailed-record limit is reached, one deterministic aggregate condition preserves the exact total count.

A captured-unsupported event is custody evidence only. It is not eligible for Slice 36B tokenization until later authority explicitly defines handling.

## 7. Source spans

A source span is a half-open `[start, end)` code-point interval bound to one input event. It records matching UTF-8 byte offsets and the SHA-256 of the exact span bytes. Invalid event types, non-integer offsets, reversed ranges, negative ranges, and out-of-bounds ranges return typed failures.

Span construction does not tokenize or interpret the source.

## 8. Authority and side-effect boundary

Slice 36A performs none of the following:

- tokenization;
- normalization;
- grammar or structural derivation;
- concept or sense lookup;
- reference resolution;
- meaning construction or selection;
- clarification or refusal generation;
- filesystem reads or writes;
- environment lookup;
- network access;
- memory reads or writes;
- route, API, or UI registration;
- tool routing;
- action or delivery;
- external-resource loading;
- LLM, embedding, vector, RAG, or learned-model use.

The package is not imported by `aiweb_language_core_bootstrap.__init__`. Importing Slice 36A performs no capture operation.

## 9. Acceptance conditions

Slice 36A is accepted only when:

1. all predecessor hashes remain exact;
2. all inherited Slice 24 and Slice 30–35 behavior checks pass;
3. the Slice 36A behavior test proves exact preservation, deterministic identity, typed failures, bounded limits, stable offsets, unsupported-state containment, and immutable records;
4. static verification proves the runtime imports only approved standard-library and bootstrap schema modules;
5. no root-package auto-import or runtime side effect is introduced;
6. exactly seven Slice 36A files are committed;
7. the repository is clean after committed verification;
8. no push occurs.
