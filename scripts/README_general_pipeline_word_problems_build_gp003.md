# GP-003 — Multi-Step Count-Change Word Problems

Build ID: GENERAL-LEARNING-TO-ANSWER-PIPELINE-MULTISTEP-WORDPROBLEMS-BUILD-GP-003
Schema:   general_pipeline_v1_build_gp003

Adds one learned domain on top of GP-001 + GP-002, with NO prior file modified:
  multi_step_count_change — a starting count changed by a sequence of add/remove
  events, solved by exact arithmetic in order and verified by independently
  re-summing the signed changes.

Examples (from instructional word-problem source text):
  Sam had 12 apples, bought 8 more, then gave away 5.        -> 15
  There were 20 birds. 7 flew away and then 4 more landed.   -> 17
  A shelf had 30 books. 12 were borrowed, then 6 returned.   -> 24
  Maria had 50 stickers. Gave away 10, lost 5, then found 3. -> 38
  A jar had 18 candies. 6 were eaten and 9 more were added.  -> 21

Routing diagnostic (new): the test + verifier feed one question per loaded
domain through match_domain and confirm each routes correctly. With all four
domains loaded the result is ZERO collisions.

How it stays clean:
  - GP-001 and GP-002 are byte-for-byte untouched. GP-003 ships two new modules
    (domains_wordproblems.py, gp003_word_problems.py) and wires in via
    gp003_word_problems.activate() — idempotent, chaining over GP-002's wrapper.
  - Same guarantees: unlearned questions refused (no guessing); governed gate
    requires positive information gain + passed exact verification before seal;
    Echo approves only faithful renderings.
  - Boundaries: in-memory only. No route, UI, LLM, file I/O, memory write,
    Chroma, Identity Vault, or CT/ledger activity.

Files installed:
  rmc_engine_v1/general_pipeline/domains_wordproblems.py
  rmc_engine_v1/general_pipeline/gp003_word_problems.py
  scripts/test_general_pipeline_word_problems_build_gp003.py
  scripts/general_pipeline_word_problems_build_gp003_verify.py
  scripts/README_general_pipeline_word_problems_build_gp003.md
  scripts/SHA256SUMS_general_pipeline_word_problems_build_gp003.txt
  scripts/MEA_GENERAL_PIPELINE_BUILD_GP003_DELIVERY_MANIFEST.json

Verify after install:
  .venv/bin/python scripts/test_general_pipeline_word_problems_build_gp003.py --forge-root "$HOME/forge"
  .venv/bin/python scripts/general_pipeline_word_problems_build_gp003_verify.py --forge-root "$HOME/forge"

Expected:
  RESULT: ...MULTISTEP-WORDPROBLEMS-BUILD-GP-003_BEHAVIOR PASS  Total:29 Passed:29 Failed:0
  RESULT: GENERAL-PIPELINE-MULTISTEP-WORDPROBLEMS-BUILD-GP-003_VERIFY PASS  Total:31 Passed:31 Failed:0

GP-001 (35/23) and GP-002 (30/26) must still pass unchanged.

Roadmap: GP-004 elementary language (spelling/pluralization, still verifiable),
then a small renderer-extension informed by several domains, then toward
riddles / word-search.
