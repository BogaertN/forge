# RSOC Symbolic Reference Preview

This is Forge's first safe Language Core bootstrap surface.

It recognizes the ten canonical RSOC glyph spellings directly from exact
Unicode source. It does not use word or subword tokenization, and it does not
normalize lookalike Unicode sequences. `Ĉ` is therefore different from
`C` followed by a combining circumflex, while the registered resurrection
glyph is exactly `R` followed by a combining circumflex (`R̂`).

## What is installed

- Exact input custody and reversible source projection.
- Longest-first matching against Forge's closed ten-contract registry.
- Code-point, UTF-8 byte, source-span, atom, registry, and contract IDs.
- Complete coverage records for recognized references, ASCII separators, and
  unresolved source.
- A deterministic, read-only receipt.
- `POST /api/rmc/symbolic-language-preview`.
- A visible **Symbolic Language Lab** tab in the Forge Operator Console.

The accepted preview document is intentionally small: exact registered glyphs
may be adjacent or separated by ASCII space, tab, carriage return, or line
feed. This is an operator-reference sequence, not an executable expression.

## What remains closed

There is no accepted operand syntax, precedence, composition law,
compatibility/commutation table, numeric transform, phase-transition executor,
or meaning law in this slice. Recognition of `χ(t)` does not invoke Grace
Override, reduce entropy, or grant any permission. Recognition of `⧜` does not
read or write memory.

## Recommended next sequence

1. Review the canonical Google Drive definitions for operand types,
   composition, transition laws, and counterexamples.
2. Build a versioned **symbol registry** (identity and definitions) separately
   from a versioned **grammar** (which arrangements are well formed).
3. Define typed field/operand envelopes without conventional word
   tokenization.
4. Add compatibility, commutation, entropy, and phase rules one law at a time,
   with accepted and refused fixtures.
5. Exercise those rules in this isolated lab, then in ProtoForge simulations.
6. Connect to the live Forge Operator Council only after the receipts prove
   deterministic behavior and every memory/action/delivery gate is explicit.

Do not test unfinished operator transitions in the live council yet. The lab is
the correct first surface because it cannot write memory or apply an operator.

## Verification

```bash
cd /home/nic/forge
python3 scripts/test_aiweb_rsoc_symbolic_reference_preview.py
python3 scripts/aiweb_rsoc_symbolic_reference_preview_verify.py

cd /home/nic/aiweb/apps/forge-operator-console
npm run build
```
