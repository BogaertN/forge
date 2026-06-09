// Patch 262-UI-MemoryPanel-P2R
// Canonical RMC API client for the Forge Operator Console.
// React is a control surface. Endpoint truth comes from /api/rmc/route-manifest.

import { useCallback, useEffect, useState } from 'react';

export type RmcRouteKey =
  | 'route_manifest'
  | 'memory_status'
  | 'chroma_status'
  | 'memory_object'
  | 'context_search_test'
  | 'context_duplicates'
  | 'context_export_manifest'
  | 'latest_memory_writes'
  | 'rmc_namespaces'
  | 'memory_recaller'
  | 'trace_spine'
  | 'phase_preview'
  | 'cymatic_preview'
  | 'resonance_output_gate'
  | 'compiler_contract'
  | 'phase_codex'
  | 'lexicon_audit'
  | 'resonance_lexicon'
  | 'dataset_growth_status'
  | 'dataset_growth_capture_preview'
  | 'dataset_growth_capture'
  | 'dataset_growth_coverage'
  | 'dataset_growth_llm_turn_preview'
  | 'dataset_growth_llm_turn_capture'
  | 'dataset_growth_document_preview'
  | 'dataset_growth_document_capture'
  | 'phase_parser'
  | 'drift_analyzer'
  | 'candidate_generator'
  | 'evolutionary_drift_explorer'
  | 'coherence_scorer'
  | 'correction_naming'
  | 'manifest_compiler'
  | 'llm_renderer_status'
  | 'output_renderer'
  | 'glyph_renderer_status'
  | 'phase_glyph'
  | 'glyph_packet'
  | 'echo_validator'
  | 'memory_writer'
  | 'gated_memory_writer'
  | 'pipeline_summary'
  | 'active_loop_state'
  | 'promotion_path_status'
  | 'promotion_path_preview'
  | 'promotion_path_promote';

export interface RmcRouteManifestRoute {
  route_key: RmcRouteKey | string;
  method: 'GET' | 'POST' | string;
  path: string;
  group: string;
  stage: string;
  pipeline_label: string;
  requires_approval: boolean;
  approval_token?: string | null;
  aliases?: string[];
}

export interface RmcRouteManifest {
  status: string;
  endpoint: '/api/rmc/route-manifest';
  mode: string;
  read_only: boolean;
  canonical_route_count: number;
  alias_count: number;
  routes: RmcRouteManifestRoute[];
  lookup: Record<string, string>;
  approval_required: Array<{ route_key: string; path: string; approval_token?: string | null }>;
  boundary?: Record<string, unknown>;
}

export interface RmcRequestParams {
  input?: string;
  text?: string;
  query?: string;
  limit?: number | string;
  selector?: string;
  path?: string;
  source_file?: string;
  chunk_id?: string;
  retrieval_backend?: 'filesystem' | 'chroma' | 'hybrid' | 'auto' | string;
  mode?: string;
  render_mode?: string;
  phase?: string;
  phase_path?: string | string[];
  candidate_id?: string;
  approval?: string;
  commit?: boolean | string;
  include_full?: boolean | string;
  llm_renderer?: 'on' | 'off' | boolean | string;
  use_llm?: boolean | string;
  llm?: boolean | string;
  model_endpoint?: string;
  model?: string;
  [key: string]: unknown;
}

