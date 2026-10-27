# Security and trust boundaries

**Status:** Initial threat model proposal. Must be implemented and tested before executing untrusted code.

**Spike policy:** [ADR-012 S2–S6](13-HARNESS-SPIKE-CONTRACT.md) narrows this baseline: no app/test/repair egress, reviewed bootstrap only, trusted model access separated from execution, pinned dependencies/skills, no waivers, and synthetic-only inputs. Exact scanner thresholds, retention and preflight denial tests are specified there; this document does not itself establish that controls work.

## Threat surfaces

User-provided requirements, repositories, dependency install scripts, tool output, test artifacts, prompts, generated code, agents and third-party harness integrations are **untrusted inputs**. An instruction discovered inside source code or test output is data; it must not expand the agent's authority.

## Baseline controls

1. Run code/test tools in per-run containers with a non-root account, minimal privileges, capped CPU/memory/time, readonly base filesystem where possible, and a dedicated ephemeral writable worktree.
2. Disable network egress by default for code execution; allow specific package registries only under a reviewed policy. Don't mount Docker socket or host SSH keys in an agent workspace.
3. Scope Git tokens to the selected repository and minimum required operations; prefer short-lived credentials. Do not expose production secrets to generated code.
4. Separate orchestration/service credentials from sandbox environment. Redact secrets from stdout/stderr, prompts, event logs, artifacts, and exception traces.
5. Gate file operations to the worktree. Validate paths (including symlinks), allowed commands, dependency installs, and workspace cleanup.
6. Require a human approval for protected-branch writes, PR merging, release promotion, and any change that exceeds declared edit scope.
7. Normalize scanner findings and block readiness on unresolved critical/high issues under the default policy. Treat scanners as evidence producers, not proof of absolute security.
8. Preserve audit trail of actor, invocation, code revision, applied policy, decision, tool identity, and scanner version.

## Threat analysis

| Risk | Suggested mitigation | Verification |
| --- | --- | --- |
| Prompt injection in repo/tool output | Treat external text as data; constrained tool capabilities and structured outputs | Inject hostile instructions into fixture files and confirm no privilege escalation |
| Arbitrary code execution escapes sandbox | No host mounts, reduced capabilities, egress control, resource limits | Attempt prohibited filesystem/network access in isolated test |
| Secret leakage | Secret broker, scoped ephemeral credentials, log redaction | Canary token in test, verify no exposure |
| Unauthorized merge | Role approval plus protected branch policy outside agents | Agent requests merge without approval; deny |
| Dependency/package compromise | Lock versions, audit dependencies, restrict installation/network | Introduce flagged dependency and verify finding |
| Forged validation claims | Gate evaluator reads signed/recorded tool results and revision refs | Agent writes “tests pass” with failed tool; gate remains failed |
| Stale approval or scan result | Hash-bound approvals, revision-sensitive result validity | Change code after approval/scan; gate invalidates |

## Disclosure and operations

No confidential source materials or credentials may enter this public repository. Configure local environment examples with placeholder values. Dependency/tool versions and licenses should be tracked in a future SBOM. Record policy exceptions with expiry, approver, and rationale. Treat readiness as advisory and human-controlled.
