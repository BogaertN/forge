// db.js - SQLite Database Layer for Self-Hosted Identity Vault
// Handles init, schema (profiles table with JSON blob for flexibility), CRUD ops for user/agent profiles,
// versioning (via timestamp/version field), logging (feedback/state tables for audits, drifts),
// encryption passthrough (store encrypted blobs), multi-agent session state, regulatory exports.
// Integrates: Query hooks for IPFS hashes, ZKP metadata, recursive feedback storage.
// Version: 1.0 | 2025 | Privacy: All data encrypted; local-only.
// Exports: initDB, getProfile, saveProfile, updateProfile, deleteProfile, logFeedback, getState, getAuditTrail.

const sqlite3 = require('sqlite3').verbose();
const path = require('path');
const { encrypt, decrypt } = require('./utils/encryption'); // Passthrough for at-rest encryption

let db; // Global DB instance (single connection for safety)

// Profiles table schema: Flexible JSON storage for user/agent (type discriminator), with versioning/audit fields
const createSchema = `
  CREATE TABLE IF NOT EXISTS profiles (
    id TEXT PRIMARY KEY,  -- user_id or agent_id
    type TEXT NOT NULL,   -- 'user' or 'agent'
    data TEXT NOT NULL,   -- Encrypted JSON blob
    version TEXT NOT NULL DEFAULT '1.0.0',
    last_updated TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    ipfs_hash TEXT,       -- For decentralized pinning
    zkp_metadata TEXT     -- Proof stubs for trust handshakes
  );

  CREATE TABLE IF NOT EXISTS feedback_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    profile_id TEXT NOT NULL,
    type TEXT NOT NULL,   -- 'feedback', 'drift', 'contradiction', 'export'
    data TEXT NOT NULL,   -- JSON: {alert: '...', timestamp: '...'}
    timestamp TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (profile_id) REFERENCES profiles (id)
  );

  CREATE TABLE IF NOT EXISTS session_state (
    id TEXT PRIMARY KEY,  -- profile_id
    phase TEXT,
    waiting_for TEXT,
    last_feedback TEXT,
    last_action TEXT,
    timestamp TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id) REFERENCES profiles (id)
  );

  CREATE INDEX IF NOT EXISTS idx_profiles_type ON profiles(type);
  CREATE INDEX IF NOT EXISTS idx_logs_profile ON feedback_logs(profile_id);
`;

// Init DB: Safe, local file-based (vault.db in project root, gitignore'd)
function initDB(dbPath) {
  return new Promise((resolve, reject) => {
    db = new sqlite3.Database(dbPath, (err) => {
      if (err) {
        console.error('DB Init Error:', err.message);
        reject(err);
      } else {
        db.exec(createSchema, (err) => {
          if (err) reject(err);
          else {
            console.log('DB Initialized: Profiles, logs, and state tables ready.');
            resolve(db);
          }
        });
      }
    });
  });
}

// Save new profile: Encrypt, insert with version/timestamp, optional IPFS/ZKP prep
async function saveProfile(type, encryptedData, id, ipfsHash = null, zkpMeta = null) {
  return new Promise((resolve, reject) => {
    const stmt = db.prepare(`
      INSERT INTO profiles (id, type, data, version, ipfs_hash, zkp_metadata)
      VALUES (?, ?, ?, ?, ?, ?)
    `);
    stmt.run(id, type, encryptedData, '1.0.0', ipfsHash, zkpMeta, function(err) {
      if (err) reject(err);
      else {
        // Init session state
        db.run(`INSERT OR IGNORE INTO session_state (id) VALUES (?)`, [id]);
        resolve(this.lastID);
      }
      stmt.finalize();
    });
  });
}

// Get profile: Fetch, decrypt, include state/logs if requested
async function getProfile(type, id, includeState = true, includeLogs = false) {
  return new Promise((resolve, reject) => {
    db.get(`
      SELECT * FROM profiles WHERE type = ? AND id = ?
    `, [type, id], (err, row) => {
      if (err) reject(err);
      else if (!row) resolve(null); // Not found
      else {
        const decrypted = decrypt(row.data, process.env.ENCRYPTION_KEY);
        if (!decrypted) reject(new Error('Decryption failed: Invalid key'));
        const profile = JSON.parse(decrypted);
        if (includeState) {
          db.get(`SELECT * FROM session_state WHERE id = ?`, [id], (err, state) => {
            if (!err) profile.session_state = state;
            if (includeLogs) getAuditTrail(id).then(logs => profile.logs = logs);
            resolve({ ...row, data: profile });
          });
        } else {
          resolve({ ...row, data: profile });
        }
      }
    });
  });
}

