# Atomic-Agent

**A harness-based, multi-agent SDLC engineering copilot.**

Atomic-Agent is a planned open-source application that takes a feature request through requirements analysis, technical design, implementation, testing, security review, remediation, traceability, and evidence-backed release assessment. The project is at its **documentation and architecture discovery** stage; no working SDLC engine is claimed yet.

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

16. [Executable harness fixture and preflight notes](docs/14-SPIKE-FIXTURE.md): synthetic defect, frozen tests, local policy contract checks.

## Current status

- Documentation baseline: **proposed**, subject to maintainer review.
- Harness selection: **open**; benchmark candidates before adopting one.
- Spike planning: **14 scoped resolutions proposed** in ADR-012; runtime selection, UI, productivity baseline and project licensing have explicit remaining dispositions. Exact provider/version pins and execution authorization remain preflight requirements.
- Harness fixture: **local synthetic baseline with deliberate AC-003 defect** and static policy checks in a proposed implementation PR; no live harness evaluation, isolation enforcement, or runnable SDLC product yet.
- MVP backend, UI, test tools, and storage: **proposed**, not yet implemented.
- Production deployment: **out of scope** for the initial demo.

## Public repository and source handling

This repository contains independently authored architecture and product planning. Do **not** commit confidential/internal challenge materials, customer data, credentials, or third-party source documents without redistribution approval. Requirement IDs in the docs are planning references and must be reconciled with any controlled source materials by an authorized owner.

## Contribution workflow

Use a focused feature branch and pull request per milestone. Record evidence, decisions, and remaining risks. An implementation PR should not be merged solely on an agent's assertion of correctness. See [CONTRIBUTING.md](CONTRIBUTING.md).
