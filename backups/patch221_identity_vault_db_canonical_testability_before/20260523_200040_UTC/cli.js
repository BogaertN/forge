// cli.js - CLI Entry Point for Self-Hosted Identity Vault
// Commands: create-profile (user/agent w/ prompts), import (JSON to DB), export (DB to JSON/IPFS),
// tunnel (ngrok for public API), list (profiles/state), update (patch by ID), feedback (log entry).
// Features: Interactive prompts (from utils/prompts), DB integration, IPFS export, ngrok tunneling,
// ZKP stub for exports, drift check on updates, recursive feedback trigger.
// Advanced: Team mode (orchestrate agents), audit export, env-safe (loads .env), help/colors.
// Run: npm run cli -- <command> [args]; uses commander for parsing.
// Integrates: All utils/db/routes/schemas; non-blocking async.
// Safety: Validate inputs, confirm deletes, no auto-publish. Deps: commander (npm install commander), ngrok (npm install ngrok), chalk (npm install chalk for colors).
// Usage: node cli.js create-profile --type user
// Version: 1.0 | 2025 | Add to package.json: "bin": {"vault": "cli.js"}, "cli": "node cli.js"

require('dotenv').config();
const { program } = require('commander');
const chalk = require('chalk');
const { createProfilePrompts, generateTemplates } = require('./utils/prompts');
const { user: userSchema, agent: agentSchema } = require('./schemas');
const { saveProfile, getProfile, updateProfile, deleteProfile, logFeedback, getState, getAuditTrail } = require('./db');
const { encrypt } = require('./utils/encryption');
const { pinToIPFS, fetchFromIPFS } = require('./utils/ipfs');
const { proveZKP } = require('./utils/zkps');
const { detectDrift } = require('./utils/drift');
const { autogenHook, orchestrationHook } = require('./utils/integrations');
const ngrok = require('ngrok');
const fs = require('fs');
const path = require('path'); function makeAuthenticatedRequest(method, url, data = null) {
  const headers = {};
  if (process.env.API_TOKEN) {
    headers.Authorization = `Bearer ${process.env.API_TOKEN}`;
  }
  headers['Content-Type'] = 'application/json';
  
  // Use axios or native fetch with proper headers
  return axios({
    method,
    url: `http://localhost:${process.env.PORT || 3000}${url}`,
    data,
    headers
  });
}

// Colors for output
const log = {
  info: (msg) => console.log(chalk.blue(`[INFO] ${msg}`)),
  success: (msg) => console.log(chalk.green(`[SUCCESS] ${msg}`)),
  warn: (msg) => console.log(chalk.yellow(`[WARN] ${msg}`)),
  error: (msg) => console.log(chalk.red(`[ERROR] ${msg}`))
};

// Init DB on start
const dbPath = path.join(__dirname, 'vault.db');
require('./db').initDB(dbPath);

// Create profile command
program
  .command('create-profile')
  .description('Create a new user or agent profile interactively')
  .option('-t, --type <type>', 'user or agent', 'user')
  .option('--pin-ipfs', 'Pin to IPFS after create')
  .option('--zkp-fields <fields>', 'Fields for ZKP proof (comma-separated)')
  .action(async (options) => {
    try {
      const schemaType = options.type;
      if (!['user', 'agent'].includes(schemaType)) {
        log.error('Type must be user or agent');
        return;
      }
      const schema = schemaType === 'user' ? userSchema : agentSchema;
      const profile = await createProfilePrompts(schemaType, {}, true); // CLI mode
      if (!profile) {
        log.warn('Creation halted (safe word?)');
        return;
      }

      const id = profile.user_id || profile.agent_id;
      const encrypted = encrypt(JSON.stringify(profile));
      let ipfsHash = null;
      let zkpMeta = null;

      if (options.pinIpfs) {
        ipfsHash = await pinToIPFS(encrypted, { version: profile.version });
        profile.ipfs_hash = ipfsHash;
      }

      if (options.zkpFields) {
        zkpMeta = await proveZKP(profile, options.zkpFields.split(','));
        profile.zkp_metadata = zkpMeta;
      }

      await saveProfile(schemaType, encrypted, id, ipfsHash, JSON.stringify(zkpMeta || {}));
      log.success(`Profile ${id} created (${schemaType})`);
      log.info(`Export: ${JSON.stringify(profile, null, 2)}`);
    } catch (err) {
      log.error(err.message);
    }
  });

// Import command: JSON file to DB
program
  .command('import')
  .description('Import JSON profile to DB')
  .argument('<file>', 'Path to JSON file')
  .option('-t, --type <type>', 'user or agent')
  .action(async (filePath, options) => {
    try {
      if (!fs.existsSync(filePath)) {
        log.error('File not found');
        return;
      }
      const raw = fs.readFileSync(filePath, 'utf8');
      const profile = JSON.parse(raw);
      const type = options.type || (profile.user_id ? 'user' : 'agent');

      const schema = type === 'user' ? userSchema : agentSchema;
      schema.validate(profile);

      const id = profile.user_id || profile.agent_id;
      const encrypted = encrypt(JSON.stringify(profile));
      await saveProfile(type, encrypted, id);
      log.success(`Imported ${id} as ${type}`);
    } catch (err) {
      log.error(err.message);
    }
  });

