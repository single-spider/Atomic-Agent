"""Transactional, versioned workflow for Atomic-Agent.

The control plane owns state and gates. Agent text cannot grant approvals,
write trusted validation evidence or change policy.
"""
from __future__ import annotations

import hashlib
import json
import sqlite3
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

POLICY_VERSION = "mvp-1"
REQUIRED_TOOLS = ("pytest", "ruff", "bandit", "dependency_audit", "secrets")
BLOCKING_SEVERITIES = frozenset({"HIGH", "CRITICAL", "UNKNOWN"})

class WorkflowError(ValueError):
    """Policy violation, invalid input, or illegal state transition."""


def canonical(obj: Any) -> str:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False)


def digest(obj: Any) -> str:
    return hashlib.sha256(canonical(obj).encode("utf-8")).hexdigest()


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


class Store:
    """SQLite-backed, transactional state with append-only artifacts/evidence."""

    def __init__(self, path: str | Path):
        self.path = str(path)
        Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        self._init()

    def _connect(self) -> sqlite3.Connection:
        db = sqlite3.connect(self.path, timeout=10)
        db.row_factory = sqlite3.Row
        db.execute("PRAGMA foreign_keys=ON")
        return db

    def _init(self) -> None:
        with self._connect() as db:
            db.executescript("""
                CREATE TABLE IF NOT EXISTS runs (
                    id TEXT PRIMARY KEY, title TEXT NOT NULL, request_json TEXT NOT NULL,
                    stage TEXT NOT NULL, version INTEGER NOT NULL DEFAULT 0,
                    created_at TEXT NOT NULL, updated_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS artifacts (
                    id TEXT PRIMARY KEY, run_id TEXT NOT NULL REFERENCES runs(id),
                    kind TEXT NOT NULL, body TEXT NOT NULL, content_hash TEXT NOT NULL,
                    revision TEXT, created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS approvals (
                    id TEXT PRIMARY KEY, run_id TEXT NOT NULL REFERENCES runs(id),
                    kind TEXT NOT NULL, actor TEXT NOT NULL, artifact_hash TEXT NOT NULL,
                    decision TEXT NOT NULL, created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS evidence (
                    id TEXT PRIMARY KEY, run_id TEXT NOT NULL REFERENCES runs(id),
                    tool TEXT NOT NULL, revision TEXT NOT NULL, status TEXT NOT NULL,
                    exit_code INTEGER NOT NULL, parsed INTEGER NOT NULL,
                    report_json TEXT NOT NULL, report_hash TEXT NOT NULL, created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS remediations (
                    id TEXT PRIMARY KEY, run_id TEXT NOT NULL REFERENCES runs(id),
                    source_revision TEXT NOT NULL, reason TEXT NOT NULL,
                    attempt INTEGER NOT NULL, created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS findings (
                    id TEXT PRIMARY KEY, run_id TEXT NOT NULL REFERENCES runs(id),
                    revision TEXT NOT NULL, severity TEXT NOT NULL,
                    status TEXT NOT NULL, detail TEXT NOT NULL, created_at TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS events (
                    seq INTEGER PRIMARY KEY AUTOINCREMENT, run_id TEXT NOT NULL REFERENCES runs(id),
                    type TEXT NOT NULL, payload_json TEXT NOT NULL, created_at TEXT NOT NULL
                );
                CREATE INDEX IF NOT EXISTS artifacts_run_kind ON artifacts(run_id, kind, created_at);
                CREATE INDEX IF NOT EXISTS evidence_run_tool ON evidence(run_id, tool, created_at);
            """)

    def _event(self, db: sqlite3.Connection, run_id: str, event: str, payload: dict) -> None:
        db.execute("INSERT INTO events(run_id,type,payload_json,created_at) VALUES(?,?,?,?)",
                   (run_id, event, canonical(payload), now()))

    def _run(self, db: sqlite3.Connection, run_id: str) -> sqlite3.Row:
        row = db.execute("SELECT * FROM runs WHERE id=?", (run_id,)).fetchone()
        if row is None:
            raise WorkflowError("unknown run")
        return row

    def create_run(self, title: str, request: dict[str, Any]) -> str:
        if not title.strip() or not isinstance(request, dict) or not request:
            raise WorkflowError("title and structured request are required")
        run_id = uuid.uuid4().hex
        with self._connect() as db:
            db.execute("INSERT INTO runs(id,title,request_json,stage,created_at,updated_at) "
                       "VALUES(?,?,?,?,?,?)", (run_id,title,canonical(request),"INTAKE",now(),now()))
            self._event(db,run_id,"RunCreated",{"title":title,"request_hash":digest(request)})
        return run_id

    def latest(self, db: sqlite3.Connection, run_id: str, kind: str) -> dict | None:
        row = db.execute("SELECT * FROM artifacts WHERE run_id=? AND kind=? "
                         "ORDER BY rowid DESC LIMIT 1", (run_id,kind)).fetchone()
        return dict(row) if row else None

    def _stage(self, db: sqlite3.Connection, run_id: str, stage: str) -> None:
        current = self._run(db,run_id)
        db.execute("UPDATE runs SET stage=?,version=version+1,updated_at=? WHERE id=?",
                   (stage,now(),run_id))
        self._event(db,run_id,"StageChanged",{"from":current["stage"],"to":stage})

    def add_artifact(self, run_id: str, kind: str, body: Any, *, revision: str | None = None) -> str:
        allowed = {"requirements":"INTAKE", "stories":"REQUIREMENTS", "criteria":"REQUIREMENTS",
                   "design":"REQUIREMENTS_APPROVED", "code":"DESIGN_APPROVED"}
        if kind not in allowed:
            raise WorkflowError("unsupported artifact kind")
        if not isinstance(body, (dict,list)) or not body:
            raise WorkflowError("artifact must be a non-empty JSON object or list")
        with self._connect() as db:
            db.execute("BEGIN IMMEDIATE")
            current = self._run(db,run_id)
            if current["stage"] != allowed[kind]:
                raise WorkflowError(f"{kind} cannot be submitted during {current['stage']}")
            if kind == "design" and not self.latest(db,run_id,"criteria"):
                raise WorkflowError("acceptance criteria missing")
            if kind == "code" and (not isinstance(revision,str) or len(revision)<8):
                raise WorkflowError("code revision identifier required")
            if kind == "code" and not self._approved(db,run_id,"design",self.latest(db,run_id,"design")):
                raise WorkflowError("missing design approval")
            artifact_id=uuid.uuid4().hex
            db.execute("INSERT INTO artifacts(id,run_id,kind,body,content_hash,revision,created_at) "
                       "VALUES(?,?,?,?,?,?,?)", (artifact_id,run_id,kind,canonical(body),digest(body),revision,now()))
            self._event(db,run_id,"ArtifactProduced",{"kind":kind,"id":artifact_id,"hash":digest(body),"revision":revision})
            if kind == "requirements":
                self._stage(db,run_id,"REQUIREMENTS")
            elif kind == "code":
                self._stage(db,run_id,"VALIDATING")
            elif kind == "design":
                self._stage(db,run_id,"DESIGN_APPROVAL")
        return artifact_id

    def _approved(self, db: sqlite3.Connection, run_id: str, kind: str, artifact: dict | None) -> bool:
        if not artifact:
            return False
        row=db.execute("SELECT decision FROM approvals WHERE run_id=? AND kind=? AND artifact_hash=? "
                       "ORDER BY rowid DESC LIMIT 1",(run_id,kind,artifact["content_hash"])).fetchone()
        return bool(row and row["decision"]=="APPROVED")

    def approve(self, run_id: str, kind: str, actor: str, artifact_hash: str, decision: str) -> str:
        if kind not in {"requirements","design","release"} or decision not in {"APPROVED","REJECTED"}:
            raise WorkflowError("invalid approval kind or decision")
        if not actor.strip() or len(artifact_hash)!=64:
            raise WorkflowError("named human and exact artifact hash required")
        expected_stage={"requirements":"REQUIREMENTS","design":"DESIGN_APPROVAL","release":"RELEASE_APPROVAL"}[kind]
        with self._connect() as db:
            db.execute("BEGIN IMMEDIATE")
            if self._run(db,run_id)["stage"]!=expected_stage:
                raise WorkflowError("approval not permitted in current stage")
            artifact=self.latest(db,run_id,"assessment" if kind=="release" else kind)
            if not artifact or artifact["content_hash"]!=artifact_hash:
                raise WorkflowError("approval does not match latest artifact")
            if kind=="requirements" and not self.latest(db,run_id,"stories"):
                raise WorkflowError("stories missing")
            if kind=="requirements" and not self.latest(db,run_id,"criteria"):
                raise WorkflowError("criteria missing")
            aid=uuid.uuid4().hex
            db.execute("INSERT INTO approvals(id,run_id,kind,actor,artifact_hash,decision,created_at) "
                       "VALUES(?,?,?,?,?,?,?)",(aid,run_id,kind,actor,artifact_hash,decision,now()))
            self._event(db,run_id,"ApprovalRecorded",{"kind":kind,"actor":actor,"decision":decision,"hash":artifact_hash})
            if decision=="REJECTED":
                self._stage(db,run_id,"BLOCKED")
            else:
                stage={"requirements":"REQUIREMENTS_APPROVED", "design":"DESIGN_APPROVED", "release":"COMPLETE"}[kind]
                self._stage(db,run_id,stage)
        return aid

    def record_evidence(self, run_id: str, tool: str, revision: str, *,
                        status: str, exit_code: int, parsed: bool, report: dict,
                        trusted_runner: bool=False) -> str:
        if not trusted_runner:
            raise WorkflowError("tool evidence must come from a trusted runner")
        if tool not in REQUIRED_TOOLS or not isinstance(report,dict):
            raise WorkflowError("invalid tool report")
        if type(exit_code) is not int or not isinstance(parsed,bool) or status not in {"COMPLETED","FAILED","TIMED_OUT"}:
            raise WorkflowError("malformed runner status")
        with self._connect() as db:
            db.execute("BEGIN IMMEDIATE")
            if self._run(db,run_id)["stage"]!="VALIDATING":
                raise WorkflowError("not validating")
            code=self.latest(db,run_id,"code")
            if not code or code["revision"]!=revision:
                raise WorkflowError("stale tool revision")
            eid=uuid.uuid4().hex
            db.execute("INSERT INTO evidence(id,run_id,tool,revision,status,exit_code,parsed,report_json,report_hash,created_at) "
                       "VALUES(?,?,?,?,?,?,?,?,?,?)",
                       (eid,run_id,tool,revision,status,exit_code,int(parsed),canonical(report),digest(report),now()))
            self._event(db,run_id,"ToolCompleted",{"id":eid,"tool":tool,"revision":revision,"status":status,"exit_code":exit_code})
        return eid

    def start_remediation(self, run_id: str, reason: str, *, trusted_orchestrator: bool=False) -> int:
        """Allow at most two corrective revisions without changing approved design."""
        if not trusted_orchestrator:
            raise WorkflowError("only the trusted orchestrator may initiate remediation")
        if not reason.strip():
            raise WorkflowError("remediation requires a linked failure reason")
        with self._connect() as db:
            db.execute("BEGIN IMMEDIATE")
            if self._run(db,run_id)["stage"] not in {"VALIDATING","NOT_READY"}:
                raise WorkflowError("remediation not allowed in current stage")
            code=self.latest(db,run_id,"code")
            if not code:
                raise WorkflowError("remediation requires a code revision")
            attempt=db.execute("SELECT COUNT(*) AS n FROM remediations WHERE run_id=?",(run_id,)).fetchone()["n"]+1
            if attempt>2:
                raise WorkflowError("remediation budget exhausted")
            rid=uuid.uuid4().hex
            db.execute("INSERT INTO remediations(id,run_id,source_revision,reason,attempt,created_at) "
                       "VALUES(?,?,?,?,?,?)",(rid,run_id,code["revision"],reason,attempt,now()))
            self._event(db,run_id,"RemediationStarted",{"id":rid,"source_revision":code["revision"],"attempt":attempt})
            self._stage(db,run_id,"DESIGN_APPROVED")
            return attempt

    def add_finding(self, run_id: str, revision: str, severity: str, detail: str,
                    status: str="OPEN") -> str:
        if severity not in {"LOW","MEDIUM","HIGH","CRITICAL","UNKNOWN"} or status not in {"OPEN","RESOLVED"}:
            raise WorkflowError("invalid finding")
        with self._connect() as db:
            self._run(db,run_id)
            fid=uuid.uuid4().hex
            db.execute("INSERT INTO findings(id,run_id,revision,severity,status,detail,created_at) "
                       "VALUES(?,?,?,?,?,?,?)",(fid,run_id,revision,severity,status,detail,now()))
            self._event(db,run_id,"FindingRecorded",{"id":fid,"severity":severity,"revision":revision})
        return fid

    def _gate(self, db: sqlite3.Connection, run_id: str) -> dict:
        code=self.latest(db,run_id,"code")
        revision=code["revision"] if code else None
        criteria=self.latest(db,run_id,"criteria")
        ac_ids = []
        if criteria:
            try:
                data=json.loads(criteria["body"])
                ac_ids=[x["id"] for x in data if isinstance(x,dict) and isinstance(x.get("id"),str)]
            except (ValueError, TypeError, KeyError):
                pass
        problems=[]
        if not ac_ids or len(ac_ids)!=len(set(ac_ids)):
            problems.append("acceptance criteria missing or malformed")
        tests=[]
        for tool in REQUIRED_TOOLS:
            row=db.execute("SELECT * FROM evidence WHERE run_id=? AND tool=? AND revision=? "
                           "ORDER BY rowid DESC LIMIT 1",(run_id,tool,revision)).fetchone()
            if not row:
                problems.append(f"{tool}: missing current-revision evidence")
                continue
            if row["status"]!="COMPLETED" or row["exit_code"]!=0 or not row["parsed"]:
                problems.append(f"{tool}: validation failed or unreadable")
            try:
                report=json.loads(row["report_json"])
            except (ValueError,TypeError):
                problems.append(f"{tool}: malformed report")
                continue
            if tool=="pytest":
                tests=report.get("passing_ac_ids",[]) if isinstance(report,dict) else []
                if report.get("skipped",0) or report.get("failed",0):
                    problems.append("pytest: skipped or failed tests")
            if tool=="dependency_audit":
                if not report.get("complete",False):
                    problems.append("dependency audit: incomplete inventory")
                if report.get("vulnerabilities",0):
                    problems.append("dependency audit: vulnerabilities detected")
            if tool=="secrets" and report.get("detected",True):
                problems.append("secrets: finding or missing negative evidence")
            if tool=="bandit":
                if report.get("high_count",0):
                    problems.append("bandit: high severity findings")
                if report.get("unknown_count",0):
                    problems.append("bandit: unknown severity")
        if ac_ids and not set(ac_ids).issubset(set(tests)):
            problems.append("mandatory acceptance criteria lack passing test evidence")
        blockers=db.execute("SELECT id,severity FROM findings WHERE run_id=? AND revision=? AND status='OPEN'",
                            (run_id,revision)).fetchall()
        for finding in blockers:
            if finding["severity"] in BLOCKING_SEVERITIES:
                problems.append(f"blocking finding: {finding['id']}")
        return {"revision":revision,"policy":POLICY_VERSION,"status":"READY" if not problems else "NOT_READY",
                "problems":problems,"mandatory_ac_ids":ac_ids,"passing_ac_ids":sorted(set(tests))}

    def assess(self, run_id: str) -> dict:
        with self._connect() as db:
            db.execute("BEGIN IMMEDIATE")
            if self._run(db,run_id)["stage"]!="VALIDATING":
                raise WorkflowError("run not in validation stage")
            verdict=self._gate(db,run_id)
            artifact_id=uuid.uuid4().hex
            db.execute("INSERT INTO artifacts(id,run_id,kind,body,content_hash,revision,created_at) "
                       "VALUES(?,?,?,?,?,?,?)",
                       (artifact_id,run_id,"assessment",canonical(verdict),digest(verdict),verdict["revision"],now()))
            self._event(db,run_id,"ReleaseAssessed",{"status":verdict["status"],"artifact_id":artifact_id})
            self._stage(db,run_id,"RELEASE_APPROVAL" if verdict["status"]=="READY" else "NOT_READY")
        return {**verdict,"artifact_id":artifact_id,"artifact_hash":digest(verdict)}

    def snapshot(self, run_id: str) -> dict:
        with self._connect() as db:
            row=self._run(db,run_id)
            artifacts=db.execute("SELECT id,kind,content_hash,revision,created_at FROM artifacts WHERE run_id=? ORDER BY rowid",(run_id,)).fetchall()
            approvals=db.execute("SELECT kind,actor,artifact_hash,decision,created_at FROM approvals WHERE run_id=? ORDER BY rowid",(run_id,)).fetchall()
            events=db.execute("SELECT seq,type,payload_json,created_at FROM events WHERE run_id=? ORDER BY seq",(run_id,)).fetchall()
            evidence=db.execute("SELECT id,tool,revision,status,exit_code,parsed,report_hash,created_at FROM evidence WHERE run_id=? ORDER BY rowid",(run_id,)).fetchall()
            findings=db.execute("SELECT id,revision,severity,status,detail,created_at FROM findings WHERE run_id=? ORDER BY rowid",(run_id,)).fetchall()
            return {"id":run_id,"title":row["title"],"stage":row["stage"],"version":row["version"],
                    "artifacts":[dict(x) for x in artifacts],"approvals":[dict(x) for x in approvals],
                    "evidence":[dict(x) for x in evidence],"findings":[dict(x) for x in findings],
                    "events":[{"seq":x["seq"],"type":x["type"],"data":json.loads(x["payload_json"]),"created_at":x["created_at"]} for x in events]}

    def request(self, run_id: str) -> dict:
        with self._connect() as db:
            row=self._run(db,run_id)
            return json.loads(row["request_json"])

    def artifact(self, run_id: str, kind: str) -> dict | None:
        with self._connect() as db:
            self._run(db,run_id)
            row=self.latest(db,run_id,kind)
            if not row:
                return None
            row["body"]=json.loads(row["body"])
            return row
