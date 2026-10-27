"""Deterministic, synthetic SDLC walkthrough using a real sandbox tool runner.

This deliberately uses a *known reference repair*, not an AI coding agent.
It is useful for exercising workflow, tool dispatch, remediation, evidence and
readiness blocking without unauthorized model calls or fabricated checks.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import tempfile
from pathlib import Path

from .agents import SyntheticAgentForTests
from .core import Store, WorkflowError
from .orchestrator import Orchestrator
from .runner import DockerRunner

ROOT = Path(__file__).resolve().parents[1]
FIXTURE = ROOT / "fixtures" / "customer_profile"


def source_sha(workspace: Path) -> str:
    return hashlib.sha256((workspace / "app" / "main.py").read_bytes()).hexdigest()


def reference_repair(workspace: Path) -> None:
    """Only for a synthetic controlled fixture. Does not implement agent generation."""
    path=workspace / "app" / "main.py"
    code=path.read_text(encoding="utf-8")
    marker='                # INTENTIONAL DEFECT (AC-003): owner must match record[\'owner_id\'].\n'
    if code.count(marker)!=1:
        raise WorkflowError("synthetic fixture marker absent or ambiguous")
    fixed=code.replace(marker, marker +
        '                if record["owner_id"] != owner:\n'
        '                    raise HTTPException(status_code=403, detail="Not profile owner")\n')
    path.write_text(fixed,encoding="utf-8")


def record(workflow: Orchestrator, run_id: str, workspace: Path, image: str, revision: str) -> dict:
    return workflow.validate_in_docker(run_id,image=image,workspace=workspace,revision=revision)


def run_fixture_demo(image: str, operator: str, *, design_approved: bool) -> dict:
    if not operator.strip():
        raise WorkflowError("named operator required")
    with tempfile.TemporaryDirectory(prefix="atomic-fixture-walkthrough-") as scratch:
        workspace=Path(scratch)/"workspace"
        shutil.copytree(FIXTURE,workspace,ignore=shutil.ignore_patterns("__pycache__",".pytest_cache","*.sqlite"))
        store=Store(Path(scratch)/"control.sqlite")
        request={"feature":"Repair authorization check on synthetic profile update", "fixture_only":True}
        run_id=store.create_run("Synthetic customer profile ownership repair",request)
        workflow=Orchestrator(store,SyntheticAgentForTests())
        hashes=workflow.analyze(run_id,request)
        store.approve(run_id,"requirements",operator,hashes["requirements"],"APPROVED")
        design=workflow.design(run_id)
        if not design_approved:
            return {"run_id":run_id,"status":"WAITING_FOR_DESIGN_APPROVAL",
                    "note":"No code or tools ran; explicit --approve-synthetic-design is required",
                    "stages":[e["data"]["to"] for e in store.snapshot(run_id)["events"] if e["type"]=="StageChanged"]}
        store.approve(run_id,"design",operator,design["content_hash"],"APPROVED")
        initial=source_sha(workspace)
        store.add_artifact(run_id,"code",{"changed_paths":["app/main.py"],"kind":"synthetic pre-existing baseline"},revision=initial)
        baseline=DockerRunner(image,workspace).validate("pytest")
        store.record_evidence(run_id,"pytest",initial,status=baseline.status,exit_code=baseline.exit_code,
                              parsed=baseline.parsed,report=baseline.report,trusted_runner=True)
        if baseline.exit_code==0 or "AC-003" in baseline.report.get("passing_ac_ids",[]):
            raise WorkflowError("unexpected reference baseline result")
        store.start_remediation(run_id,"AC-003 authorization acceptance test failed",trusted_orchestrator=True)
        reference_repair(workspace)
        revised=source_sha(workspace)
        store.add_artifact(run_id,"code",{"changed_paths":["app/main.py"],"kind":"deterministic reference patch, not AI"},revision=revised)
        tools=record(workflow,run_id,workspace,image,revised)
        final_pytest=tools["pytest"]
        if (final_pytest["status"]!="COMPLETED" or not final_pytest["parsed"]):
            raise WorkflowError("synthetic reference patch failed final Pytest validation")
        # Trusted local deterministic diff-pattern scan. Not a comprehensive secret scanner.
        content=(workspace/"app"/"main.py").read_text()
        import re
        patterns=(r"-----BEGIN (?:RSA |EC )?PRIVATE KEY-----",r"AKIA[0-9A-Z]{16}",r"sk-[A-Za-z0-9]{30,}")
        detected=any(re.search(pattern,content) for pattern in patterns)
        store.record_evidence(run_id,"secrets",revised,status="FAILED" if detected else "COMPLETED",
                              exit_code=1 if detected else 0,parsed=True,
                              report={"detected":detected,"patterns_checked":len(patterns)},trusted_runner=True)
        # Dependency audit remains intentionally MISSING: no trusted
        # transitive lock/advisory attestation exists for this demo image.
        # A JSON file supplied by an agent/operator must not forge READY.
        readiness=store.assess(run_id)
        return {"run_id":run_id,"mode":"DETERMINISTIC_REFERENCE_FIXTURE",
                "baseline":{"exit_code":baseline.exit_code,"report":baseline.report},
                "repair":{"before":initial,"after":revised,"changed_paths":["app/main.py"]},
                "checks":tools,"release_recommendation":readiness,
                "note":"Synthetic developer/test infrastructure only. No live coding harness or production release."}


def main() -> int:
    parser=argparse.ArgumentParser(description="Run reference fixture through the guarded control plane")
    parser.add_argument("--image",required=True,help="reviewed immutable Docker image ID or digest")
    parser.add_argument("--operator",required=True,help="operator identifier (synthetic exercise)")
    parser.add_argument("--approve-synthetic-design",action="store_true")
    args=parser.parse_args()
    result=run_fixture_demo(args.image,args.operator,design_approved=args.approve_synthetic_design)
    print(json.dumps(result,indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
