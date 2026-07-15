# Slice 36C — Symbolic Grammar-Operator Registry

This package adds an inert, closed and versioned grammar-operator registry to
the isolated AI.Web language-core bootstrap.

## It does

- preserve 8 canonical FBSC Volume II grammar definitions
- preserve 17 bounded language-core extension responsibilities
- preserve exact domains, ranges, prerequisites and authority flags
- preserve advisory phase affinities only where FBSC explicitly defines them
- preserve typed proposal refusals
- validate stable identities and closed-world registry invariants

## It does not

- tokenize words
- map lexemes to operators
- recognize negation, commands, requests or references
- create operator candidates
- bind or apply operators
- assign phases
- create meaning
- infer permission
- select a route, tool or action
- import legacy RMC
- map FBSC grammar operators directly to RSOC core operators
- push to GitHub

## Explicit import

```python
from aiweb_language_core_bootstrap.symbolic_grammar_operator_registry import (
    build_default_symbolic_grammar_operator_registry,
)
```

Importing the package performs no work. Building the registry creates immutable
inert records only.

## Test

```text
/usr/bin/python3 -B scripts/test_aiweb_slice36c_symbolic_grammar_operator_registry.py
```

## Verification

The independent verifier checks exact paths, predecessor hashes, import
boundaries, registry counts, source-authority markers, all inherited tests and
the Slice 36C behavior suite.
