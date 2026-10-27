# Project charter

**Status:** Proposed public baseline. **Product:** Atomic-Agent. **Stage:** Architecture discovery.

## Vision

Enable a developer to submit a bounded application feature request and obtain a reviewable implementation together with evidence connecting the original intent to code, tests, security checks, corrections, and a release recommendation.

## Core product promise

Given a feature request and selected repository, Atomic-Agent can: clarify intent; ask for missing decisions; generate stories and measurable acceptance criteria; propose a design; pause for approval; instruct a coding harness to implement in an isolated workspace; generate and execute tests; run scanners; review findings; attempt bounded remediation; revalidate; assemble a release report; and request a final human decision.

The output is a **proposed change** plus recorded evidence, never an unconditional assertion of production safety.

## Users and roles

- **Requester:** supplies the feature, constraints, and clarifications.
- **Developer/reviewer:** approves design or code changes, inspects evidence, and decides whether to merge.
- **Maintainer/admin:** configures supported execution environments, models, repositories, quality policy, and access controls.
- **Read-only observer:** views progress and audit records without executing or modifying code.

MVP can combine roles within one local authenticated operator, but must preserve the underlying distinction in records.

## Scope boundaries

**In scope:** one repository and one feature per run; a reference application stack; structured artifacts; bounded agent delegation; isolated code/test execution; scanner integration; traceability; approval pauses; release recommendation; simple dashboard.

**Not in first MVP:** unattended production deployment; generalized autonomous product management; cross-repository monorepo refactors; supporting all languages; unlimited autonomous retries; infrastructure provisioning in customer accounts; compliance certification; agent self-modification in production.

## Architectural principles

1. **Harness-first:** reuse tested coding-agent mechanics through a replaceable adapter.
2. **Control plane owns policy:** the harness cannot waive mandatory gates or grant itself approvals.
3. **Evidence over prose:** statuses derive from stored tool results with timestamps and artifact versions.
4. **Human governance:** ambiguous material requirements and defined approval steps block forward motion.
5. **Explicit assumptions:** guesses are tracked as proposals, with rationale and approval status.
6. **Sandbox by default:** generated code is untrusted until independently inspected and executed in an isolated environment.
7. **Progressive disclosure:** dashboard summarizes, then drills into each artifact and tool log.
8. **Modularity:** agent prompts/skills evolve independently of workflow and data contracts.

## What success means

For the defined MVP scenario, a user can observe an entire run including at least one intentional test failure, corrective patch, re-run, and an evidence-backed recommendation. An auditor can navigate from a requirement ID to acceptance criteria, implementation change, test case, test result, scanner result, human approval, and final decision.

## Constraints and dependencies

- Model provider, budgets, hosting, credential strategy, and selected harness are **not decided**.
- Reference stack proposed: Python/FastAPI, Pytest, Ruff, a Python-focused security scanner, SQLite then PostgreSQL if needed, and Docker. Validate with a spike.
- Internal sponsor materials, if any, are separate controlled inputs and should not be copied into this public repository.
- Original scope should remain configurable as the project learns from hands-on evaluations.

## Explicit non-goal

Replacing human merge/release authority is not a project objective.
