# Harness comparison fixture: first executable slice

**State:** Development fixture and static policy helper implementation. This PR does **not** select a harness, make model calls, execute scanners, establish a Docker sandbox, or satisfy ADR-012 preflight.

## Included

- Independently authored synthetic FastAPI profile-edit API and SQLite storage in `fixtures/customer_profile/app/main.py`.
- Reviewed contract and SHA-256-frozen golden tests in `fixtures/customer_profile/DESIGN.md`, `FROZEN.json` and `tests/golden`.
- One deliberately missing ownership check for AC-003; other five mandatory ACs and an OpenAPI/404 test succeed.
- A standard-library test classifier `scripts/check_baseline.py` that checks test names, skipped status and exactly one expected failure, rather than treating arbitrary pytest failure as success.
- `scripts/check_frozen.py` checks that operator-owned golden tests, declared design and dependency declarations match their frozen hashes.
- Pure-Python contract helpers in `spike/policy.py` for version-bound approval, path screening, budget reservation, fail-closed tool evidence, and test-canary redaction; associated passing tests in `tests/unit`.
- `spike/preflight.py` statically identifies missing operator/model/approval/evidence configuration. The blank example manifest is deliberately BLOCKED and is never execution authorization.

## Developer verification

Use an appropriately isolated **synthetic development** environment with `fastapi`, `pydantic`, `email-validator`, `httpx`, `pytest` installed. Tested locally under Python 3.13.5, FastAPI 0.128.2, Pydantic 2.13.5, pytest 9.0.2 and httpx 0.28.1. The ADR-012 intended runner is Python 3.12, which is **not verified** by this result.

```bash
python scripts/check_frozen.py
python scripts/check_baseline.py
python -m pytest -q tests/unit
python -m spike.preflight spike/preflight.example.json  # expected nonzero: BLOCKED
```

To prove the golden suite accepts the intended minimal repair, create a separate disposable *copy* of the fixture, add a real owner check in the copied `app/main.py` after loading the profile, and run `python scripts/check_baseline.py --repaired` from that copy. Do not fix the intentionally broken baseline in the repository.

## Caveats and next steps

The source file path allowlist is a **logical contract** only; a Python check cannot enforce OS-level path restrictions when running arbitrary code. Likewise configuration hashes cannot prove that cancellation, egress and budget controls actually executed. Implement container policy, denial probes, immutable signed/revision-matched tool reports, and the reviewed trusted dependency audit before harness invocations.

`fixtures/customer_profile/pyproject.toml` pins direct dependency versions for the development fixture but is **not** a complete, hash-locked Python 3.12 dependency inventory. A trusted operator must generate and review a full transitive lock/image and produce the trusted audit record before ADR-012 candidate runs. No runtime license or model use is authorized by this slice.

The benchmark base revision should be frozen to a commit containing this fixture after review. Both candidates must use identical source, golden tests, model, limits and approved design/hash as stipulated by ADR-012.
