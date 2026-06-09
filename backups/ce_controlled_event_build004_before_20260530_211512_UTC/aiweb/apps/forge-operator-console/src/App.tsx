import { useState, type ReactElement } from 'react';
import { OperatorLayout } from './shell/OperatorLayout';
import { ForgeOutputTab } from './tabs/ForgeOutputTab';
import { ProtoForgeTab } from './tabs/ProtoForgeTab';
import { IdentityVaultTab } from './tabs/IdentityVaultTab';
import { ContributionEconomyTab } from './tabs/ContributionEconomyTab';
import { EchoForgeTab } from './tabs/EchoForgeTab';
import { RmcMemoryTab } from './tabs/RmcMemoryTab';
import { RmcDeepDryRunTab } from './tabs/RmcDeepDryRunTab';
import { ContextLibraryTab } from './tabs/ContextLibraryTab';
import { AuditReceiptsTab } from './tabs/AuditReceiptsTab';
import { SystemStatusTab } from './tabs/SystemStatusTab';
import type { OperatorTabId } from './api/types';

const tabRenderers: Record<OperatorTabId, ReactElement> = {
  forge_output: <ForgeOutputTab />,
  protoforge_simulations: <ProtoForgeTab />,
  identity_vault: <IdentityVaultTab />,
  contribution_economy: <ContributionEconomyTab />,
  echoforge: <EchoForgeTab />,
  rmc_memory: <RmcMemoryTab />,
  rmc_deep_dry_run: <RmcDeepDryRunTab />,
  context_library: <ContextLibraryTab />,
  audit_receipts: <AuditReceiptsTab />,
  system_status: <SystemStatusTab />,
};

export default function App() {
  const [activeTab, setActiveTab] = useState<OperatorTabId>('forge_output');

  return (
    <OperatorLayout activeTab={activeTab} onTabChange={setActiveTab}>
      {tabRenderers[activeTab]}
    </OperatorLayout>
  );
}
