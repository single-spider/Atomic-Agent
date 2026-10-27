# Harness spike contract (ADR-012)

**Date:** 2026-10-27. **Status:** PROPOSED for maintainer review; normative for the spike once this PR is accepted. **Scope:** Milestone 1 only, not production policy or a claim of implemented controls.

**Accountability:** the repository maintainer accepts this contract and assigns a spike operator; the operator records configuration and evidence. No human approval, provider authorization, license grant, benchmark result, or harness selection is implied by this document.

## Decision and alternatives

Resolve experiment inputs before comparing runtimes. Use one synthetic existing-repository repair task, local patch output, a headless driver, external policy enforcement, and identical bounded model/tool settings. This exercises the adapter rather than building the whole SDLC product.

Greenfield generation adds scaffolding variance; PR output adds credentials and remote side effects; a dashboard adds no adapter feasibility evidence; per-candidate provider tuning confounds the comparison. Defer those alternatives. Full identity separation and waiver governance remain future product decisions, not implicit permissions.

This contract supplies spike-only resolutions for Q-02 through Q-10, Q-12 through Q-14, Q-17 and Q-18. Q-01 requires measured evidence; Q-11 and Q-15 are deferred; Q-16 remains a maintainer decision with a license preflight. See the [register](11-QUESTIONS.md) for each disposition.

## S1 — Scenario and reference stack (Q-02, Q-03, Q-05)

- Edit **one existing, independently authored synthetic fixture repository**. Greenfield generation and arbitrary customer repositories are not required for this spike; supporting them later requires a new scope decision.
- Target Python 3.12, FastAPI/Pydantic, SQLite, Pytest with HTTPX/TestClient, Ruff, Bandit and pip-audit. Pin exact Python patch, packages and transitive dependencies in the preflight manifest/lockfile. This is the target app stack, not a requirement that every harness use Python internally.
- Use the customer-profile scenario and AC-001 through AC-006 in the [demo plan](09-DEMO-ACCEPTANCE.md). Fixture design: `PATCH /profiles/{profile_id}`, optional email/phone with at least one supplied, unknown fields rejected; email validated by a locked email validator and phone by `^\+[1-9][0-9]{7,14}$`. Use seeded synthetic profiles and fixed, non-secret **test-only** bearer identities, not production authentication.
- Freeze responses in fixture OpenAPI and golden tests before evaluation: 200 updated profile, 401 missing/invalid identity, 403 another owner's profile, 404 missing profile, 422 invalid payload, 500 generic error for injected storage failure. Unauthorized, invalid and failed writes leave storage unchanged. Audit successful writes atomically with actor, profile ID, changed field names and UTC timestamp, never contact values. Validate OpenAPI through a deterministic fixture test.
- The starting fixture implements these behaviors except an intentionally missing ownership check. Record a real AC-003 failure before repair. The bounded feature request is to enforce profile ownership without regressions. Both candidates receive the same approved design, request, base commit, developer skill and failure evidence. Golden tests, lockfiles and runner/security configuration are read-only to the coding agent; only declared app source paths are writable.
- Export a UTF-8 Git patch plus base commit, resulting tree/content hash, changed paths and before/after evidence. A local disposable branch is an implementation detail, not the delivery contract. Verify the patch applies to a fresh base and reproduces final checks. **No remote push, PR creation, merge or deployment by the spike agent.** A human-reviewed PR containing spike scripts/report is separate from this generated-change output.

## S2 — Approval and authority (Q-04, Q-12, Q-13, Q-18)

- One named local operator may hold requester, design-approver and release-reviewer roles for the synthetic spike. Record roles separately; do not claim two-person approval or production identity assurance. Agents/harnesses can hold none of these approval roles.
- Require operator approval bound to the fixture design hash, edit scope and policy version **before coding dispatch**. Changed design/scope invalidates approval. Test rejected, absent and stale approval; agent text claiming approval cannot unblock dispatch.
- Within approved design/source scope, allow autonomous sandbox remediation, capped at **two repair attempts after the initial coding attempt**. Every patch references its triggering finding, old/new revision and attempt. Stop on repeated identical patch/failure, timeout, cancellation or exhausted budget; retain the failed outcome. No new approval per in-scope repair.
- Scope expansion, dependency changes, edits to golden tests/policy, or any design change stop dispatch and require a new hash-bound operator decision. Approval never substitutes for sandbox restrictions.
- **No waivers and no CONDITIONAL result in the spike.** A mandatory failed/missing/stale check blocks success; critical/high findings cannot be waived. Exception requests are MANUAL REVIEW, not PASS. Future conditional-release policy remains open.
- The control plane computes gates; Release Assurance may explain them. The operator records the final decision tied to the final code hash, gate bundle hash and policy version. A recommendation before that decision is awaiting approval, never a completed release. Only the human repository maintainer authorizes an eventual merge, separately from assessment. No merge credential is supplied to the agent.

