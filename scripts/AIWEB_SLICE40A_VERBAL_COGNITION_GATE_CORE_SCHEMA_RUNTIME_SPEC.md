# AI.Web Slice 40A Verbal Cognition Gate Core Schema Runtime Specification

## Status

Schema-only increment. No gate evaluator is installed.

## Accepted parent

- Repository: `/home/nic/forge`
- Branch: `main`
- HEAD: `643686b8664fe938b8e87e6335cf6ecc3c87e1d3`
- Tree: `a83b0561ff7858d0ea69db0f92ed6494fcde26aa`
- Subject: `Slice 39H disabled bootstrap integration closeout`

## Purpose

Create immutable typed companion records that can later preserve candidate-
specific verbal-cognition gate review without evaluating any candidate.

## Approved gate families

1. `expectancy`
2. `congruity`
3. `connectedness`
4. `recoverable_purpose`

`intended_purport` remains the architecture alias associated with the
recoverable-purpose family. It is not a second hidden evaluator.

## Admitted record types

1. `VerbalCognitionGateIdentity`
2. `VerbalCognitionGateProfileIdentity`
3. `GateCandidateInputReference`
4. `GateRequirementReference`
5. `GateReasonGround`
6. `GateTraceReference`
7. `GateProvenanceReference`
8. `GateLimitationReference`
9. `VerbalCognitionGateReviewRecord`
10. `VerbalCognitionGateFamily`
11. `GateEvaluationState`

## Evaluation-state boundary

The closed Slice 40A states are custody states only:

- `not_evaluated`
- `ready_for_later_evaluation`
- `evaluation_deferred`
- `evaluation_unavailable`

They do not mean satisfied, failed, accepted, rejected, clarified, ambiguous,
unsupported, refusal-relevant, held, blocked, or eligible for selection.

## MSM-v1 decision

Decision value: `versioned_companion_required`.

The accepted Slice 35 schema is not modified or automatically migrated.
MSM-v1 non-selection outcome population belongs to later Slice 40 composition
and integration work, not Slice 40A.

## Deferred work

- deterministic identity calculation;
- validation and canonical serialization;
- lifecycle transitions;
- expectancy, congruity, connectedness, and recoverable-purpose evaluation;
- composed dispositions and the exact positive disposition name;
- ambiguity, clarification, unsupported, refusal, hold, and blocked states;
- MSM-v1 gate integration;
- disabled bootstrap integration and Slice 40 closeout;
- selected meaning, which belongs to Slice 41;
- truth, evidence, permission, route, execution, memory, rendering, delivery,
  and external-resource authority.
