# Architecture decision log

The records below are **proposals** until reviewed and assigned ACCEPTED status. New ADRs should identify context, options, decision, evidence, consequences, date and owner.

| ADR | Topic | Current status | Proposed direction |
| --- | --- | --- | --- |
| ADR-001 | Harness integration | PROPOSED | adapter seam; select runtime via spike |
| ADR-002 | Orchestration | PROPOSED | Python state machine first, benchmark durable options |
| ADR-003 | Backend/runtime | PROPOSED | Python/FastAPI with isolated background worker |
| ADR-004 | Storage | PROPOSED | SQLite for demo, upgradeable to PostgreSQL |
| ADR-005 | Sandbox | PROPOSED | isolated ephemeral Docker workspace per run |
| ADR-006 | Agent organization | PROPOSED | eight specialized profiles, separate tool runners |
| ADR-007 | Gate authority | PROPOSED | deterministic policy outside model/harness |
| ADR-008 | User interface | OPEN | React versus Streamlit after UX sketch |
| ADR-009 | Repo output | OPEN | local patch/branch versus GitHub PR integration |
| ADR-010 | Auth/model/provider | OPEN | provider, credentials, roles and budget |
| ADR-011 | Licensing | OPEN | select project license with third-party obligations review |
| ADR-012 | Harness spike contract | PROPOSED — spike-only resolutions | [fixed synthetic repair scenario, local patch, external controls, evidence and preflight](13-HARNESS-SPIKE-CONTRACT.md); 14 scoped answers, no harness winner |

## ADR-012 scope and review

**Date:** 2026-10-27. **Accountable roles:** repository maintainer (acceptance), assigned spike operator (execution/evidence); no named assignment or approval is fabricated. The [full record](13-HARNESS-SPIKE-CONTRACT.md) contains context, alternatives, decisions, consequences, preflight, output requirements and reversal rules.

It resolves planning inputs for Milestone 1 only, effective when this PR is accepted. Related ADR-003/004/005/007/009/010 proposals are constrained for this experiment, not globally ACCEPTED. ADR-001 remains PROPOSED pending executable comparison; ADR-008 and productivity benchmarking are deferred; ADR-011 remains OPEN. Required implementation evidence in the decision process below still applies to infrastructure adoption. No spike execution or measured runtime/security success is claimed by ADR-012.

## Decision process

1. Create an issue/PR proposing the decision and its acceptance criteria.
2. Show at least one credible alternative and implementation consequences.
3. For infrastructure or harness decisions, attach an executable spike and measured evidence.
4. Approve a dated, versioned ADR; update dependent docs/contracts.
5. On reversal, add SUPERSEDED link rather than deleting prior rationale.

## Guardrails during discovery

Unresolved ADRs should not be quietly converted into implementation facts. A developer may prototype assumptions on a disposable branch, but production-directed changes require a documented decision. The public repository license is undecided; avoid assuming that third-party code can be copied or redistributed merely because it is public.
