# AI.Web Slice 20 — Delivery, Action, and Tool-Routing Boundary Scaffold

## Purpose

Slice 20 creates boundary records that prevent language understanding from becoming real-world action.

The scaffold records this rule:

- Understanding a request is not doing the request.
- A capability reference is not invocation.
- A route existing is not permission.
- A draft is not sent.
- An implementation request is not code execution.

## What this slice adds

This slice adds a negative-authority scaffold only:

- delivery/action/tool-routing boundary records
- authority-separation records
- receipt generation
- verifier and test scripts

## What this slice does not add

This slice does not add:

- tool invocation
- router activation
- transport activation
- delivery implementation
- public release implementation
- draft sending
- code execution
- shell execution
- network execution
- route registry
- UI integration
- service integration
- daemon integration
- deployment integration
- GP-014 modification, import, call, wrapping, or promotion
- GP-015 repair

## Verification

Run from the repository root:

```bash
PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/home/nic/forge /home/nic/forge/.venv/bin/python3 \
  /home/nic/forge/scripts/test_aiweb_slice20_delivery_action_tool_routing_boundary_scaffold.py

PYTHONDONTWRITEBYTECODE=1 PYTHONPATH=/home/nic/forge /home/nic/forge/.venv/bin/python3 \
  /home/nic/forge/scripts/aiweb_slice20_delivery_action_tool_routing_boundary_verify.py /home/nic/forge
```

The verifier accepts exact pre-commit untracked context, exact pre-commit staged context, and clean committed Slice 20 or later descendant context.
