"""Forge-owned provisional seed registry for the v0 meaning preview.

Nothing in this registry is imported from the glyph packet, Google Drive,
Panini, Chomsky, or another language-core branch.  Those materials may inform
future operator review, but they have zero authority in this preview.
"""

from __future__ import annotations

from typing import Final

from ..schema import stable_record_id
from .schema import (
    ForgeSeedRegistry,
    PredicateDefinition,
    ProvisionalConcept,
    ProvisionalSense,
    RoleDefinition,
)


REGISTRY_OWNER: Final[str] = "forge_operator_system"
REGISTRY_VERSION: Final[str] = "forge-meaning-seed-v0"


def _surface_variants(*forms: str) -> tuple[tuple[str, ...], ...]:
    """Return one declared form for each ASCII lookup spelling.

    Source custody remains exact.  The compiler's bounded ASCII case key is a
    lookup aid only, so storing title/upper-case copies here would create
    duplicate registry forms without adding a distinct sense.
    """

    declared: list[tuple[str, ...]] = []
    declared_keys: set[tuple[str, ...]] = set()
    for form in forms:
        words = tuple(form.split(" "))
        lookup_key = tuple(_ascii_key(word) for word in words)
        if words and lookup_key not in declared_keys:
            declared.append(words)
            declared_keys.add(lookup_key)
    return tuple(declared)


def _ascii_key(text: str) -> str:
    """Fold ASCII letter case without normalizing the declared text."""

    return "".join(
        chr(ord(character) + 32) if "A" <= character <= "Z" else character
        for character in text
    )


def _duplicates(values: tuple[str, ...]) -> tuple[str, ...]:
    seen: set[str] = set()
    duplicates: list[str] = []
    for value in values:
        if value in seen and value not in duplicates:
            duplicates.append(value)
        seen.add(value)
    return tuple(sorted(duplicates))


def _concept(
    key: str,
    label: str,
    semantic_class: str,
    definition: str,
) -> ProvisionalConcept:
    body = {
        "concept_key": key,
        "preferred_label": label,
        "semantic_class": semantic_class,
        "provisional_definition": definition,
        "registry_owner": REGISTRY_OWNER,
        "registry_version": REGISTRY_VERSION,
        "provisional": True,
        "external_reference_authority": False,
    }
    return ProvisionalConcept(
        concept_id=stable_record_id("forge_preview_concept", body),
        **body,
    )


def _sense(
    key: str,
    concept: ProvisionalConcept,
    forms: tuple[tuple[str, ...], ...],
    gloss: str,
) -> ProvisionalSense:
    body = {
        "sense_key": key,
        "concept_ref": concept.concept_id,
        "exact_surface_forms": forms,
        "provisional_gloss": gloss,
        "registry_owner": REGISTRY_OWNER,
        "registry_version": REGISTRY_VERSION,
        "provisional": True,
        "external_reference_authority": False,
    }
    return ProvisionalSense(
        sense_id=stable_record_id("forge_preview_sense", body),
        **body,
    )


def _predicate(
    key: str,
    label: str,
    forms: tuple[str, ...],
    roles: tuple[str, ...],
) -> PredicateDefinition:
    body = {
        "predicate_key": key,
        "preferred_label": label,
        "exact_surface_forms": forms,
        "required_roles": roles,
        "registry_owner": REGISTRY_OWNER,
        "registry_version": REGISTRY_VERSION,
        "provisional": True,
    }
    return PredicateDefinition(
        predicate_id=stable_record_id("forge_preview_predicate", body),
        **body,
    )


def _role(key: str, description: str) -> RoleDefinition:
    body = {
        "role_key": key,
        "description": description,
        "registry_owner": REGISTRY_OWNER,
        "registry_version": REGISTRY_VERSION,
        "provisional": True,
    }
    return RoleDefinition(
        role_id=stable_record_id("forge_preview_role", body),
        **body,
    )


