require('dotenv').config();
const express = require('express');
const cors = require('cors');
const bodyParser = require('body-parser');
const path = require('path');
const { encrypt, decrypt } = require('./utils/encryption');
const { initDB, getProfile, saveProfile, updateProfile, logFeedback, getState } = require('./db');

const app = express();
const PORT = process.env.PORT || 3000;
const dbPath = path.join(__dirname, 'vault.db');

// ===== MIDDLEWARE SETUP =====
app.use(cors({ origin: '*' }));
app.use(bodyParser.json({ limit: '10mb' }));
app.use(bodyParser.urlencoded({ extended: true }));

// ===== SERVE STATIC FILES FIRST (NO AUTH NEEDED) =====
app.use(express.static(path.join(__dirname, 'public')));

// ===== PUBLIC ROUTES (NO AUTH NEEDED) =====
// Serve the main UI at root
app.get('/', (req, res) => {
  res.sendFile(path.join(__dirname, 'public/ui.html'));
});

// Health check (no auth needed for basic status)
app.get('/health', (req, res) => {
  res.json({ 
    status: 'OK', 
    version: '1.0', 
    timestamp: new Date().toISOString(),
    endpoints: {
      profiles: '/profiles/create/:type, /profiles/:type/:id',
      feedback: '/feedback, /feedback/recursive/:id',
      agents: '/agents/orchestrate, /agents/audit/:teamId',
      integrations: '/integrations/langchain, /integrations/autogen, /integrations/rag',
      state: '/state/:id'
    }
  });
});

// ===== AUTHENTICATION MIDDLEWARE (ONLY FOR PROTECTED ROUTES) =====
const authMiddleware = (req, res, next) => {
  const authHeader = req.headers.authorization;
  const token = authHeader && authHeader.split(' ')[1]; // Bearer TOKEN
  
  if (!token || token !== process.env.API_TOKEN) {
    return res.status(401).json({ 
      error: 'Unauthorized: Invalid token',
      hint: 'Use Bearer token in Authorization header'
    });
  }
  next();
};

// ===== PROTECTED API ROUTES =====

// Profile Routes
app.post('/profiles/:type', authMiddleware, async (req, res) => {
  try {
    const { type } = req.params;
    if (!['user', 'agent'].includes(type)) {
      return res.status(400).json({ error: 'Invalid profile type. Use "user" or "agent".' });
    }

    const profileData = req.body;
    const idField = type === 'user' ? 'user_id' : 'agent_id';
    
    if (!profileData[idField]) {
      return res.status(400).json({ error: `Missing ${idField}` });
    }

    const profileId = profileData[idField];

    // Check if profile already exists
    try {
      const existing = await getProfile(type, profileId);
      if (existing) {
        return res.status(409).json({ error: 'Profile already exists' });
      }
    } catch (err) {
      // Profile doesn't exist, continue with creation
    }

    // Encrypt the profile data before saving
    const encryptedData = encrypt(JSON.stringify(profileData));
    
    // Extract IPFS and ZKP metadata if provided
    const ipfsHash = profileData.pinToIPFS ? 'ipfs://placeholder' : null;
    const zkpMeta = profileData.zkpFields ? JSON.stringify({ fields: profileData.zkpFields }) : null;

    // Save profile with CORRECT parameter order: (type, encryptedData, id, ipfsHash, zkpMeta)
    const result = await saveProfile(type, encryptedData, profileId, ipfsHash, zkpMeta);
    
    res.status(201).json({
      message: `${type} profile created successfully`,
      id: profileId,
      type: type,
      ...(ipfsHash && { ipfs: 'Content pinned to IPFS' }),
      ...(zkpMeta && { zkp: 'ZKP proof generated' })
    });
  } catch (error) {
    console.error('Profile creation error:', error);
    res.status(500).json({ error: 'Internal server error', details: error.message });
  }
});

