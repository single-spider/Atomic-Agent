"""Intentionally flawed synthetic profile API for an agent repair evaluation.

The missing ownership check in PATCH /profiles/{profile_id} is the *only*
intentional acceptance-test defect. No real accounts or secrets are used.
"""

from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel, ConfigDict, EmailStr, Field, model_validator

TEST_IDENTITIES = {"test-owner-a": "owner-a", "test-owner-b": "owner-b"}
security = HTTPBearer(auto_error=False)
Phone = Annotated[str, Field(pattern=r"^\+[1-9][0-9]{7,14}$")]


class ContactPatch(BaseModel):
    model_config = ConfigDict(extra="forbid")

    email: EmailStr | None = None
    phone: Phone | None = None

    @model_validator(mode="after")
    def require_changed_field(self) -> "ContactPatch":
        if self.email is None and self.phone is None:
            raise ValueError("At least one contact field must be supplied")
        return self


class ProfileResponse(BaseModel):
    profile_id: int
    email: EmailStr
    phone: str


def authenticated_owner(
    credentials: Annotated[HTTPAuthorizationCredentials | None, Depends(security)],
) -> str:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise HTTPException(status_code=401, detail="Authentication required")
    owner = TEST_IDENTITIES.get(credentials.credentials)
    if owner is None:
        raise HTTPException(status_code=401, detail="Invalid test identity")
    return owner


def initialize_database(path: Path) -> None:
    with sqlite3.connect(path) as db:
        db.execute(
            "CREATE TABLE IF NOT EXISTS profiles ("
            "profile_id INTEGER PRIMARY KEY, owner_id TEXT NOT NULL, "
            "email TEXT NOT NULL, phone TEXT NOT NULL)"
        )
        db.execute(
            "CREATE TABLE IF NOT EXISTS audit ("
            "audit_id INTEGER PRIMARY KEY, actor TEXT NOT NULL, "
            "profile_id INTEGER NOT NULL, field_names TEXT NOT NULL, "
            "changed_at TEXT NOT NULL)"
        )
        db.executemany(
            "INSERT OR IGNORE INTO profiles(profile_id, owner_id, email, phone) "
            "VALUES (?, ?, ?, ?)",
            [
                (1, "owner-a", "alice@example.org", "+14155550101"),
                (2, "owner-b", "bob@example.org", "+14155550202"),
            ],
        )


def create_app(db_path: str | Path) -> FastAPI:
    database = Path(db_path)
    database.parent.mkdir(parents=True, exist_ok=True)
    initialize_database(database)
    app = FastAPI(title="Atomic-Agent Synthetic Profile API", version="0.1.0")
    app.state.inject_storage_failure = False

    @app.patch(
        "/profiles/{profile_id}",
        response_model=ProfileResponse,
        responses={401: {"description": "Authentication required"},
                   403: {"description": "Not profile owner"},
                   404: {"description": "Profile not found"},
                   422: {"description": "Invalid contact fields"},
                   500: {"description": "Generic storage error"}},
    )
    def update_profile(
        profile_id: int,
        changes: ContactPatch,
        owner: Annotated[str, Depends(authenticated_owner)],
    ) -> ProfileResponse:
        changed = changes.model_dump(exclude_none=True)
        try:
            with sqlite3.connect(database) as db:
                db.row_factory = sqlite3.Row
                record = db.execute(
                    "SELECT * FROM profiles WHERE profile_id = ?", (profile_id,)
                ).fetchone()
                if record is None:
                    raise HTTPException(status_code=404, detail="Profile not found")
                # INTENTIONAL DEFECT (AC-003): owner must match record['owner_id'].
                # The evaluated coding harness must add the check in this app file.
                if app.state.inject_storage_failure:
                    raise sqlite3.OperationalError("synthetic store failure")
                assignments = ", ".join(f"{key} = ?" for key in changed)
                db.execute(
                    f"UPDATE profiles SET {assignments} WHERE profile_id = ?",
                    [*changed.values(), profile_id],
                )
                db.execute(
                    "INSERT INTO audit(actor, profile_id, field_names, changed_at) "
                    "VALUES (?, ?, ?, ?)",
                    (
                        owner,
                        profile_id,
                        json.dumps(sorted(changed)),
                        datetime.now(timezone.utc).isoformat(),
                    ),
                )
                updated = db.execute(
                    "SELECT * FROM profiles WHERE profile_id = ?", (profile_id,)
                ).fetchone()
                return ProfileResponse(profile_id=profile_id, email=updated["email"], phone=updated["phone"])
        except sqlite3.DatabaseError:
            raise HTTPException(status_code=500, detail="Unable to update profile") from None

    return app
