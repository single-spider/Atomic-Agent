# Atomic-Agent

**A harness-based, multi-agent SDLC engineering copilot.**

Atomic-Agent is an **experimental local SDLC control-plane MVP** with durable requirement/design/code artifacts, eight typed agent roles, human approvals, deterministic release gates, traceability and a browser dashboard. A frozen synthetic Python API fixture exercises failure, reference remediation and real Docker validation. The project **does not yet execute a live coding harness** or claim full autonomous SDLC/release readiness.

## Design direction

Reuse an existing coding-agent harness for model/tool execution, workspace interaction, and code edits. Build Atomic-Agent's differentiating layer for **durable SDLC orchestration, typed artifacts, deterministic quality gates, human approval, and end-to-end traceability**. The specific harness is **not selected**; compare candidates through an executable spike first.

## Documentation

Start here in order:

1. [Project charter](docs/00-CHARTER.md): goals, users, boundaries, principles.
2. [Requirements baseline](docs/01-REQUIREMENTS.md): capability IDs, quality attributes, assumptions.
3. [Architecture](docs/02-ARCHITECTURE.md): components, ownership boundaries, integration seams.
4. [Agent contracts](docs/03-AGENTS.md): responsibilities, input/output, permissions.
5. [Workflow and quality gates](docs/04-WORKFLOW-GATES.md): transitions, failure handling, approvals.
6. [Harness evaluation](docs/05-HARNESS-DECISION.md): candidates, selection rubric, spike plan.
7. [Artifacts and traceability](docs/06-ARTIFACTS.md): records, linkage, versioning, audit.
8. [Security model](docs/07-SECURITY.md): sandbox, secrets, scans, trust boundaries.
9. [MVP and PR roadmap](docs/08-MVP-ROADMAP.md): sequencing and scope control.
10. [Demo and acceptance](docs/09-DEMO-ACCEPTANCE.md): reproducible end-to-end scenario.
11. [Architecture decisions](docs/10-DECISIONS.md): proposals and decision process.
12. [Open questions](docs/11-QUESTIONS.md): decisions that require explicit resolution.
13. [Testing and observability](docs/12-TESTING-OBSERVABILITY.md): platform tests and run evidence.
14. [Contributing](CONTRIBUTING.md): branch, review, and merge expectations.
15. [Harness spike contract / ADR-012](docs/13-HARNESS-SPIKE-CONTRACT.md): scoped decisions, fixture, controls, preflight and comparison evidence.
16. [Fixture implementation](docs/14-SPIKE-FIXTURE.md) and [control plane](docs/15-CONTROL-PLANE.md).
17. [Agent roles and dashboard](docs/16-AGENT-ORCHESTRATION.md).
18. [Docker boundary probes](docs/17-SANDBOX-PROBES.md) and [synthetic walkthrough](docs/18-OFFLINE-WALKTHROUGH.md).
19. [Traceability rules](docs/19-TRACEABILITY.md) and [current MVP status](docs/20-MVP-STATUS.md).

16. [Executable harness fixture and preflight notes](docs/14-SPIKE-FIXTURE.md): synthetic defect, frozen tests, local policy contract checks.

## Quick start

For local developer verification (Python 3.12+), install test dependencies and start the API:

```bash
python -m pip install -e '.[test]'
python -m pytest -q tests/unit tests/integration
python scripts/check_frozen.py
python scripts/check_baseline.py
export ATOMIC_OPERATOR_ID=local-reviewer
export ATOMIC_OPERATOR_TOKEN='replace-with-a-random-local-token'
uvicorn atomic_agent.api:app --host 127.0.0.1 --port 8000
```

Open http://127.0.0.1:8000 to use the dashboard. Keep this experimental single-operator API on localhost. For a real-container synthetic demonstration, see [offline walkthrough](docs/18-OFFLINE-WALKTHROUGH.md) and the GitHub Actions Docker job.

## What is implemented

- Versioned SQLite workflow, artifacts, approval gates and event timeline.
- Human-reviewed criterion-to-code links, mandatory test/security evidence policy and release recommendation.
- Eight agent role contracts, a replaceable harness interface and a **test-only** deterministic fixture adapter.
- Restricted Docker validation commands and CI denial probes for the synthetic FastAPI fixture.
- Known synthetic authorization repair with actual regression testing and a deliberately blocked release when a trusted dependency audit is absent.

[Implementation status and blocking dependencies](docs/20-MVP-STATUS.md) identifies what remains for live end-to-end development. These capabilities are under active development.

## Current status

- Documentation baseline: merged, with new executable code and versioned design decisions.
- Harness selection: **open**; benchmark candidates before adopting one.
- Spike planning: **14 scoped resolutions proposed** in ADR-012; runtime selection, UI, productivity baseline and project licensing have explicit remaining dispositions. Exact provider/version pins and execution authorization remain preflight requirements.
- Harness fixture: **local synthetic baseline with deliberate AC-003 defect** and static policy checks in a proposed implementation PR; no live harness evaluation, isolation enforcement, or runnable SDLC product yet.
- Local backend, dashboard, persistence and synthetic validation: **implemented as experimental MVP**. End-to-end live model execution remains unimplemented.
- Production deployment: **out of scope** for the initial demo.

## Public repository and source handling

This repository contains independently authored architecture and product planning. Do **not** commit confidential/internal challenge materials, customer data, credentials, or third-party source documents without redistribution approval. Requirement IDs in the docs are planning references and must be reconciled with any controlled source materials by an authorized owner.

## Contribution workflow

Use a focused feature branch and pull request per milestone. Record evidence, decisions, and remaining risks. An implementation PR should not be merged solely on an agent's assertion of correctness. See [CONTRIBUTING.md](CONTRIBUTING.md).
