# Requirements baseline and assumptions

**Status:** Proposed public interpretation, pending owner reconciliation. This document is an independently authored engineering specification, not a reproduction of any controlled brief.

## Requirement lifecycle

A request consists of a title, narrative, repository/ref, desired stack, constraints, priority, and optional attachments. Intake produces a stable requirement ID. The analyst records functional behavior, nonfunctional needs, rules, dependencies, ambiguities, assumptions, stories, and verifiable acceptance criteria. Material unanswered questions are represented as BLOCKED rather than invented facts.

## Functional capability inventory

The identifiers below are stable references for implementation planning. Their wording and acceptance tests may be refined by PR.

| ID | Capability | Verification expectation |
| --- | --- | --- |
| FR-01 | Requirement intake | Persist versioned feature request and unique ID |
| FR-02 | Requirement decomposition | Produce functional/nonfunctional needs and rules |
| FR-03 | Story and criterion generation | Each story has measurable criteria IDs |
| FR-04 | Ambiguity detection | Open questions and assumptions are visible and actionable |
| FR-05 | Technical design | Generate components, API/data contracts, error and security considerations |
| FR-06 | Implementation | Write proposed code only against approved design in isolated workspace |
| FR-07 | Test authoring | Link positive, negative, boundary, and authorization cases to criteria |
| FR-08 | Test execution | Capture command, environment, exit status, and test results |
| FR-09 | AI code review | Findings contain severity, location, evidence, and fix suggestion |
| FR-10 | Static analysis | Execute configured deterministic analysis and retain reports |
| FR-11 | Security validation | Execute configured security checks and normalize severity |
| FR-12 | Remediation | Propose/apply bounded patch linked to triggering finding |
| FR-13 | Revalidation | Re-run impacted and mandatory checks after each patch |
| FR-14 | Traceability | Link request, story, criterion, design, code, tests, and results |
| FR-15 | Quality gates | Programmatic state transitions enforce required controls |
| FR-16 | Release assessment | Produce READY / CONDITIONAL / MANUAL REVIEW / NOT READY with evidence |
| FR-17 | Human control | Required approvals are attributed, versioned, and checked |
| FR-18 | Observability | Store agent/tool events, outcomes, durations, and failures |

## Nonfunctional requirements, currently proposed

- **Security:** no untrusted generated code runs directly on the orchestrator host; no plaintext credentials in logs or generated artifacts.
- **Auditability:** every state transition is attributable to policy, operator, or tool evidence. Evidence references exact artifact versions.
- **Reliability:** resumable after restart at an approval boundary; idempotent externally visible operations; bounded retries and timeouts.
- **Isolation:** workspace and credentials scoped to run; parallel runs must not see each other's files or secrets.
- **Extensibility:** replace harness/model without rewriting artifact schema or quality policy.
- **Performance:** capture latency, token use, and execution expense per run; no numerical SLA until benchmarked.
- **Portability:** local Docker deployment first; external services optional through adapters.
- **Usability:** show blockers, pending approvals, and next permitted actions within one run view.

## Acceptance criterion rules

Each acceptance criterion has: ID, requirement_id, testable statement, verification method, priority, and lifecycle status. Statements use explicit input, action, observable outcome, and negative case when applicable. Generated criteria are proposals pending clarification/approval. An implementation or release cannot satisfy a criterion solely because an LLM says it is satisfied.

## Quality gate examples

- Requirements gate requires testable criteria, explicit ambiguity disposition, and a documented NFR review.
- Design gate requires version-matched human approval before code generation.
- Code/test/security gates require successful deterministic checks and no blocking findings.
- Traceability gate requires every mandatory criterion to have at least one executed test with recorded result.
- Release gate requires prerequisite gates and final authorization.

See [workflow policy](04-WORKFLOW-GATES.md) for proposed transitions and exact blocking behavior.

## Requirement decisions and remaining scope

The [ADR-012 spike contract](13-HARNESS-SPIKE-CONTRACT.md) proposes bounded answers for Milestone 1, effective on maintainer acceptance; it does not finalize the entire MVP:

1. Existing synthetic repository repair only; broader intake/greenfield support deferred.
2. Python 3.12/FastAPI/Pydantic/SQLite target, exact versions pinned at preflight.
3. Fixture OpenAPI defines responses and is validated by a deterministic test; generalized spec generation is later work.
4. 100% mandatory AC-to-executed-passing-test mapping; no numeric code-coverage threshold.
5. No conditional releases/waivers in spike; visible nonblocking residual findings follow S3, dependency vulnerabilities always block.
6. Reproducible patch plus base/result hashes; no remote Git writes by coding agents.
7. One named human can hold separate recorded roles; agents cannot approve; design and final evidence approvals are hash-bound.
8. No sandbox egress; reviewed bootstrap and trusted model access are separate.

Every original question and its follow-up remains tracked in the [clarification register](11-QUESTIONS.md).
