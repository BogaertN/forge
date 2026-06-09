import { useEffect } from 'react';

export function TerminusOverlay({ open, onClose }: { open: boolean; onClose: () => void }) {
  useEffect(() => {
    if (!open) return undefined;
    const onKey = (event: KeyboardEvent) => {
      if (event.key === 'Escape') onClose();
    };
    window.addEventListener('keydown', onKey);
    return () => window.removeEventListener('keydown', onKey);
  }, [open, onClose]);

  if (!open) return null;

  return (
    <div className="terminus-overlay-backdrop" role="dialog" aria-modal="true" aria-label="Terminus high-security shell overlay">
      <section className="terminus-overlay-shell">
        <header className="terminus-overlay-header">
          <div>
            <div className="terminus-overlay-eyebrow">High-security HTML shell</div>
            <h2>Terminus</h2>
          </div>
          <div className="terminus-overlay-actions">
            <span>Hidden until operator opens it</span>
            <button onClick={onClose}>Hide Terminus</button>
          </div>
        </header>
        <div className="terminus-overlay-boundary">
          Operator Console remains the visible control surface. This frame is loaded only by explicit left-rail action; it receives no RMC write authority, no Identity Vault authority, and no arbitrary browser shell authority.
        </div>
        <iframe
          className="terminus-overlay-frame"
          src="/"
          title="AI.Web Terminus high-security HTML shell"
          sandbox="allow-same-origin allow-scripts allow-forms allow-downloads"
        />
      </section>
    </div>
  );
}