const FALLBACK_ROUTES: Record<RmcRouteKey, string> = {
  route_manifest: '/api/rmc/route-manifest',
  memory_status: '/api/rmc/memory-status',
  chroma_status: '/api/rmc/chroma-status',
  memory_object: '/api/rmc/memory-object',
  context_search_test: '/api/rmc/context-search-test',
  context_duplicates: '/api/rmc/context-duplicates',
  context_export_manifest: '/api/rmc/context-export-manifest',
  latest_memory_writes: '/api/rmc/latest-memory-writes',
  rmc_namespaces: '/api/rmc/namespaces',
  memory_recaller: '/api/rmc/memory-recaller',
  trace_spine: '/api/rmc/trace-spine',
  phase_preview: '/api/rmc/phase-preview',
  cymatic_preview: '/api/rmc/cymatic-preview',
  resonance_output_gate: '/api/rmc/resonance-output-gate',
  compiler_contract: '/api/rmc/compiler-contract',
  phase_codex: '/api/rmc/phase-codex',
  lexicon_audit: '/api/rmc/lexicon-audit',
  resonance_lexicon: '/api/rmc/resonance-lexicon',
  dataset_growth_status: '/api/rmc/dataset-growth/status',
  dataset_growth_capture_preview: '/api/rmc/dataset-growth/capture-preview',
  dataset_growth_capture: '/api/rmc/dataset-growth/capture',
  dataset_growth_coverage: '/api/rmc/dataset-growth/coverage',
  dataset_growth_llm_turn_preview: '/api/rmc/dataset-growth/llm-turn-preview',
  dataset_growth_llm_turn_capture: '/api/rmc/dataset-growth/llm-turn-capture',
  dataset_growth_document_preview: '/api/rmc/dataset-growth/document-preview',
  dataset_growth_document_capture: '/api/rmc/dataset-growth/document-capture',
  phase_parser: '/api/rmc/phase-parser',
  drift_analyzer: '/api/rmc/drift-analyzer',
  candidate_generator: '/api/rmc/candidate-conclusion',
  evolutionary_drift_explorer: '/api/rmc/evolutionary-drift-explorer',
  coherence_scorer: '/api/rmc/coherence-scorer',
  correction_naming: '/api/rmc/correction-naming',
  manifest_compiler: '/api/rmc/manifest-compiler',
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

let routeManifestCache: RmcRouteManifest | null = null;
let routeManifestPromise: Promise<RmcRouteManifest> | null = null;

function appendParams(path: string, params: RmcRequestParams = {}): string {
  const search = new URLSearchParams();
  Object.entries(params).forEach(([key, value]) => {
    if (value === undefined || value === null || value === '') return;
    if (Array.isArray(value)) {
      search.set(key, value.join(','));
      return;
    }
    if (typeof value === 'boolean') {
      search.set(key, value ? 'true' : 'false');
      return;
    }
    search.set(key, String(value));
  });
  const query = search.toString();
  return query ? `${path}?${query}` : path;
}

async function readJson<T>(response: Response): Promise<T> {
  if (!response.ok) {
    throw new Error(`HTTP ${response.status} ${response.statusText}`.trim());
  }
  return (await response.json()) as T;
}

async function fetchJson<T>(path: string, params: RmcRequestParams = {}): Promise<T> {
  const response = await fetch(appendParams(path, params));
  return readJson<T>(response);
}

export async function fetchRouteManifest(force = false): Promise<RmcRouteManifest> {
  if (!force && routeManifestCache) return routeManifestCache;
  if (!force && routeManifestPromise) return routeManifestPromise;
  routeManifestPromise = fetchJson<RmcRouteManifest>(FALLBACK_ROUTES.route_manifest)
    .then((manifest) => {
      routeManifestCache = manifest;
      return manifest;
    })
    .catch(() => {
      const routes = Object.entries(FALLBACK_ROUTES).map(([route_key, path]) => ({
        route_key,
        method: 'GET',
        path,
        group: 'fallback',
        stage: route_key,
        pipeline_label: 'client fallback route; server manifest unavailable',
        requires_approval: route_key === 'gated_memory_writer' || route_key === 'promotion_path_promote',
        approval_token: route_key === 'promotion_path_promote' ? 'APPROVE_RMC_PROMOTION' : route_key === 'gated_memory_writer' ? 'APPROVE_RMC_MEMORY_WRITE' : null,
        aliases: [],
      }));
      const manifest: RmcRouteManifest = {
        status: 'FALLBACK',
        endpoint: '/api/rmc/route-manifest',
        mode: 'client_fallback_manifest_RewireUI_R1',
        read_only: true,
        canonical_route_count: routes.length,
        alias_count: 0,
        routes,
        lookup: { ...FALLBACK_ROUTES },
        approval_required: routes.filter((r) => r.requires_approval).map((r) => ({ route_key: r.route_key, path: r.path, approval_token: r.approval_token })),
        boundary: { ui_is_authority: false, forge_governs: true, fallback: true },
      };
      routeManifestCache = manifest;
      return manifest;
    })
    .finally(() => {
      routeManifestPromise = null;
    });
  return routeManifestPromise;
}

export async function getCanonicalRmcPath(routeKey: RmcRouteKey): Promise<string> {
  const manifest = await fetchRouteManifest();
  return manifest.lookup?.[routeKey] || FALLBACK_ROUTES[routeKey];
}

export async function fetchRmcEndpoint<T = Record<string, unknown>>(routeKey: RmcRouteKey, params: RmcRequestParams = {}): Promise<T> {
  const path = await getCanonicalRmcPath(routeKey);
  return fetchJson<T>(path, params);
}

export const getRouteManifest = fetchRouteManifest;
export const getMemoryStatus = () => fetchRmcEndpoint('memory_status');
export const getChromaStatus = () => fetchRmcEndpoint('chroma_status');
export const getMemoryObject = (params: RmcRequestParams = {}) => fetchRmcEndpoint('memory_object', params);
export const getContextSearchTest = (params: RmcRequestParams = {}) => fetchRmcEndpoint('context_search_test', params);
export const getContextDuplicates = () => fetchRmcEndpoint('context_duplicates');
export const getContextExportManifest = () => fetchRmcEndpoint('context_export_manifest');
export const getLatestMemoryWrites = (params: RmcRequestParams = {}) => fetchRmcEndpoint('latest_memory_writes', params);
export const getRmcNamespaces = () => fetchRmcEndpoint('rmc_namespaces');
export const getMemoryRecaller = (params: RmcRequestParams = {}) => fetchRmcEndpoint('memory_recaller', params);
export const getTraceSpine = (params: RmcRequestParams = {}) => fetchRmcEndpoint('trace_spine', params);
export const getPhaseParser = (params: RmcRequestParams = {}) => fetchRmcEndpoint('phase_parser', params);
export const getDriftAnalyzer = (params: RmcRequestParams = {}) => fetchRmcEndpoint('drift_analyzer', params);
export const getCandidateGenerator = (params: RmcRequestParams = {}) => fetchRmcEndpoint('candidate_generator', params);
export const getEvolutionaryDriftExplorer = (params: RmcRequestParams = {}) => fetchRmcEndpoint('evolutionary_drift_explorer', params);
export const getCoherenceScorer = (params: RmcRequestParams = {}) => fetchRmcEndpoint('coherence_scorer', params);
export const getCorrectionNaming = (params: RmcRequestParams = {}) => fetchRmcEndpoint('correction_naming', params);
export const getManifestCompiler = (params: RmcRequestParams = {}) => fetchRmcEndpoint('manifest_compiler', params);
export const getLlmRendererStatus = () => fetchRmcEndpoint('llm_renderer_status');
export const getOutputRenderer = (params: RmcRequestParams = {}) => fetchRmcEndpoint('output_renderer', params);
export const getGlyphRendererStatus = () => fetchRmcEndpoint('glyph_renderer_status');
export const getPhaseGlyph = (params: RmcRequestParams = {}) => fetchRmcEndpoint('phase_glyph', params);
export const getGlyphPacket = (params: RmcRequestParams = {}) => fetchRmcEndpoint('glyph_packet', params);
export const getEchoValidator = (params: RmcRequestParams = {}) => fetchRmcEndpoint('echo_validator', params);
export const getMemoryWriter = (params: RmcRequestParams = {}) => fetchRmcEndpoint('memory_writer', params);
export const getGatedMemoryWriter = (params: RmcRequestParams = {}) => fetchRmcEndpoint('gated_memory_writer', params);
export const getPipelineSummary = (params: RmcRequestParams = {}) => fetchRmcEndpoint('pipeline_summary', params);
export const getActiveLoopState = (params: RmcRequestParams = {}) => fetchRmcEndpoint('active_loop_state', params);
export const getPromotionStatus = () => fetchRmcEndpoint('promotion_path_status');
export const getPromotionPreview = (candidateId: string) => fetchRmcEndpoint('promotion_path_preview', { candidate_id: candidateId });
export const getPromotionCommitPreview = (candidateId: string) => fetchRmcEndpoint('promotion_path_promote', { candidate_id: candidateId });

export const getPhaseCodex = () => fetchRmcEndpoint('phase_codex');
export const getDatasetGrowthStatus = () => fetchRmcEndpoint('dataset_growth_status');
export const getDatasetGrowthCoverage = () => fetchRmcEndpoint('dataset_growth_coverage');
export const getPromotionPromote = (candidateId: string, approval: string) => fetchRmcEndpoint('promotion_path_promote', { candidate_id: candidateId, approval });
export const promoteCandidate = getPromotionPromote;

export interface AsyncRmcState<T> {
  data: T | null;
  error: string | null;
  loading: boolean;
  reload: () => void;
}

export function useRmcEndpoint<T = Record<string, unknown>>(routeKey: RmcRouteKey, params: RmcRequestParams = {}): AsyncRmcState<T> {
  const [data, setData] = useState<T | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [reloadToken, setReloadToken] = useState(0);
  const reload = useCallback(() => setReloadToken((value) => value + 1), []);
  const paramKey = JSON.stringify(params);

  useEffect(() => {
    let cancelled = false;
    setLoading(true);
    setError(null);
    fetchRmcEndpoint<T>(routeKey, params)
      .then((value) => { if (!cancelled) setData(value); })
      .catch((err: unknown) => { if (!cancelled) setError(err instanceof Error ? err.message : String(err)); })
      .finally(() => { if (!cancelled) setLoading(false); });
    return () => { cancelled = true; };
  }, [routeKey, paramKey, reloadToken]);

  return { data, error, loading, reload };
}

export function useRmcPipeline(input: string): AsyncRmcState<Record<string, unknown>> {
  return useRmcEndpoint('pipeline_summary', { input, include_full: '1' });
}

export function useActiveLoopState(input: string): AsyncRmcState<Record<string, unknown>> {
  return useRmcEndpoint('active_loop_state', { input });
}

export function useLlmRendererStatus(): AsyncRmcState<Record<string, unknown>> {
  return useRmcEndpoint('llm_renderer_status');
}
