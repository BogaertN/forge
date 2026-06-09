// Patch 262-UI-MemoryPanel-P3
// JavaScript compatibility copy of UI-side safety guards for gated RMC actions.
// These guards do not authorize writes. Forge/RMC backend remains the authority.

export const PROMOTION_TOKEN = 'APPROVE_RMC_PROMOTION';

function clean(value) {
  return typeof value === 'string' ? value.trim() : '';
}

function getPreviewCandidateId(preview) {
  const direct = clean(preview?.candidate_id);
  if (direct) return direct;
  const stable = preview?.stable_memory_preview;
  return clean(stable?.source_candidate_id);
}

function duplicateDetected(preview) {
  const duplicate = preview?.duplicate_check;
  return Boolean(duplicate?.duplicate);
}

export function buildPromotionConfirmationPhrase(candidateId) {
  const id = clean(candidateId);
  return id ? `PROMOTE ${id}` : '';
}

export function evaluatePromotionArmState(input) {
  const candidateId = clean(input?.candidateId);
  const preview = input?.preview ?? null;
  const previewCandidateId = getPreviewCandidateId(preview);
  const expectedConfirmation = buildPromotionConfirmationPhrase(candidateId);
  const unsafePathCount = Array.isArray(preview?.unsafe_paths) ? preview.unsafe_paths.length : 0;
  const missingFieldCount = Array.isArray(preview?.missing_required_fields) ? preview.missing_required_fields.length : 0;
  const previewCurrent = Boolean(candidateId && previewCandidateId && candidateId === previewCandidateId);
  const previewAllowsPromotion = Boolean(preview?.promotion_allowed === true);
  const tokenExact = clean(input?.approvalToken) === PROMOTION_TOKEN;
  const confirmationExact = Boolean(expectedConfirmation && clean(input?.confirmationPhrase) === expectedConfirmation);
  const previewReadOnly = preview?.writes_files === false && preview?.memory_write_allowed === false;
  const backendWritesOnPreview = preview?.writes_files === true || preview?.memory_write_allowed === true;
  const duplicate = duplicateDetected(preview);

  const reasonCodes = [];
  if (!candidateId) reasonCodes.push('candidate_id_required');
  if (!preview) reasonCodes.push('promotion_preview_required');
  if (preview && !previewCurrent) reasonCodes.push('preview_candidate_mismatch');
  if (preview && !previewAllowsPromotion) reasonCodes.push('preview_does_not_allow_promotion');
  if (!tokenExact) reasonCodes.push('exact_approval_token_required');
  if (!confirmationExact) reasonCodes.push('exact_confirmation_phrase_required');
  if (unsafePathCount > 0) reasonCodes.push('unsafe_paths_present');
  if (missingFieldCount > 0) reasonCodes.push('missing_required_fields_present');
  if (duplicate) reasonCodes.push('duplicate_promotion_detected');
  if (backendWritesOnPreview) reasonCodes.push('preview_must_be_read_only');

  return {
    armed: reasonCodes.length === 0,
    reasonCodes,
    candidateId,
    expectedConfirmation,
    previewCurrent,
    previewAllowsPromotion,
    tokenExact,
    confirmationExact,
    unsafePathCount,
    missingFieldCount,
    duplicateDetected: duplicate,
    previewReadOnly,
    backendWritesOnPreview,
  };
}
