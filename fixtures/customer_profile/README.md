# Synthetic profile API (intentionally defective)

This is an independent, test-only FastAPI fixture for the ADR-012 harness comparison. No real accounts, private repository data, or production credentials are used. `test-owner-a` and `test-owner-b` are public fixture identities and are never valid outside this test process.

The endpoint `PATCH /profiles/{profile_id}` supports optional email/phone fields (at least one required), strict schema validation, owner authentication, 404 on missing profile, SQLite persistence, atomic metadata-only audit, and generic 500 on injected storage failures.

**Expected baseline:** six AC tests and one OpenAPI test are collected. Only `test_ac003_other_owner_forbidden_and_storage_unchanged` is expected to fail; this is the deliberate missing authorization check in `app/main.py`. Never modify the golden tests, lockfiles, runner policy, or the fixture design when repairing it. An evaluated coding agent may edit only `app/main.py`.

To run from repository root with prerequisites already installed:

```bash
python -m pytest -q fixtures/customer_profile/tests/golden
```

Run in a controlled synthetic development environment for fixture authoring. Actual harness executions require the container boundary, pinned Python 3.12/tool versions, approved provider and complete preflight specified by ADR-012. Passing local tests does **not** demonstrate those controls.
