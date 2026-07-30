#!/usr/bin/env python3
"""Read-only acceptance test for the actual eight-record Language Core baseline.

The outer process snapshots the promoted records and their governance receipts,
then starts a fresh Python child so the Ask Forge adapter cannot reuse a stale
module-global provider.  No temporary records are created and no promotion API
is called.
"""

from __future__ import annotations

import hashlib
import os
from pathlib import Path
import stat
import subprocess
import sys


def _protected_snapshot(repository: Path) -> tuple[tuple[object, ...], ...]:
    roots = (
        repository / "memory" / "rmc_language_core_v1",
        repository / "memory" / "rmc_language_core_governance_v1",
    )
    rows: list[tuple[object, ...]] = []
    for root in roots:
        if not root.exists():
            rows.append((str(root.relative_to(repository)), "MISSING"))
            continue
        for path in (root, *sorted(root.rglob("*"))):
            metadata = path.lstat()
            relative = str(path.relative_to(repository))
            common = (
                relative,
                stat.S_IMODE(metadata.st_mode),
                metadata.st_uid,
                metadata.st_gid,
                metadata.st_size,
                metadata.st_mtime_ns,
                metadata.st_ino,
                metadata.st_nlink,
            )
            if stat.S_ISREG(metadata.st_mode):
                rows.append(
                    (
                        *common,
                        "FILE",
                        hashlib.sha256(path.read_bytes()).hexdigest(),
                    )
                )
            elif stat.S_ISDIR(metadata.st_mode):
                rows.append((*common, "DIRECTORY"))
            elif stat.S_ISLNK(metadata.st_mode):
                rows.append((*common, "SYMLINK", os.readlink(path)))
            else:
                rows.append((*common, "OTHER"))
    return tuple(rows)


class Ledger:
    def __init__(self) -> None:
        self.checks = 0
        self.failures: list[str] = []

    def check(self, condition: bool, message: str) -> None:
        self.checks += 1
        if not condition:
            self.failures.append(message)


def _snapshot_key(item: object) -> tuple[object, ...]:
    return (
        item.meaning_candidate_ref,
        item.exact_semantic_contract_refs,
        item.exact_concept_refs,
        item.exact_relation_refs,
        item.exact_ancestry_refs,
    )