## S3 — Deterministic evidence and blocking rules (Q-06, Q-07)

Run checks independently of agent prose with trusted runner configuration on the final immutable revision. Freeze versions, arguments, rules and severity mapping before the first candidate. Every run records command, image digest, tool version, code revision, timestamps, exit code, parsed report and redacted logs.

| Check | Required evidence | Blocking rule |
| --- | --- | --- |
| Build/import and Ruff | compile/import smoke test, `ruff check` report | build/import failure or any configured Ruff violation |
| Pytest | JUnit XML including OpenAPI and AC tests | nonzero exit, missing/malformed report, required test absent, skipped, xfailed or failed |
| Bandit | JSON app-source scan, all confidence levels | any HIGH finding; map HIGH/MEDIUM/LOW to identical normalized severities |
| Dependency audit | pip-audit JSON over complete locked target dependencies and pinned advisory snapshot or recorded query response | any known vulnerability; incomplete inventory, advisory data or audit |
| Secret check | pinned deterministic credential patterns plus synthetic-canary leak test on diff, exported artifacts and logs | detected credential or unredacted canary; fixture identities explicitly classified as non-secret |
| External review findings | structured finding with location, evidence and revision | unresolved CRITICAL/HIGH from any source, including authorization defects scanners miss |

Bandit MEDIUM/LOW findings are visible residual risks, not silent suppressions. Dependency vulnerabilities block even without severity metadata. Unknown severity/incomplete output blocks pending review. No rule disabling or new suppressions during evaluation. Pin and test the secret checker at preflight; this proves configured checks ran, not exhaustive secret detection.

Require **100% of mandatory AC-001 through AC-006** to map to at least one actually executed passing test on the final revision; all mandatory tests must pass. AC-003 includes another-owner denial and unchanged-storage assertions. Pre-reviewed golden tests, not model-authored assertions, determine success. Code line/branch coverage has **no numeric threshold** here and must not be presented as AC coverage.

Each edit invalidates prior build/test/security evidence. Targeted diagnostic reruns are allowed, but all mandatory checks rerun on final revision and after patch reapplication. Deliberate failing-test, missing-scanner, fake-pass and stale-evidence probes must keep gates failed. Experiment completion may include failed candidates; they cannot be described as passing the spike.

## S4 — Model, fairness and resource limits (Q-08)

Do not hard-code a paid provider or assume permission to send data or spend money. Before live calls the operator supplies and approves a manifest containing:

- Provider endpoint, immutable model revision where offered (otherwise model ID, date and alias limitation), decoding parameters/seed where supported, context limits and data-handling approval.
- Same provider/model, task, fixture, skill, tool policy and ceilings for both candidates; no extra native subagents, online skill discovery or hidden calls outside the manifest.
- **USD 5 per candidate, USD 10 total** ceilings including coding, repairs, cancellation probes and model-using retries; **20 minutes total wall time per candidate**, **10 minutes per invocation**, **30 tool/model steps per invocation**, **two repair attempts**.
- **10-second cancellation deadline**, including child tools. After the deadline forcibly stop the isolated process group/container and mark the probe failed if clean cancellation was not observed.
- Trusted control-plane cost accounting with pre-call reservation using configured prices and output-token limits. Deny calls whose worst-case reservation exceeds remaining budget. Unknown price/usage or unmetered native calls fail closed. Label estimates as estimates, not billed cost.

These ceilings are **not authorization to use credentials or incur charges**. Missing approved model configuration, rates, necessary credentials or tested external budget/cancel controls means BLOCKED before live execution. Provider keys stay in a trusted gateway/runtime, never in the app sandbox, prompts or artifacts. Fake-model contract tests need no paid calls but cannot establish comparative coding quality. Real local-model runs must follow the same manifest/control requirements; record zero API price where applicable and hardware usage separately.

Use two eligible runtimes from the [candidate list](05-HARNESS-DECISION.md), starting with DeepSeek Harness and OpenHands Software Agent SDK, subject to compatibility/license preflight. Harness² remains a complementary optimization study, not a necessary third runtime. A command-based adapter is a fallback only with a recorded reason a primary candidate is ineligible. Do not silently change model/permissions to make one candidate work. Without a common model/control setup report **no comparable winner**.

One controlled run per candidate is feasibility evidence, not statistical superiority or productivity improvement. Record all failed attempts and setup effort; apply the existing rubric only after hard blockers pass. A tie or no eligible candidate is valid for Q-01.

## S5 — Network, dependencies and skills (Q-09, Q-14)

