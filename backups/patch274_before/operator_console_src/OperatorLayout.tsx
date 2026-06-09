import type { ReactNode } from 'react';
import { LeftRail } from './LeftRail';
import { RightAuditRail } from './RightAuditRail';
import { TopTabs } from './TopTabs';
import { OperatorLifecycleMenu } from './OperatorLifecycleMenu';
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
  return (
    <div className="operator-console">
      <header className="chrome">
        <div className="brand">AI.WEB FORGE OPERATOR CONSOLE</div>
        <div className="chrome-actions">
          <div className="chrome-note">production frontend scaffold · Patch 263S lifecycle controls</div>
          <OperatorLifecycleMenu />
        </div>
      </header>
      <TopTabs activeTab={activeTab} onTabChange={onTabChange} />
      <div className="workspace">
        <LeftRail activeTab={activeTab} onTabChange={onTabChange} />
        <main className="main-panel">{children}</main>
        <RightAuditRail />
      </div>
    </div>
  );
}