def _fresh_checks(repository: Path) -> int:
    before = _protected_snapshot(repository)
    sys.path.insert(0, str(repository))

    from aiweb_language_core_bootstrap.governed_semantic_charter import (
        proposed_semantic_charter,
    )
    from aiweb_language_core_bootstrap.meaning_compiler_preview import (
        compile_meaning_preview,
    )
    from aiweb_language_core_bootstrap.meaning_compiler_preview.registry import (
        forge_seed_registry,
    )
    from aiweb_language_core_bootstrap.meaning_compiler_preview.semantic_contract import (
        semantic_contract_for_candidate,
    )
    from rmc_engine_v1.meaning_compiler_preview import (
        build_language_core_preview_response,
    )
    from rmc_engine_v1.operator_council_preview import (
        build_operator_council_preview,
    )
    from rmc_engine_v1.rmc_exact_language_store import (
        evaluate_exact_identity_resonance,
        load_trusted_rmc_language_store,
    )

    ledger = Ledger()
    charter = proposed_semantic_charter()
    provider = load_trusted_rmc_language_store(repository)
    fixtures = {item.fixture_key: item for item in charter.replay_fixtures}
    records_by_signature: dict[str, list[object]] = {}
    for record in provider.records:
        records_by_signature.setdefault(record.semantic_signature_ref, []).append(record)

    ledger.check(len(fixtures) == 8, "charter must contain exactly eight fixtures")
    ledger.check(provider.trusted is True, "fresh provider must be trusted")
    ledger.check(
        provider.load_status == "TRUSTED_STRUCTURED",
        "fresh provider must load as TRUSTED_STRUCTURED",
    )
    ledger.check(provider.stable_record_count == 8, "provider must expose eight stable records")
    ledger.check(provider.live_record_count == 0, "baseline must not depend on live records")
    ledger.check(provider.rejected_record_count == 0, "provider must reject no records")
    ledger.check(len(provider.records) == 8, "provider record tuple must contain eight records")
    ledger.check(provider.read_only is True, "provider must be read-only")
    ledger.check(provider.memory_write_performed is False, "provider must not write memory")
    ledger.check(provider.tokenization_used is False, "provider must not tokenize")
    ledger.check(provider.embedding_used is False, "provider must not embed")
    ledger.check(provider.vector_used is False, "provider must not use vectors")
    ledger.check(
        provider.similarity_scoring_used is False,
        "provider must not use similarity scoring",
    )

    role_ids = {item.role_key: item.role_id for item in forge_seed_registry().roles}
    exact_results: dict[str, tuple[object, tuple[object, ...], dict[str, object]]] = {}
    record_by_fixture: dict[str, object] = {}

    for fixture_key, fixture in fixtures.items():
        label = f"fixture {fixture_key}"
        records = records_by_signature.get(fixture.expected_semantic_signature, [])
        ledger.check(len(records) == 1, f"{label} must map to one promoted record")
        if len(records) != 1:
            continue
        record = records[0]
        record_by_fixture[fixture_key] = record
        ledger.check(record.store_class == "stable", f"{label} record must be stable")
        ledger.check(
            record.lifecycle_state == "accepted_stable",
            f"{label} record must have the accepted stable lifecycle",
        )
        ledger.check(record.record_id == record.expected_id(), f"{label} record ID must verify")
        ledger.check(record.raw_text_present is False, f"{label} record cannot contain raw text")
        ledger.check(record.token_stream_present is False, f"{label} record cannot contain tokens")
        ledger.check(record.embedding_present is False, f"{label} record cannot contain embeddings")
        ledger.check(record.vector_present is False, f"{label} record cannot contain vectors")

        compiled = compile_meaning_preview(
            fixture.exact_source_text,
            rmc_snapshot=provider.snapshot,
        )
        selected = compiled.selected_meaning
        ledger.check(compiled.status.value == "PREVIEW_READY", f"{label} must compile ready")
        ledger.check(selected is not None, f"{label} must select one meaning")
        if selected is None:
            continue
        contract = semantic_contract_for_candidate(selected, compiled.frame_candidates)
        ledger.check(
            selected.meaning_candidate_id == fixture.expected_meaning_candidate_ref,
            f"{label} selected candidate must match the charter",
        )
        ledger.check(
            selected.semantic_signature == fixture.expected_semantic_signature,
            f"{label} semantic signature must match the charter",
        )
        ledger.check(
            selected.predicate_ref == fixture.expected_predicate_ref,
            f"{label} predicate must match the charter",
        )
        ledger.check(
            selected.negated is fixture.expected_negated,
            f"{label} polarity must match the charter",
        )
        ledger.check(
            contract.semantic_contract_id == record.semantic_contract_ref,
            f"{label} exact semantic contract must match promoted RMC",
        )
        ledger.check(contract.speech_act == record.speech_act, f"{label} speech act must match")
        ledger.check(contract.purport == record.purport, f"{label} purport must match")
        ledger.check(contract.frame_key == record.frame_key, f"{label} frame must match")
        ledger.check(
            contract.grammar_rule_ref == record.grammar_rule_ref,
            f"{label} grammar rule must match",
        )

        exact = evaluate_exact_identity_resonance(
            provider.records,
            compiled.meaning_candidates,
            compiled.frame_candidates,
        )
        full = tuple(
            item
            for item in exact
            if item.meaning_candidate_ref == selected.meaning_candidate_id
            and item.memory_record_ref == record.record_id
            and item.exact_semantic_contract_refs == (record.semantic_contract_ref,)
            and set(item.exact_concept_refs) == set(record.concept_refs)
            and set(item.exact_sense_refs) == set(record.sense_refs)
            and set(item.exact_relation_refs) == set(record.relation_refs)
            and set(item.exact_role_refs) == set(record.role_refs)
            and set(item.exact_ancestry_refs) == set(record.ancestry_refs)
        )
        ledger.check(len(full) == 1, f"{label} must have one complete exact-ID resonance")
        ledger.check(
            all(item.approximate_match_used is False for item in exact),
            f"{label} cannot use approximate matching",
        )
        ledger.check(
            all(item.used_for_selection is False for item in exact),
            f"{label} external RMC audit cannot select meaning",
        )

        response = build_language_core_preview_response(
            {"source_text": fixture.exact_source_text}
        )
        exact_results[fixture_key] = (compiled, exact, response)
        receipt = response.get("receipt") or {}
        council = response.get("operator_council") or {}
        council_result = council.get("result") or {}
        evidence = council_result.get("evidence") or {}
        recommendation = council_result.get("recommendation") or {}
        council_boundary = council.get("boundary") or {}
        surface_boundary = response.get("boundary") or {}
        response_provider = response.get("trusted_rmc_provider") or {}
        response_resonances = response.get("rmc_exact_identity_resonances") or []
        all_response_refs = {str(item.get("resonance_id", "")) for item in response_resonances}
        admitted_refs = set(
            response.get("operator_council_admitted_rmc_exact_resonance_refs") or []
        )

        ledger.check(response.get("status") == "PREVIEW_READY", f"{label} Ask Forge must be ready")
        ledger.check(
            response_provider.get("provider_result_id") == provider.provider_result_id,
            f"{label} Ask Forge must use the fresh provider snapshot",
        )
        ledger.check(
            response_provider.get("load_status") == "TRUSTED_STRUCTURED"
            and response_provider.get("stable_record_count") == 8,
            f"{label} Ask Forge must disclose the eight-record trusted provider",
        )
        ledger.check(
            len(full) == 1 and full[0].resonance_id in admitted_refs,
            f"{label} complete semantic-contract support must reach Council",
        )
        ledger.check(admitted_refs <= all_response_refs, f"{label} Council refs must be audited refs")
        ledger.check(
            receipt.get("operator_council_admitted_rmc_exact_resonance_count")
            == len(admitted_refs),
            f"{label} receipt must bind admitted Council count",
        )
        ledger.check(
            set(receipt.get("operator_council_admitted_rmc_exact_resonance_refs") or ())
            == admitted_refs,
            f"{label} receipt must bind admitted Council refs",
        )
        ledger.check(
            council.get("status") == "RECOMMEND_FOR_OPERATOR_REVIEW",
            f"{label} Council must recommend exact evidence for operator review",
        )
        ledger.check(council.get("recommendation_only") is True, f"{label} Council is advisory")
        ledger.check(
            evidence.get("selected_meaning_support_status") == "EXACT_SUPPORT",
            f"{label} Council must record EXACT_SUPPORT",
        )
        ledger.check(
            record.semantic_contract_ref in set(evidence.get("rmc_evidence_refs") or ()),
            f"{label} Council evidence must cite the semantic contract",
        )
        ledger.check(recommendation.get("executable") is False, f"{label} cannot execute")
        ledger.check(recommendation.get("authoritative") is False, f"{label} is not authority")
        ledger.check(
            recommendation.get("operator_decision_required") is True,
            f"{label} still requires a human decision",
        )
        for field in (
            "decision_authority",
            "memory_write_performed",
            "tool_routing_performed",
            "action_performed",
            "delivery_performed",
            "tokenization_performed",
            "model_called",
            "embedding_used",
            "vector_used",
            "similarity_scoring_used",
        ):
            ledger.check(council_boundary.get(field) is False, f"{label} Council boundary {field}=false")
        for field in (
            "memory_write_performed",
            "tool_routing_performed",
            "action_performed",
            "delivery_performed",
            "model_called",
            "embedding_used",
            "vector_used",
            "similarity_scoring_used",
        ):
            ledger.check(surface_boundary.get(field) is False, f"{label} surface boundary {field}=false")

    adversarial = (
        ("polarity", "forge_uses_rmc", "Forge does not use RMC memory."),
        ("speech_act", "forge_uses_rmc", "Can Forge use RMC memory?"),
        ("grammar", "define_rmc", "What does RMC mean?"),
        ("predicate", "forge_uses_rmc", "Forge reports RMC memory."),
        ("concept", "forge_uses_rmc", "Forge uses the manifest."),
    )
    for category, reference_key, source in adversarial:
        label = f"adversarial {category}"
        reference = record_by_fixture.get(reference_key)
        ledger.check(reference is not None, f"{label} reference record must exist")
        if reference is None:
            continue
        compiled = compile_meaning_preview(source, rmc_snapshot=provider.snapshot)
        selected = compiled.selected_meaning
        ledger.check(compiled.status.value == "PREVIEW_READY", f"{label} source must compile")
        ledger.check(selected is not None, f"{label} must select a candidate")
        if selected is None:
            continue
        contract = semantic_contract_for_candidate(selected, compiled.frame_candidates)
        concepts = {item.concept_ref for item in selected.roles}
        exact = evaluate_exact_identity_resonance(
            provider.records,
            compiled.meaning_candidates,
            compiled.frame_candidates,
        )
        response = build_language_core_preview_response({"source_text": source})
        council = response.get("operator_council") or {}
        evidence = (council.get("result") or {}).get("evidence") or {}

        ledger.check(
            contract.semantic_contract_id != reference.semantic_contract_ref,
            f"{label} must differ from the promoted semantic contract",
        )
        ledger.check(
            all(not item.exact_semantic_contract_refs for item in exact),
            f"{label} must receive no exact semantic-contract resonance",
        )
        ledger.check(
            council.get("status") == "HOLD_FOR_EVIDENCE",
            f"{label} must be held rather than recommended",
        )
        ledger.check(
            evidence.get("selected_meaning_support_status")
            == "NO_ADEQUATE_EXACT_SUPPORT",
            f"{label} must disclose inadequate exact support",
        )
        ledger.check(evidence.get("rmc_evidence_refs") == (), f"{label} must cite no RMC support")
        ledger.check(
            (council.get("result") or {}).get("recommendation", {}).get("executable") is False,
            f"{label} cannot execute",
        )

        common = (
            contract.predicate_ref == reference.predicate_ref,
            concepts == set(reference.concept_refs),
            contract.speech_act == reference.speech_act,
            contract.purport == reference.purport,
            contract.negated is reference.negated,
            contract.frame_key == reference.frame_key,
            contract.grammar_rule_ref == reference.grammar_rule_ref,
        )
        if category == "polarity":
            ledger.check(all(common[index] for index in (0, 1, 2, 3)), f"{label} controls other semantics")
            ledger.check(contract.negated is not reference.negated, f"{label} must reverse polarity")
        elif category == "speech_act":
            ledger.check(all(common[index] for index in (0, 1, 4)), f"{label} controls predicate/concepts/polarity")
            ledger.check(contract.speech_act != reference.speech_act, f"{label} must change speech act")
        elif category == "grammar":
            ledger.check(all(common[index] for index in (0, 1, 2, 3, 4, 5)), f"{label} controls non-grammar fields")
            ledger.check(
                contract.grammar_rule_ref != reference.grammar_rule_ref,
                f"{label} must change only the grammar rule among contract fields",
            )
        elif category == "predicate":
            ledger.check(all(common[index] for index in (1, 2, 3, 4, 5, 6)), f"{label} controls non-predicate fields")
            ledger.check(contract.predicate_ref != reference.predicate_ref, f"{label} must change predicate")
        elif category == "concept":
            ledger.check(all(common[index] for index in (0, 2, 3, 4, 5, 6)), f"{label} controls non-concept fields")
            ledger.check(concepts != set(reference.concept_refs), f"{label} must change concept identity")

    # Regression for the adapter/Council boundary: the full audit retains
    # role-only rows, the adapter excludes them from Council, and direct
    # Council callers still fail closed if they supply one.
    inspect_compiled, inspect_exact, inspect_response = exact_results["inspect_manifest"]
    snapshot_keys = {_snapshot_key(item) for item in inspect_compiled.rmc_context.resonances}
    unbound = tuple(item for item in inspect_exact if _snapshot_key(item) not in snapshot_keys)
    ledger.check(bool(unbound), "inspect audit must expose irrelevant partial rows for regression")
    ledger.check(
        all(not item.exact_semantic_contract_refs for item in unbound),
        "irrelevant regression rows cannot claim a semantic contract",
    )
    ledger.check(
        any(item.exact_role_refs or item.exact_sense_refs for item in unbound),
        "irrelevant regression rows must be role/sense-only overlaps",
    )
    audit_refs = {
        str(item.get("resonance_id", ""))
        for item in inspect_response.get("rmc_exact_identity_resonances", ())
    }
    admitted_refs = set(
        inspect_response.get("operator_council_admitted_rmc_exact_resonance_refs", ())
    )
    unbound_refs = {item.resonance_id for item in unbound}
    ledger.check(unbound_refs <= audit_refs, "surface must preserve unbound rows for audit")
    ledger.check(not (unbound_refs & admitted_refs), "adapter must not send unbound rows to Council")
    direct_rejection = build_operator_council_preview(
        inspect_compiled,
        exact_rmc_resonances=(unbound[0],),
    )
    ledger.check(
        direct_rejection.get("status") == "HELD_INVALID_EVIDENCE",
        "direct Council must still reject unbound supplied evidence",
    )
    ledger.check(
        "exact_rmc_resonance_not_bound_to_snapshot"
        in set(direct_rejection.get("issue_codes") or ()),
        "direct Council rejection must identify snapshot binding",
    )

    after = _protected_snapshot(repository)
    ledger.check(after == before, "acceptance test must not modify promoted records or receipts")

    print("AI.WEB PROMOTED LANGUAGE BASELINE")
    print(f"checks={ledger.checks}")
    print(f"failures={len(ledger.failures)}")
    print(f"provider_status={provider.load_status}")
    print(f"stable_records={provider.stable_record_count}")
    print(f"exact_fixtures={len(exact_results)}")
    print(f"adversarial_holds={len(adversarial)}")
    print("memory_mutations=0")
    for failure in ledger.failures:
        print("FAIL: " + failure)
    print("RESULT=" + ("PASS" if not ledger.failures else "FAIL"))
    return 0 if not ledger.failures else 1


def main() -> int:
    if len(sys.argv) >= 2 and sys.argv[1] == "--fresh-child":
        repository = Path(sys.argv[2] if len(sys.argv) >= 3 else ".").resolve()
        return _fresh_checks(repository)

    repository = Path(sys.argv[1] if len(sys.argv) >= 2 else Path(__file__).parents[1]).resolve()
    before = _protected_snapshot(repository)
    completed = subprocess.run(
        [sys.executable, "-B", str(Path(__file__).resolve()), "--fresh-child", str(repository)],
        cwd=repository,
        text=True,
        capture_output=True,
        check=False,
    )
    if completed.stdout:
        print(completed.stdout, end="")
    if completed.stderr:
        print(completed.stderr, end="", file=sys.stderr)
    after = _protected_snapshot(repository)
    if after != before:
        print("FAIL: outer immutable snapshot changed while fresh child ran")
        print("RESULT=FAIL")
        return 1
    if completed.returncode == 0:
        print("fresh_provider_process=PASS")
        print("outer_immutable_snapshot=PASS")
    return completed.returncode


if __name__ == "__main__":
    raise SystemExit(main())
