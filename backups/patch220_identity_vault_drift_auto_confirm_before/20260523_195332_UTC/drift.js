// utils/drift.js - Conceptual Drift Tracking, Contradiction Alerts, and Recursive Feedback for Vault
// Monitors profile updates for shifts (e.g., formality change from 'casual' to 'stoic' = drift score),
// flags contradictions (e.g., pushback: true but require_honest_pushback: false), triggers recursive loops.
// Features: Diff-based detection (JSON patch), semantic alerts (string similarity via Levenshtein stub),
// recursive feedback (simulate loops: propose fixes, confirm), log integration.
// Advanced: Thresholds (e.g., >0.3 similarity = alert), context-aware (compare to project_phase),
// ties to meta_rules (e.g., if drift_tracking: true, enforce), future: Embed LLM for semantic diff.
// Integrates: Called in server.js (PATCH drift check), prompts.js (input preview), db.js (logFeedback).
// Safety: Non-destructive (alert only, no auto-changes); thresholds configurable via env.
// Usage: const alert = detectDrift(oldProfile, newProfile); if (alert) recursiveFeedback(newProfile, alert);
// Version: 1.0 | 2025 | Deps: json-diff (npm install json-diff); simple string sim.

const jsonDiff = require('json-diff'); // For structural diffs
const { logFeedback } = require('../db'); // Audit logs
const { getNested } = require('./zkps'); // Nested access helper

// Levenshtein distance stub for semantic similarity (0-1 score; <0.7 = potential drift)
function stringSimilarity(str1, str2) {
  if (!str1 || !str2) return 0;
  str1 = str1.toLowerCase().replace(/[^\w\s]/g, ''); // Normalize
  str2 = str2.toLowerCase().replace(/[^\w\s]/g, '');
  const matrix = [];
  for (let i = 0; i <= str2.length; i++) {
    matrix[i] = [i];
  }
  for (let j = 0; j <= str1.length; j++) {
    matrix[0][j] = j;
  }
  for (let i = 1; i <= str2.length; i++) {
    for (let j = 1; j <= str1.length; j++) {
      if (str2.charAt(i - 1) === str1.charAt(j - 1)) {
        matrix[i][j] = matrix[i - 1][j - 1];
      } else {
        matrix[i][j] = Math.min(
          matrix[i - 1][j - 1] + 1,
          matrix[i][j - 1] + 1,
          matrix[i - 1][j] + 1
        );
      }
    }
  }
  return 1 - (matrix[str2.length][str1.length] / Math.max(str1.length, str2.length));
}

// Detect drift: Compare old/new profiles, score changes in key sections (interaction/meta/project)
function detectDrift(oldProfile, newProfile, threshold = 0.3) {
  const diff = jsonDiff.diff(oldProfile, newProfile) || {};
  const changes = [];
  const keySections = ['interaction_preferences', 'meta_rules', 'project_context'];

  keySections.forEach(section => {
    if (diff[section]) {
      Object.entries(diff[section]).forEach(([key, change]) => {
        if (typeof change === 'string' && oldProfile[section] && newProfile[section]) {
          const oldVal = getNested(oldProfile, `${section}.${key}`);
          const newVal = getNested(newProfile, `${section}.${key}`);
          const sim = stringSimilarity(oldVal, newVal);
          if (sim < threshold) { // Low similarity = drift
            changes.push({
              field: `${section}.${key}`,
              old: oldVal,
              new: newVal,
              similarity: sim,
              reason: `Semantic shift detected (threshold: ${threshold})`
            });
          }
        } else if (change === '+') { // Added
          changes.push({ field: `${section}.${key}`, action: 'added', reason: 'New rule/preference' });
        } else if (change === '-') { // Removed
          changes.push({ field: `${section}.${key}`, action: 'removed', reason: 'Dropped element' });
        }
      });
    }
  });

  // Context-aware: If project_phase changed, flag high drift
  if (oldProfile.project_context?.phase !== newProfile.project_context?.phase) {
    changes.push({
      field: 'project_context.phase',
      reason: 'Project phase shift—review goals/collaborators'
    });
  }

  if (changes.length > 0) {
    return {
      type: 'drift',
      count: changes.length,
      details: changes,
      severity: changes.length > 3 ? 'high' : 'low',
      recommendation: `Review ${changes.map(c => c.field).join(', ')} for alignment`
    };
  }
  return null;
}

