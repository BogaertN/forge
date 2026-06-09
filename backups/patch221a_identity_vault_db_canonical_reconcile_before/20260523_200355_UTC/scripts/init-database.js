const sqlite3 = require('sqlite3').verbose();
const path = require('path');
const fs = require('fs');

// Create data directory if it doesn't exist
const dataDir = path.dirname(process.env.DB_PATH || './data/identity_vault.db');
if (!fs.existsSync(dataDir)) {
  fs.mkdirSync(dataDir, { recursive: true });
}

const dbPath = process.env.DB_PATH || './data/identity_vault.db';
console.log('Initializing database at:', dbPath);

const db = new sqlite3.Database(dbPath, (err) => {
  if (err) {
    console.error('Error opening database:', err.message);
    process.exit(1);
  }
  console.log('Connected to SQLite database');
});

// Create tables
const initializeSchema = () => {
  const queries = [
    // User profiles table
    `CREATE TABLE IF NOT EXISTS user_profiles (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      user_id TEXT UNIQUE NOT NULL,
      canonical_name TEXT NOT NULL,
      interaction_preferences TEXT DEFAULT '{}',
      meta_rules TEXT DEFAULT '{}',
      session_defaults TEXT DEFAULT '{}',
      drift_tracking TEXT DEFAULT '{}',
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
      updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
      version INTEGER DEFAULT 1,
      is_active INTEGER DEFAULT 1
    )`,

    // Agent profiles table
    `CREATE TABLE IF NOT EXISTS agent_profiles (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      agent_id TEXT UNIQUE NOT NULL,
      canonical_name TEXT NOT NULL,
      role TEXT,
      capabilities TEXT DEFAULT '{}',
      limits TEXT DEFAULT '{}',
      enforcement TEXT DEFAULT '{}',
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
      updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
      version INTEGER DEFAULT 1,
      is_active INTEGER DEFAULT 1
    )`,

    // Audit logs table
    `CREATE TABLE IF NOT EXISTS audit_logs (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      profile_id TEXT NOT NULL,
      profile_type TEXT NOT NULL,
      action TEXT NOT NULL,
      details TEXT,
      timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
      ip_address TEXT,
      user_agent TEXT
    )`,

    // Session state table
    `CREATE TABLE IF NOT EXISTS session_state (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      profile_id TEXT NOT NULL,
      profile_type TEXT NOT NULL,
      session_data TEXT DEFAULT '{}',
      created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
      updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
      expires_at DATETIME
    )`,

    // Feedback logs table
    `CREATE TABLE IF NOT EXISTS feedback_logs (
      id INTEGER PRIMARY KEY AUTOINCREMENT,
      profile_id TEXT NOT NULL,
      feedback_type TEXT NOT NULL,
      message TEXT,
      data TEXT DEFAULT '{}',
      timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
      resolved INTEGER DEFAULT 0
    )`,

    // Create indexes for better performance
    `CREATE INDEX IF NOT EXISTS idx_user_profiles_user_id ON user_profiles(user_id)`,
    `CREATE INDEX IF NOT EXISTS idx_agent_profiles_agent_id ON agent_profiles(agent_id)`,
    `CREATE INDEX IF NOT EXISTS idx_audit_logs_profile ON audit_logs(profile_id, profile_type)`,
    `CREATE INDEX IF NOT EXISTS idx_session_state_profile ON session_state(profile_id, profile_type)`,
    `CREATE INDEX IF NOT EXISTS idx_feedback_logs_profile ON feedback_logs(profile_id)`
  ];

  const runQuery = (query, index = 0) => {
    if (index >= queries.length) {
      console.log('✅ Database schema initialized successfully');
      
      // Verify tables were created
      db.all("SELECT name FROM sqlite_master WHERE type='table'", (err, tables) => {
        if (err) {
          console.error('Error checking tables:', err.message);
        } else {
          console.log('📋 Created tables:', tables.map(t => t.name).join(', '));
        }
        db.close((err) => {
          if (err) {
            console.error('Error closing database:', err.message);
          } else {
            console.log('Database connection closed');
          }
        });
      });
      return;
    }

    db.run(queries[index], (err) => {
      if (err) {
        console.error(`Error running query ${index}:`, err.message);
        console.error('Query was:', queries[index]);
        process.exit(1);
      } else {
        console.log(`✓ Query ${index + 1}/${queries.length} completed`);
        runQuery(queries, index + 1);
      }
    });
  };

  runQuery(queries);
};

// Enable foreign keys and WAL mode
db.serialize(() => {
  db.run("PRAGMA foreign_keys = ON");
  db.run("PRAGMA journal_mode = WAL");
  db.run("PRAGMA synchronous = NORMAL");
  db.run("PRAGMA cache_size = 1000");
  db.run("PRAGMA temp_store = memory");
  
  console.log('⚙️  Database pragmas set');
  initializeSchema();
});