_CONCEPT_SPECS: Final[tuple[tuple[str, str, str, str, tuple[str, ...]], ...]] = (
    (
        "forge",
        "Forge",
        "operator_system",
        "the main operator system named Forge",
        ("forge",),
    ),
    (
        "forge_core",
        "Forge Core",
        "system_component",
        "the provisional central operating component of Forge",
        ("forge core", "core"),
    ),
    (
        "language_core",
        "Language Core",
        "language_component",
        "the provisional Forge component that compiles source forms into symbolic meaning candidates",
        ("language core", "core"),
    ),
    (
        "rmc_memory",
        "RMC Memory",
        "memory_component",
        "the read-only resonance context layer identified as RMC in this preview",
        ("rmc", "rmc memory"),
    ),
    (
        "meaning",
        "Meaning",
        "semantic_object",
        "a provisional symbolic relation among a predicate, roles, and concepts",
        ("meaning",),
    ),
    (
        "word",
        "Word",
        "source_form",
        "a written source form retained with its exact source span",
        ("word", "words"),
    ),
    (
        "language",
        "Language",
        "symbolic_system",
        "a system of forms and relations used to express meaning",
        ("language",),
    ),
    (
        "authority",
        "Authority",
        "authority_role",
        "a recognized standing or power assigned to a participant or system",
        ("authority", "authorities"),
    ),
    (
        "artifact",
        "Artifact",
        "stored_artifact",
        "a bounded record or object that can be inspected and reported",
        ("artifact", "artifacts"),
    ),
    (
        "anomaly",
        "Anomaly",
        "deviation",
        "an unexpected or irregular condition that can be described",
        ("anomaly", "anomalies"),
    ),
    (
        "ability",
        "Ability",
        "capability",
        "the capacity to act, reach, or influence a bounded target",
        ("ability", "abilities"),
    ),
    (
        "abstraction",
        "Abstraction",
        "conceptual_object",
        "a simplified model or idea that captures a bounded pattern",
        ("abstraction", "abstractions"),
    ),
    (
        "academy",
        "Academy",
        "institution",
        "a bounded institution for learning and instruction",
        ("academy", "academies"),
    ),
    (
        "access",
        "Access",
        "capability",
        "the ability to reach or use a bounded object",
        ("access",),
    ),
    (
        "account",
        "Account",
        "record",
        "a bounded record of state or ownership",
        ("account", "accounts"),
    ),
    (
        "accuracy",
        "Accuracy",
        "quality",
        "a bounded measure of correctness or exactness",
        ("accuracy",),
    ),
    (
        "achievement",
        "Achievement",
        "result",
        "a successful outcome from a bounded action or process",
        ("achievement", "achievements"),
    ),
    (
        "acquisition",
        "Acquisition",
        "obtainment",
        "a bounded act of taking hold or obtaining something",
        ("acquisition", "acquisitions"),
    ),
    (
        "active",
        "Active",
        "state",
        "a condition of being engaged or operating",
        ("active",),
    ),
    (
        "activity",
        "Activity",
        "operation",
        "a bounded operation or process that can be described",
        ("activity", "activities"),
    ),
    (
        "adaptation",
        "Adaptation",
        "change",
        "a bounded change made to fit a context or target",
        ("adaptation", "adaptations"),
    ),
    (
        "addition",
        "Addition",
        "supplement",
        "an extra item or contribution added to a bounded structure",
        ("addition", "additions"),
    ),
    (
        "address",
        "Address",
        "reference",
        "a bounded locator or reference point",
        ("address", "addresses"),
    ),
    (
        "adjustment",
        "Adjustment",
        "change",
        "a bounded refinement or correction applied to a thing",
        ("adjustment", "adjustments"),
    ),
    (
        "admin",
        "Admin",
        "human_role",
        "a participant assigned to manage or approve bounded operations",
        ("admin", "admins"),
    ),
    (
        "advance",
        "Advance",
        "progress",
        "a movement or step forward in a bounded process",
        ("advance", "advances"),
    ),
    (
        "advantage",
        "Advantage",
        "benefit",
        "a bounded benefit or gain available in a process",
        ("advantage", "advantages"),
    ),
    (
        "adventure",
        "Adventure",
        "journey",
        "a bounded exploration or quest that unfolds over time",
        ("adventure", "adventures"),
    ),
    (
        "adviser",
        "Adviser",
        "human_role",
        "a participant who offers guidance within a bounded process",
        ("adviser", "advisers", "advisor", "advisors"),
    ),
    (
        "agenda",
        "Agenda",
        "plan",
        "a bounded plan or list of points for review",
        ("agenda", "agendas"),
    ),
    (
        "agency",
        "Agency",
        "institution",
        "an organizational body or actor with bounded authority",
        ("agency", "agencies"),
    ),
    (
        "alert",
        "Alert",
        "signal",
        "a flagged notice or warning state",
        ("alert", "alerts"),
    ),
    (
        "alias",
        "Alias",
        "label",
        "an alternate label for a bounded concept or record",
        ("alias", "aliases"),
    ),
    (
        "alignment",
        "Alignment",
        "relation",
        "a bounded relation that places items in a shared arrangement",
        ("alignment", "alignments"),
    ),
    (
        "allocation",
        "Allocation",
        "distribution",
        "a bounded distribution of resources or attention",
        ("allocation", "allocations"),
    ),
    (
        "allowance",
        "Allowance",
        "permission",
        "a bounded permission or concession granted within a structure",
        ("allowance", "allowances"),
    ),
    (
        "alternative",
        "Alternative",
        "option",
        "a bounded option or substitute considered in a process",
        ("alternative", "alternatives"),
    ),
    (
        "amendment",
        "Amendment",
        "revision",
        "a bounded revision to a record, plan, or text",
        ("amendment", "amendments"),
    ),
    (
        "analysis",
        "Analysis",
        "review",
        "a bounded review or study of a thing or process",
        ("analysis", "analyses"),
    ),
    (
        "analyst",
        "Analyst",
        "human_role",
        "a participant who performs a bounded analysis",
        ("analyst", "analysts"),
    ),
    (
        "anchor",
        "Anchor",
        "reference_point",
        "a fixed point used to stabilize or locate a bounded structure",
        ("anchor", "anchors"),
    ),
    (
        "answer",
        "Answer",
        "response",
        "a provisional reply produced for an inquiry or request",
        ("answer", "answers"),
    ),
    (
        "anticipation",
        "Anticipation",
        "expectation",
        "a bounded expectation of a future state or event",
        ("anticipation",),
    ),
    (
        "apology",
        "Apology",
        "apology",
        "a bounded expression of regret or acknowledgment",
        ("apology", "apologies"),
    ),
    (
        "apparatus",
        "Apparatus",
        "instrument",
        "a structured instrument or tool used in a process",
        ("apparatus", "apparatuses"),
    ),
    (
        "appendix",
        "Appendix",
        "supplement",
        "an attached supplement or reference section",
        ("appendix", "appendices"),
    ),
    (
        "application",
        "Application",
        "use_case",
        "a bounded use case or practical deployment of a method",
        ("application", "applications"),
    ),
    (
        "approval",
        "Approval",
        "consent",
        "a bounded consent or authorization for action",
        ("approval", "approvals"),
    ),
    (
        "approximation",
        "Approximation",
        "estimate",
        "a bounded estimate of a value or state",
        ("approximation", "approximations"),
    ),
    (
        "archive",
        "Archive",
        "stored_artifact",
        "a preserved record or container retained for later review",
        ("archive", "archives"),
    ),
    (
        "area",
        "Area",
        "region",
        "a bounded region or scope within a larger structure",
        ("area", "areas"),
    ),
    (
        "arithmetic",
        "Arithmetic",
        "formal_method",
        "a bounded method of counting or calculating quantities",
        ("arithmetic",),
    ),
    (
        "arm",
        "Arm",
        "body_part",
        "a bounded limb used for action or manipulation",
        ("arm", "arms"),
    ),
    (
        "argument",
        "Argument",
        "claim",
        "a bounded claim or reason offered in review or debate",
        ("argument", "arguments"),
    ),
    (
        "article",
        "Article",
        "record",
        "a bounded written record or entry",
        ("article", "articles"),
    ),
    (
        "aspect",
        "Aspect",
        "feature",
        "a bounded feature or angle of a thing",
        ("aspect", "aspects"),
    ),
    (
        "assembly",
        "Assembly",
        "group",
        "a bounded group or collection gathered together",
        ("assembly", "assemblies"),
    ),
    (
        "assessment",
        "Assessment",
        "evaluation",
        "a bounded evaluation or judgment of a thing",
        ("assessment", "assessments"),
    ),
    (
        "asset",
        "Asset",
        "resource",
        "a bounded resource available for use or review",
        ("asset", "assets"),
    ),
    (
        "assignment",
        "Assignment",
        "task",
        "a bounded task or duty assigned to a participant",
        ("assignment", "assignments"),
    ),
    (
        "assistant",
        "Assistant",
        "support_role",
        "a participant that supports another participant or process",
        ("assistant", "assistants"),
    ),
    (
        "association",
        "Association",
        "relation",
        "a bounded relation or grouping between things",
        ("association", "associations"),
    ),
    (
        "assumption",
        "Assumption",
        "supposition",
        "a bounded supposition taken as a provisional basis",
        ("assumption", "assumptions"),
    ),
    (
        "attribute",
        "Attribute",
        "descriptor",
        "a named property or feature of a bounded concept",
        ("attribute", "attributes"),
    ),
    (
        "auditor",
        "Auditor",
        "human_role",
        "a participant assigned to inspect and review bounded records",
        ("auditor", "auditors"),
    ),
    (
        "agent",
        "Agent",
        "actor",
        "a participant that can act within a bounded process",
        ("agent", "agents"),
    ),
    (
        "algorithm",
        "Algorithm",
        "formal_method",
        "a declared procedure for processing or transforming information",
        ("algorithm", "algorithms"),
    ),
    (
        "action",
        "Action",
        "operation",
        "a bounded act that can be inspected or reported",
        ("action", "actions"),
    ),
    (
        "batch",
        "Batch",
        "group",
        "a bounded collection of items processed together",
        ("batch", "batches"),
    ),
    (
        "baseline",
        "Baseline",
        "reference_point",
        "a bounded reference point used to compare or evaluate change",
        ("baseline", "baselines"),
    ),
    (
        "benefit",
        "Benefit",
        "advantage",
        "a bounded gain or positive outcome available in a process",
        ("benefit", "benefits"),
    ),
    (
        "benchmark",
        "Benchmark",
        "measure",
        "a bounded reference measure used for comparison",
        ("benchmark", "benchmarks"),
    ),
    (
        "belief",
        "Belief",
        "supposition",
        "a bounded conviction or assumption held in context",
        ("belief", "beliefs"),
    ),
    (
        "bias",
        "Bias",
        "preference",
        "a bounded skew or inclination affecting judgment",
        ("bias", "biases"),
    ),
    (
        "blueprint",
        "Blueprint",
        "plan",
        "a bounded design or structural plan for implementation",
        ("blueprint", "blueprints"),
    ),
    (
        "boundary",
        "Boundary",
        "limit",
        "a bounded limit or edge separating regions or roles",
        ("boundary", "boundaries"),
    ),
    (
        "budget",
        "Budget",
        "plan",
        "a bounded allocation of resources for a process",
        ("budget", "budgets"),
    ),
    (
        "memory",
        "Memory",
        "context_component",
        "a bounded context record available to Forge without granting selection authority",
        ("memory",),
    ),
    (
        "vector_memory",
        "Vector Memory",
        "memory_design",
        "a memory design represented as a provisional comparison concept only",
        ("vector memory",),
    ),
    (
        "operator",
        "Operator",
        "human_role",
        "the human authority who reviews and controls Forge",
        ("operator",),
    ),
    (
        "system",
        "System",
        "system_class",
        "a bounded collection of related components",
        ("system",),
    ),
    (
        "status",
        "Status",
        "reportable_state",
        "a declared state available for inspection or reporting",
        ("status",),
    ),
    (
        "manifest",
        "Manifest",
        "structured_record",
        "a structured record that declares a bounded set of items",
        ("manifest",),
    ),
    (
        "file",
        "File",
        "stored_artifact",
        "a named stored artifact",
        ("file", "files"),
    ),
    (
        "result",
        "Result",
        "preview_record",
        "a structured output record produced by a bounded operation",
        ("result", "results"),
    ),
    (
        "symbolic_math",
        "Symbolic Math",
        "formal_method",
        "explicit composition and relation operations over declared symbolic records",
        ("symbolic math", "symbolic mathematics"),
    ),
    (
        "grammar",
        "Grammar",
        "composition_rules",
        "a bounded set of declared rules for composing source forms",
        ("grammar",),
    ),
    (
        "lexicon",
        "Lexicon",
        "sense_registry",
        "a provisional registry connecting exact surface forms to declared senses",
        ("lexicon",),
    ),
    (
        "context",
        "Context",
        "relation_record",
        "a bounded set of exact references considered alongside a meaning candidate",
        ("context",),
    ),
    (
        "resonance",
        "Resonance",
        "exact_reference_relation",
        "an exact shared concept, relation, or ancestry reference in this preview",
        ("resonance",),
    ),
)


