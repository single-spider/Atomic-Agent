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

## Decision process

1. Create an issue/PR proposing the decision and its acceptance criteria.
2. Show at least one credible alternative and implementation consequences.
3. For infrastructure or harness decisions, attach an executable spike and measured evidence.
4. Approve a dated, versioned ADR; update dependent docs/contracts.
5. On reversal, add SUPERSEDED link rather than deleting prior rationale.

## Guardrails during discovery

Unresolved ADRs should not be quietly converted into implementation facts. A developer may prototype assumptions on a disposable branch, but production-directed changes require a documented decision. The public repository license is undecided; avoid assuming that third-party code can be copied or redistributed merely because it is public.
