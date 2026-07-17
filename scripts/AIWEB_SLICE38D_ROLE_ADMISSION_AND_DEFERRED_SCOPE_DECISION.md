# Slice 38D Role Admission and Deferred-Scope Decision

## Decision

Slice 38D admits the following exact Forge-owned participant-role identities:

1. `initiator`
2. `actor`
3. `action_subject`
4. `content`
5. `source`
6. `recipient`
7. `instrument`
8. `condition`
9. `standard`
10. `result`
11. `output_target`

The registry is a closed, read-only identity registry. Admission does not assign a role to any source occurrence.

## Why `action_subject` is admitted instead of `affected_entity`

The roadmap lists `affected entity` as a review category, not an automatic production identity. Before Slice 38E defines frame and effect boundaries, `affected_entity` can collapse read-only inspection subjects into modification targets, runtime targets, memory targets, delivery targets, or other consequence-bearing targets. Slice 38D therefore admits the narrower `action_subject`: the participant that a non-executing frame is structurally about or toward, without claiming actual effect.

## Why `location` remains deferred

A location-like value can represent physical place, source location, file path, route, destination, runtime target, output target, or delivery target. Those meanings require frame context, concept compatibility, effect boundaries, and later capability-reference law. `location` is therefore deferred rather than admitted loosely.

## Permanent boundaries

- semantic relation is not participant role;
- concept candidate is not role assignment;
- source span is not actor;
- grammatical position is not participant role;
- role identity is not occurrence assignment;
- role identity is not frame completion;
- role identity is not permission, proof, capability, route, invocation, action, memory authority, rendering, or delivery.

## Lifecycle and governance

Every admitted role preserves candidate ancestry and an explicit architecture-admission transition. The registry also provides governed schemas for dependencies, relationships, corrections, and conflicts. No live correction or conflict is invented by this slice; both active sets remain empty.

## Deferred implementation

Predicate-frame constraints remain Slice 38E work. Effect boundaries and capability-family references remain Slice 38F work. Occurrence-level predicate, role, and frame candidate proposal remains Slice 38G work. Disabled integration and Slice 38 closeout remain Slice 38H work.
