# Harness selection: decision pending

**Status:** Proposed evaluation, no winner selected.

**Experiment inputs:** [ADR-012 / spike contract](13-HARNESS-SPIKE-CONTRACT.md) resolves the scope and control ambiguities in the [register](11-QUESTIONS.md). Once accepted, apply it before running candidates; it does not decide the winner or prove any runtime safe.

## Decision statement

Select an open-source harness/runtime for model interaction, tool calls, coding workspaces, and agent execution without turning Atomic-Agent's gate policy or artifact system into harness-specific code. Choose by a reproducible spike and record an ADR.

## Candidates

| Candidate | Hypothesis to test | Potential limitation |
| --- | --- | --- |
| [DeepSeek Harness](https://github.com/deepseek-ai/deepseek-harness) | Agent runtime and plugin model may suit specialized SDLC roles | Verify SDK stability, sandbox isolation, extensibility, and release maturity |
| [OpenHands Software Agent SDK](https://github.com/OpenHands/software-agent-sdk) | Embeddable coding agent with workspace/tool support may simplify Python integration | Verify event/control interfaces, operational burden, compatibility |
| [Google Research Harness²](https://github.com/google-research/harness2) | Useful experiments for optimizing skills/prompts/subagent setup | Focused on harness optimization; likely complementary rather than core application runtime |
| Custom small adapter + existing command-based coding CLI | Baseline to estimate lowest viable integration cost | Might require more lifecycle/session management |

Repositories are research links, not endorsements or integration commitments. Confirm licenses, versions, maintenance, and security posture again at implementation time.

For the first comparison, preflight DeepSeek Harness and OpenHands Software Agent SDK. Retain Harness² as a complementary optimization study; document any fallback to a command-based adapter. Exact revision/license/model compatibility and enforcement controls must be checked before execution. No comparable setup or no eligible runtime is a valid no-winner result, not permission to weaken policy.

## Evaluation criteria (100-point proposal)

- 20: controllable execution, typed/tool APIs, resumable/cancellable sessions
- 20: isolated workspace, scoped permissions, network restrictions, secret safety
- 15: integration with Python backend and custom agent profiles/skills
- 15: deterministic event/trace collection, logs, costs, intermediate results
- 10: reliable code edits/tests/Git diff extraction
- 10: licensing, documentation, maintenance, deployment footprint
- 10: model/provider flexibility and latency/cost

Score 0–5 on each category, calculate weighted score. Minimum blockers regardless of score: isolation feasible, inspectable tool calls, clean cancellation, compliance with license, and ability to impose human approvals **externally**.

## Required spike

Use the existing synthetic ownership-repair fixture, frozen golden tests, local patch output, model/budget manifest and offline app sandbox in ADR-012. The headless spike driver need only exercise the approval/validation boundary, not implement the full product workflow or dashboard.

On identical fixture codebase and feature request, for each eligible candidate:

1. Create isolated session and inject one specialized developer skill.
2. Generate a change and inspect modified files/diff.
3. Interrupt/cancel an execution and record its status.
4. Execute a deterministic test command with retained exit code/log.
5. Enforce an external deny rule (e.g. prohibit writing outside workspace).
6. Run an intentionally failing test, feed output into remediation, rerun.
7. Export model/tool/step events and measure time, cost, and environment setup complexity.
8. Verify that an orchestrator-controlled approval pause cannot be bypassed by agent text.

Record exact version, configuration, model, scenario, outcomes, measurements, failures, and reproduction steps.

Completion also requires all final mandatory checks, patch reapplication on a clean base, 100% AC-to-passing-test evidence, external budget/approval/path/egress/cancel probes and reviewed redacted exports per ADR-012. Unexecuted checks cannot earn scores or be reported as passing. Apply hard blockers before weighted scoring; one run per candidate substantiates feasibility only, not productivity gains.

## Decision outcome template

- Selected runtime and version:
- Alternative(s) rejected and why:
- Architectural impact and required adapters:
- Security review:
- Measured scores:
- Known risks and rollback strategy:
- Owner, date, and decision status:

Until this form is completed, harness-dependent implementation is exploratory.
