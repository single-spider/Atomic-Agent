# Incremental MVP and pull-request roadmap

**Status:** Proposed order; avoid committing to calendar dates before the harness spike.

## Milestone 0 — Documentation baseline

**PR 001 (this PR):** charter, requirements, architecture proposal, agent contracts, workflow/gates, harness evaluation, artifact schema, security, demo, observability and contributor process.

Exit: documentation is internally consistent; open decisions are visible; no implementation claims; maintainer review completed.

## Milestone 1 — Harness spike

**PR 002:** prove adapter feasibility on one local reference repository using two candidate runtimes. Include reproducible scripts, evaluation scores and an ADR selecting a harness or explaining no winner.

Prerequisite: accept [ADR-012 / spike contract](13-HARNESS-SPIKE-CONTRACT.md), assign operator and complete its model/version/license/security preflight. See the [18-question disposition](11-QUESTIONS.md); UI and productivity claims do not block this milestone, and no provider/spending approval is inferred.

Exit: report all eight harness evaluation steps and ADR-012 hard-blocker outcomes for two candidates (or documented ineligibility), patch reapplication, real AC-003 failure/repair, all final mandatory checks and 100% AC mapping, cancellation, external approval/permission/budget enforcement, and redacted reproducible evidence. Record winner or no winner in ADR-001. Experiment completion is not candidate success or full MVP acceptance; no measured results exist in this planning PR.

## Milestone 2 — Run/artifact/control-plane skeleton

**PR 003:** FastAPI intake, stable IDs, state machine, SQLite persistence/migrations, event log, adapter interface, and local API tests.

Exit: a workflow can checkpoint, pause/resume, reject illegal transitions and survive simulated interruption.

## Milestone 3 — Analyst and design approval

**PR 004:** versioned analyst/design outputs, schema validation, ambiguity handling, explicit assumptions, human design approval with revision hash.

Exit: ambiguous intake blocks; approved design version is required for code dispatch.

## Milestone 4 — Code, tests, and deterministic tools

**PR 005:** harness coding session, Git diff extraction, test generation, Pytest execution, Ruff/build checks, scanner adapter.

Exit: true tool exit codes and parsed reports linked to the precise revision; failed gate blocks progress.

## Milestone 5 — Review and bounded remediation

**PR 006:** code/security review roles, normalized findings, localized remediation, revalidation/invalidation logic.

Exit: intentionally induced defect is found, patched, and all mandatory checks rerun on final revision; repair budget enforced.

## Milestone 6 — Traceability, dashboard and release report

**PR 007:** trace graph, gate evidence API, run timeline, approval interactions, release categories, exportable summary.

Exit: an evaluator can follow one requirement through artifacts/code/tests/scans/fix and decision.

## Milestone 7 — Packaging and reproducibility

**PR 008:** Docker setup, CI, platform tests, setup guide, fixture demo, scripts, known limitations, security review.

Exit: clean checkout reproduces controlled demo with documented environment, no secrets committed.

## Prioritization

**P0:** one working end-to-end path, deterministic gates, approval, traceability, sandbox, remediation loop.
**P1:** richer dashboard, provider variants, detailed observability and role-specific UI.
**P2:** multi-language, organization policy packs, distributed workers, recursive harness optimization.

## PR exit template

Each PR should state objective, changed contracts, test evidence, risk/security impact, rollout/rollback, docs updated, and follow-up issues. No PR is merged merely because its author reports success.
