# GENERIC_REVISION_CANDIDATE_V1

Status: GENERIC_REVISION_CANDIDATE_READY_NO_LIVE_WRITE

- target: stack_linker_breather
- candidate_status: ready_for_sandbox_rerun
- recommended_next_patch: Patch 141 — Generic Revision Sandbox Rerun

```json
{
  "authority": {
    "engine_file_write_authority": false,
    "ledger_mutation_authority": false,
    "model_generation_called": true,
    "patch_apply_authority": false,
    "project_file_write_authority": false,
    "writes_forge_memory_only": true
  },
  "base_candidate_file_path": "/home/nic/forge/memory/generic_revision_candidates_v1/2026_05_17_125228_revision_candidate_2026_05_17_102321_candidate_stack_linker_core.py",
  "base_candidate_sha256": "14aa7209449df19e2901302dd03cd48b1e5c81950223fb05166f9aa27da1fe25",
  "candidate_compile": {
    "py_compile_status": "PASS",
    "returncode": 0,
    "shell": false,
    "stderr": "",
    "stdout": ""
  },
  "candidate_file_path": "/home/nic/forge/memory/generic_revision_candidates_v1/2026_05_18_170530_revision_loop_candidate_2026_05_17_125228_revision_candidate_2026_05_17_102321_candidate_stack_linker_core.py",
  "candidate_sha256": "4ed82164b5f29c0c7f1163829a60a35c8e91bcb721bf196256554f88c4f4f784",
  "candidate_status": "ready_for_sandbox_rerun",
  "created_at": "2026-05-18T17:05:30",
  "diff_path": "/home/nic/forge/memory/generic_revision_candidates_v1/2026_05_18_170530_revision_loop_candidate.diff",
  "diff_preview": "--- a//home/nic/forge/memory/generic_revision_candidates_v1/2026_05_17_125228_revision_candidate_2026_05_17_102321_candidate_stack_linker_core.py\n+++ b//home/nic/forge/memory/generic_revision_candidates_v1/2026_05_17_125228_revision_candidate_2026_05_17_102321_candidate_stack_linker_core.py (revision loop candidate only)\n@@ -3,9 +3,14 @@\n sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), \".\")))\n \n from core_breather.core_breather import CoreBreather\n-from recursive_field_breather.field_breather import breathe_phase as field_breathe\n+from recursive_field_breather.field_breather import FieldBreather\n import time\n import json\n+\n+_field_breather_instance = FieldBreather()\n+def field_breathe(phase=None):\n+    return _field_breather_instance.breathe()\n+\n \n _core_breather_instance = CoreBreather()\n def core_breathe(phase=None):\n",
  "llm_candidate_plan": {
    "candidate_action": "USE_CLASS_BREATHER_WRAPPER",
    "model": "qwen3:8b",
    "model_generation_called": true,
    "preview": "Thinking...\nOkay, let's see. The problem here is an ImportError: cannot import name 'breathe_phase' from 'recursive_field_breather.field_breather'. The candidate code is trying to import 'breathe_phase' as field_breathe from the field_breather module. But the dependency file, field_breather.py, doesn't have a function named breathe_phase. Instead, it has a class FieldBreather with a breathe() method.\n\nSo the candidate is trying to import a function that doesn't exist. The dependency exposes a class with a breathe method. According to the decision rule, if the candidate imports a missing function but the dependency has a class with the same method name, we should revise the candidate to use the class instead. \n\nThe current candidate code is importing the breathe_phase function, which isn't present. The correct approach would be to use the FieldBreather class and call its breathe method. So the fix is to change the import statement to use the class and adjust the code to instantiate the class and call the method. \n\nTherefore, the recommendation is to REVISE_CANDIDATE and use the CLASS_BREATHER_WRAPPER. The missing symbol is breathe_phase, and the class name is FieldBreather. The method name is breathe. The alias in the candidate code is field_breathe, which should be replaced with an instance of the class calling the breathe method. The tests need to be rerun to check if the changes resolve the import error.\n...done thinking.\n\nRECOMMENDATION: REVISE_CANDIDATE\nCANDIDATE_ACTION: USE_CLASS_BREATHER_WRAPPER\nIMPORT_MODULE: recursive_field_breather.field_breather\nMISSING_SYMBOL: breathe_phase\nCLASS_NAME: FieldBreather\nMETHOD_NAME: breathe\nALIAS_NAME: field_breathe\nRATIONALE: The candidate incorrectly imports a missing function 'breathe_phase' from a module that only exposes a class with a 'breathe()' method. We need to replace the function import with class-based usage.\nTESTS_TO_RERUN: sandbox_packages/stack_linker_breather/test_stack_linker_core.py\n\n",
    "prompt_path": "/home/nic/forge/memory/generic_revision_loop_v1/2026_05_18_170418_prompt_revision_loop_stack_linker_breather.txt",
    "prompt_sha256": "1819eb7840c35057ff46f313c407005e24d3f8ee9354acbc6ba2a81931cfa5d8",
    "provider": "ollama",
    "raw_response_path": "/home/nic/forge/memory/generic_revision_loop_v1/2026_05_18_170418_response_raw_revision_loop_stack_linker_breather.txt",
    "raw_response_sha256": "6b8fa2fa9e6b627552e2ff3a451eca178bddc205938d55c6e708ef00f04f333a",
    "recommendation": "REVISE_CANDIDATE",
    "returncode": 0,
    "stderr_path": "/home/nic/forge/memory/generic_revision_loop_v1/2026_05_18_170418_response_stderr_revision_loop_stack_linker_breather.txt",
    "stderr_sha256": "1ee6e46e3e4903d0a1a05c72ea79f8a8ee34b9102f42b08d9218549d12689823",
    "subprocess_shell_false": true,
    "timeout": false
  },
  "loop_candidate_action": "USE_CLASS_BREATHER_WRAPPER",
  "problems": [],
  "recommended_next_patch": "Patch 141 \u2014 Generic Revision Sandbox Rerun",
  "repair_strategy": {
    "alias": "field_breathe",
    "changed": true,
    "class_name": "FieldBreather",
    "instance_name": "_field_breather_instance",
    "method_name": "breathe",
    "missing_symbol": "breathe_phase",
    "module": "recursive_field_breather.field_breather",
    "problems": []
  },
  "report_type": "GENERIC_REVISION_CANDIDATE_V1",
  "schema_version": "generic_revision_candidate_v1_patch142",
  "source_revision_recommendation": "REVISE_CANDIDATE",
  "status": "GENERIC_REVISION_CANDIDATE_READY_NO_LIVE_WRITE",
  "target": "stack_linker_breather"
}
```