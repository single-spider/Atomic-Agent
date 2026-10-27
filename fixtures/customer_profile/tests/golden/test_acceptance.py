"""Frozen acceptance tests. The baseline MUST fail AC-003 before repair."""

import json

from conftest import audit, profile

A = {"Authorization": "Bearer test-owner-a"}
B = {"Authorization": "Bearer test-owner-b"}


def test_ac001_owner_updates_profile_and_persists(fixture_env):
    client, db, _ = fixture_env
    resp = client.patch("/profiles/1", json={"email": "newalice@example.org"}, headers=A)
    assert resp.status_code == 200
    assert resp.json()["email"] == "newalice@example.org"
    assert profile(db, 1)[1] == "newalice@example.org"


def test_ac002_missing_or_invalid_identity_denied(fixture_env):
    client, db, _ = fixture_env
    for headers in ({}, {"Authorization": "Bearer invalid-identity"}):
        resp = client.patch("/profiles/1", json={"phone": "+14155550303"}, headers=headers)
        assert resp.status_code == 401
    assert profile(db, 1)[2] == "+14155550101"
    assert audit(db) == []


def test_ac003_other_owner_forbidden_and_storage_unchanged(fixture_env):
    client, db, _ = fixture_env
    original = profile(db, 2)
    resp = client.patch("/profiles/2", json={"email": "hijacked@example.org"}, headers=A)
    assert resp.status_code == 403
    assert profile(db, 2) == original
    assert audit(db) == []


def test_ac004_invalid_payload_rejected_without_partial_write(fixture_env):
    client, db, _ = fixture_env
    original = profile(db, 1)
    invalids = [
        {},
        {"email": "not-an-email"},
        {"phone": "1234"},
        {"email": "new@example.org", "unknown": "value"},
        {"email": "valid@example.org", "phone": "bad"},
    ]
    for payload in invalids:
        resp = client.patch("/profiles/1", json=payload, headers=A)
        assert resp.status_code == 422, payload
    assert profile(db, 1) == original
    assert audit(db) == []


def test_ac005_audit_contains_metadata_without_contact_values(fixture_env):
    client, db, _ = fixture_env
    email = "audited@example.org"
    resp = client.patch("/profiles/1", json={"email": email}, headers=A)
    assert resp.status_code == 200
    records = audit(db)
    assert len(records) == 1
    actor, changed_id, fields, timestamp = records[0]
    assert actor == "owner-a" and changed_id == 1
    assert json.loads(fields) == ["email"]
    assert timestamp.endswith("+00:00")
    assert email not in repr(records)


def test_ac006_storage_failure_is_generic_and_atomic(fixture_env):
    client, db, app = fixture_env
    before = profile(db, 1)
    app.state.inject_storage_failure = True
    resp = client.patch("/profiles/1", json={"email": "fail@example.org"}, headers=A)
    assert resp.status_code == 500
    assert resp.json() == {"detail": "Unable to update profile"}
    assert profile(db, 1) == before
    assert audit(db) == []


def test_openapi_contract_and_missing_resource(fixture_env):
    client, db, _ = fixture_env
    spec = client.get("/openapi.json").json()
    patch_spec = spec["paths"]["/profiles/{profile_id}"]["patch"]
    assert {"200", "401", "403", "404", "422", "500"} <= set(patch_spec["responses"])
    r = client.patch("/profiles/999", json={"email": "valid@example.org"}, headers=B)
    assert r.status_code == 404
    assert audit(db) == []
