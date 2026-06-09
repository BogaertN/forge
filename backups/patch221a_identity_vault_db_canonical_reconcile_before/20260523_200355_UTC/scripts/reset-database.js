const fs = require('fs');
const path = require('path');

console.log('🔄 Resetting database...');

// Remove existing database
const dbPath = process.env.DB_PATH || './data/identity_vault.db';
const walPath = dbPath + '-wal';
const shmPath = dbPath + '-shm';

// Remove all database files
[dbPath, walPath, shmPath].forEach(file => {
  if (fs.existsSync(file)) {
    fs.unlinkSync(file);
    console.log('🗑️  Removed:', file);
  }
});

console.log('✅ Database reset complete');
console.log('💡 Now run: node scripts/init-database.js');
