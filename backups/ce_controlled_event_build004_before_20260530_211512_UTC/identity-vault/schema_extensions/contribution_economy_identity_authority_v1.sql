-- AI.Web Identity Vault — Contribution Economy Contributor Authority Schema v1
-- Build ID: CE-IV-LEDGER-CAPSULE-BUILD-001
-- Purpose: immutable Identity Vault principal binding and append-only consent/audit events.
-- Existing user_profiles and agent_profiles rows are never altered by this schema.

PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS contributor_principals (
    principal_id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL UNIQUE,
    principal_type TEXT NOT NULL CHECK (principal_type IN ('human_owner_builder', 'human_contributor', 'authorized_node')),
    authority_status TEXT NOT NULL CHECK (authority_status IN ('internal_contribution_authority_active', 'revoked_by_append_only_event')),
    disclosure_class TEXT NOT NULL CHECK (disclosure_class = 'private_identity_vault_only'),
    pseudonymous_alias_id TEXT,
    source_user_profile_hash TEXT NOT NULL CHECK (length(source_user_profile_hash) = 64),
    authority_manifest_relative_path TEXT NOT NULL,
    authority_manifest_hash TEXT NOT NULL CHECK (length(authority_manifest_hash) = 64),
    identity_proof_hash TEXT NOT NULL CHECK (length(identity_proof_hash) = 64),
    schema_version TEXT NOT NULL,
    created_at_utc TEXT NOT NULL,
    record_hash TEXT NOT NULL UNIQUE CHECK (length(record_hash) = 64),
    FOREIGN KEY (user_id) REFERENCES user_profiles(user_id)
);

CREATE TABLE IF NOT EXISTS contributor_consent_events (
    consent_event_id TEXT PRIMARY KEY,
    consent_record_id TEXT NOT NULL,
    principal_id TEXT NOT NULL,
    event_type TEXT NOT NULL CHECK (event_type IN ('initial_scope_grant', 'scope_replacement', 'scope_revocation')),
    local_identity_storage_authorized INTEGER NOT NULL CHECK (local_identity_storage_authorized IN (0, 1)),
    internal_attribution_reference_authorized INTEGER NOT NULL CHECK (internal_attribution_reference_authorized IN (0, 1)),
    capsule_candidate_reference_authorized INTEGER NOT NULL CHECK (capsule_candidate_reference_authorized IN (0, 1)),
    public_display_authorized INTEGER NOT NULL CHECK (public_display_authorized IN (0, 1)),
    portability_authorized INTEGER NOT NULL CHECK (portability_authorized IN (0, 1)),
    economic_processing_authorized INTEGER NOT NULL CHECK (economic_processing_authorized IN (0, 1)),
    ct_minting_authorized INTEGER NOT NULL CHECK (ct_minting_authorized IN (0, 1)),
    investment_processing_authorized INTEGER NOT NULL CHECK (investment_processing_authorized IN (0, 1)),
    authorization_basis TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status IN ('active_limited_internal_consent', 'revoked', 'superseded')),
    effective_at_utc TEXT NOT NULL,
    prior_consent_event_hash TEXT,
    event_hash TEXT NOT NULL UNIQUE CHECK (length(event_hash) = 64),
    schema_version TEXT NOT NULL,
    FOREIGN KEY (principal_id) REFERENCES contributor_principals(principal_id)
);

CREATE TABLE IF NOT EXISTS contributor_authority_audit_events (
    audit_event_id TEXT PRIMARY KEY,
    principal_id TEXT NOT NULL,
    event_type TEXT NOT NULL,
    event_payload_json TEXT NOT NULL,
    prior_audit_event_hash TEXT,
    event_hash TEXT NOT NULL UNIQUE CHECK (length(event_hash) = 64),
    recorded_at_utc TEXT NOT NULL,
    schema_version TEXT NOT NULL,
    FOREIGN KEY (principal_id) REFERENCES contributor_principals(principal_id)
);

CREATE INDEX IF NOT EXISTS idx_contributor_principals_user_id ON contributor_principals(user_id);
CREATE INDEX IF NOT EXISTS idx_contributor_consent_events_principal_id ON contributor_consent_events(principal_id);
CREATE INDEX IF NOT EXISTS idx_contributor_authority_audit_events_principal_id ON contributor_authority_audit_events(principal_id);

CREATE TRIGGER IF NOT EXISTS block_update_contributor_principals BEFORE UPDATE ON contributor_principals
BEGIN SELECT RAISE(ABORT, 'contributor_principals is append-only; register a correction event instead'); END;
CREATE TRIGGER IF NOT EXISTS block_delete_contributor_principals BEFORE DELETE ON contributor_principals
BEGIN SELECT RAISE(ABORT, 'contributor_principals cannot be deleted'); END;
CREATE TRIGGER IF NOT EXISTS block_update_contributor_consent_events BEFORE UPDATE ON contributor_consent_events
BEGIN SELECT RAISE(ABORT, 'contributor_consent_events is append-only; insert a replacement or revocation event'); END;
CREATE TRIGGER IF NOT EXISTS block_delete_contributor_consent_events BEFORE DELETE ON contributor_consent_events
BEGIN SELECT RAISE(ABORT, 'contributor_consent_events cannot be deleted'); END;
CREATE TRIGGER IF NOT EXISTS block_update_contributor_authority_audit_events BEFORE UPDATE ON contributor_authority_audit_events
BEGIN SELECT RAISE(ABORT, 'contributor_authority_audit_events is append-only'); END;
CREATE TRIGGER IF NOT EXISTS block_delete_contributor_authority_audit_events BEFORE DELETE ON contributor_authority_audit_events
BEGIN SELECT RAISE(ABORT, 'contributor_authority_audit_events cannot be deleted'); END;
