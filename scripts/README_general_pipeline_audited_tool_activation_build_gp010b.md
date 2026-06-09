# GP-010B-R1 — Audited Tool Activation Integration

This build supersedes the voided install-only GP-010B packet. It installs and actively binds the exact GP-010A-audited dependency set in one governed transaction.

Active answer-path integrations:
- Lark 1.3.1 parses only the existing linear-equation grammar into the AI.Web typed AST.
- SymPy 1.14.0 solves only that validated AST and emits an exact substitution proof receipt.
- mpmath 1.3.0 is SymPy transitive support.

Active verification-only integration:
- Hypothesis 6.155.1 generates valid equations and refusal attacks in the GP-010B test harness.
- sortedcontainers 2.4.0 is Hypothesis transitive support.

No raw user text is passed to SymPy. No new domain, corpus ingestion, memory write, Identity Vault action, Contribution Economy action, CT mint, or ledger write is added.