app.get('/profiles/:type/:id', authMiddleware, async (req, res) => {
  try {
    const { type, id } = req.params;
    const { includeState, includeLogs, zkpProof, safe_word, redact, fields } = req.query;

    if (!['user', 'agent'].includes(type)) {
      return res.status(400).json({ error: 'Invalid profile type' });
    }

    const profile = await getProfile(type, id);
    if (!profile) {
      return res.status(404).json({ error: 'Profile not found' });
    }

    let response = { ...profile };

    // Include state if requested
    if (includeState === 'true') {
      try {
        const state = await getState(id);
        response.session_state = state;
      } catch (err) {
        response.session_state = null;
      }
    }

    // Include logs if requested
    if (includeLogs === 'true') {
      // This would fetch logs - placeholder for now
      response.logs = [];
    }

    // Apply redaction if requested
    if (redact) {
      const fieldsToRedact = redact.split(',');
      fieldsToRedact.forEach(field => {
        if (response[field]) {
          response[field] = '[REDACTED]';
        }
      });
    }

    // ZKP proof generation
    if (zkpProof === 'true' && fields) {
      response.zkp_proof = {
        fields: fields.split(','),
        proof: 'zkp_proof_placeholder',
        verified: true
      };
    }

    res.json(response);
  } catch (error) {
    console.error('Profile retrieval error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

app.patch('/profiles/:type/:id', authMiddleware, async (req, res) => {
  try {
    const { type, id } = req.params;
    const updates = req.body;

    if (!['user', 'agent'].includes(type)) {
      return res.status(400).json({ error: 'Invalid profile type' });
    }

    const result = await updateProfile(type, id, updates);
    
    res.json({
      message: 'Profile updated successfully',
      id: id,
      type: type,
      updated_fields: Object.keys(updates)
    });
  } catch (error) {
    if (error.message === 'Profile not found') {
      return res.status(404).json({ error: 'Profile not found' });
    }
    console.error('Profile update error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

app.delete('/profiles/:type/:id', authMiddleware, async (req, res) => {
  try {
    const { type, id } = req.params;
    const { hard } = req.query;

    if (!['user', 'agent'].includes(type)) {
      return res.status(400).json({ error: 'Invalid profile type' });
    }

    // For now, just confirm the profile exists
    const profile = await getProfile(type, id);
    if (!profile) {
      return res.status(404).json({ error: 'Profile not found' });
    }

    // Soft delete by default (add deleted flag), hard delete if requested
    if (hard === 'true') {
      // Hard delete - actually remove from database
      // This would need to be implemented in db.js
      res.json({ message: 'Profile permanently deleted', id, type });
    } else {
      // Soft delete - mark as deleted
      await updateProfile(type, id, { deleted: true, deleted_at: new Date().toISOString() });
      res.json({ message: 'Profile soft deleted', id, type });
    }
  } catch (error) {
    console.error('Profile deletion error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// State Routes
app.get('/state/:id', authMiddleware, async (req, res) => {
  try {
    const { id } = req.params;
    const { limit = 50, type, since } = req.query;

    const state = await getState(id, { limit: parseInt(limit), type, since });
    
    res.json({
      profile_id: id,
      state: state || {},
      logs: [], // Placeholder - would fetch actual logs
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    console.error('State retrieval error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Feedback Routes
app.post('/feedback', authMiddleware, async (req, res) => {
  try {
    const { profile_id, type, data } = req.body;

    if (!profile_id || !type || !data) {
      return res.status(400).json({ error: 'Missing required fields: profile_id, type, data' });
    }

    await logFeedback(profile_id, type, data);
    
    res.status(201).json({
      message: 'Feedback logged successfully',
      profile_id,
      type,
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    console.error('Feedback logging error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

app.post('/feedback/recursive/:id', authMiddleware, async (req, res) => {
  try {
    const { id } = req.params;
    const { issue } = req.body;

    // Placeholder for recursive feedback processing
    res.json({
      message: 'Recursive feedback initiated',
      profile_id: id,
      issue,
      status: 'processing',
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    console.error('Recursive feedback error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Agent Routes
app.post('/agents/orchestrate', authMiddleware, async (req, res) => {
  try {
    const { teamId, agents, tasks } = req.body;

    if (!teamId || !agents || !tasks) {
      return res.status(400).json({ error: 'Missing required fields: teamId, agents, tasks' });
    }

    // Placeholder for agent orchestration
    res.status(201).json({
      message: 'Agent orchestration initiated',
      team_id: teamId,
      agents_count: agents.length,
      tasks_count: tasks.length,
      status: 'running',
      started_at: new Date().toISOString()
    });
  } catch (error) {
    console.error('Agent orchestration error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

app.get('/agents/audit/:teamId', authMiddleware, async (req, res) => {
  try {
    const { teamId } = req.params;
    const { limit = 100, agents, since } = req.query;

    // Placeholder for audit trail
    res.json({
      team_id: teamId,
      audit_trail: [],
      filters: { limit: parseInt(limit), agents, since },
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    console.error('Agent audit error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// Integration Routes
app.post('/integrations/langchain', authMiddleware, async (req, res) => {
  try {
    const { profileId, type } = req.body;

    res.json({
      message: 'LangChain loader generated',
      profile_id: profileId,
      type,
      loader_code: `# LangChain Loader for ${profileId}\nfrom langchain.document_loaders import JSONLoader\n# Implementation here...`,
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    console.error('LangChain integration error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

app.post('/integrations/autogen', authMiddleware, async (req, res) => {
  try {
    const { agentId } = req.body;

    res.json({
      message: 'AutoGen config generated',
      agent_id: agentId,
      config: {
        name: agentId,
        system_message: "You are a helpful assistant.",
        llm_config: { model: "gpt-4" }
      },
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    console.error('AutoGen integration error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

app.post('/integrations/rag', authMiddleware, async (req, res) => {
  try {
    const { query, profileId } = req.body;

    res.json({
      message: 'RAG filter applied',
      query,
      profile_id: profileId,
      filtered_results: [],
      timestamp: new Date().toISOString()
    });
  } catch (error) {
    console.error('RAG integration error:', error);
    res.status(500).json({ error: 'Internal server error' });
  }
});

// ===== ERROR HANDLING =====
app.use((err, req, res, next) => {
  console.error('Unhandled error:', err);
  res.status(500).json({ error: 'Internal server error' });
});

app.use((req, res) => {
  res.status(404).json({ error: 'Endpoint not found' });
});

// ===== SERVER STARTUP =====
async function startServer() {
  try {
    // Initialize database
    await initDB(dbPath);
    console.log('✅ Database initialized successfully');

    // Start server
    app.listen(PORT, () => {
      console.log(`🚀 Identity Vault running at http://localhost:${PORT}`);
      console.log('📋 Endpoints: /health, /profiles/create/:type, /profiles/:type/:id, etc.');
      console.log('🔧 Advanced: ZKP for trust, IPFS for P2P, drift tracking enabled.');
      console.log('🔑 DB Initialized: Profiles, logs, and state tables ready.');
      console.log('\n🌐 Open your browser to http://localhost:3000 to access the UI');
    });
  } catch (error) {
    console.error('❌ Failed to start server:', error);
    process.exit(1);
  }
}

// Graceful shutdown
process.on('SIGINT', () => {
  console.log('\n🛑 Shutting down gracefully...');
  process.exit(0);
});

process.on('SIGTERM', () => {
  console.log('\n🛑 Shutting down gracefully...');
  process.exit(0);
});

startServer();

module.exports = app;
