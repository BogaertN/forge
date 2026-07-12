"""Invariant verification for Slice 19 RMC Echo Boundary Scaffold."""

from __future__ import annotations

from pathlib import Path

from .authority import ECHO_AUTHORITY_DENIALS, authority_decision_for_claim, build_authority_report
from .boundary import BOUNDARY_STATEMENTS, build_boundary_report, validate_boundary_report
from .core import ECHO_RELATIONSHIP, IMPLEMENTATION_STATE, SLICE_ID, SLICE_TITLE
from .receipt import build_slice19_receipt

# Tokens are assembled to avoid the scanner matching its own guard list as a
# forbidden dependency or authority call.
FORBIDDEN_SOURCE_TOKENS: tuple[str, ...] = (
    "import " + "aiweb_gp014",
    "from " + "aiweb_gp014",
    "import " + "gp014",
    "from " + "gp014",
    "import " + "gp015",
    "from " + "gp015",
    "deliv" + "er(",
    "public_" + "release(",
    "approve_" + "output(",
    "render_" + "authority(",
)


def verify_slice19_invariants(package_root: Path | None = None) -> tuple[str, ...]:
    """Return invariant failures for the Slice 19 scaffold.

    An empty tuple means the local scaffold preserves its boundary contract.
    """

    failures: list[str] = []

    boundary_report = build_boundary_report()
    failures.extend(validate_boundary_report(boundary_report))

    if boundary_report.get("slice") != SLICE_ID:
        failures.append("slice id mismatch")
    if boundary_report.get("title") != SLICE_TITLE:
        failures.append("slice title mismatch")
    if boundary_report.get("implementation_state") != IMPLEMENTATION_STATE:
        failures.append("implementation state mismatch")
    if boundary_report.get("relationship") != ECHO_RELATIONSHIP:
        failures.append("relationship mismatch")
    if len(BOUNDARY_STATEMENTS) != 12:
        failures.append("unexpected boundary statement count")

    authority_report = build_authority_report()
    if authority_report.get("authority_layer") != "later_separate_authority_layer":
        failures.append("authority layer mismatch")

    for claim_key in sorted(ECHO_AUTHORITY_DENIALS):
        decision = authority_decision_for_claim(claim_key)
        if decision.get("allowed") is not False:
            failures.append(f"denied claim was allowed: {claim_key}")
        if decision.get("decision") != "denied_by_slice19_boundary":
            failures.append(f"denied claim had wrong decision: {claim_key}")

    positive = authority_decision_for_claim("separate later authority layer")
    if positive.get("allowed") is not True:
        failures.append("separate later authority layer description was not allowed")
    if positive.get("decision") != "allowed_as_boundary_description_only":
        failures.append("positive boundary description had wrong decision")

    unknown = authority_decision_for_claim("ship to public")
    if unknown.get("allowed") is not False:
        failures.append("unknown authority claim was allowed")

    receipt = build_slice19_receipt()
    receipt_body = receipt.get("receipt")
    if not isinstance(receipt_body, dict):
        failures.append("receipt body missing")
    else:
        if receipt_body.get("repo_write_authorized") is not False:
            failures.append("receipt grants repo write")
        if receipt_body.get("delivery_authorized") is not False:
            failures.append("receipt grants delivery")
        if receipt_body.get("public_release_authorized") is not False:
            failures.append("receipt grants public release")
        if receipt_body.get("output_approval_authorized") is not False:
            failures.append("receipt grants output approval")
        if receipt_body.get("production_integration_authorized") is not False:
            failures.append("receipt grants production integration")
        if receipt_body.get("gp014_modified") is not False:
            failures.append("receipt modifies GP-014")
        if receipt_body.get("gp014_imported") is not False:
            failures.append("receipt imports GP-014")
        if receipt_body.get("gp014_called") is not False:
            failures.append("receipt calls GP-014")
        if receipt_body.get("gp015_repaired") is not False:
            failures.append("receipt repairs GP-015")
        if receipt_body.get("boundary_validation_failures") != []:
            failures.append("receipt contains boundary validation failures")

    digest = receipt.get("receipt_sha256")
    if not isinstance(digest, str) or len(digest) != 64:
        failures.append("receipt digest is invalid")

    if package_root is not None:
        root = Path(package_root)
        if not root.is_dir():
            failures.append("package root missing: " + str(root))
        else:
            for path in sorted(root.rglob("*.py")):
                text = path.read_text(encoding="utf-8", errors="replace")
                for token in FORBIDDEN_SOURCE_TOKENS:
                    if token in text:
                        failures.append(f"forbidden token {token!r} found in {path}")

    return tuple(failures)


def verification_report(package_root: Path | None = None) -> dict[str, object]:
    """Return a JSON-friendly invariant verification report."""

    failures = verify_slice19_invariants(package_root=package_root)
    return {
        "slice": SLICE_ID,
        "title": SLICE_TITLE,
        "implementation_state": IMPLEMENTATION_STATE,
        "relationship": ECHO_RELATIONSHIP,
        "failure_count": len(failures),
        "failures": list(failures),
        "verdict": "PASS" if not failures else "FAIL",
    }
