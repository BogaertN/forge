# GENERIC_REVISION_LOOP_LLM_V1

Status: GENERIC_REVISION_LOOP_LLM_READY_NO_WRITE_AUTHORITY

- target: stack_linker_breather
- recommendation: REVISE_CANDIDATE
- candidate_action: USE_CLASS_BREATHER_WRAPPER

```json
{
  "authority": {
    "engine_file_write_authority": false,
    "model_generation_called": true,
    "patch_apply_authority": false,
    "project_file_write_authority": false,
    "writes_forge_memory_only": true
  },
  "candidate_action": "USE_CLASS_BREATHER_WRAPPER",
  "created_at": "2026-05-18T17:04:47",
  "llm_review": {
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
  "recommendation": "REVISE_CANDIDATE",
  "report_type": "GENERIC_REVISION_LOOP_LLM_V1",
  "sandbox_run_sha256": "0a63fd3d26abc9e5788b961298dd7b60d9f1829c1d98dcbf307ba039f4df4796",
  "schema_version": "generic_revision_loop_v1_patch142",
  "status": "GENERIC_REVISION_LOOP_LLM_READY_NO_WRITE_AUTHORITY",
  "target": "stack_linker_breather"
}
```