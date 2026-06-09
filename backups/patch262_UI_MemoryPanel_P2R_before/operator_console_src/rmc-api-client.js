// Patch 262-UI-MemoryPanel-P2
// JavaScript compatibility wrapper for canonical RMC API calls.

const FALLBACK_ROUTES = {
  route_manifest: '/api/rmc/route-manifest',
  memory_status: '/api/rmc/memory-status',
  chroma_status: '/api/rmc/chroma-status',
  memory_object: '/api/rmc/memory-object',
  memory_recaller: '/api/rmc/memory-recaller',
  trace_spine: '/api/rmc/trace-spine',
  phase_parser: '/api/rmc/phase-parser',
  drift_analyzer: '/api/rmc/drift-analyzer',
  candidate_generator: '/api/rmc/candidate-conclusion',
  coherence_scorer: '/api/rmc/coherence-scorer',
  correction_naming: '/api/rmc/correction-naming',
  manifest_compiler: '/api/rmc/manifest-compiler',
  phase_codex: '/api/rmc/phase-codex',
  dataset_growth_status: '/api/rmc/dataset-growth/status',
  dataset_growth_coverage: '/api/rmc/dataset-growth/coverage',
  llm_renderer_status: '/api/rmc/llm-renderer/status',
  output_renderer: '/api/rmc/output-renderer',
  glyph_renderer_status: '/api/rmc/glyph-renderer/status',
  phase_glyph: '/api/rmc/phase-glyph',
  glyph_packet: '/api/rmc/glyph-packet',
  echo_validator: '/api/rmc/echo-validator',
  memory_writer: '/api/rmc/memory-writer',
  gated_memory_writer: '/api/rmc/gated-memory-writer',
  pipeline_summary: '/api/rmc/pipeline-summary',
  active_loop_state: '/api/rmc/active-loop-state',
  promotion_path_status: '/api/rmc/promotion-path/status',
  promotion_path_preview: '/api/rmc/promotion-path/preview',
  promotion_path_promote: '/api/rmc/promotion-path/promote',
};

let routeManifestCache = null;

function appendParams(path, params = {}) {
  const search = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value === undefined || value === null || value === '') return;
    if (Array.isArray(value)) search.set(key, value.join(','));
    else if (typeof value === 'boolean') search.set(key, value ? 'true' : 'false');
    else search.set(key, String(value));
  });
  const query = search.toString();
  return query ? `${path}?${query}` : path;
}

async function readJson(response) {
  if (!response.ok) throw new Error(`HTTP ${response.status} ${response.statusText}`.trim());
  return response.json();
}

async function fetchJson(path, params = {}) {
  return readJson(await fetch(appendParams(path, params)));
}

export async function fetchRouteManifest(force = false) {
  if (!force && routeManifestCache) return routeManifestCache;
  try {
    routeManifestCache = await fetchJson(FALLBACK_ROUTES.route_manifest);
  } catch (_err) {
    routeManifestCache = {
      status: 'FALLBACK',
      lookup: { ...FALLBACK_ROUTES },
      routes: [],
      approval_required: [
        { route_key: 'promotion_path_promote', path: FALLBACK_ROUTES.promotion_path_promote, approval_token: 'APPROVE_RMC_PROMOTION' },
        { route_key: 'gated_memory_writer', path: FALLBACK_ROUTES.gated_memory_writer, approval_token: 'APPROVE_RMC_MEMORY_WRITE' },
      ],
      read_only: true,
    };
  }
  return routeManifestCache;
}

export async function getCanonicalRmcPath(routeKey) {
  const manifest = await fetchRouteManifest();
  return (manifest.lookup && manifest.lookup[routeKey]) || FALLBACK_ROUTES[routeKey];
}

export async function fetchRmcEndpoint(routeKey, params = {}) {
  const path = await getCanonicalRmcPath(routeKey);
  return fetchJson(path, params);
}

export const getRouteManifest = fetchRouteManifest;
export const getMemoryStatus = () => fetchRmcEndpoint('memory_status');
export const getChromaStatus = () => fetchRmcEndpoint('chroma_status');
export const getMemoryRecaller = (params = {}) => fetchRmcEndpoint('memory_recaller', params);
export const getTraceSpine = (params = {}) => fetchRmcEndpoint('trace_spine', params);
export const getPhaseCodex = () => fetchRmcEndpoint('phase_codex');
export const getDatasetGrowthStatus = () => fetchRmcEndpoint('dataset_growth_status');
export const getDatasetGrowthCoverage = () => fetchRmcEndpoint('dataset_growth_coverage');
export const getLlmRendererStatus = () => fetchRmcEndpoint('llm_renderer_status');
export const getOutputRenderer = (params = {}) => fetchRmcEndpoint('output_renderer', params);
export const getGlyphRendererStatus = () => fetchRmcEndpoint('glyph_renderer_status');
export const getPhaseGlyph = (params = {}) => fetchRmcEndpoint('phase_glyph', params);
export const getGlyphPacket = (params = {}) => fetchRmcEndpoint('glyph_packet', params);
export const getPromotionStatus = () => fetchRmcEndpoint('promotion_path_status');
export const getPromotionPreview = (candidateId) => fetchRmcEndpoint('promotion_path_preview', { candidate_id: candidateId });
export const getPromotionPromote = (candidateId, approval) => fetchRmcEndpoint('promotion_path_promote', { candidate_id: candidateId, approval });
export const promoteCandidate = getPromotionPromote;
export const getPipelineSummary = (params = {}) => fetchRmcEndpoint('pipeline_summary', params);
export const getActiveLoopState = (params = {}) => fetchRmcEndpoint('active_loop_state', params);
