import sqlite3

import pytest
from fastapi.testclient import TestClient

from atomic_agent.api import create_app
from atomic_agent.core import Store, WorkflowError


def seeded(store):
    run=store.create_run("Update contact API",{"feature":"profile update"})
    store.add_artifact(run,"requirements",{"functional":["update own profile"]})
    store.add_artifact(run,"stories",[{"id":"ST-1","text":"As owner update my contact details"}])
    store.add_artifact(run,"criteria",[{"id":"AC-001","text":"owner update"},{"id":"AC-003","text":"deny non-owner"}])
    requirements=store.artifact(run,"requirements")
    store.approve(run,"requirements","reviewer",requirements["content_hash"],"APPROVED")
    store.add_artifact(run,"design",{"path":"PATCH /profiles/{profile_id}"})
    return run


def code_ready(store):
    run=seeded(store)
    design=store.artifact(run,"design")
    store.approve(run,"design","reviewer",design["content_hash"],"APPROVED")
    store.add_artifact(run,"code",{"paths":["app/main.py"]},revision="revision-123456")
    return run


def report(tool, ac=None):
    if tool=="pytest":return {"passing_ac_ids":ac or ["AC-001","AC-003"],"skipped":0,"failed":0}
    if tool=="dependency_audit":return {"complete":True,"vulnerabilities":0}
    if tool=="bandit":return {"high_count":0}
    if tool=="secrets":return {"detected":False}
    return {"checked":True}


def fill(store, run):
    for tool in ("pytest","ruff","bandit","dependency_audit","secrets"):
        store.record_evidence(run,tool,"revision-123456",status="COMPLETED",exit_code=0,parsed=True,report=report(tool),trusted_runner=True)


def test_approval_and_stage_guards(tmp_path):
    s=Store(tmp_path/"runs.sqlite")
    run=seeded(s)
    with pytest.raises(WorkflowError,match="not permitted"):
        s.approve(run,"requirements","reviewer","0"*64,"APPROVED")
    with pytest.raises(WorkflowError,match="cannot be submitted"):
        s.add_artifact(run,"code",{"changed":True},revision="revision-123456")
    design=s.artifact(run,"design")
    with pytest.raises(WorkflowError,match="does not match"):
        s.approve(run,"design","reviewer","0"*64,"APPROVED")
    s.approve(run,"design","reviewer",design["content_hash"],"APPROVED")
    s.add_artifact(run,"code",{"changed":True},revision="revision-123456")
    assert s.snapshot(run)["stage"]=="VALIDATING"


def test_untrusted_tool_data_cannot_promote_release(tmp_path):
    s=Store(tmp_path/"s.db"); run=code_ready(s)
    with pytest.raises(WorkflowError,match="trusted runner"):
        s.record_evidence(run,"pytest","revision-123456",status="COMPLETED",exit_code=0,parsed=True,report=report("pytest"))
    result=s.assess(run)
    assert result["status"]=="NOT_READY"
    assert len(result["problems"])>=5
    assert s.snapshot(run)["stage"]=="NOT_READY"


def test_ready_requires_all_evidence_and_human_release(tmp_path):
    s=Store(tmp_path/"s.db"); run=code_ready(s)
    fill(s,run)
    result=s.assess(run)
    assert result["status"]=="READY",result["problems"]
    assert s.snapshot(run)["stage"]=="RELEASE_APPROVAL"
    with pytest.raises(WorkflowError,match="does not match"):
        s.approve(run,"release","reviewer","0"*64,"APPROVED")
    s.approve(run,"release","reviewer",result["artifact_hash"],"APPROVED")
    assert s.snapshot(run)["stage"]=="COMPLETE"


def test_security_finding_blocks(tmp_path):
    s=Store(tmp_path/"s.db"); run=code_ready(s)
    fill(s,run)
    s.add_finding(run,"revision-123456","HIGH","missing authorization")
    result=s.assess(run)
    assert result["status"]=="NOT_READY"
    assert any("blocking finding" in p for p in result["problems"])


def test_api_keeps_tool_evidence_internal(tmp_path, monkeypatch):
    monkeypatch.setenv("ATOMIC_OPERATOR_ID", "reviewer")
    monkeypatch.setenv("ATOMIC_OPERATOR_TOKEN", "a-strong-synthetic-test-token")
    app=create_app(tmp_path/"api.sqlite")
    client=TestClient(app)
    denied=client.post("/runs",json={"title":"Feature","requirement":{"feature":"x"}})
    assert denied.status_code==401
    client.headers.update({"X-Atomic-Operator-Token": "a-strong-synthetic-test-token"})
    run=client.post("/runs",json={"title":"Feature","requirement":{"feature":"x"}})
    assert run.status_code==201
    run_id=run.json()["id"]
    assert client.get(f"/runs/{run_id}").json()["stage"]=="INTAKE"
    assert client.post(f"/runs/{run_id}/assess").status_code==409
    assert client.post(f"/runs/{run_id}/evidence",json={"fake":"success"}).status_code==404
    assert client.get("/health").json()["status"]=="ok"


def test_store_persists_artifacts_and_events_across_reopen(tmp_path):
    db=tmp_path/"persist.sqlite"; s=Store(db)
    run=seeded(s); snapshot=s.snapshot(run)
    reopened=Store(db).snapshot(run)
    assert reopened==snapshot
    assert [event["type"] for event in reopened["events"]].count("ApprovalRecorded")==1


def test_remediation_records_attempts_and_invalidation(tmp_path):
    s=Store(tmp_path/"x.sqlite"); run=code_ready(s)
    s.record_evidence(run,"pytest","revision-123456",status="FAILED",exit_code=1,parsed=True,
                      report={"passing_ac_ids":["AC-001"],"failed":1},trusted_runner=True)
    with pytest.raises(WorkflowError,match="trusted orchestrator"):
        s.start_remediation(run,"pytest failure")
    assert s.start_remediation(run,"pytest failure",trusted_orchestrator=True)==1
    s.add_artifact(run,"code",{"paths":["app/main.py"],"patch":"fix 1"},revision="revision-234567")
    assert s.start_remediation(run,"still failing",trusted_orchestrator=True)==2
    s.add_artifact(run,"code",{"paths":["app/main.py"],"patch":"fix 2"},revision="revision-345678")
    with pytest.raises(WorkflowError,match="exhausted"):
        s.start_remediation(run,"third failure",trusted_orchestrator=True)
    assessment=s.assess(run)
    assert assessment["status"]=="NOT_READY"
    assert any("current-revision" in problem for problem in assessment["problems"])
