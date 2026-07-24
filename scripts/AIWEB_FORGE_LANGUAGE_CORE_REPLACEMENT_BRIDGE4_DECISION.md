# AI.Web Forge Language-Core Replacement Bridge 4 Decision

Bridge 4 is the first Forge-facing candidate-meaning custody increment after Bridge 3.

## Source-derived ruling

The live post-Bridge-3 source proves that candidate meaning construction and selected meaning are separate authorities. Slice 39F/39G may construct and preserve candidate custody. Slice 41 authority forbids automatic selection from first, only, safest, most similar, or highest-confidence candidates. Exact Slice 40H gate custody and successful Slice 41C eligibility are required before Slice 41D selected-meaning construction.

Therefore Bridge 4:

1. Requires an explicit caller-supplied action root: `inspect`, `report`, or `request`.
2. Runs the accepted source through the real Slice 37, Slice 38, Slice 39F, and Slice 39G chain.
3. Returns exact candidate and MSM custody identifiers without ranking or selection.
4. Accepts an explicit exact candidate-ID nomination only as a validated Slice 16 boundary hold.
5. Holds before Slice 41C because exact Slice 40H gate custody is not yet connected.
6. Does not call Slice 41D or Slice 41E.
7. Does not route tools, execute actions, write memory, call an LLM, or replace Forge.

Bridge 4 is not full language-core replacement. Explicit generation and review model lanes remain visible for later controlled replacement.
