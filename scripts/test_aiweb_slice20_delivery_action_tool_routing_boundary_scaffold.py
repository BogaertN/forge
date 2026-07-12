#!/usr/bin/env python3
"""Tests for Slice 20 delivery/action/tool-routing boundary scaffold."""

from __future__ import annotations

from pathlib import Path
import ast
import sys

REPO = Path(__file__).resolve().parents[1]
if str(REPO) not in sys.path:
    sys.path.insert(0, str(REPO))

from aiweb_delivery_action_tool_routing_boundary_scaffold.authority import build_authority_separation_record
from aiweb_delivery_action_tool_routing_boundary_scaffold.boundary import check_boundary_integrity
from aiweb_delivery_action_tool_routing_boundary_scaffold.core import build_boundary_record, get_required_sentinels
from aiweb_delivery_action_tool_routing_boundary_scaffold.receipt import build_receipt

SOURCE_PATHS = (
    "aiweb_delivery_action_tool_routing_boundary_scaffold/__init__.py",
    "aiweb_delivery_action_tool_routing_boundary_scaffold/authority.py",
    "aiweb_delivery_action_tool_routing_boundary_scaffold/boundary.py",
    "aiweb_delivery_action_tool_routing_boundary_scaffold/core.py",
    "aiweb_delivery_action_tool_routing_boundary_scaffold/receipt.py",
    "aiweb_delivery_action_tool_routing_boundary_scaffold/verify.py",
    "scripts/aiweb_slice20_delivery_action_tool_routing_boundary_verify.py",
)

PROHIBITED_ACTION_FRAGMENTS = (
    "os." + "system(",
    "socket" + ".",
    "requests" + ".",
    "urllib" + ".request",
    "smtplib" + ".",
    "send" + "_email(",
    "send" + "_draft(",
    "forward" + "_emails(",
    "create" + "_event(",
    "update" + "_event(",
    "delete" + "_event(",
    "gmail" + ".",
    "gcal" + ".",
)


def test_boundary_record_is_negative_authority_only() -> None:
    record = build_boundary_record()
    values = set(str(value) for value in record.to_dict().values())
    assert record.understanding_request_boundary == "understanding_is_not_doing"
    assert record.capability_reference_boundary == "capability_reference_is_not_invocation"
    assert record.route_existence_boundary == "route_existence_is_not_permission"
    assert record.draft_boundary == "draft_is_not_sent"
    assert record.implementation_request_boundary == "implementation_request_is_not_code_execution"
    assert record.delivery_boundary == "delivery_is_not_implemented"
    assert record.action_boundary == "action_execution_is_not_implemented"
    assert record.tool_routing_boundary == "tool_routing_is_not_implemented"
    assert record.transport_boundary == "transport_is_not_implemented"
    assert record.output_approval_boundary == "output_approval_is_not_granted"
    assert record.gp014_boundary == "gp014_not_modified_imported_called_wrapped_or_promoted"
    assert record.gp015_boundary == "gp015_not_repaired"
    assert record.sentinel_count == len(get_required_sentinels())
    assert "implementation_request_is_not_code_execution" in values


def test_authority_separation_grants_no_permission() -> None:
    authority = build_authority_separation_record()
    assert authority.permission_required_for_invocation is True
    assert authority.permission_required_for_delivery is True
    assert authority.permission_required_for_code_execution is True
    assert authority.permission_required_for_sending_drafts is True
    assert authority.this_scaffold_grants_permission is False


def test_boundary_integrity_and_receipt() -> None:
    result = check_boundary_integrity()
    assert result.passed, result.failures
    receipt = build_receipt()
    assert receipt.verdict == "PASS"
    assert receipt.runtime_effect == "no_delivery_no_action_no_tool_invocation_no_code_execution"
    assert receipt.production_effect == "no_route_no_ui_no_registry_no_daemon_no_network_no_deployment"


def test_sources_parse_and_do_not_contain_action_fragments() -> None:
    for rel in SOURCE_PATHS:
        path = REPO / rel
        assert path.is_file(), rel
        text = path.read_text(encoding="utf-8")
        ast.parse(text, filename=str(path))
        for fragment in PROHIBITED_ACTION_FRAGMENTS:
            assert fragment not in text, f"{rel} contains prohibited fragment {fragment!r}"


def main() -> int:
    for test in (
        test_boundary_record_is_negative_authority_only,
        test_authority_separation_grants_no_permission,
        test_boundary_integrity_and_receipt,
        test_sources_parse_and_do_not_contain_action_fragments,
    ):
        test()
    print("SLICE20_DELIVERY_ACTION_TOOL_ROUTING_BOUNDARY_TEST=PASS")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
