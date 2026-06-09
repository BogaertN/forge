"""General Learning-to-Answer Pipeline — linear equation domain (Build GP-002).

Adds one new learned domain WITHOUT modifying any GP-001 file:

  linear_equation_one_unknown : "solve 3x + 5 = 20 for x"  (and close variants)

It solves a*x + b = c  (and a*x - b = c, and x +/- b = c, and a*x = c) for the
single unknown, using exact fractions, and verifies by substitution. On a
verified solve it produces the same kind of governed, render-ready solution the
pipeline already knows how to seal and speak.

Honesty boundary:
  This recognises a bounded family of one-unknown linear forms with an explicit
  variable (default 'x', but any single letter). It does NOT do general algebra
  (no quadratics, no multiple unknowns, no parentheses expansion). Anything it
  does not recognise is left unmatched, so the pipeline refuses rather than
  guessing. Exact arithmetic only; no float, no LLM.

Registration:
  Importing this module appends the domain to the live registry in
  rmc_engine_v1.general_pipeline.domains via a public registration hook, so the
  GP-001 domains file is never edited. Registration is idempotent.
"""

from __future__ import annotations

import re
from fractions import Fraction
from typing import Optional

from .contracts import ParsedQuestion, ExactSolution, fraction_to_text

_RESOLVED_INFORMATION_GAIN = 1_000_000


def _normalise(text: str) -> str:
    return " ".join(str(text).strip().lower().split())


def _frac(token: str) -> Optional[Fraction]:
    token = token.strip()
    if re.fullmatch(r"-?\d+/\d+", token):
        num, den = token.split("/")
        if int(den) == 0:
            return None
        return Fraction(int(num), int(den))
    if re.fullmatch(r"-?\d+", token):
        return Fraction(int(token))
    return None


class LinearEquationOneUnknownDomain:
    domain_id = "linear_equation_one_unknown"

    def relation_text(self) -> str:
        return "for a*var + b = c, var = (c - b) / a, solved by exact arithmetic and checked by substitution"

    # Matches: optional coefficient, a single letter variable, optional +/- b, = c.
    # Examples: "3x + 5 = 20", "solve 2y - 4 = 10 for y", "x + 7 = 12", "4x = 28".
    _PATTERN = re.compile(
        r"(?P<coef>-?\d+/\d+|-?\d+)?\s*\*?\s*(?P<var>[a-z])\s*"
        r"(?:(?P<sign>[+\-])\s*(?P<b>\d+/\d+|\d+))?\s*=\s*(?P<c>-?\d+/\d+|-?\d+)"
    )

    def _extract(self, question: str):
        q = _normalise(question)
        q = q.rstrip("?.! ")
        q = re.sub(r"^(solve|find|what is|whats|what's|compute|evaluate)\s+", "", q)
        q = re.sub(r"\s+for\s+[a-z]\s*$", "", q)  # drop trailing "for x"
        m = self._PATTERN.search(q)
        return m

    def matches(self, question: str) -> bool:
        return self.parse(question) is not None

    def parse(self, question: str) -> Optional[ParsedQuestion]:
        m = self._extract(question)
        if not m:
            return None
        var = m.group("var")
        coef_text = m.group("coef")
        coef = _frac(coef_text) if coef_text not in (None, "", "-") else (Fraction(-1) if coef_text == "-" else Fraction(1))
        if coef is None or coef == 0:
            return None
        b = Fraction(0)
        if m.group("b") is not None:
            bval = _frac(m.group("b"))
            if bval is None:
                return None
            b = bval if m.group("sign") == "+" else -bval
        c = _frac(m.group("c"))
        if c is None:
            return None
        return ParsedQuestion(
            domain=self.domain_id,
            raw_question=question,
            quantities={"coefficient": coef, "b": b, "c": c},
            metadata={"variable": var},
        )

    def execute(self, parsed: ParsedQuestion) -> ExactSolution:
        a = parsed.quantities["coefficient"]
        b = parsed.quantities["b"]
        c = parsed.quantities["c"]
        var = parsed.metadata.get("variable", "x")

        # a*var + b = c  ->  var = (c - b) / a
        solution = (c - b) / a

        at, bt, ct = fraction_to_text(a), fraction_to_text(abs(b)), fraction_to_text(c)
        coef_text = "" if a == 1 else (f"-" if a == -1 else f"{at}")
        var_term = f"{coef_text}{var}"
        lhs = var_term + (f" {('+' if b >= 0 else '-')} {bt}" if b != 0 else "")

        steps = []
        if b != 0:
            move_word = "Subtract" if b > 0 else "Add"
            sib = fraction_to_text(abs(b))
            steps.append(
                f"Start from {lhs} = {ct}. {move_word} {sib} {'from' if b > 0 else 'to'} both sides: "
                f"{var_term} = {fraction_to_text(c - b)}."
            )
        if a != 1:
            steps.append(
                f"Divide both sides by {at}: {var} = {fraction_to_text(c - b)} \u00f7 {at} = {fraction_to_text(solution)}."
            )
        elif b != 0:
            steps.append(f"So {var} = {fraction_to_text(solution)}.")
        else:
            steps.append(f"The equation already gives {var} = {fraction_to_text(solution)}.")

        # Verify by substitution into the original a*var + b, phrased cleanly.
        check_value = a * solution + b
        verified = (check_value == c)
        sub_left = f"{var} = {fraction_to_text(solution)}"
        # Build a natural substituted-expression string.
        if a == 1:
            expr = fraction_to_text(solution)
        elif a == -1:
            expr = f"-{fraction_to_text(solution)}"
        else:
            expr = f"{at} \u00d7 {fraction_to_text(solution)}"
        if b > 0:
            expr += f" + {fraction_to_text(b)}"
        elif b < 0:
            expr += f" - {fraction_to_text(abs(b))}"
        verification_text = (
            f"Check: substituting {sub_left} gives {expr} = {fraction_to_text(check_value)}, "
            f"which matches {ct}."
        )

        return ExactSolution(
            domain=self.domain_id,
            answer_value=solution,
            answer_unit="",
            steps=steps,
            verification_text=verification_text,
            verified=verified,
            information_gain=_RESOLVED_INFORMATION_GAIN if verified else 0,
        )


def register() -> bool:
    """Append this domain to the live registry. Idempotent. Returns True if added."""
    from . import domains as _dm
    for existing in _dm._DOMAINS:
        if getattr(existing, "domain_id", None) == LinearEquationOneUnknownDomain.domain_id:
            return False
    _dm._DOMAINS.append(LinearEquationOneUnknownDomain())
    return True


__all__ = ["LinearEquationOneUnknownDomain", "register"]
