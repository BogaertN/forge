"""Exact reconstruction proof for Slice 36B source-field projections."""

from __future__ import annotations

import hashlib

from ..schema import stable_record_id
from .schema import (
    PROJECTION_SCHEMA_VERSION,
    PROJECTION_SPEC_ID,
    PROJECTION_SPEC_VERSION,
    SourceFieldProjectionRecord,
    SourceFieldReconstructionResult,
)


def _result(
    *,
    ok: bool,
    reason_code: str,
    projection_id: str,
    reconstructed_text: str,
    reconstructed_utf8_hex: str,
    reconstructed_utf8_byte_length: int,
    reconstructed_code_point_length: int,
    reconstructed_source_sha256: str,
    validation_issue_codes: tuple[str, ...],
) -> SourceFieldReconstructionResult:
    body = {
        "ok": ok,
        "reason_code": reason_code,
        "projection_id": projection_id,
        "reconstructed_text": reconstructed_text,
        "reconstructed_utf8_hex": reconstructed_utf8_hex,
        "reconstructed_utf8_byte_length": reconstructed_utf8_byte_length,
        "reconstructed_code_point_length": reconstructed_code_point_length,
        "reconstructed_source_sha256": reconstructed_source_sha256,
        "validation_issue_codes": validation_issue_codes,
        "projection_spec_id": PROJECTION_SPEC_ID,
        "projection_spec_version": PROJECTION_SPEC_VERSION,
        "schema_version": PROJECTION_SCHEMA_VERSION,
    }
    return SourceFieldReconstructionResult(
        result_id=stable_record_id(
            "source_field_reconstruction_result",
            body,
        ),
        **body,
    )


def reconstruct_source_field(
    projection: object,
) -> SourceFieldReconstructionResult:
    """Reconstruct exact UTF-8 bytes and text without external state."""

    if type(projection) is not SourceFieldProjectionRecord:
        return _result(
            ok=False,
            reason_code="invalid_source_field_projection_type",
            projection_id="",
            reconstructed_text="",
            reconstructed_utf8_hex="",
            reconstructed_utf8_byte_length=0,
            reconstructed_code_point_length=0,
            reconstructed_source_sha256="",
            validation_issue_codes=(
                "invalid_source_field_projection_type",
            ),
        )

    issues: list[str] = []
    byte_parts: list[bytes] = []
    expected_code_point_offset = 0
    expected_byte_offset = 0

    try:
        for expected_ordinal, atom in enumerate(projection.code_points):
            if atom.ordinal != expected_ordinal:
                issues.append("noncontiguous_atom_ordinal")
            if atom.code_point_start != expected_code_point_offset:
                issues.append("noncontiguous_code_point_offset")
            if atom.code_point_end != atom.code_point_start + 1:
                issues.append("invalid_atom_code_point_width")
            if atom.utf8_byte_start != expected_byte_offset:
                issues.append("noncontiguous_utf8_byte_offset")
            decoded = bytes.fromhex(atom.utf8_hex)
            if not decoded:
                issues.append("empty_atom_utf8_bytes")
            if atom.utf8_byte_end != atom.utf8_byte_start + len(decoded):
                issues.append("invalid_atom_utf8_byte_width")
            text = decoded.decode("utf-8", "strict")
            if text != atom.exact_text:
                issues.append("atom_text_utf8_mismatch")
            if len(text) != 1:
                issues.append("atom_not_one_code_point")
            byte_parts.append(decoded)
            expected_code_point_offset = atom.code_point_end
            expected_byte_offset = atom.utf8_byte_end
    except (ValueError, UnicodeError, TypeError, OverflowError):
        issues.append("atom_utf8_reconstruction_failed")

    reconstructed_bytes = b"".join(byte_parts)
    try:
        reconstructed_text = reconstructed_bytes.decode("utf-8", "strict")
    except UnicodeError:
        reconstructed_text = ""
        issues.append("reconstructed_utf8_decode_failed")

    reconstructed_hash = hashlib.sha256(reconstructed_bytes).hexdigest()
    if len(reconstructed_bytes) != projection.source_utf8_byte_length:
        issues.append("reconstructed_utf8_length_mismatch")
    if len(reconstructed_text) != projection.source_code_point_length:
        issues.append("reconstructed_code_point_length_mismatch")
    if reconstructed_hash != projection.source_sha256:
        issues.append("reconstructed_source_hash_mismatch")

    unique_issues = tuple(dict.fromkeys(issues))
    return _result(
        ok=not unique_issues,
        reason_code=(
            "source_field_reconstructed_exactly"
            if not unique_issues
            else unique_issues[0]
        ),
        projection_id=projection.projection_id,
        reconstructed_text=reconstructed_text,
        reconstructed_utf8_hex=reconstructed_bytes.hex(),
        reconstructed_utf8_byte_length=len(reconstructed_bytes),
        reconstructed_code_point_length=len(reconstructed_text),
        reconstructed_source_sha256=reconstructed_hash,
        validation_issue_codes=unique_issues,
    )
