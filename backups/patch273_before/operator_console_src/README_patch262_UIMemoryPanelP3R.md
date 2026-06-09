# Patch 262-UI-MemoryPanel-P3R

Repair patch for Memory Panel Phase 2 gated-action hardening.

P3 correctly added the promotion arming guard, but the JavaScript compatibility
copy used ESM `export` syntax while the Forge-side Node verification environment
loads `.js` files as CommonJS. The React app uses the TypeScript source, but the
verifier still needs an executable JS compatibility target.

P3R changes:

- Keeps `rmc-ui-guards.ts` as the React/TypeScript source of truth.
- Converts `rmc-ui-guards.js` to a CommonJS compatibility module.
- Updates the behavior test to load the JS guard with `createRequire`.
- Keeps the same safety contract: preview required, exact token required, exact
  confirmation phrase required, duplicate/unsafe/missing-field blocks enforced.
- Does not change backend authority, does not call shell, does not write files,
  and does not perform promotion.
