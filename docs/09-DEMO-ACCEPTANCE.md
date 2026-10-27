# MVP demonstration and acceptance plan

**Status:** Proposed reproducible evaluation fixture.

## Reference scenario

A customer-profile API allows an authenticated customer to update permitted contact fields. It validates required field formats, prevents updates to another customer's profile, records an audit entry, and returns documented success/error responses.

This is a **new public demo scenario description**. Business-specific values below are assumptions to approve before building; they do not purport to reproduce private requirements.

## Proposed example criteria

- **AC-001:** authenticated owner updates an allowed contact field, receives success response, stored profile reflects change.
- **AC-002:** unauthenticated caller is rejected with the configured authentication error.
- **AC-003:** authenticated caller cannot update another customer's profile; storage is unchanged.
- **AC-004:** invalid email/phone payload is rejected with a documented validation error; no partial update.
- **AC-005:** successful change generates an audit record with actor, profile, changed fields and timestamp, without logging contact field values.
- **AC-006:** unexpected data-store failure returns a bounded server error without stack trace or secrets in response.

**Milestone 1 fixture decisions:** [ADR-012 S1](13-HARNESS-SPIKE-CONTRACT.md#s1--scenario-and-reference-stack-q-02-q-03-q-05) fixes the path, optional fields with at least one supplied, validation/error responses, SQLite storage, atomic value-free audit and synthetic test-only identities. S6 fixes spike evidence retention; fixture data is ephemeral. These are experiment decisions, not a production authentication/business-data retention policy.

The spike starts with this existing synthetic API and an intentional AC-003 failure, then exports a verified repair patch with frozen tests. It does not need the entire ten-step product UI/workflow below. All six ACs still require real final passing evidence. Full intake/decomposition, generated-test quality, durable workflow and dashboard acceptance remain later milestones.

## Demo sequence

1. Submit one feature request. Show structured story/criteria and highlighted ambiguities.
2. Answer a clarification and approve a specific design hash.
3. Dispatch coding task to selected harness with scoped workspace permissions.
4. Generate tests mapped to AC-001 through AC-006.
5. Deliberately introduce a missing ownership check in a fixture or generated change.
6. Run Pytest and show AC-003 failing; run static/security tools and capture results.
7. Invoke defect resolver with failure evidence and produce a narrow patch.
8. Rerun mandatory validation on the new revision, show stale evidence invalidation.
9. Inspect traceability graph and release gate decisions; require final reviewer approval.
10. Export report containing revision, findings, tool results, approval events, and decision.

Do not hard-code scanner success or fabricate failing tests. The pipeline must execute actual commands in a sandbox.

## Measurable MVP acceptance

| ID | Test | Pass condition |
| --- | --- | --- |
| AT-01 | Structured intake | requirement/story/criterion IDs persist across restart |
| AT-02 | Ambiguity control | material unanswered question blocks code dispatch |
| AT-03 | Human design approval | rejected/changed design cannot be implemented under stale approval |
| AT-04 | Harness runtime | code diff produced in isolated workspace and events captured |
| AT-05 | Deterministic tools | actual pytest result shown with command, revision and exit code |
| AT-06 | Security gate | a critical/high finding or missing mandatory check blocks READY |
| AT-07 | Bounded repair | failed test triggers recorded change, retry cap, and revalidation |
| AT-08 | Traceability | AC-003 maps to test, code revision, execution result and finding |
| AT-09 | Final release state | recommendation derives from gate evidence and required approvals |
| AT-10 | Isolation/audit | unauthorized filesystem/network attempts denied and logged |

## Demo evidence bundle

Store an anonymized run JSON export, redacted event timeline, test report, scanner report, before/after diff, trace graph, release assessment, and human approval IDs. Capture timing and cost but do not claim quantified productivity improvement without a baseline comparison.

## Baseline comparison (optional)

Run identical feature manually or with a single coding assistant, capturing elapsed time, failures, criteria coverage, reviewer effort, and cost. Mark uncontrolled comparisons as indicative, not causal proof.
