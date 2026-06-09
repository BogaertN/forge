// tests/db.canonical.test.js
// Patch 221: protects Identity Vault canonical DB path normalization.
// This test is static on purpose: it proves code defaults do not fall back to root vault.db.

const fs = require('fs');
const path = require('path');

const root = path.resolve(__dirname, '..');
const dbJsPath = path.join(root, 'db.js');

function readText(filePath) {
  return fs.readFileSync(filePath, 'utf8');
}

describe('Identity Vault canonical database path', () => {
  test('db.js references data/identity_vault.db as the canonical local database', () => {
    const text = readText(dbJsPath);
    expect(text).toContain('identity_vault.db');
    expect(text).toContain('data');
  });

  test('db.js does not directly default to root-level vault.db', () => {
    const text = readText(dbJsPath);
    const forbidden = /path\.(join|resolve)\(__dirname,\s*['"]vault\.db['"]\)/;
    expect(forbidden.test(text)).toBe(false);
  });
});
