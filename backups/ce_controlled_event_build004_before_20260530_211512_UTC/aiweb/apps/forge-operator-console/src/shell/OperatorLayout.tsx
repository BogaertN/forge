import { useCallback, useEffect, useState, type ReactNode } from 'react';
import { LeftRail } from './LeftRail';
import { RightAuditRail } from './RightAuditRail';
import { TopTabs } from './TopTabs';
import { OperatorLifecycleMenu } from './OperatorLifecycleMenu';
import { TerminusOverlay } from './TerminusOverlay';
import type { OperatorTabId } from '../api/types';

export function OperatorLayout({
  activeTab,
  onTabChange,
  children,
}: {
  activeTab: OperatorTabId;
  onTabChange: (tab: OperatorTabId) => void;
  children: ReactNode;
}) {
  const [terminusOpen, setTerminusOpen] = useState(false);
  const openTerminus = useCallback(() => setTerminusOpen(true), []);
  const closeTerminus = useCallback(() => setTerminusOpen(false), []);

  useEffect(() => {
    window.addEventListener('aiweb-open-terminus', openTerminus);
    return () => window.removeEventListener('aiweb-open-terminus', openTerminus);
  }, [openTerminus]);

  return (
    <div className="operator-console">
      <header className="chrome">
        <div className="brand">AI.WEB FORGE OPERATOR CONSOLE</div>
        <div className="chrome-actions">
          <div className="chrome-note">production frontend scaffold · Patch 274 build manifest</div>
          <OperatorLifecycleMenu />
        </div>
      </header>
      <TopTabs activeTab={activeTab} onTabChange={onTabChange} />
      <div className="workspace">
        <LeftRail activeTab={activeTab} onTabChange={onTabChange} />
        <main className="main-panel">{children}</main>
        <RightAuditRail />
      </div>
      <TerminusOverlay open={terminusOpen} onClose={closeTerminus} />
    </div>
  );
}
