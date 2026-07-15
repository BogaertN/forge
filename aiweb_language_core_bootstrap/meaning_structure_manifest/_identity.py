"""Package and schema identity for MeaningStructureManifest v1.

Slice 35A exposes identity constants only. It does not perform validation,
serialization, lifecycle transitions, persistence, integration, or runtime work.
"""

from typing import Final

PACKAGE_NAME: Final[str] = (
    "aiweb_language_core_bootstrap.meaning_structure_manifest"
)
PACKAGE_ID: Final[str] = "aiweb-forge-meaning-structure-manifest"
SCHEMA_NAME: Final[str] = "MeaningStructureManifest"
SCHEMA_ABBREVIATION: Final[str] = "MSM-v1"
SCHEMA_VERSION: Final[str] = "MSM-v1"
SCHEMA_ID: Final[str] = "aiweb-forge-meaning-structure-manifest-v1"
AUTHORITY_DOCUMENT: Final[str] = (
    "Document 2 of 10 - MeaningStructureManifest v1"
)
