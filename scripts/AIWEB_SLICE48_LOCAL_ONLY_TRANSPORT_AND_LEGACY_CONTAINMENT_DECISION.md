# Slice 48 Local-Only Transport and Legacy Containment Decision

## Source-grounded findings

The inspected committed source contains an older desktop orchestrator that starts `main.py`, waits for TCP port 7477, builds a separate React console, launches Chrome, and trusts an already-open port. The inspected `main.py` contains a historical server that binds with an empty host string, exposes many HTTP routes, accepts CORS `*`, and includes browser command surfaces. That source is historical product scaffolding and is not a safe foundation for the narrow Slice 48 boundary.

## Binding decision

Slice 48 neither modifies nor invokes those paths. It adds a separate stdlib-only service with an owner-only Unix domain socket and explicit lifecycle control. This is containment, not replacement of the historical application launcher.

The service is intentionally not connected to:

- `main.py`;
- `scripts/aiweb_os_appctl.py`;
- port 7477;
- the operator console;
- the Terminus browser surface;
- any language route;
- memory, resources, tools, actions, or delivery.

## Why AF_UNIX

AF_UNIX provides a real local process boundary without choosing a TCP port or creating LAN exposure. Filesystem ownership and mode `0600` restrict connections to the current user, and Linux peer credentials are checked when available.

## Deferred decision

A future Slice 49 inspection API must decide its own read-only request surface and local-access protections. Slice 48 does not pre-authorize HTTP, TCP, or any language-record endpoint.
