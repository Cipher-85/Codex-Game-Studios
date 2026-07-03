# Codex Conversion Review Phase Plan

Purpose: review `PLAN.md`, verify upstream `Donchitos/Claude-Code-Game-Studios`, and produce a Codex-native implementation plan without exceeding the context window.

## Phase 1 - Upstream Inventory

Status: complete in this pass.

Inputs:
- Local GLM plan: `PLAN.md` (scope skim only; full critique deferred)
- Upstream source: shallow clone of `https://github.com/Donchitos/Claude-Code-Game-Studios`

Outputs:
- `docs/codex-conversion/upstream-inventory.md`
- `docs/codex-conversion/session-summary.md`

## Phase 2 - GLM Plan Review and Codex Mechanism Verification

Goal: read `PLAN.md` in bounded sections, verify current Codex-native mechanisms from local Codex docs/tools where possible, and write the executive verdict plus critical corrections.

Outputs:
- `docs/codex-conversion/glm-plan-review.md`
- initial `docs/codex-conversion/codex-mapping-matrix.md`
- updated `docs/codex-conversion/session-summary.md`

## Phase 3 - Corrected Architecture and Full Mapping Matrix

Goal: define the target Codex layout, coexistence boundaries, and a row-by-row mapping for every upstream component category.

Outputs:
- `docs/codex-conversion/corrected-architecture.md`
- completed `docs/codex-conversion/codex-mapping-matrix.md`
- updated `docs/codex-conversion/risk-register.md`

## Phase 4 - Validation Suite and Risk Register

Goal: design executable automated checks for inventory completeness, no `.claude/` dependency, hook/config validity, skill metadata validity, coexistence, and sample workflow smoke tests.

Outputs:
- `docs/codex-conversion/validation-suite.md`
- completed `docs/codex-conversion/risk-register.md`
- updated `docs/codex-conversion/session-summary.md`

## Phase 5 - Final Executable Implementation Plan

Goal: convert the corrected architecture, mapping matrix, and validation suite into an implementation plan that Codex GPT-5.5 can execute task-by-task.

Outputs:
- `docs/codex-conversion/implementation-plan.md`
- final pass updates to all review artifacts
- updated `docs/codex-conversion/session-summary.md`

