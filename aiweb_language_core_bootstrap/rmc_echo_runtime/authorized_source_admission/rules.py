"""Closed Slice 43C admission and rejection rules."""

from __future__ import annotations

from .schema import SourceAdmissionCode, SourceAdmissionStatus


REJECTION_PRIORITY = (
    SourceAdmissionCode.RAW_TEXT_WITHOUT_ACCEPTED_ANCESTRY,
    SourceAdmissionCode.REQUEST_TYPE_INVALID,
    SourceAdmissionCode.REQUEST_ID_INVALID,
    SourceAdmissionCode.REQUEST_OPERATION_INVALID,
    SourceAdmissionCode.SOURCE_TYPE_INVALID,
    SourceAdmissionCode.UNSUPPORTED_VERSION,
    SourceAdmissionCode.ALREADY_DELIVERED_CANDIDATE,
    SourceAdmissionCode.UNAUTHORIZED_CANDIDATE,
    SourceAdmissionCode.MISSING_REQUIRED_LINK,
    SourceAdmissionCode.RECOMPUTED_OR_FABRICATED_IDENTITY,
    SourceAdmissionCode.IDENTITY_MISMATCH,
    SourceAdmissionCode.ORPHAN_EXPRESSION,
    SourceAdmissionCode.INCONSISTENT_ANCESTRY,
    SourceAdmissionCode.PREDECESSOR_VALIDATION_FAILED,
    SourceAdmissionCode.SOURCE_NOT_COMPLETED,
    SourceAdmissionCode.SOURCE_NOT_ACCEPTED,
    SourceAdmissionCode.ADMISSION_RECORD_INVALID,
    SourceAdmissionCode.DOWNSTREAM_AUTHORITY_PROHIBITED,
)


STATUS_BY_CODE = {
    SourceAdmissionCode.RAW_TEXT_WITHOUT_ACCEPTED_ANCESTRY:
        SourceAdmissionStatus.HELD_RAW_TEXT,
    SourceAdmissionCode.UNSUPPORTED_VERSION:
        SourceAdmissionStatus.HELD_UNSUPPORTED_VERSION,
    SourceAdmissionCode.IDENTITY_MISMATCH:
        SourceAdmissionStatus.HELD_IDENTITY_INVALID,
    SourceAdmissionCode.RECOMPUTED_OR_FABRICATED_IDENTITY:
        SourceAdmissionStatus.HELD_IDENTITY_INVALID,
    SourceAdmissionCode.MISSING_REQUIRED_LINK:
        SourceAdmissionStatus.HELD_MISSING_LINK,
    SourceAdmissionCode.ORPHAN_EXPRESSION:
        SourceAdmissionStatus.HELD_ORPHAN_EXPRESSION,
    SourceAdmissionCode.ALREADY_DELIVERED_CANDIDATE:
        SourceAdmissionStatus.HELD_ALREADY_DELIVERED,
    SourceAdmissionCode.UNAUTHORIZED_CANDIDATE:
        SourceAdmissionStatus.HELD_UNAUTHORIZED_CANDIDATE,
    SourceAdmissionCode.INCONSISTENT_ANCESTRY:
        SourceAdmissionStatus.HELD_INCONSISTENT_ANCESTRY,
    SourceAdmissionCode.SOURCE_NOT_COMPLETED:
        SourceAdmissionStatus.HELD_SOURCE_NOT_ACCEPTED,
    SourceAdmissionCode.SOURCE_NOT_ACCEPTED:
        SourceAdmissionStatus.HELD_SOURCE_NOT_ACCEPTED,
    SourceAdmissionCode.PREDECESSOR_VALIDATION_FAILED:
        SourceAdmissionStatus.HELD_SOURCE_NOT_ACCEPTED,
}


def status_for_codes(
    codes: tuple[SourceAdmissionCode, ...],
) -> SourceAdmissionStatus:
    code_set = set(codes)
    for code in REJECTION_PRIORITY:
        if code in code_set:
            return STATUS_BY_CODE.get(
                code,
                SourceAdmissionStatus.HELD_INVALID_REQUEST,
            )
    return SourceAdmissionStatus.HELD_INVALID_REQUEST


__all__ = (
    "REJECTION_PRIORITY",
    "STATUS_BY_CODE",
    "status_for_codes",
)
