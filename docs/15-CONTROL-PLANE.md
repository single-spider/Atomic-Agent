# Control-plane MVP (implementation slice)

**Status:** Experimental Python/FastAPI implementation. A real end-to-end autonomous SDLC run is not yet available. Candidate harnesses have not been selected or authorized.

## What is implemented

- SQLite durable runs, stages, append-only artifact snapshots, named approval records and event history.
- Requirements, stories, acceptance criteria, design and code artifact intake with guarded stage transitions.
- Human design/release approval tied to exact artifact hashes. Release gate requires tool evidence matching the most recent code revision.
- Mandatory Pytest, Ruff, Bandit, trusted dependency audit and secrets evidence; missing evidence is blocking. Unresolved high/critical findings block readiness. No waivers.
- Bounded two-attempt remediation transition returning to code submission; earlier test results are stale when revision changes.
- FastAPI with one local named operator token. With no configured operator identity/token, sensitive endpoints fail closed. This is a local MVP auth model, not production identity management.
- Docker command builder for fixed test/static/security tools, with offline execution, non-root user, resource limits and read-only source. No host fallback if Docker is absent. A pinned image digest is mandatory to initialize it.
- Trusted-bootstrap dependency-audit result verifier bound to an exact lock hash. The runtime does not fetch advisories inside the offline sandbox.

## Local start

Install dependencies inside a developer environment: `python -m pip install -e '.[test]'`. Set environment variables `ATOMIC_OPERATOR_ID` and `ATOMIC_OPERATOR_TOKEN` (use a long random token) before starting `uvicorn atomic_agent.api:app --host 127.0.0.1 --port 8000`.

All `/runs` routes require header `X-Atomic-Operator-Token`. The `/health` route is public. `GET /runs/{id}` includes stage, events and artifact metadata. Created artifacts expose their exact `content_hash` via `GET /runs/{id}/artifacts/{kind}` so a human can approve that same version.

Manual workflow:

1. POST `/runs` with `title` and structured `requirement`.
2. POST `/runs/{id}/artifacts` with `kind=requirements`, `stories`, `criteria` in order.
3. POST `/runs/{id}/approvals` with `kind=requirements`, named `actor`, latest hash and APPROVED.
4. POST a `design` artifact, then approve the latest design hash.
5. POST a `code` artifact with repository revision ID. The run moves to VALIDATING.
6. A trusted worker, not the public API, must attach deterministic tool evidence matching that revision. Then POST `/runs/{id}/assess` to receive a READY/NOT_READY recommendation. Missing tools correctly produce NOT_READY.
7. READY requires separate final release approval bound to the assessment hash before COMPLETE. No merge/deployment operation is exposed.

The `Store` is a single-user local prototype; direct callers inside the same Python process are privileged. Hostile code must run in a separate sandbox with no access to this process or its database. Never expose the dev API publicly or treat a dashboard identity string alone as a real human proof. The executable harness and an authenticated internal evidence-ingestion service remain separate work.

## Verified locally

- Python 3.13.5 developer tests: 18 green control-plane/runner checks at the time of this implementation, plus original fixture tests; the intentional authorization bug remains in the golden baseline.
- Docker command argument isolation tests are mocks; there was no Docker daemon in this environment, so **real container boundary security has not been proven**.
- The shared fixture runner container image and full pinned dependency lock are pending.

## Limits and follow-up

- No actual DeepSeek/OpenHands harness execution, multi-agent provider session, deployment action, hosted model credentials or paid calls are present.
- The gate evaluator trusts only internal caller evidence and has no cryptographic remote attestation. A future trusted runner service must authenticate receipts before adding them.
- No persistence encryption or multiuser RBAC. Approval hashes govern versions but stronger identity/audit protections are required before deployment.
- A separate end-to-end orchestration runner, test mapping parser, secure live harness sessions and dashboard remain upcoming milestones.
