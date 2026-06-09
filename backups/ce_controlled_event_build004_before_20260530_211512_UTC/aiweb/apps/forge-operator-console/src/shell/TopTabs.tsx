import type { OperatorTabId } from '../api/types';

const tabs: Array<{ id: OperatorTabId; label: string }> = [
  { id: 'forge_output', label: 'Forge Output' },
  { id: 'protoforge_simulations', label: 'ProtoForge Simulations' },
  { id: 'identity_vault', label: 'Identity Vault' },
  { id: 'contribution_economy', label: 'Contribution Economy' },
  { id: 'echoforge', label: 'EchoForge' },
  { id: 'rmc_memory', label: 'RMC Memory' },
  { id: 'rmc_deep_dry_run', label: 'Deep Dry-Run' },
  { id: 'context_library', label: 'Context Library' },
  { id: 'audit_receipts', label: 'Audit / Receipts' },
  { id: 'system_status', label: 'System Status' },
];

export function TopTabs({
  activeTab,
  onTabChange,
}: {
  activeTab: OperatorTabId;
  onTabChange: (tab: OperatorTabId) => void;
}) {
  return (
    <nav className="top-tabs" aria-label="Operator console tabs">
      {tabs.map((tab) => (
        <button
          key={tab.id}
          className={tab.id === activeTab ? 'tab active' : 'tab'}
          onClick={() => onTabChange(tab.id)}
        >
          {tab.label}
        </button>
      ))}
    </nav>
  );
}
