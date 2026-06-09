"""General Learning-to-Answer Pipeline — domain library (Build GP-001).

A *domain* is the unit of capability growth. Each domain is a small, explicit
object with four responsibilities:

  matches(question)   -> bool        : does this question belong to this domain?
  parse(question)     -> ParsedQuestion | None
  execute(parsed)     -> ExactSolution
  relation_text()     -> str         : the governed relation, for source ancestry

Honesty boundary (read this):
  This is NOT general natural-language understanding. Each domain recognises a
  bounded family of phrasings using explicit patterns. A question that no domain
  recognises is REFUSED, never guessed. That refusal is a feature: the system
  says "I have not learned that kind of problem yet" rather than fabricating.

  To teach the system a new kind of problem, add a new Domain here (plus tests).
  The engine never changes; only the library grows.

Build GP-001 ships two domains at the true beginning of arithmetic:
  - whole_number_arithmetic : "what is A plus/minus/times/divided by B"
  - fraction_change_capacity: "X was a/b full; after N removed it was c/d full;
                               what is the full capacity?"  (the Build 011 family)

All arithmetic uses exact fractions.Fraction. No floats. No LLM.
"""

from __future__ import annotations

import re
from fractions import Fraction
from typing import List, Optional, Protocol

from .contracts import ParsedQuestion, ExactSolution, fraction_to_text

# Information-gain micro unit awarded when an unknown is genuinely resolved.
# (The engine treats >0 as "this produced new knowledge, not recall".)
_RESOLVED_INFORMATION_GAIN = 1_000_000


def _normalise(text: str) -> str:
    return " ".join(str(text).strip().lower().split())


def _parse_number(token: str) -> Optional[Fraction]:
    """Parse an integer or simple a/b fraction token into an exact Fraction."""
    token = token.strip()
    if re.fullmatch(r"\d+/\d+", token):
        num, den = token.split("/")
        if int(den) == 0:
            return None
        return Fraction(int(num), int(den))
    if re.fullmatch(r"\d+", token):
        return Fraction(int(token))
    return None


class Domain(Protocol):
    domain_id: str

    def relation_text(self) -> str: ...
    def matches(self, question: str) -> bool: ...
    def parse(self, question: str) -> Optional[ParsedQuestion]: ...
    def execute(self, parsed: ParsedQuestion) -> ExactSolution: ...


# ---------------------------------------------------------------------------
# Domain 1 — whole-number (and simple-fraction) arithmetic
# ---------------------------------------------------------------------------

_OP_WORDS = {
    "plus": "add", "added to": "add", "sum of": "add", "+": "add",
    "minus": "subtract", "less": "subtract", "-": "subtract",
    "times": "multiply", "multiplied by": "multiply", "x": "multiply", "*": "multiply",
    "divided by": "divide", "over": "divide", "/": "divide",
}

_OP_SYMBOL = {"add": "+", "subtract": "-", "multiply": "\u00d7", "divide": "\u00f7"}
_OP_VERB = {"add": "adding", "subtract": "subtracting", "multiply": "multiplying", "divide": "dividing"}


class WholeNumberArithmeticDomain:
    domain_id = "whole_number_arithmetic"

    def relation_text(self) -> str:
        return "answer = left_operand (operation) right_operand, computed by exact arithmetic"

    def _find_op(self, q: str):
        # Longest operator phrase first so "multiplied by" beats "by", etc.
        for phrase in sorted(_OP_WORDS, key=len, reverse=True):
            pattern = re.escape(phrase)
            if not phrase.isalpha():
                regex = pattern  # symbols can sit between digits
            else:
                regex = r"\b" + pattern + r"\b"
            m = re.search(regex, q)
            if m:
                return _OP_WORDS[phrase], m.start(), m.end()
        return None

    def matches(self, question: str) -> bool:
        return self.parse(question) is not None

    def parse(self, question: str) -> Optional[ParsedQuestion]:
        q = _normalise(question)
        # This domain answers short, direct arithmetic expressions only.
        # Reject multi-clause word problems so the right domain handles them.
        if len(q.split()) > 12:
            return None
        if any(w in q for w in (" full", "capacity", "removed", "remaining", "left over")):
            return None
        q = q.rstrip("?.! ")
        # strip a leading "what is" / "compute" / "calculate"
        q = re.sub(r"^(what is|whats|what's|compute|calculate|evaluate)\s+", "", q)
        found = self._find_op(q)
        if not found:
            return None
        op, start, end = found
        left_text = q[:start].strip()
        right_text = q[end:].strip()
        # take the last number token on the left and first on the right
        left_tokens = left_text.split()
        right_tokens = right_text.split()
        if not left_tokens or not right_tokens:
            return None
        left = _parse_number(left_tokens[-1])
        right = _parse_number(right_tokens[0])
        if left is None or right is None:
            return None
        if op == "divide" and right == 0:
            return None
        return ParsedQuestion(
            domain=self.domain_id,
            raw_question=question,
            quantities={"left": left, "right": right},
            metadata={"operation": op},
        )

    def execute(self, parsed: ParsedQuestion) -> ExactSolution:
        left = parsed.quantities["left"]
        right = parsed.quantities["right"]
        op = parsed.metadata["operation"]
        if op == "add":
            answer = left + right
        elif op == "subtract":
            answer = left - right
        elif op == "multiply":
            answer = left * right
        elif op == "divide":
            answer = left / right
        else:  # pragma: no cover - guarded by parse
            raise ValueError(f"unknown operation {op!r}")

        sym = _OP_SYMBOL[op]
        lt, rt, at = fraction_to_text(left), fraction_to_text(right), fraction_to_text(answer)
        steps = [f"{lt} {sym} {rt} = {at}"]

        # Exact verification: invert the operation where well-defined.
        verified = False
        verification_text = ""
        if op == "add":
            verified = (answer - right == left)
            verification_text = f"Check: {at} - {rt} = {fraction_to_text(answer - right)}, which matches {lt}."
        elif op == "subtract":
            verified = (answer + right == left)
            verification_text = f"Check: {at} + {rt} = {fraction_to_text(answer + right)}, which matches {lt}."
        elif op == "multiply":
            if right != 0:
                verified = (answer / right == left)
                verification_text = f"Check: {at} \u00f7 {rt} = {fraction_to_text(answer / right)}, which matches {lt}."
            else:
                verified = (answer == 0)
                verification_text = f"Check: multiplying by 0 gives 0, and the result is {at}."
        elif op == "divide":
            verified = (answer * right == left)
            verification_text = f"Check: {at} \u00d7 {rt} = {fraction_to_text(answer * right)}, which matches {lt}."

        return ExactSolution(
            domain=self.domain_id,
            answer_value=answer,
            answer_unit="",
            steps=steps,
            verification_text=verification_text,
            verified=verified,
            information_gain=_RESOLVED_INFORMATION_GAIN if verified else 0,
        )