- Separate trusted setup/model access from untrusted app execution. Only trusted runtime/gateway reaches the approved model endpoint; agent-requested shell/code tools execute in the restricted sandbox, never in that service or on the orchestrator host. A candidate unable to enforce this split is ineligible.
- A reviewed build/bootstrap step may reach explicit package/index and advisory hosts to prepare hash-locked dependencies/scanner data. Record host allowlist, redirects/mirrors, hashes, licenses, lockfiles and advisory timestamp/hash. Freeze the same target image and advisory data for both candidates. Audit each runtime's own dependency set at preflight too; app scanning is not runtime supply-chain assurance.
- App code, tests, repairs and install hooks run with **no internet egress**, no model key, host SSH keys/Docker socket or privileged mode. Use a non-root per-run container, dropped capabilities, read-only base and isolated writable volume. Set/record CPU, memory, PID, disk and time limits and demonstrate enforcement. No bind mount exposing the host checkout or unrelated files.
- No dependency fetching/installation in agent sessions. Changes require operator-reviewed bootstrap, new lock/image hashes and reruns for both candidates. No `curl | sh`, floating tags, unpinned VCS installs or arbitrary plugins/MCP endpoints.
- Use one small repository-authored developer skill at a recorded commit/hash for both candidates. No copying candidate prompts/skills/source here without license review. Inventory runtime license/NOTICE obligations for exact revisions and retain required notices. This decision redistributes no vendor code/images.
- Probe forbidden outbound/DNS access, traversal/symlink writes outside allowed source paths, hostile repo/tool text, unauthorized tools and test/policy edits. Capture enforcement-boundary denials; prompt instructions are not isolation evidence.

## S6 — Data boundary and retention (Q-10, Q-17)

- **Synthetic/authorized redistributable fixture data only.** No private repositories, customer data, confidential briefs or real credentials in the spike, prompts, logs or public report. Public visibility alone is not redistribution permission. New data classes require a separately approved policy.
- Persist only redacted structured evidence locally outside tracked source in an operator-only, **unsynced** directory, with content hashes and retention deadline. Do not persist raw unredacted transcripts. Redact before persistence/export; scan exports including diffs and exceptions using canary tests. On redaction failure record a denial without the sensitive value.
- Destroy workspaces, ephemeral credentials and transient buffers at close, cancellation or failure. Keep redacted local evidence **14 days from completion**, then delete through a documented cleanup command and retain a content-free deletion receipt. Interrupted-run deadlines start from last activity. No silent extensions or backup/sync copies.
- Publish only operator-reviewed sanitized summaries and necessary synthetic reproduction artifacts. They enter normal Git history with no 14-day deletion guarantee; never publish material requiring later deletion. Separately approve provider-side retention in the manifest; local deletion does not establish provider deletion.

## S7 — Preflight, outputs and completion

The spike PR must supply executable scripts and evidence. This planning PR supplies no fabricated measurements or selected runtime.

**Before live runs**, record:

1. Named operator, approved contract/design/policy hashes and writable paths; reviewed fixture tests and expected before/after outcomes.
2. Fixture base, stack lock/image digests, candidate commits, runtime/skill licenses/notices, scanner rules/advisory data and sanitized configuration.
3. Approved provider/model/data handling, enforceable budgets/rates, network allowlists, sandbox resource limits, evidence location and retention deadline.
4. Passing local boundary tests for approvals, path/egress denial, redaction, budgets, cancellation and fail-closed parsing. Missing controls block execution; document candidate incompatibility instead of relaxing controls.

**For each candidate**, execute all eight [required spike steps](05-HARNESS-DECISION.md#required-spike), including real failing/passing tests, repair, cancellation, external deny, specialized skill and approval-bypass probes. Keep reproducible adapters, event/status mapping, environment manifest, before/after patches, test/scanner reports, gates, approvals, latency/usage/cost and setup effort. Verify patches in fresh isolated workspaces. Publish only evidence allowed by S6.

**Completion:** report experiment completion separately from candidate success; score eligible candidates with the rubric, list all hard-blocker outcomes, and propose an evidence-backed ADR-001 update (winner or no winner). Do not assert full MVP/demo acceptance: durable orchestration, UI, production authentication, waiver policy and merge integration are later work.

**Remaining owner actions:** maintainer selects project license/contributor policy (Q-16) before external code reuse/distribution; operator supplies approved provider and exact pins before execution. These are explicit obligations, not hidden permissions. Revisit Q-11 for Milestone 6 and Q-15 before quantified productivity claims.

**Reversal:** supersede ADR-012 and rerun both candidates if scenario, model, security policy or ceilings change. No runtime migration is required yet because none is selected/implemented.
