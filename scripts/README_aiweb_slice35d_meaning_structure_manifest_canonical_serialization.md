# Slice 35D — MeaningStructureManifest Canonical Serialization and Versioning

Slice 35D adds one isolated module:

```text
aiweb_language_core_bootstrap.meaning_structure_manifest.serialization
```

It provides:

- deterministic canonical JSON bytes;
- strict fail-closed deserialization;
- exact package and schema version checks;
- exact record and enum reconstruction;
- Slice 35B validation on both sides of the boundary;
- Slice 35C lifecycle-history conformance checking;
- byte-for-byte round-trip equivalence;
- stable canonical SHA-256 calculation;
- explicit rejection of unknown or incompatible versions;
- no automatic migration or upgrade behavior.

## Public module API

```python
from aiweb_language_core_bootstrap.meaning_structure_manifest.serialization import (
    CANONICAL_FORMAT_ID,
    CANONICAL_FORMAT_VERSION,
    SERIALIZATION_SPEC_ID,
    SERIALIZATION_SPEC_VERSION,
    CanonicalSerializationError,
    SerializationErrorCode,
    canonical_manifest_sha256,
    deserialize_manifest,
    serialize_manifest,
)
```

The original `meaning_structure_manifest` root package keeps its accepted Slice 35A export surface unchanged. Slice 35D must be imported through its explicit submodule.

## Canonical format

The format is versioned canonical JSON using sorted object names, compact separators, ASCII escaping and no non-standard numeric constants. Accepted payloads contain no byte-order mark, leading or trailing whitespace, alternate field spellings, omitted fields, unknown fields or duplicate keys.

## Version behavior

Only canonical format version `1` and schema version `MSM-v1` are accepted. Any other version fails closed.

No migration, automatic upgrade, fallback parser or compatibility guess exists.

## Test commands

From `/home/nic/forge`:

```bash
PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 -B \
  scripts/test_aiweb_slice35a_meaning_structure_manifest_core_schema.py

PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 -B \
  scripts/test_aiweb_slice35b_meaning_structure_manifest_deterministic_validation.py

PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 -B \
  scripts/aiweb_slice35b_meaning_structure_manifest_deterministic_validation_verify.py

PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 -B \
  scripts/test_aiweb_slice35c_meaning_structure_manifest_lifecycle_transition_law.py

PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 -B \
  scripts/aiweb_slice35c_meaning_structure_manifest_lifecycle_transition_law_verify.py

PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 -B \
  scripts/test_aiweb_slice35d_meaning_structure_manifest_canonical_serialization.py

PYTHONDONTWRITEBYTECODE=1 /usr/bin/python3 -B \
  scripts/aiweb_slice35d_meaning_structure_manifest_canonical_serialization_verify.py
```

## Boundaries

Slice 35D does not persist files, load files, connect routes, integrate the bootstrap, write memory, write evidence, invoke tools, perform actions, use models or migrate older objects. Slice 35E remains responsible for bounded integration and Slice 35 closeout.