_DECLARED_POLYSEMOUS_SURFACES: Final[
    dict[tuple[str, ...], frozenset[str]]
] = {
    # ``core`` deliberately names two provisional component concepts.  The
    # compiler must hold both candidates until exact RMC context or an
    # operator clarification distinguishes them.
    ("core",): frozenset({"forge_core", "language_core"}),
}


def validate_forge_seed_registry(
    registry: ForgeSeedRegistry,
) -> tuple[str, ...]:
    """Return deterministic integrity errors for a Forge seed registry.

    A non-empty result means the registry must not be installed.  Intentional
    polysemy is declared above; every other duplicate lookup form is rejected.
    This validates records and references, not dictionary size.
    """

    if type(registry) is not ForgeSeedRegistry:
        raise TypeError("registry must be a ForgeSeedRegistry")

    errors: list[str] = []

    record_groups = (
        ("concept", registry.concepts, "concept_key", "concept_id"),
        ("sense", registry.senses, "sense_key", "sense_id"),
        ("predicate", registry.predicates, "predicate_key", "predicate_id"),
        ("role", registry.roles, "role_key", "role_id"),
    )
    for group_name, records, key_name, id_name in record_groups:
        keys = tuple(str(getattr(record, key_name)) for record in records)
        identifiers = tuple(str(getattr(record, id_name)) for record in records)
        for duplicate in _duplicates(keys):
            errors.append(f"duplicate_{group_name}_key:{duplicate}")
        for duplicate in _duplicates(identifiers):
            errors.append(f"duplicate_{group_name}_id:{duplicate}")
        for record in records:
            if not str(getattr(record, key_name)):
                errors.append(f"empty_{group_name}_key")
            if not str(getattr(record, id_name)):
                errors.append(f"empty_{group_name}_id")
            if getattr(record, "registry_owner", "") != registry.owner:
                errors.append(
                    f"{group_name}_owner_mismatch:{getattr(record, key_name)}"
                )
            if getattr(record, "registry_version", "") != registry.version:
                errors.append(
                    f"{group_name}_version_mismatch:{getattr(record, key_name)}"
                )
            if getattr(record, "provisional", None) is not True:
                errors.append(
                    f"non_provisional_{group_name}:{getattr(record, key_name)}"
                )

    concept_by_id = {concept.concept_id: concept for concept in registry.concepts}
    role_keys = {role.role_key for role in registry.roles}
    if registry.external_reference_authority is not False:
        errors.append("registry_external_reference_authority_enabled")
    if registry.imported_reference_definitions_used is not False:
        errors.append("registry_imported_reference_definitions_enabled")

    for concept in registry.concepts:
        if not concept.preferred_label.strip():
            errors.append(f"empty_concept_label:{concept.concept_key}")
        if not concept.semantic_class.strip():
            errors.append(f"empty_semantic_class:{concept.concept_key}")
        if not concept.provisional_definition.strip():
            errors.append(f"empty_provisional_definition:{concept.concept_key}")
        if concept.external_reference_authority is not False:
            errors.append(
                f"concept_external_reference_authority_enabled:{concept.concept_key}"
            )

    sense_surfaces: dict[tuple[str, ...], list[ProvisionalSense]] = {}
    for sense in registry.senses:
        if sense.concept_ref not in concept_by_id:
            errors.append(f"unknown_sense_concept_ref:{sense.sense_key}")
        if not sense.provisional_gloss.strip():
            errors.append(f"empty_provisional_gloss:{sense.sense_key}")
        if sense.external_reference_authority is not False:
            errors.append(
                f"sense_external_reference_authority_enabled:{sense.sense_key}"
            )
        local_keys: list[tuple[str, ...]] = []
        for surface in sense.exact_surface_forms:
            lookup_key = tuple(_ascii_key(word) for word in surface)
            if not lookup_key or any(not word for word in lookup_key):
                errors.append(f"empty_sense_surface_form:{sense.sense_key}")
                continue
            if lookup_key in local_keys:
                errors.append(
                    "duplicate_sense_surface_form:"
                    f"{sense.sense_key}:{' '.join(lookup_key)}"
                )
            local_keys.append(lookup_key)
            sense_surfaces.setdefault(lookup_key, []).append(sense)

    for lookup_key, senses in sorted(sense_surfaces.items()):
        distinct_senses = {sense.sense_id: sense for sense in senses}
        if len(distinct_senses) < 2:
            continue
        concept_keys = frozenset(
            concept_by_id[sense.concept_ref].concept_key
            for sense in distinct_senses.values()
            if sense.concept_ref in concept_by_id
        )
        if _DECLARED_POLYSEMOUS_SURFACES.get(lookup_key) != concept_keys:
            errors.append(
                "undeclared_polysemous_surface_form:"
                f"{' '.join(lookup_key)}:{','.join(sorted(concept_keys))}"
            )

    predicate_surfaces: dict[str, str] = {}
    for predicate in registry.predicates:
        local_keys: set[str] = set()
        for surface in predicate.exact_surface_forms:
            lookup_key = _ascii_key(surface)
            if not lookup_key:
                errors.append(f"empty_predicate_surface_form:{predicate.predicate_key}")
                continue
            if lookup_key in local_keys:
                errors.append(
                    "duplicate_predicate_surface_form:"
                    f"{predicate.predicate_key}:{lookup_key}"
                )
            local_keys.add(lookup_key)
            prior = predicate_surfaces.setdefault(lookup_key, predicate.predicate_key)
            if prior != predicate.predicate_key:
                errors.append(
                    "conflicting_predicate_surface_form:"
                    f"{lookup_key}:{prior},{predicate.predicate_key}"
                )
        if len(set(predicate.required_roles)) != len(predicate.required_roles):
            errors.append(f"duplicate_predicate_role:{predicate.predicate_key}")
        for role_key in predicate.required_roles:
            if role_key not in role_keys:
                errors.append(
                    f"unknown_predicate_role:{predicate.predicate_key}:{role_key}"
                )

    return tuple(sorted(set(errors)))


