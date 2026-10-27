# Platform testing, evaluation, and observability

**Status:** Proposed system test strategy.

**Milestone 1:** [ADR-012](13-HARNESS-SPIKE-CONTRACT.md) defines the frozen synthetic repair fixture, six mandatory AC mappings, exact check/blocking policy, clean-base patch verification, external-control probes and evidence retention. Use reviewed golden tests for harness comparison; generated-test usefulness and the complete platform pyramid remain later product evaluations.

## Testing pyramid

- **Unit:** JSON/schema validation, requirement parsing helpers, ID linking, gate rule evaluation, severity normalization, state transition legality, retry budgets, hash-based approval invalidation.
- **Contract:** adapter event/status translation, tool-runner result parsing, persistence and approval API semantics.
- **Integration:** fake harness to simulate success/failure/cancel/timeouts, real Pytest/Ruff/scanner invocation inside a sandbox, crash/restart replay.
- **End-to-end:** reference customer-profile scenario with deliberate authorization bug, remediation loop, and traceability/export verification.
- **Adversarial:** hostile code comments/tool output, forbidden commands, poisoned dependency, secret canary, stale approval, tool output spoofing, uncontrolled retries.

## Golden fixtures

Maintain fixture repos with: uncomplicated passing feature; ambiguous requirement; invalid agent JSON; failing tests; security finding; remediation success; remediation exhaustion; scanner unavailable; approval rejection; and log containing injection attempt. Save expected gate states and mappings, not exact LLM prose.

## Agent assessment

Track per-role schema adherence, criterion specificity, missing-question detection, code/test usefulness, reviewer correctness and false positives, repair effectiveness, and release recommendation alignment with deterministic policy. Keep model/provider/version, prompt/skill revision, budgets, and fixture ID alongside results.

## Observability data

Each run emits correlated IDs: run_id, stage_id, invocation_id, tool_run_id, workspace_id, artifact_version, revision_id, trace_id. Capture timestamps, latency, stage transitions, model token/cost estimate if available, tool invocation metadata, exit status, failure class, redacted logs, findings, gate outcomes, approvals, and budget exhaustion.

Use structured event records as system-of-record. OpenTelemetry spans are an optional export and must never replace durable audit events.

## Dashboard views

**Overview:** runs by stage and readiness state, blocked count, coverage, test pass rate, security finding counts, quality gate distribution.

**Run detail:** request -> stories/criteria -> design/approval -> code/diff -> test cases/results -> scans/review -> defects/remediation -> revalidation -> release recommendation; include timeline and failures.

Metrics must be labeled accurately. "Coverage" should mean AC-to-test mapping coverage unless runtime code coverage is explicitly available.

## Exit criteria

A clean local checkout can execute automated platform tests and the fixture end-to-end. A run's release recommendation can be reproduced from stored policy and evidence. User can identify why any blocked gate failed without reading raw model transcripts.
