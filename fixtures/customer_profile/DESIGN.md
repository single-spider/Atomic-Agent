# Frozen synthetic fixture design for ADR-012

## Public test identities

- `test-owner-a` authorizes owner `owner-a` (profile 1).
- `test-owner-b` authorizes owner `owner-b` (profile 2).
- Tokens are public, synthetic and never accepted outside this local fixture.

## HTTP contract

`PATCH /profiles/{profile_id}` accepts JSON with optional email and phone, with at least one valid field. Unknown fields are rejected. Phone must match `^\+[1-9][0-9]{7,14}$`. Email uses Pydantic `EmailStr` and its installed email-validator dependency. Status codes: 200 update, 401 identity failure, 403 non-owner, 404 missing profile, 422 invalid payload, 500 injected SQLite failure. OpenAPI should advertise these responses.

## Persisted behavior

Profiles are seeded in a temporary SQLite database per golden test. A successful update writes profile changes and a metadata-only audit row atomically: actor, profile ID, changed field names and UTC timestamp. All rejected or failed requests leave the profile and audit data unchanged. The audit must never contain the new contact field values.

## Mandatory acceptance cases

| Criterion | Frozen test name |
| --- | --- |
| AC-001 | test_ac001_owner_updates_profile_and_persists |
| AC-002 | test_ac002_missing_or_invalid_identity_denied |
| AC-003 | test_ac003_other_owner_forbidden_and_storage_unchanged |
| AC-004 | test_ac004_invalid_payload_rejected_without_partial_write |
| AC-005 | test_ac005_audit_contains_metadata_without_contact_values |
| AC-006 | test_ac006_storage_failure_is_generic_and_atomic |

`test_openapi_contract_and_missing_resource` checks OpenAPI and 404 as auxiliary fixture requirements.

The baseline has exactly one intentional defect: missing owner check in `app/main.py`. This fixture is not a finished product, and an operator must approve the design hash and code-edit scope before calling an agent. `DESIGN.md` and `tests/golden/*` are read-only to harness agents. The golden fixture hashes are recorded in `FROZEN.json`.
