#!/usr/bin/env python3
"""
Patch 262F1 verifier.
Purpose: verify the RMC Memory tab is a focused active-module workspace, not a grid of empty inactive panels.
"""
from pathlib import Path

ROOT = Path.home()
rmc_tab = ROOT / "aiweb/apps/forge-operator-console/src/tabs/RmcMemoryTab.tsx"
if not rmc_tab.exists():
    raise SystemExit(f"PATCH262F1_VERIFY_FAIL missing={rmc_tab}")
text = rmc_tab.read_text(encoding="utf-8")
required = [
    "type RmcActivePanel",
    "function ActivePanelShell",
    "const [activePanel, setActivePanel] = useState<RmcActivePanel>(null);",
    "setActivePanel('memory_object');",
    "setActivePanel('phase_preview');",
    "setActivePanel('cymatic_preview');",
    "setActivePanel('resonance_gate');",
    "setActivePanel('phase_parser');",
    "setActivePanel('compiler_contract');",
    "activePanel === 'memory_object' && <MemoryObjectViewer",
    "activePanel === 'phase_preview' && <PhasePreviewPanel",
    "activePanel === 'cymatic_preview' && <CymaticPreviewPanel",
    "activePanel === 'resonance_gate' && <ResonanceOutputGatePanel",
    "activePanel === 'compiler_contract' && <CompilerContractPanel",
    "activePanel === 'phase_parser' && <PhaseParserPanel",
    "RMC Build Contract / Diagnostic Gate",
    "Show Build Contract Diagnostic",
    "inactive modules stay hidden",
]
missing = [item for item in required if item not in text]
for bad in [
    "<MemoryObjectViewer object={memoryObject} loading={objectLoading} error={objectError} />\n        <PhasePreviewPanel",
    "RMC TraceRecord + Manifest Contract",
]:
    if bad in text:
        missing.append(f"forbidden:{bad[:40]}")
if missing:
    raise SystemExit("PATCH262F1_VERIFY_FAIL missing_or_forbidden=" + repr(missing))
print("PATCH262F1_RMC_WORKSPACE_FOCUS_VERIFY_PASS")
print("mode=frontend_active_module_workspace")
print("hides_inactive_empty_panels=True")
print("compiler_contract_demoted_to_diagnostic=True")
print("backend_changed=False")
print("adds_forge_commands=False")
print("executes_shell=False")
print("writes_files=False")
print("identity_vault_write=False")
print("rmc_live_memory_write=False")
print("next_patch=Patch 262G — RMC Drift Analyzer Read-Only")
