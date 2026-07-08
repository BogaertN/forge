# AI.Web Slice 15 — Corpus / Evidence / Memory / Trace Separation Scaffold

Slice 15 is a boundary-only scaffold. It introduces deterministic records that keep source mentions, examples, evidence records, memory records, memory requests, trace records, corpus entries, and authority references from collapsing into each other.

Hard laws preserved by this scaffold:

- A source mention is not evidence.
- Evidence is not memory.
- Memory is not external truth.
- Trace is not unrestricted corpus.
- A memory request does not write memory.
- Corpus presence is not authority.
- An example is not proof.
- A trace is not permission.
- Evidence custody is not evidence validation.
- Memory custody is not memory write authority.

This slice does not fetch, ingest, validate, index, write, route, deliver, admit, or authorize anything. It only represents category boundaries and rejection behavior.
