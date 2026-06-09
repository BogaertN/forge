import { useEffect, useState } from 'react';
import { capturePage, getSeenPages } from '../api/forgeClient';
import type { PageCaptureResponse, SeenPageItem } from '../api/types';

function normalizeUrl(value: string): string {
  const trimmed = value.trim();
  if (!trimmed) return '';
  if (/^https?:\/\//i.test(trimmed)) return trimmed;
  return `https://${trimmed}`;
}

function isHttpUrl(value: string): boolean {
  try {
    const parsed = new URL(value);
    return parsed.protocol === 'http:' || parsed.protocol === 'https:';
  } catch {
    return false;
  }
}

export function PageCapturePanel() {
  const [url, setUrl] = useState('');
  const [seenPages, setSeenPages] = useState<SeenPageItem[]>([]);
  const [result, setResult] = useState<PageCaptureResponse | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  async function reloadSeenPages() {
    try {
      const pages = await getSeenPages();
      setSeenPages(Array.isArray(pages) ? pages.slice().reverse().slice(0, 8) : []);
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    }
  }

  useEffect(() => {
    void reloadSeenPages();
  }, []);

  async function handleCapture() {
    const target = normalizeUrl(url);
    setError('');
    setResult(null);

    if (!isHttpUrl(target)) {
      setError('Enter an http:// or https:// URL.');
      return;
    }

    setLoading(true);
    try {
      const response = await capturePage(target);
      setResult(response);
      await reloadSeenPages();
    } catch (err) {
      setError(err instanceof Error ? err.message : String(err));
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="page-capture-runner">
      <div className="runner-header">
        <div>
          <div className="card-key">Page Capture / Seen Pages</div>
          <p>Routes through Forge <code>/api/read-page</code> and <code>/api/seen-pages</code>. Capture writes only to Forge browser memory.</p>
        </div>
        <span className="runner-mode runner-safe">MEMORY ONLY</span>
      </div>

      <label htmlFor="page-capture-url">URL to capture</label>
      <div className="page-capture-row">
        <input
          id="page-capture-url"
          value={url}
          placeholder="https://example.com"
          onChange={(event) => setUrl(event.target.value)}
          onKeyDown={(event) => {
            if (event.key === 'Enter') {
              void handleCapture();
            }
          }}
        />
        <button disabled={loading} onClick={() => void handleCapture()}>{loading ? 'Capturing…' : 'Capture Page'}</button>
        <button disabled={loading} onClick={() => void reloadSeenPages()}>Refresh Seen</button>
      </div>

      <div className="runner-hints">No shell. No LLM. No Identity Vault write. No RMC live memory write.</div>
      {error && <div className="error-panel">Page capture error: {error}</div>}

      {result && (
        <div className={`output-slot page-capture-result ${result.status === 'OK' ? 'page-capture-ok' : 'page-capture-error'}`}>
          <div className="output-slot-header">
            <span>{result.title || result.url || 'Captured page'}</span>
            <strong>{result.status}</strong>
          </div>
          <div className="mini-report-path">{result.fetched_at || '—'} · {result.file || 'no file'} · {result.url || ''}</div>
          <pre>{result.status === 'OK' ? (result.text_preview || 'No preview returned.') : (result.error || 'Capture failed.')}</pre>
        </div>
      )}

      <div className="seen-pages-panel">
        <div className="card-key">Seen Pages</div>
        {seenPages.length > 0 ? (
          <div className="seen-page-list">
            {seenPages.map((page) => (
              <button
                className="seen-page-item"
                key={`${page.fetched_at || ''}-${page.url}`}
                title={page.url}
                onClick={() => setUrl(page.url)}
              >
                <span>{page.title || page.url}</span>
                <small>{page.fetched_at || '—'}</small>
              </button>
            ))}
          </div>
        ) : (
          <div className="muted small-note">No seen pages recorded yet.</div>
        )}
      </div>
    </div>
  );
}