// Update profile: Version bump, encrypt updates, log changes for audit
async function updateProfile(type, id, updates, partial = true) {
  return new Promise((resolve, reject) => {
    // Fetch current for versioning
    db.get(`SELECT data, version FROM profiles WHERE type = ? AND id = ?`, [type, id], async (err, row) => {
      if (err || !row) reject(new Error('Profile not found'));
      else {
        const current = JSON.parse(decrypt(row.data, process.env.ENCRYPTION_KEY));
        const updatedProfile = partial ? { ...current, ...updates } : updates;
        const newVersion = `${parseFloat(row.version) + 0.1}`.substring(0, 5);
        updatedProfile.version = newVersion;
        updatedProfile.last_updated = new Date().toISOString();
        const encrypted = encrypt(JSON.stringify(updatedProfile), process.env.ENCRYPTION_KEY);
        
        // Update DB
        db.run(`
          UPDATE profiles SET data = ?, version = ?, last_updated = CURRENT_TIMESTAMP
          WHERE type = ? AND id = ?
        `, [encrypted, newVersion, type, id], function(err) {
          if (err) reject(err);
          else {
            // Log change for audit
            logFeedback(id, { type: 'update', changes: Object.keys(updates || {}), oldVersion: row.version });
            // Update state timestamp
            db.run(`UPDATE session_state SET timestamp = CURRENT_TIMESTAMP WHERE id = ?`, [id]);
            resolve(this.changes);
          }
        });
      }
    });
  });
}

// Delete profile: Soft-delete via flag (for audits); hard-delete optional
async function deleteProfile(type, id, hard = false) {
  return new Promise((resolve, reject) => {
    if (hard) {
      db.run(`DELETE FROM profiles WHERE type = ? AND id = ?`, [type, id], function(err) {
        if (err) reject(err);
        else {
          // Cascade delete logs/state
          db.run(`DELETE FROM feedback_logs WHERE profile_id = ?`, [id]);
          db.run(`DELETE FROM session_state WHERE id = ?`, [id]);
          resolve(this.changes);
        }
      });
    } else {
      // Soft: Add deleted flag to data
      updateProfile(type, id, { deleted: true, version: '0.0.0' }).then(resolve).catch(reject);
    }
  });
}

// Log feedback/drift/contradictions: For recursive loops, audits, regulatory
async function logFeedback(profileId, logData) {
  return new Promise((resolve, reject) => {
    const stmt = db.prepare(`
      INSERT INTO feedback_logs (profile_id, type, data)
      VALUES (?, ?, ?)
    `);
    logData.timestamp = new Date().toISOString();
    stmt.run(profileId, logData.type, JSON.stringify(logData), function(err) {
      if (err) reject(err);
      else resolve(this.lastID);
      stmt.finalize();
    });
  });
}

// Get state: Session phase, waiting, last action/feedback (memory preservation)
async function getState(id) {
  return new Promise((resolve, reject) => {
    db.get(`SELECT * FROM session_state WHERE id = ?`, [id], (err, row) => {
      if (err) reject(err);
      else resolve(row || { id, phase: '', waiting_for: '', last_feedback: '', last_action: '' });
    });
  });
}

// Update state: For carryover, e.g., after agent actions
async function updateState(id, updates) {
  return new Promise((resolve, reject) => {
    const fields = Object.keys(updates).map(k => `${k} = ?`).join(', ');
    const values = Object.values(updates);
    values.push(id, ...values); // id first, then updates
    db.run(`
      UPDATE session_state SET ${fields}, timestamp = CURRENT_TIMESTAMP
      WHERE id = ?
    `, values, function(err) {
      if (err) reject(err);
      else resolve(this.changes);
    });
  });
}

// Get audit trail: Full logs for profile (regulatory exports, drift review)
async function getAuditTrail(profileId, limit = 100) {
  return new Promise((resolve, reject) => {
    db.all(`
      SELECT * FROM feedback_logs
      WHERE profile_id = ?
      ORDER BY timestamp DESC
      LIMIT ?
    `, [profileId, limit], (err, rows) => {
      if (err) reject(err);
      else {
        rows.forEach(row => {
          row.data = JSON.parse(row.data);
        });
        resolve(rows);
      }
    });
  });
}

// Close DB (graceful shutdown)
function closeDB() {
  if (db) {
    db.close((err) => {
      if (err) console.error('DB Close Error:', err.message);
      else console.log('DB closed safely.');
    });
  }
}

// Export for server.js
module.exports = {
  initDB,
  saveProfile,
  getProfile,
  updateProfile,
  deleteProfile,
  logFeedback,
  getState,
  updateState,
  getAuditTrail,
  closeDB
};
