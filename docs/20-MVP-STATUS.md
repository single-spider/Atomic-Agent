# Implementation status and release-blocking dependencies

This page distinguishes demonstrated code from the originally proposed end-to-end SDLC target. The current repository is an **experimental, local single-operator MVP**, and must not be represented as an autonomous production-grade release agent.

## Verified development capabilities

- Structured requirement intake, persistently versioned artifacts, stage transition policy and event history.
- Eight role configurations with typed outputs; default no-harness refusal and an explicitly labeled synthetic test adapter.
- Requirements and design approval by a configured local operator token, bound to exact artifact hashes.
- Synthetic FastAPI benchmark with six measurable acceptance criteria and exactly one intentional AC-003 ownership defect.
- A no-build dashboard to inspect runs, submit artifacts, approve stages, inspect events and record criterion-to-code links.
- An isolated-container **development probe** with Python 3.12, real golden Pytest, Ruff and Bandit, restrictive non-root/no-network/read-only flags and basic denial tests verified in GitHub Actions.
- Bounded remediation state transition, a known deterministic synthetic reference repair, real revalidation, and a fail-closed NOT_READY decision when trusted audit evidence is absent.
- Reviewer-approved criterion-to-code-revision links, with mapping invalidation on new revision.
- Hash checking of the exact source revision and golden-test/design/dependency-declaration inputs before dispatch to deterministic tools.

## Open requirements before a true live AI-powered end-to-end demo

1. **Harness selection, licensing and exact revisions:** approve a comparison candidate pair, inspect runtime terms and pick a runnable worker architecture. The default SDK shell of some harnesses has broad permissions; don't put it in the trusted API process.
2. **Model & gateway authorization:** select an approved provider/model, authorize data transfer and cost ceilings, and separate model credentials/gateway from untrusted agent tools.
3. **Live agent execution:** implement secure, cancellable and budget-enforced isolated worker services for coding and the remaining specialized agent skills; run both eligible harnesses on identical benchmark inputs.
4. **Strong sandbox preflight:** complete malicious code/path/symlink/network, cancellation, PID, filesystem and credential probes with actual harness tools, not just fixed development commands.
5. **Dependency and vulnerability assurance:** freeze Python 3.12 base image digest, complete hash-locked transitive dependencies, trusted online advisory audit and an immutable evidence receipt tied to the final worktree revision. Current `Dockerfile.fixture-dev` is NOT sufficient.
6. **Authenticated validation evidence:** a remote trusted runner must authenticate or attest its receipts. A local method parameter indicating trusted provenance is only a process boundary convention.
7. **End-to-end generated artifacts:** produce real requirements, user stories, design, code and generated tests from the selected AI runtime, validate their schemas, map generated test cases to criteria and ensure programmatic release policy is authoritative.
8. **Operational hardening:** adopt production identity/RBAC/permissions and secure audit retention, full recovery/replay/cancel semantics, confidential data rules, and signed human approvals.
9. **Actual deployment workflow:** prepare Docker Compose or equivalent packaging and a human-controlled GitHub PR/merge flow. The current app never performs an automatic release.
10. **Release evidence and benchmark:** test the complete happy/failing/human-review paths on real selected harnesses, record costs and runtimes, and produce an independent readiness report before claiming the original brief's deliverables are complete.

## Verification commands

```bash
python -m pip install -e '.[test]'
python -m pytest -q tests/unit tests/integration
python scripts/check_frozen.py
python scripts/check_baseline.py
ATOMIC_OPERATOR_ID=local ATOMIC_OPERATOR_TOKEN='replace-with-a-long-random-secret' uvicorn atomic_agent.api:app --host 127.0.0.1 --port 8000
```

The local API/dashboard is at http://127.0.0.1:8000. Do not expose this single-operator development service to the public internet. Optional model-specific endpoints fail closed without an approved harness adapter. The Docker CI image and benchmark remain synthetic only.