# ---------------------------------------------------------------------------
# Domain 2 — fraction-change capacity (the Build 011 family), exact + verified
# ---------------------------------------------------------------------------

class FractionChangeCapacityDomain:
    domain_id = "fraction_change_capacity"

    def relation_text(self) -> str:
        return "whole_capacity = removed_amount / (initial_fraction - final_fraction)"

    _PATTERN = re.compile(
        r"(?:a|an|the)?\s*(?P<object>[a-z ]+?)\s+(?:was|is)\s+(?P<initial>\d+/\d+|\d+)\s+full"
        r".*?after\s+(?P<removed>\d+/\d+|\d+)\s+(?P<unit>[a-z]+)\s+(?:were|was|are|is)\s+removed"
        r".*?(?:it\s+(?:was|is))\s+(?P<final>\d+/\d+|\d+)\s+full",
        re.IGNORECASE | re.DOTALL,
    )

    def matches(self, question: str) -> bool:
        return self.parse(question) is not None

    def parse(self, question: str) -> Optional[ParsedQuestion]:
        q = _normalise(question)
        m = self._PATTERN.search(q)
        if not m:
            return None
        initial = _parse_number(m.group("initial"))
        final = _parse_number(m.group("final"))
        removed = _parse_number(m.group("removed"))
        if initial is None or final is None or removed is None:
            return None
        if initial - final == 0:
            return None
        obj = m.group("object").strip()
        # keep only the trailing noun phrase (drop filler like "storage")
        obj = " ".join(obj.split()[-2:]) if obj else "container"
        return ParsedQuestion(
            domain=self.domain_id,
            raw_question=question,
            quantities={"initial": initial, "final": final, "removed": removed},
            metadata={"object": obj, "unit": m.group("unit").strip()},
        )

    def execute(self, parsed: ParsedQuestion) -> ExactSolution:
        initial = parsed.quantities["initial"]
        final = parsed.quantities["final"]
        removed = parsed.quantities["removed"]
        unit = parsed.metadata.get("unit", "")

        delta = initial - final
        capacity = removed / delta

        dt = fraction_to_text(delta)
        rt = fraction_to_text(removed)
        ct = fraction_to_text(capacity)
        steps = [
            f"The fill changed from {fraction_to_text(initial)} to {fraction_to_text(final)}, "
            f"a decrease of {dt} of the whole.",
            f"That decrease equals the {rt} {unit} removed, so {dt} of the capacity = {rt} {unit}.",
            f"Capacity = {rt} \u00f7 {dt} = {ct} {unit}.",
        ]

        # Exact verification by substitution.
        initial_amount = initial * capacity
        final_amount = final * capacity
        diff = initial_amount - final_amount
        verified = (diff == removed)
        verification_text = (
            f"Check: {fraction_to_text(initial)} of {ct} is {fraction_to_text(initial_amount)} {unit}, "
            f"and {fraction_to_text(final)} of {ct} is {fraction_to_text(final_amount)} {unit}; "
            f"the difference is {fraction_to_text(diff)} {unit}, which matches the amount removed."
        )

        return ExactSolution(
            domain=self.domain_id,
            answer_value=capacity,
            answer_unit=unit,
            steps=steps,
            verification_text=verification_text,
            verified=verified,
            information_gain=_RESOLVED_INFORMATION_GAIN if verified else 0,
        )


_DOMAINS: List[Domain] = [
    FractionChangeCapacityDomain(),
    WholeNumberArithmeticDomain(),
]


def all_domains() -> List[Domain]:
    return list(_DOMAINS)


def match_domain(question: str) -> Optional[Domain]:
    """Return the first domain that recognises the question, or None.

    None means the system has not learned this kind of problem. The pipeline
    must refuse, never guess."""
    for domain in _DOMAINS:
        try:
            if domain.matches(question):
                return domain
        except Exception:
            # A domain that errors on an unfamiliar string simply does not match.
            continue
    return None


__all__ = [
    "Domain",
    "WholeNumberArithmeticDomain",
    "FractionChangeCapacityDomain",
    "all_domains",
    "match_domain",
]
