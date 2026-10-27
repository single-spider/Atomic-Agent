# Artifact schema and requirement traceability

**Status:** Logical data-model proposal, independent of storage engine.

## Core entities

| Record | Required fields |
| --- | --- |
| FeatureRequest | requirement_id, title, description, requester, repository_ref, version, created_at |
| Story | story_id, requirement_id, text, version, status |
| AcceptanceCriterion | ac_id, story_id, statement, verification_method, priority, version |
| Assumption | assumption_id, source_ref, text, impact, decision, approver_ref |
| TechnicalDesign | design_id, requirement_version, API/data/component refs, content_hash, approval_ref |
| CodeRevision | revision_id, repository, base_commit, commit_or_diff_ref, changed_paths, workspace_ref |
| TestCase | test_id, linked_ac_ids, path, test_type, code_revision |
| ToolRun | tool_run_id, kind, command_template, image_digest, revision_id, status, exit_code, logs_ref |
| Finding | finding_id, severity, source_tool_or_agent, evidence_ref, revision_id, component, status |
| Remediation | remediation_id, finding_ids, before_revision, after_revision, attempt, outcome |
| Approval | approval_id, actor, role, object_type, object_hash, decision, timestamp |
| GateResult | gate_id, policy_version, revision_id, status, evidence_ids, reasons |
| ReleaseAssessment | assessment_id, revision_id, status, gate_refs, blockers, approval_refs |
| RunEvent | event_id, run_id, type, actor, payload_ref, time, idempotency_key |

All records have immutable IDs, schema_version, timestamps and run_id where relevant. Large logs/code live in a content-addressed artifact storage area, referenced from the database.

## Traceability graph

    Requirement -> Story -> Acceptance Criterion
                      |             |
                      v             v
                 Design Version -> Code Revision -> Test Case -> ToolRun Result
                                        |                |
                                        +--> Findings --+--> Remediation
                                        |
                                        +--> Gate Results -> Release Assessment

Use an explicit join/edge table with from_type, from_id, to_type, to_id, relation_type, created_at. Every link points to a specific artifact **version**, not a mutable latest pointer.

## Example trace

    REQ-001 -> STORY-001 -> AC-002
    AC-002 -> TEST-authorization-01
    TEST-authorization-01 -> RUN-pytest-008 (PASS, revision abc123)
    AC-002 -> CODE-REV-abc123 (api/profile.py)
    CODE-REV-abc123 -> GATE-test-009

Illustrative values only. A readiness check queries the graph and verifies the selected revision is current.

## Versioning and policy

- AI outputs are proposals until required approvals.
- On code revision change, mark all revision-dependent validations stale. Preserve their historical records.
- Approval references a content hash; mutations require renewed approval when policy says so.
- Findings and waivers are durable objects with state history.
- Artifact retention, privacy, and export rules require explicit decisions before multi-user usage.

## Storage/API guidance

Support endpoints for create run; read run/event timeline; list artifact versions; retrieve trace links; submit decision; read gate evidence; cancel/resume run. Mutations use optimistic version checking and idempotency keys to avoid duplicate dispatch.
