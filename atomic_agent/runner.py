"""Docker-based fixed-command validation boundary for approved workspaces.

Live use requires an independently reviewed pinned image, Docker configuration,
trusted lock/audit manifest, approval and adversarial boundary preflight. This
module never silently switches to host execution when Docker is unavailable.
"""
from __future__ import annotations

import hashlib
import json
import re
import shutil
import subprocess
import tempfile
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from .core import WorkflowError

IMAGE_RE = re.compile(r"^(?:sha256:[a-f0-9]{64}|[a-z0-9][a-z0-9./_:-]*@sha256:[a-f0-9]{64})$")
TOOLS = {
    "pytest": ("python", "-m", "pytest", "-p", "no:cacheprovider", "-q", "tests/golden", "--junitxml=/reports/junit.xml"),
    "ruff": ("ruff", "check", "--no-cache", "--output-format", "json", "app"),
    "bandit": ("bandit", "-r", "app", "-f", "json"),
}
AC_CASES = {
    "AC-001": "test_ac001_owner_updates_profile_and_persists",
    "AC-002": "test_ac002_missing_or_invalid_identity_denied",
    "AC-003": "test_ac003_other_owner_forbidden_and_storage_unchanged",
    "AC-004": "test_ac004_invalid_payload_rejected_without_partial_write",
    "AC-005": "test_ac005_audit_contains_metadata_without_contact_values",
    "AC-006": "test_ac006_storage_failure_is_generic_and_atomic",
}


@dataclass(frozen=True)
class ToolResult:
    tool: str
    status: str
    exit_code: int
    parsed: bool
    report: dict[str, Any]
    output_digest: str


def parse_junit(path: Path) -> dict[str, Any]:
    if path.is_symlink() or not path.is_file() or path.stat().st_size > 2_000_000:
        raise WorkflowError("JUnit report missing or unsafe")
    try:
        root = ET.fromstring(path.read_bytes())
    except ET.ParseError as exc:
        raise WorkflowError("JUnit report malformed") from exc
    cases = list(root.iter("testcase"))
    if not cases:
        raise WorkflowError("JUnit report contains no tests")
    rows = [(node.attrib.get("name"), node.find("failure") is None and
             node.find("error") is None and node.find("skipped") is None)
            for node in cases]
    names = [name for name, _ in rows]
    if len(names) != len(set(names)):
        raise WorkflowError("JUnit report contains duplicate test names")
    passed = {name for name, good in rows if good}
    return {
        "passing_ac_ids": sorted(ac for ac, test in AC_CASES.items() if test in passed),
        "failed": sum(not good for _, good in rows),
        "skipped": sum(node.find("skipped") is not None for node in cases),
        "total": len(cases),
    }


def parse_tool(tool: str, result_code: int, raw: str, reports: Path) -> tuple[bool, dict]:
    if tool == "pytest":
        try:
            report = parse_junit(reports / "junit.xml")
        except WorkflowError:
            return False, {"reason": "missing/malformed JUnit"}
        return True, report
    try:
        data = json.loads(raw)
    except ValueError:
        return False, {"reason": "non-JSON tool output"}
    if tool == "ruff":
        if not isinstance(data,list):
            return False, {"reason": "Ruff output not a list"}
        return True, {"violation_count":len(data)}
    if tool == "bandit":
        if not isinstance(data,dict) or not isinstance(data.get("results"),list):
            return False, {"reason": "Bandit results malformed"}
        high=sum(f.get("issue_severity")=="HIGH" for f in data["results"] if isinstance(f,dict))
        unknown=sum(f.get("issue_severity") not in {"HIGH","MEDIUM","LOW"} for f in data["results"] if isinstance(f,dict))
        return True,{"high_count":high,"unknown_count":unknown,"total":len(data["results"])}
    raise WorkflowError("unsupported validation tool")


class DockerRunner:
    def __init__(self, image: str, workspace: str | Path):
        if not IMAGE_RE.fullmatch(image):
            raise WorkflowError("Docker image must be pinned to a sha256 image ID or registry digest")
        root=Path(workspace).resolve()
        if not root.is_dir() or root.is_symlink():
            raise WorkflowError("workspace must be a real directory")
        self.image=image
        self.workspace=root

    def validate(self, tool: str, timeout: int=120) -> ToolResult:
        if tool not in TOOLS:
            raise WorkflowError("unapproved deterministic tool")
        if timeout<=0 or timeout>300:
            raise WorkflowError("tool timeout must be between 1 and 300 seconds")
        if shutil.which("docker") is None:
            raise WorkflowError("Docker unavailable; refusing unsafe host fallback")
        with tempfile.TemporaryDirectory(prefix="atomic-tool-") as tmp:
            out=Path(tmp)
            out.chmod(0o777)  # writable to isolated unprivileged uid
            cmd=["docker","run","--rm","--network=none","--read-only",
                 "--cap-drop=ALL","--security-opt=no-new-privileges",
                 "--user=65534:65534","--pids-limit=64","--memory=512m","--cpus=1",
                 "--tmpfs=/tmp:rw,noexec,nosuid,nodev,size=64m",
                 "--mount",f"type=bind,src={self.workspace},dst=/work,readonly",
                 "--mount",f"type=bind,src={out},dst=/reports",
                 "--workdir=/work","--env=HOME=/tmp","--env=PYTHONDONTWRITEBYTECODE=1",
                 self.image,*TOOLS[tool]]
            try:
                proc=subprocess.run(cmd,text=True,stdout=subprocess.PIPE,stderr=subprocess.PIPE,
                                    timeout=timeout,check=False)
            except subprocess.TimeoutExpired:
                return ToolResult(tool,"TIMED_OUT",124,False,{"reason":"execution timed out"},"")
            # Do not persist arbitrary tool text. Only a digest and parsed aggregate.
            output_digest=hashlib.sha256((proc.stdout+proc.stderr).encode()).hexdigest()
            parsed,report=parse_tool(tool,proc.returncode,proc.stdout,out)
            if tool=="ruff" and report.get("violation_count",0)>0:
                parsed=True  # parser succeeded; exit code is authoritative
            if tool=="bandit" and report.get("unknown_count",0)>0:
                parsed=False  # unrecognized severity must fail closed
            return ToolResult(tool,"COMPLETED" if proc.returncode==0 else "FAILED",
                              proc.returncode,parsed,report,output_digest)


def parse_trusted_dependency_audit(payload: dict, lock_sha256: str) -> tuple[bool,dict]:
    """Review a TRUSTED bootstrap artifact, never execute pip-audit in agent sandbox."""
    if not re.fullmatch(r"[a-f0-9]{64}",lock_sha256):
        return False,{"reason":"invalid dependency lock hash"}
    if (not isinstance(payload,dict) or payload.get("lock_sha256")!=lock_sha256
        or payload.get("complete") is not True or not isinstance(payload.get("dependencies"),list)
        or not isinstance(payload.get("advisory_snapshot_sha256"),str)
        or not re.fullmatch(r"[a-f0-9]{64}",payload["advisory_snapshot_sha256"])):
        return False,{"reason":"incomplete/mismatched trusted audit"}
    dependencies=payload["dependencies"]
    if not dependencies or any(not isinstance(row,dict) or "name" not in row or
                               "version" not in row or not isinstance(row.get("vulns"),list)
                               for row in dependencies):
        return False,{"reason":"incomplete dependency inventory"}
    problems=sum(len(row["vulns"]) for row in dependencies)
    return problems==0,{"complete":True,"dependency_count":len(dependencies),"vulnerabilities":problems}
