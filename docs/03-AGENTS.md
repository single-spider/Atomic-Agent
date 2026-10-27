# Agent specifications and contracts

**Status:** Proposed contract-first design. Agents are configurations of an existing harness, with prompts/skills, tool allowlists, and versioned output schemas.

## Contract conventions

Each invocation is passed: run_id, task_id, stage, input_artifact_ids, approved_context_version, workspace_ref (if relevant), policy_version, tool allowlist, max_steps, timeout, cost budget, and idempotency key. Every response contains: schema_version, agent_role, input_version_refs, proposed_artifact_refs, findings, assumptions, unresolved_questions, and completion_status. Store prompts/skill versions alongside the invocation.

Return statuses: SUCCESS, NEEDS_CLARIFICATION, NEEDS_APPROVAL, FAILED, ABORTED. The orchestrator validates schema, references, and permissions before accepting results.

## Eight specialized roles

| Agent | Inputs | Expected outputs | Permission boundary |
| --- | --- | --- | --- |
| Business Analyst | feature request, constraints | stories, functional/NFR list, criteria, ambiguities | read intake; write proposal artifacts |
| Solution Architect | approved requirements, prior design context | component model, API/data contracts, risks, design decision proposals | read requirements; write design |
| Developer | approved design, repository, approved file scope | code patch/commit, implementation notes | read/write sandbox repo only |
| Test Engineer | criteria, design, code ref | unit/API/negative/boundary tests and AC mappings | write test files in sandbox |
| Code Reviewer | implementation diff, requirements, test outcomes | severity-ranked findings with evidence | read-only code and artifacts |
| Security Reviewer | code, threat model, scanner reports | security findings, compensating controls | read-only; invoke approved scanners |
| Defect Resolver | failing checks, review findings, current code | minimal patch, affected-component list, before/after explanation | scoped write in sandbox, capped attempts |
| Release Assurance | immutable gate results, approvals, residual risks | recommendation with evidence IDs and unresolved blockers | read-only, no ability to change gates |

The high-level proposal explicitly treats security as its own agent, while deterministic scanners remain independent tools.

## Example structured finding

    {
      "finding_id": "FIND-009",
      "category": "AUTHORIZATION",
      "severity": "HIGH",
      "component": "api/customer.py",
      "evidence_ref": "scan-run-04",
      "location": {"path": "api/customer.py", "line": 71},
      "recommendation": "Verify ownership before updating the record",
      "status": "OPEN"
    }

This is illustrative schema data, not a claim of any detected vulnerability.

## Skill composition

Skills should provide narrow domain knowledge and output constraints rather than entire workflow policy. Proposed skills: requirement-decomposition, acceptance-criteria-writing, api-contract-design, fastapi-implementation, pytest-generation, secure-code-review, defect-localization, release-evidence-summary.

Each skill needs: owner, version, target agents, input/output examples, tool requirements, failure cases, evaluation fixture, and prompt-injection defenses. The control plane decides dispatch and permission grants; agents may request capabilities but cannot self-escalate.

## Tool execution contracts

Tool invocations are separate evidence producers with command template, allowlisted arguments, container image digest, workspace revision, timeout, exit code, logs, and normalized findings. Test passing means a real runner returned success and results were parsed; an agent's statement that tests pass is never sufficient.

## Agent failure handling

If an agent outputs invalid schema, retry once with validation errors and bounded budget. If still invalid, mark FAILED and request intervention. If requirements conflict, produce NEEDS_CLARIFICATION. Code-writing agents cannot silently update the approved design. All patches are linked to an originating task or finding.

## Evaluation

Measure schema validity, missing-information detection, acceptance-criteria quality, edit locality, test usefulness, reviewer false-positive rate, remediator fix rate, and release recommendation correctness on fixture tasks. Results guide prompt changes; see [testing](12-TESTING-OBSERVABILITY.md).