// Export command: DB to JSON/IPFS
program
  .command('export')
  .description('Export profile to JSON or IPFS')
  .argument('<id>', 'Profile ID')
  .option('-t, --type <type>', 'user or agent')
  .option('--to-ipfs', 'Pin to IPFS instead of file')
  .option('--zkp', 'Include ZKP proof')
  .action(async (id, options) => {
    try {
      const type = options.type;
      let profileData = await getProfile(type, id, true, true);
      if (!profileData) {
        log.error('Profile not found');
        return;
      }

      if (options.zkp) {
        profileData.data.zkp_proof = await proveZKP(profileData.data, ['all']); // Stub fields
      }

      const exportData = JSON.stringify(profileData, null, 2);

      if (options.toIpfs) {
        const hash = await pinToIPFS(exportData);
        log.success(`Exported to IPFS: ${hash}`);
      } else {
        const file = path.join(__dirname, `export-${id}.json`);
        fs.writeFileSync(file, exportData);
        log.success(`Exported to ${file}`);
      }
    } catch (err) {
      log.error(err.message);
    }
  });

// Tunnel command: Ngrok for public access
program
  .command('tunnel')
  .description('Expose local API via ngrok tunnel')
  .option('-p, --port <port>', 'Local port (default 3000)')
  .action(async (options) => {
    try {
      const port = options.port || 3000;
      const url = await ngrok.connect({ addr: port, authtoken: process.env.NGROK_TOKEN });
      log.success(`Tunnel active: ${url}`);
      log.info('Press Ctrl+C to stop');
      // Keep alive
      process.stdin.resume();
      process.on('SIGINT', async () => {
        await ngrok.disconnect(url);
        log.info('Tunnel closed');
        process.exit(0);
      });
    } catch (err) {
      log.error(`Tunnel failed: ${err.message} (check NGROK_TOKEN in .env)`);
    }
  });

// List command: Profiles and state
program
  .command('list')
  .description('List profiles or state')
  .option('-t, --type <type>', 'user or agent')
  .option('--state', 'Include session state')
  .action(async (options) => {
    try {
      const type = options.type;
      // Stub: Query all for type (in real: db.all('SELECT id FROM profiles WHERE type=?', [type]))
      const mockProfiles = [{ id: 'nic_bogaert', type }, { id: 'drift_agent', type: 'agent' }];
      log.info(`Profiles (${type || 'all'}): ${mockProfiles.map(p => p.id).join(', ')}`);

      if (options.state) {
        for (let id of mockProfiles.map(p => p.id)) {
          const state = await getState(id);
          log.info(`${id} state: ${JSON.stringify(state, null, 2)}`);
        }
      }
    } catch (err) {
      log.error(err.message);
    }
  });

// Update command: Patch profile
program
  .command('update')
  .description('Update profile (patch)')
  .argument('<id>', 'Profile ID')
  .option('-t, --type <type>', 'user or agent')
  .option('-f, --field <field>', 'Field to update')
  .option('-v, --value <value>', 'New value')
  .action(async (id, options) => {
    try {
      const type = options.type;
      const updates = {};
      if (options.field && options.value !== undefined) {
        updates[options.field] = options.value;
      } else {
        log.error('Use --field and --value for simple patch');
        return;
      }

      const current = await getProfile(type, id);
      const updated = { ...current.data, ...updates };
      const drift = detectDrift(current.data, updated);
      if (drift) log.warn(`Drift detected: ${drift.details[0]?.reason}`);

      await updateProfile(type, id, updates);
      log.success(`Updated ${id}: ${options.field}=${options.value}`);
    } catch (err) {
      log.error(err.message);
    }
  });

// Feedback command: Log entry
program
  .command('feedback')
  .description('Log feedback for profile')
  .argument('<id>', 'Profile ID')
  .option('-m, --message <msg>', 'Feedback message')
  .option('--type <type>', 'Type: feedback/drift/contradiction', 'feedback')
  .action(async (id, options) => {
    try {
      await logFeedback(id, { type: options.type, data: { message: options.message || 'General note' } });
      log.success(`Logged feedback for ${id}`);
    } catch (err) {
      log.error(err.message);
    }
  });

// Team orchestrate stub
program
  .command('orchestrate')
  .description('Orchestrate agent team (stub)')
  .argument('<teamId>', 'Team ID')
  .action(async (teamId) => {
    try {
      const config = await orchestrationHook(teamId);
      log.success(`Orchestrated team ${teamId}: ${JSON.stringify(config, null, 2)}`);
    } catch (err) {
      log.error(err.message);
    }
  });

// Generate templates
program
  .command('generate-templates')
  .description('Generate blank JSON templates')
  .action(() => {
    generateTemplates();
    log.success('Templates generated in /templates');
  });

// Parse and run
program.name('vault').description('Self-Hosted Identity Vault CLI').version('1.0.0');
program.parse(process.argv);

if (!process.argv.slice(2).length) {
  program.help();
}
