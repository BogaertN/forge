# Forge Language-Core Bridge 5B

Bridge 5B corrects the exact version-custody seam between the current Slice
38 predicate/frame registries and the Slice 40C through 40F gate-family
validators.

It preserves the frozen `v1.0.0` test path and admits a current pair only
through exact read-only registry identity, exact version equality, and the
exact frame-to-predicate link.

This package does not modify `main.py` and does not expose a new Forge
command. Full Bridge 5 gate construction remains blocked until this
compatibility correction is accepted and committed separately.
