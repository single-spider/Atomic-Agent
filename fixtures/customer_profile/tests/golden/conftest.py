"""Golden tests are operator-owned and read-only to the coding harness."""

import sqlite3
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

APP_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(APP_ROOT))
from app.main import create_app  # noqa: E402


@pytest.fixture
def fixture_env(tmp_path):
    db_path = tmp_path / "synthetic.sqlite"
    app = create_app(db_path)
    with TestClient(app) as client:
        yield client, db_path, app


def profile(db_path, profile_id):
    with sqlite3.connect(db_path) as db:
        return db.execute(
            "SELECT owner_id, email, phone FROM profiles WHERE profile_id = ?", (profile_id,)
        ).fetchone()


def audit(db_path):
    with sqlite3.connect(db_path) as db:
        return db.execute(
            "SELECT actor, profile_id, field_names, changed_at FROM audit ORDER BY audit_id"
        ).fetchall()