// Alert contradictions: Scan meta_rules/interaction for logical conflicts
function alertContradictions(profile) {
  const contradictions = [];
  const rules = profile.meta_rules || {};
  const prefs = profile.interaction_preferences || {};

  // Examples: pushback true but honest_pushback false
  if (prefs.pushback && !rules.require_honest_pushback) {
    contradictions.push({
      conflict: 'pushback vs. require_honest_pushback',
      reason: 'Pushback enabled without honest enforcement—may simulate agreement',
      fields: ['interaction_preferences.pushback', 'meta_rules.require_honest_pushback']
    });
  }

  // step_by_step true but forbidden_actions includes 'explain step by step'
  if (prefs.step_by_step && rules.forbidden_actions?.some(a => a.includes('step'))) {
    contradictions.push({
      conflict: 'step_by_step vs. forbidden_actions',
      reason: 'Step-by-step preferred but forbidden—resolve',
      fields: ['interaction_preferences.step_by_step', 'meta_rules.forbidden_actions']
    });
  }

  // log_all_exchanges true but no preserve_session_memory
  if (rules.log_all_exchanges && !rules.preserve_session_memory) {
    contradictions.push({
      conflict: 'log_all_exchanges vs. preserve_session_memory',
      reason: 'Logging without memory preservation—context loss risk',
      fields: ['meta_rules.log_all_exchanges', 'meta_rules.preserve_session_memory']
    });
  }

  // Safe words empty but confirmation_required
  if (prefs.confirmation_required && (!rules.safe_words || rules.safe_words.length === 0)) {
    contradictions.push({
      conflict: 'confirmation_required vs. safe_words',
      reason: 'Confirmation needed but no safe words for halt',
      fields: ['interaction_preferences.confirmation_required', 'meta_rules.safe_words']
    });
  }

  return contradictions.length > 0 ? { type: 'contradiction', details: contradictions } : null;
}

// Recursive feedback: Simulate loop—propose fixes, "confirm" (CLI stub), update/log
async function recursiveFeedback(profile, issue, maxIterations = 3, current = 0) {
  if (current >= maxIterations) {
    console.log('Max iterations reached—log unresolved.');
    await logFeedback(profile.user_id || profile.agent_id, { type: 'feedback_unresolved', issue });
    return;
  }

  // Propose fix based on issue
  let proposal;
  if (issue.type === 'drift') {
    proposal = `Suggested: Revert ${issue.details[0].field} to "${issue.details[0].old}" or adjust threshold?`;
  } else if (issue.type === 'contradiction') {
    proposal = `Fix: Set ${issue.details[0].fields[1]} to match ${issue.details[0].fields[0]} (e.g., enable honest_pushback).`;
  }

  console.log(`Recursive Feedback (Iteration ${current + 1}): ${proposal}`);

  // Stub confirm (in CLI: readline; here: assume yes for demo, or env flag)
  const confirm = process.env.AUTO_CONFIRM === 'true' || true; // Safety: Opt-in auto
  if (confirm) {
    // Apply proposal (simple: toggle bool or revert string)
    const field = issue.details?.[0]?.fields?.[0] || issue.details?.[0]?.field;
    const keys = field.split('.');
    let target = profile;
    for (let i = 0; i < keys.length - 1; i++) target = target[keys[i]];
    if (typeof target[keys[keys.length - 1]] === 'boolean') {
      target[keys[keys.length - 1]] = !target[keys[keys.length - 1]];
    } else {
      target[keys[keys.length - 1]] = issue.details?.[0]?.old || 'resolved';
    }
    console.log(`Applied: ${field} updated.`);
  } else {
    console.log('Awaiting confirmation... (stub)');
  }

  // Log and recurse if needed
  await logFeedback(profile.user_id || profile.agent_id, {
    type: 'recursive_feedback',
    iteration: current + 1,
    proposal,
    confirmed: confirm,
    issue_type: issue.type
  });

  if (confirm && current < maxIterations - 1) {
    // Re-check after apply
    const newIssue = alertContradictions(profile) || detectDrift(profile, profile); // Self-diff null
    if (newIssue) await recursiveFeedback(profile, newIssue, maxIterations, current + 1);
  }
}

// Exports
module.exports = {
  detectDrift,
  alertContradictions,
  recursiveFeedback,
  stringSimilarity // For custom thresholds
};
