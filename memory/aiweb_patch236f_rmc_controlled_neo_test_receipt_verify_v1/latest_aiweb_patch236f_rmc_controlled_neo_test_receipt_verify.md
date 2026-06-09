# Patch 236F — Controlled Neo RMC Test Receipt Verification

Generated: `20260524_122603_UTC`
Verdict: `RMC_TEST_RECEIPT_VERIFIED_GOVERNED_NEO`
OK: `True`
Checks: `38/38`
Agent: `neo.local`
Receipt path: `/home/nic/aiweb/runtime_wrappers/ancestral_memory/agents/neo.local/receipts/neo_handshake_test_20260524_121937_UTC.json`
Receipt hash reported: `174adc1c00d0354dd954e1db000f482969d90bf238c5615be4bdce233c07104e`
Receipt hash computed: `174adc1c00d0354dd954e1db000f482969d90bf238c5615be4bdce233c07104e`
File sha256 actual: `c2607d96baba40638156fde38f7382f0579c8858da102e5a7d1ac141f3f2b7b7`

## Boundary

No Identity Vault DB write. No RMC memory write. No agent/long-term/private/shared memory write. No full chat or secret data write/read. No autonomous execution.

## Blockers

None.

## Memory pollution snapshot

- `agent_memory` path=`/home/nic/aiweb/runtime_wrappers/ancestral_memory/agents/neo.local/agent_memory` file_count=`0`
- `long_term_memory` path=`/home/nic/aiweb/runtime_wrappers/ancestral_memory/agents/neo.local/long_term_memory` file_count=`0`
- `private_memory` path=`/home/nic/aiweb/runtime_wrappers/ancestral_memory/agents/neo.local/private_memory` file_count=`0`
- `shared_memory_local` path=`/home/nic/aiweb/runtime_wrappers/ancestral_memory/agents/neo.local/shared_memory` file_count=`0`
- `memory` path=`/home/nic/aiweb/runtime_wrappers/ancestral_memory/agents/neo.local/memory` file_count=`0`
- `memories` path=`/home/nic/aiweb/runtime_wrappers/ancestral_memory/agents/neo.local/memories` file_count=`0`
- `shared_memory_root` path=`/home/nic/aiweb/runtime_wrappers/ancestral_memory/shared_memory` file_count=`0`
- `shared_root` path=`/home/nic/aiweb/runtime_wrappers/ancestral_memory/shared` file_count=`0`
