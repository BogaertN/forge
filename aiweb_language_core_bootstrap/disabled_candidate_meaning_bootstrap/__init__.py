"""Slice 39H disabled candidate-meaning bootstrap and closeout surface."""
from .fixtures import get_disabled_candidate_meaning_fixture, is_exact_accepted_fixture, list_disabled_candidate_meaning_fixtures
from .integration import REQUESTED_OPERATION, REASON_DISABLED, build_disabled_candidate_meaning_bootstrap_state, build_fixture_invocation, build_slice39_acceptance_record, build_slice39_rollback_metadata, run_disabled_candidate_meaning_bootstrap
from .schema import *
from .validation import PUBLIC_VALIDATORS, validate_acceptance_record, validate_fixture, validate_integration_result, validate_integration_state, validate_invocation, validate_rollback_metadata, validate_stage_receipt
__all__ = tuple(name for name in globals() if not name.startswith("_"))
