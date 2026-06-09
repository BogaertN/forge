CREATE TABLE IF NOT EXISTS contribution_event_evidence_manifests_v1 (
    evidence_manifest_id TEXT PRIMARY KEY,
    event_id TEXT NOT NULL UNIQUE,
    evidence_manifest_hash TEXT NOT NULL UNIQUE CHECK (length(evidence_manifest_hash) = 64),
    evidence_manifest_json TEXT NOT NULL,
    schema_version TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS controlled_write_authorizations_v1 (
    authorization_id TEXT PRIMARY KEY,
    event_id TEXT NOT NULL UNIQUE,
    capsule_id TEXT NOT NULL UNIQUE,
    principal_id TEXT NOT NULL,
    persistence_consent_event_hash TEXT NOT NULL CHECK (length(persistence_consent_event_hash) = 64),
    approval_token_hash TEXT NOT NULL CHECK (length(approval_token_hash) = 64),
    authorization_hash TEXT NOT NULL UNIQUE CHECK (length(authorization_hash) = 64),
    status TEXT NOT NULL CHECK (status = 'consumed_single_controlled_write'),
    schema_version TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS contribution_event_payloads_v1 (
    event_id TEXT PRIMARY KEY,
    event_hash TEXT NOT NULL UNIQUE CHECK (length(event_hash) = 64),
    event_payload_json TEXT NOT NULL,
    schema_version TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS memory_capsule_candidate_payloads_v1 (
    capsule_id TEXT PRIMARY KEY,
    top_level_hash TEXT NOT NULL UNIQUE CHECK (length(top_level_hash) = 64),
    candidate_payload_json TEXT NOT NULL,
    schema_version TEXT NOT NULL
);
CREATE TABLE IF NOT EXISTS controlled_write_receipts_v1 (
    write_receipt_id TEXT PRIMARY KEY,
    event_id TEXT NOT NULL UNIQUE,
    capsule_id TEXT NOT NULL UNIQUE,
    principal_id TEXT NOT NULL,
    transaction_hash TEXT NOT NULL UNIQUE CHECK (length(transaction_hash) = 64),
    receipt_json TEXT NOT NULL,
    status TEXT NOT NULL CHECK (status = 'committed_pending_validation_not_finalized_not_minted'),
    schema_version TEXT NOT NULL
);
CREATE TRIGGER IF NOT EXISTS block_update_evidence_manifests_v1 BEFORE UPDATE ON contribution_event_evidence_manifests_v1 BEGIN SELECT RAISE(ABORT, 'contribution_event_evidence_manifests_v1 is append-only'); END;
CREATE TRIGGER IF NOT EXISTS block_delete_evidence_manifests_v1 BEFORE DELETE ON contribution_event_evidence_manifests_v1 BEGIN SELECT RAISE(ABORT, 'contribution_event_evidence_manifests_v1 cannot be deleted'); END;
CREATE TRIGGER IF NOT EXISTS block_update_controlled_write_authorizations_v1 BEFORE UPDATE ON controlled_write_authorizations_v1 BEGIN SELECT RAISE(ABORT, 'controlled_write_authorizations_v1 is append-only'); END;
CREATE TRIGGER IF NOT EXISTS block_delete_controlled_write_authorizations_v1 BEFORE DELETE ON controlled_write_authorizations_v1 BEGIN SELECT RAISE(ABORT, 'controlled_write_authorizations_v1 cannot be deleted'); END;
CREATE TRIGGER IF NOT EXISTS block_update_contribution_event_payloads_v1 BEFORE UPDATE ON contribution_event_payloads_v1 BEGIN SELECT RAISE(ABORT, 'contribution_event_payloads_v1 is append-only'); END;
CREATE TRIGGER IF NOT EXISTS block_delete_contribution_event_payloads_v1 BEFORE DELETE ON contribution_event_payloads_v1 BEGIN SELECT RAISE(ABORT, 'contribution_event_payloads_v1 cannot be deleted'); END;
CREATE TRIGGER IF NOT EXISTS block_update_memory_capsule_candidate_payloads_v1 BEFORE UPDATE ON memory_capsule_candidate_payloads_v1 BEGIN SELECT RAISE(ABORT, 'memory_capsule_candidate_payloads_v1 is append-only'); END;
CREATE TRIGGER IF NOT EXISTS block_delete_memory_capsule_candidate_payloads_v1 BEFORE DELETE ON memory_capsule_candidate_payloads_v1 BEGIN SELECT RAISE(ABORT, 'memory_capsule_candidate_payloads_v1 cannot be deleted'); END;
CREATE TRIGGER IF NOT EXISTS block_update_controlled_write_receipts_v1 BEFORE UPDATE ON controlled_write_receipts_v1 BEGIN SELECT RAISE(ABORT, 'controlled_write_receipts_v1 is append-only'); END;
CREATE TRIGGER IF NOT EXISTS block_delete_controlled_write_receipts_v1 BEFORE DELETE ON controlled_write_receipts_v1 BEGIN SELECT RAISE(ABORT, 'controlled_write_receipts_v1 cannot be deleted'); END;
