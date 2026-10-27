"""Minimal approval-first FastAPI facade for Atomic-Agent's control plane."""
from __future__ import annotations

import os
import secrets
from pathlib import Path
from typing import Any, Literal

from fastapi import Depends, FastAPI, Header, HTTPException
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from .core import Store, WorkflowError
from .agents import HarnessAdapter
from .orchestrator import Orchestrator
from .ui import PAGE


class NewRun(BaseModel):
    title: str = Field(min_length=1)
    requirement: dict[str, Any]


class ArtifactInput(BaseModel):
    kind: Literal["requirements", "stories", "criteria", "design", "code"]
    body: dict[str, Any] | list[Any]
    revision: str | None = None


class ApprovalInput(BaseModel):
    kind: Literal["requirements", "design", "release"]
    actor: str = Field(min_length=1)
    artifact_hash: str = Field(min_length=64, max_length=64)
    decision: Literal["APPROVED", "REJECTED"]


def create_app(db_path: str | Path | None = None, harness: HarnessAdapter | None = None) -> FastAPI:
    path = str(db_path or os.getenv("ATOMIC_DB_PATH", "/tmp/atomic-agent/atomic.sqlite"))
    store = Store(path)
    operator_token = os.getenv("ATOMIC_OPERATOR_TOKEN", "")
    operator_id = os.getenv("ATOMIC_OPERATOR_ID", "")

    def require_operator(x_atomic_operator_token: str | None = Header(default=None)) -> str:
        # No dev bypass: mutation and sensitive reads require an explicit token.
        if not operator_token or not operator_id:
            raise HTTPException(503, "operator authorization is not configured")
        if not x_atomic_operator_token or not secrets.compare_digest(
            x_atomic_operator_token, operator_token
        ):
            raise HTTPException(401, "operator authorization required")
        return operator_id
    api = FastAPI(title="Atomic-Agent Control Plane", version="0.1.0")
    api.state.store = store
    orchestrator = Orchestrator(store, harness)

    @api.exception_handler(WorkflowError)
    async def handle_workflow_error(_request, exc: WorkflowError):
        from fastapi.responses import JSONResponse
        return JSONResponse(status_code=409, content={"detail": str(exc)})

    @api.get("/", response_class=HTMLResponse)
    def dashboard():
        return PAGE

    @api.post("/runs/{run_id}/agent/analyze")
    def agent_analyze(run_id: str, operator: str = Depends(require_operator)):
        return orchestrator.analyze(run_id, store.request(run_id))

    @api.post("/runs/{run_id}/agent/design")
    def agent_design(run_id: str, operator: str = Depends(require_operator)):
        result=orchestrator.design(run_id)
        return {"artifact_id": result["id"], "artifact_hash": result["content_hash"]}

    @api.post("/runs/{run_id}/agent/propose-tests")
    def agent_tests(run_id: str, operator: str = Depends(require_operator)):
        return {"proposals": orchestrator.propose_tests(run_id)}

    @api.get("/health")
    def health():
        return {"status": "ok", "phase": "mvp-control-plane"}

    @api.post("/runs", status_code=201)
    def create_run(payload: NewRun, operator: str = Depends(require_operator)):
        run_id = store.create_run(payload.title, payload.requirement)
        return store.snapshot(run_id)

    @api.get("/runs/{run_id}")
    def get_run(run_id: str, operator: str = Depends(require_operator)):
        return store.snapshot(run_id)

    @api.get("/runs/{run_id}/artifacts/{kind}")
    def get_artifact(run_id: str, kind: str, operator: str = Depends(require_operator)):
        artifact = store.artifact(run_id, kind)
        if artifact is None:
            raise HTTPException(status_code=404, detail="artifact not found")
        return artifact

    @api.post("/runs/{run_id}/artifacts", status_code=201)
    def add_artifact(run_id: str, payload: ArtifactInput, operator: str = Depends(require_operator)):
        artifact_id = store.add_artifact(run_id, payload.kind, payload.body, revision=payload.revision)
        return {"artifact_id": artifact_id, "stage": store.snapshot(run_id)["stage"]}

    @api.post("/runs/{run_id}/approvals", status_code=201)
    def approve(run_id: str, payload: ApprovalInput, operator: str = Depends(require_operator)):
        if payload.actor != operator:
            raise HTTPException(403, "approval actor must match authenticated operator")
        approval_id = store.approve(run_id, payload.kind, payload.actor,
                                    payload.artifact_hash, payload.decision)
        return {"approval_id": approval_id, "stage": store.snapshot(run_id)["stage"]}

    @api.post("/runs/{run_id}/assess")
    def assess(run_id: str, operator: str = Depends(require_operator)):
        return store.assess(run_id)

    return api


app = create_app()
