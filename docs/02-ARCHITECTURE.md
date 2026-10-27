# Proposed system architecture

**Status:** Design proposal, not a finalized technology decision.

## Layered view

    Browser / CLI
        |
        v
    API and authentication
        |
        v
    SDLC control plane (durable workflow and policy engine)
        |            |                |
        |            |                +--> Artifact / evidence store
        |            +--> Approval / notification service
        v
    Agent dispatch + typed contracts
        |
        v
    Harness adapter (replaceable)
        |
        +--> Coding runtime + sandboxed workspace + Git
        +--> Model tools and skills
        +--> Test / static / security tool runners
        |
        v
    Normalized evidence --> policy evaluator --> run status / recommendation

## Ownership boundaries

| Component | Must own | Must not own |
| --- | --- | --- |
| API/UI | intake, display, approve/reject actions | authoritative gate pass/fail inference |
| Orchestrator | transition rules, dispatch, retries, cancellation, approvals | low-level model prompt loop |
| Agent definitions | task-specific reasoning, output proposals, tool requests | overrides of gate policy |
| Harness adapter | launch/stop sessions, tool invocation, workspace, event stream | business requirement truth or release approval |
| Tool runners | bounded commands, deterministic exit/result reports | LLM interpretation of result |
| Evidence store | immutable result records, version refs, audit | editing past results in place |
| Gate evaluator | deterministic policy checks and reason codes | generating missing evidence |
| Release agent | readable recommendation and residual-risk narrative | unilateral release authorization |

## Adapter seams

The control plane should depend on a small harness interface:

- create_session(run_id, workspace_id, agent_profile, model_config) -> session_id
- execute(session_id, task, artifact_refs, limits) -> invocation_id
- stream_events(invocation_id) -> normalized event stream
- cancel(invocation_id) -> outcome
- collect_changes(session_id) -> commit/diff/modified file references
- close_session(session_id) -> cleanup result

Adapter implementations must translate native events and exceptions into common statuses: COMPLETED, FAILED, TIMED_OUT, CANCELLED, POLICY_DENIED. A harness must not be trusted to supply final gate status.

## Data and control flow

1. Intake creates a versioned run and feature record.
2. Analysis agent proposes requirement artifacts.
3. Clarifications/requirements approval are handled by control plane.
4. Design agent proposes an architecture and API/data artifacts.
5. Human approves a specific design version.
6. Coding agent executes with scoped write permissions inside a sandbox.
7. Test-generation agent writes tests linked to acceptance criteria.
8. Deterministic build/test/static/security tools run with captured evidence; applicable checks may run concurrently.
9. Review agent emits structured findings; policy synthesizes blocking issues.
10. Remediation agent receives selected findings and a bounded repair budget. Any modification invalidates affected prior checks.
11. Revalidation, traceability checks, readiness assessment, and final human approval close the run.

## Durable run state

Persist run_id, stage, status, input/artifact version IDs, assigned workspace, approval requests, gate decisions, invocation IDs, and timestamps. Use append-only events for replay and a materialized current-state projection for dashboard reads. A worker crash must not silently mark a stage complete.

## Suggested runtime composition

- Python/FastAPI for the API and orchestrator facade; a background worker for potentially long agent executions.
- SQLite for local development, a migration path to PostgreSQL.
- Docker sandbox per run for tests/builds, with resource and egress restrictions.
- Harness selected by the spike in [harness evaluation](05-HARNESS-DECISION.md).
- Configurable scanners (e.g. Ruff, Bandit, dependency audit) behind tool-runner contracts.
- React or Streamlit for a simple evidence-first dashboard, decision pending.

## System invariants

- Each run has one active mutable worktree version; saved artifacts are immutable versioned snapshots.
- A human approval grants permission for a hash/version, not all future changes.
- Mandatory gate evidence must match the latest code revision and policy version.
- No privileged token or production secret is available to generated code by default.
- Paused and failed steps remain inspectable and can be explicitly resumed.

## Design trade-offs

A simple custom state machine may suffice for a small demo. LangGraph or another durable orchestrator becomes useful if checkpointing, fan-out, human interrupts, and resume behavior justify its complexity. Decide through a prototype, not preference. Choose local single-user first unless authentication/multi-tenant use is required by project evaluation.

See [artifacts](06-ARTIFACTS.md) and [workflow](04-WORKFLOW-GATES.md) for contracts.