def _build_registry() -> ForgeSeedRegistry:
    concepts = tuple(
        _concept(key, label, semantic_class, definition)
        for key, label, semantic_class, definition, _forms in _CONCEPT_SPECS
    )
    by_key = {concept.concept_key: concept for concept in concepts}
    senses = tuple(
        _sense(
            f"{key}_preview_sense",
            by_key[key],
            _surface_variants(*forms),
            definition,
        )
        for key, _label, _semantic_class, definition, forms in _CONCEPT_SPECS
    )
    predicates = (
        _predicate("be", "be", ("am", "is", "are", "was", "were", "be"), ("subject", "object")),
        _predicate("mean", "mean", ("mean", "means", "meant"), ("definition_target",)),
        _predicate("inspect", "inspect", ("inspect", "inspects", "inspected"), ("object",)),
        _predicate("report", "report", ("report", "reports", "reported"), ("object",)),
        _predicate("explain", "explain", ("explain", "explains", "explained"), ("object",)),
        _predicate("compare", "compare", ("compare", "compares", "compared"), ("comparison_left", "comparison_right")),
        _predicate("use", "use", ("use", "uses", "used"), ("actor", "object")),
        _predicate("remember", "remember", ("remember", "remembers", "remembered"), ("actor", "object")),
        _predicate("store", "store", ("store", "stores", "stored"), ("actor", "object")),
        _predicate("retrieve", "retrieve", ("retrieve", "retrieves", "retrieved"), ("actor", "object")),
        _predicate("describe", "describe", ("describe", "describes", "described"), ("object",)),
        _predicate("analyze", "analyze", ("analyze", "analyzes", "analyzed"), ("object",)),
        _predicate("audit", "audit", ("audit", "audits", "audited"), ("object",)),
        _predicate("assert", "assert", ("assert", "asserts", "asserted"), ("object",)),
        _predicate("absorb", "absorb", ("absorb", "absorbs", "absorbed"), ("object",)),
        _predicate("accelerate", "accelerate", ("accelerate", "accelerates", "accelerated"), ("object",)),
        _predicate("accept", "accept", ("accept", "accepts", "accepted"), ("object",)),
        _predicate("access", "access", ("access", "accesses", "accessed"), ("object",)),
        _predicate("accompany", "accompany", ("accompany", "accompanies", "accompanied"), ("object",)),
        _predicate("accomplish", "accomplish", ("accomplish", "accomplishes", "accomplished"), ("object",)),
        _predicate("accumulate", "accumulate", ("accumulate", "accumulates", "accumulated"), ("object",)),
        _predicate("achieve", "achieve", ("achieve", "achieves", "achieved"), ("object",)),
        _predicate("acquire", "acquire", ("acquire", "acquires", "acquired"), ("object",)),
        _predicate("activate", "activate", ("activate", "activates", "activated"), ("object",)),
        _predicate("adapt", "adapt", ("adapt", "adapts", "adapted"), ("object",)),
        _predicate("add", "add", ("add", "adds", "added"), ("object",)),
        _predicate("address", "address", ("address", "addresses", "addressed"), ("object",)),
        _predicate("adjust", "adjust", ("adjust", "adjusts", "adjusted"), ("object",)),
        _predicate("admire", "admire", ("admire", "admires", "admired"), ("object",)),
        _predicate("admit", "admit", ("admit", "admits", "admitted"), ("object",)),
        _predicate("adopt", "adopt", ("adopt", "adopts", "adopted"), ("object",)),
        _predicate("advance", "advance", ("advance", "advances", "advanced"), ("object",)),
        _predicate("advise", "advise", ("advise", "advises", "advised"), ("object",)),
        _predicate("affect", "affect", ("affect", "affects", "affected"), ("object",)),
        _predicate("afford", "afford", ("afford", "affords", "afforded"), ("object",)),
        _predicate("agree", "agree", ("agree", "agrees", "agreed"), ("object",)),
        _predicate("aim", "aim", ("aim", "aims", "aimed"), ("object",)),
        _predicate("alert", "alert", ("alert", "alerts", "alerted"), ("object",)),
        _predicate("align", "align", ("align", "aligns", "aligned"), ("object",)),
        _predicate("allow", "allow", ("allow", "allows", "allowed"), ("actor", "object")),
        _predicate("alter", "alter", ("alter", "alters", "altered"), ("object",)),
        _predicate("amend", "amend", ("amend", "amends", "amended"), ("object",)),
        _predicate("announce", "announce", ("announce", "announces", "announced"), ("object",)),
        _predicate("answer", "answer", ("answer", "answers", "answered"), ("object",)),
        _predicate("anticipate", "anticipate", ("anticipate", "anticipates", "anticipated"), ("object",)),
        _predicate("apologize", "apologize", ("apologize", "apologizes", "apologized"), ("object",)),
        _predicate("appeal", "appeal", ("appeal", "appeals", "appealed"), ("object",)),
        _predicate("appear", "appear", ("appear", "appears", "appeared"), ("object",)),
        _predicate("append", "append", ("append", "appends", "appended"), ("object",)),
        _predicate("apply", "apply", ("apply", "applies", "applied"), ("object",)),
        _predicate("appoint", "appoint", ("appoint", "appoints", "appointed"), ("object",)),
        _predicate("appreciate", "appreciate", ("appreciate", "appreciates", "appreciated"), ("object",)),
        _predicate("approach", "approach", ("approach", "approaches", "approached"), ("object",)),
        _predicate("approve", "approve", ("approve", "approves", "approved"), ("object",)),
        _predicate("argue", "argue", ("argue", "argues", "argued"), ("object",)),
        _predicate("arrange", "arrange", ("arrange", "arranges", "arranged"), ("object",)),
        _predicate("arrest", "arrest", ("arrest", "arrests", "arrested"), ("object",)),
        _predicate("arrive", "arrive", ("arrive", "arrives", "arrived"), ("object",)),
        _predicate("ask", "ask", ("ask", "asks", "asked"), ("object",)),
        _predicate("assign", "assign", ("assign", "assigns", "assigned"), ("actor", "object")),
        _predicate("assist", "assist", ("assist", "assists", "assisted"), ("actor", "object")),
        _predicate("associate", "associate", ("associate", "associates", "associated"), ("object",)),
        _predicate("assume", "assume", ("assume", "assumes", "assumed"), ("object",)),
        _predicate("assure", "assure", ("assure", "assures", "assured"), ("object",)),
        _predicate("attach", "attach", ("attach", "attaches", "attached"), ("actor", "object")),
        _predicate("attack", "attack", ("attack", "attacks", "attacked"), ("object",)),
        _predicate("attempt", "attempt", ("attempt", "attempts", "attempted"), ("object",)),
        _predicate("attend", "attend", ("attend", "attends", "attended"), ("object",)),
        _predicate("attract", "attract", ("attract", "attracts", "attracted"), ("object",)),
        _predicate("attribute", "attribute", ("attribute", "attributes", "attributed"), ("object",)),
        _predicate("authorize", "authorize", ("authorize", "authorizes", "authorized"), ("object",)),
        _predicate("avoid", "avoid", ("avoid", "avoids", "avoided"), ("object",)),
        _predicate("award", "award", ("award", "awards", "awarded"), ("object",)),
        _predicate("awaken", "awaken", ("awaken", "awakens", "awakened"), ("object",)),
        _predicate("balance", "balance", ("balance", "balances", "balanced"), ("object",)),
        _predicate("ban", "ban", ("ban", "bans", "banned"), ("object",)),
        _predicate("base", "base", ("base", "bases", "based"), ("object",)),
        _predicate("batch", "batch", ("batch", "batches", "batched"), ("object",)),
        _predicate("begin", "begin", ("begin", "begins", "began"), ("object",)),
        _predicate("behave", "behave", ("behave", "behaves", "behaved"), ("object",)),
        _predicate("belong", "belong", ("belong", "belongs", "belonged"), ("object",)),
        _predicate("bind", "bind", ("bind", "binds", "bound"), ("object",)),
        _predicate("block", "block", ("block", "blocks", "blocked"), ("object",)),
        _predicate("boost", "boost", ("boost", "boosts", "boosted"), ("object",)),
        _predicate("build", "build", ("build", "builds", "built"), ("object",)),
        _predicate("borrow", "borrow", ("borrow", "borrows", "borrowed"), ("object",)),
        _predicate("broadcast", "broadcast", ("broadcast", "broadcasts"), ("object",)),
        _predicate("burn", "burn", ("burn", "burns", "burned"), ("object",)),
        _predicate("buy", "buy", ("buy", "buys", "bought"), ("object",)),
    )
    roles = tuple(
        _role(key, description)
        for key, description in (
            ("requester", "source role that issues a request"),
            ("actor", "concept expected to carry the predicate relation"),
            ("subject", "concept about which a simple clause makes a statement"),
            ("object", "concept bound as the object or complement"),
            ("definition_target", "concept for which a provisional definition is requested"),
            ("comparison_left", "left concept in a bounded comparison"),
            ("comparison_right", "right concept in a bounded comparison"),
        )
    )
    body = {
        "owner": REGISTRY_OWNER,
        "version": REGISTRY_VERSION,
        "concepts": concepts,
        "senses": senses,
        "predicates": predicates,
        "roles": roles,
        "external_reference_authority": False,
        "imported_reference_definitions_used": False,
    }
    registry = ForgeSeedRegistry(
        registry_id=stable_record_id("forge_preview_registry", body),
        **body,
    )
    errors = validate_forge_seed_registry(registry)
    if errors:
        raise ValueError("invalid Forge seed registry: " + ";".join(errors))
    return registry


FORGE_SEED_REGISTRY: Final[ForgeSeedRegistry] = _build_registry()


def forge_seed_registry() -> ForgeSeedRegistry:
    """Return the immutable Forge-owned v0 seed registry."""

    return FORGE_SEED_REGISTRY


__all__ = (
    "FORGE_SEED_REGISTRY",
    "REGISTRY_OWNER",
    "REGISTRY_VERSION",
    "forge_seed_registry",
    "validate_forge_seed_registry",
)
