# Slice 48 local runtime service boundary

This slice creates a real local service process but deliberately does not start Forge's historical `main.py` runtime.

After the package is applied, the real behavior test and verifier must be run on `/home/nic/forge`. Nothing may be staged or committed until the returned result packet passes review.

The first controlled service launch after commit is:

```text
/home/nic/forge/.venv/bin/python3 -B /home/nic/forge/scripts/aiweb_slice48_local_runtime_service.py start
```

That launches only the Slice 48 boundary. It does not open the Operator Console and does not create a language API.
