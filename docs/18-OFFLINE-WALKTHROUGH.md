# Synthetic end-to-end walkthrough

**Purpose:** validate the engineering control plane with an independently authored synthetic fixture, without a real model or candidate harness. This is an integration demonstration, not proof of productivity, AI code generation, or release readiness.

## Reproduce

Build a local Python 3.12 fixture image with `docker build -f docker/Dockerfile.fixture-dev -t atomic-fixture:dev .` in a trusted bootstrap environment. Determine immutable **local image ID** with `docker image inspect --format '{{.Id}}' atomic-fixture:dev` and then run:

```bash
python -m atomic_agent.demo --image "sha256:..." --operator "LOCAL-SYNTHETIC-OPERATOR" --approve-synthetic-design
```

Without `--approve-synthetic-design`, the workflow stops at DESIGN_APPROVAL and **does not execute code**. Providing this flag represents a deliberate decision to approve the *synthetic demonstration* design, not a production-level identity/signature ceremony.

With approval, the walkthrough:

1. Opens a durable SQLite run and uses the labeled **deterministic test adapter** to propose requirements, stories, six criteria and design.
2. Persists named approvals tied to requirement/design hashes.
3. Copies the synthetic fixture to a disposable workspace and records its baseline code hash.
4. Runs **real Pytest inside the restricted Docker runner** to capture the deliberate AC-003 failure.
5. Initiates remediation attempt 1 and applies a built-in, known reference ownership check only to `app/main.py`. The synthetic reference patch is not produced by an LLM.
6. Records a new code hash and reruns real Pytest, Ruff and Bandit in Docker, plus a limited local regex-based credential check.
7. Evaluates mandatory release gates against the final revision. Missing trusted dependency audit evidence must cause **NOT_READY**, regardless of successful tests. No release/merge is executed.

GitHub Actions runs this demonstration following the sandbox denial probes. The resulting synthetic report includes revision hashes, parsed tool outcomes and gate blockers. Logs should be kept redacted and published only after explicit review.

## Required for a full live SDLC demonstration

- A reviewed remote DeepSeek/OpenHands worker integrated through the adapter interface and isolated from host/control-plane secrets, with an independently enforced model-access gateway.
- Approved model/provider/data usage, exact pinned Python 3.12 dependencies/skill/runtime revisions, budget limits, cancellation enforcement and human-design input.
- Actual requirement analysis, code and test generation, code review, security review, bounded remediation and final revalidation from those agents.
- A trusted complete dependency/audit feed, secret scanner, and evidence receipts bound to final revision.
- Tested traceability, release report, operator approval and a separate human Git merge process.

A successful synthetic fixture walkthrough **does not** select a harness or satisfy the live candidate comparison milestone.
