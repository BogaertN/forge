PRAGMA foreign_keys = ON;
CREATE TABLE IF NOT EXISTS contributor_principal_status_events_v2 (
    status_event_id TEXT PRIMARY KEY,
    principal_id TEXT NOT NULL,
    event_type TEXT NOT NULL CHECK (event_type IN ('authority_activation','authority_suspension','authority_revocation','authority_restoration')),
    authority_status TEXT NOT NULL CHECK (authority_status IN ('active','suspended','revoked')),
    reason_code TEXT NOT NULL,
    prior_status_event_hash TEXT,
    event_hash TEXT NOT NULL UNIQUE CHECK (length(event_hash) = 64),
    effective_at_utc TEXT NOT NULL,
    schema_version TEXT NOT NULL,
    FOREIGN KEY (principal_id) REFERENCES contributor_principals(principal_id)
);
CREATE TABLE IF NOT EXISTS contributor_consent_events_v2 (
    consent_event_id TEXT PRIMARY KEY,
    consent_record_id TEXT NOT NULL,
    principal_id TEXT NOT NULL,
    event_type TEXT NOT NULL CHECK (event_type IN ('initial_scope_grant','scope_replacement','scope_revocation')),
    local_identity_storage_authorized INTEGER NOT NULL CHECK (local_identity_storage_authorized IN (0,1)),
    internal_attribution_reference_authorized INTEGER NOT NULL CHECK (internal_attribution_reference_authorized IN (0,1)),
    capsule_candidate_reference_authorized INTEGER NOT NULL CHECK (capsule_candidate_reference_authorized IN (0,1)),
    public_display_authorized INTEGER NOT NULL CHECK (public_display_authorized IN (0,1)),
    portability_authorized INTEGER NOT NULL CHECK (portability_authorized IN (0,1)),
    economic_processing_authorized INTEGER NOT NULL CHECK (economic_processing_authorized IN (0,1)),
    ct_minting_authorized INTEGER NOT NULL CHECK (ct_minting_authorized IN (0,1)),
    investment_processing_authorized INTEGER NOT NULL CHECK (investment_processing_authorized IN (0,1)),
    authorization_basis TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('active','revoked')),
    effective_at_utc TEXT NOT NULL,
    prior_consent_event_hash TEXT,
    event_hash TEXT NOT NULL UNIQUE CHECK (length(event_hash) = 64),
    schema_version TEXT NOT NULL,
    FOREIGN KEY (principal_id) REFERENCES contributor_principals(principal_id)
);
CREATE INDEX IF NOT EXISTS idx_contributor_principal_status_events_v2_principal ON contributor_principal_status_events_v2(principal_id, effective_at_utc);
CREATE INDEX IF NOT EXISTS idx_contributor_consent_events_v2_principal ON contributor_consent_events_v2(principal_id, effective_at_utc);
CREATE TRIGGER IF NOT EXISTS block_update_contributor_principal_status_events_v2 BEFORE UPDATE ON contributor_principal_status_events_v2
BEGIN SELECT RAISE(ABORT, 'contributor_principal_status_events_v2 is append-only'); END;
CREATE TRIGGER IF NOT EXISTS block_delete_contributor_principal_status_events_v2 BEFORE DELETE ON contributor_principal_status_events_v2
BEGIN SELECT RAISE(ABORT, 'contributor_principal_status_events_v2 cannot be deleted'); END;
CREATE TRIGGER IF NOT EXISTS block_update_contributor_consent_events_v2 BEFORE UPDATE ON contributor_consent_events_v2
BEGIN SELECT RAISE(ABORT, 'contributor_consent_events_v2 is append-only'); END;
CREATE TRIGGER IF NOT EXISTS block_delete_contributor_consent_events_v2 BEFORE DELETE ON contributor_consent_events_v2
BEGIN SELECT RAISE(ABORT, 'contributor_consent_events_v2 cannot be deleted'); END;
