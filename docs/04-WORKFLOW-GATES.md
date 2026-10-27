# SDLC workflow and quality gate specification

**Status:** Proposed. The policy engine is deterministic and versioned.

**Milestone 1 overlay:** [ADR-012](13-HARNESS-SPIKE-CONTRACT.md) defines the spike's exact mandatory tools, 100% AC mapping, single-operator role records, bounded in-scope repairs and hash-bound approvals. No waivers/CONDITIONAL path is enabled in the spike. The workflow below remains the broader product proposal, not a requirement to implement every stage before comparing harnesses.

## States

    DRAFT -> ANALYZING -> REQUIREMENTS_REVIEW
          -> DESIGNING -> DESIGN_APPROVAL
          -> IMPLEMENTING -> TESTING
          -> VALIDATING -> REVIEWING
          -> [REMEDIATING -> REVALIDATING -> REVIEWING]*
          -> TRACEABILITY_CHECK -> READINESS_ASSESSMENT
          -> RELEASE_APPROVAL -> COMPLETE

Any active stage may move to FAILED or CANCELLED. Review states can move to BLOCKED/WAITING_FOR_HUMAN. Starred loop is capped by retry policy; on exhaustion, route to MANUAL_REVIEW or NOT_READY. The workflow must record every transition.

## Gate definitions

| Gate | Inputs | PASS only if | Fail response |
| --- | --- | --- | --- |
| G1 Requirement | latest request, criteria, NFR disposition | criteria testable; ambiguities resolved or explicitly approved; required NFRs considered | BLOCKED |
| G2 Design approval | approved requirement version, design hash, approval event | authorized person approves exact design version | WAITING_FOR_HUMAN |
| G3 Code quality | code revision, build/static results | build succeeds, mandatory analysis completed, blocking violations absent | REMEDIATE |
| G4 Test | criteria mappings, test execution | mandatory tests ran/passed; each mandatory criterion has test evidence | REMEDIATE |
| G5 Security | code revision, scanner outputs | mandatory checks completed; secrets exposure absent; no unresolved blocking finding | REMEDIATE or NOT_READY |
| G6 Traceability | graph of requirement to code/tests/results | each mandatory link is present and references current revisions | BLOCKED |
| G7 Release | all previous gates, blocking defect list, approvals | gates pass, blocking defects absent, final human decision recorded | WAITING_FOR_HUMAN or NOT_READY |

Policy must define severity-to-blocking mapping. Default proposed policy: CRITICAL/HIGH unresolved security issues block; failures to run a mandatory scanner fail closed; exceptions require recorded authorization and cannot silently become PASS.

## Failure and revalidation semantics

- Every code edit creates a new revision and invalidates stale build, test, and security evidence for that revision.
- Rerun targeted tests for diagnosis; before release recommendation, rerun every mandatory check on the final revision.
- Retries must be bounded by max_attempts, runtime, cost, and no-progress detection; proposed default is two remediation attempts per defect cluster, configurable.
- Review defects and deterministic failures enter one deduplicated finding registry. Findings have stable IDs and state transitions.
- A blocking failure cannot be overwritten by a favorable LLM interpretation.

## Human approval mechanics

Approval event includes approver identity, role, object_type, exact object_id+hash, decision, time, rationale, and policy version. Rejecting a design routes back to design or requirements. Updating an approved design invalidates the existing approval. Release approval is distinct from a readiness recommendation.

## Release recommendation enumeration

- **READY:** every mandatory gate passed; no blocking issues; required approvals recorded. The system may recommend merging, but merge is human-controlled.
- **CONDITIONAL:** no blocking findings under an explicitly defined waiver policy; residual low/medium issues and approver are recorded.
- **MANUAL REVIEW:** unresolved ambiguity, policy exception request, insufficient evidence, or an exhausted repair loop demands intervention.
- **NOT READY:** failed mandatory gates or unresolved unwaived blocking defects.

Recommendation payload contains status, policy_version, evaluated_revision, gate_results, blocking_finding_ids, residual_risks, approval_refs, timestamp, and readable reasoning.

## Workflow events

Required examples: RunCreated, StageStarted, AgentInvoked, ArtifactProduced, ToolCompleted, FindingOpened, PatchApplied, GateEvaluated, ApprovalRequested, ApprovalRecorded, StageCompleted, RunFailed, ReleaseAssessed. Events must support idempotency to prevent duplicate effects on retries.

## Parallelism

Independent review and deterministic scanners may run in parallel on the **same immutable revision**. A remediation patch creates a new revision and triggers a fresh validation group. Dispatch synchronization belongs to the orchestrator, not to a prompt.
