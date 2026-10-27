"""Agent dispatch around a durable, human-controlled workflow.

The module does not launch a model or claim tool execution by itself.
"""
from __future__ import annotations

from pathlib import Path
from typing import Any

from .agents import HarnessAdapter, NoHarness, invoke
from .core import Store, WorkflowError
from .runner import DockerRunner
from .integrity import verify_source_revision, verify_frozen_inputs
from spike.policy import validate_candidate_paths


class Orchestrator:
    def __init__(self, store: Store, harness: HarnessAdapter | None = None):
        self.store=store
        self.harness=harness or NoHarness()

    def analyze(self, run_id: str, request: dict) -> dict:
        result=invoke(self.harness,"business_analyst",{"run_id":run_id,"request":request})
        if result["questions"]:
            raise WorkflowError("material requirement clarifications required: human review before proceeding")
        for name in ("requirements","stories","criteria"):
            self.store.add_artifact(run_id,name,result[name])
        return {k:self.store.artifact(run_id,k)["content_hash"] for k in ("requirements","stories","criteria")}

    def design(self, run_id: str) -> dict:
        requirements=self.store.artifact(run_id,"requirements")
        criteria=self.store.artifact(run_id,"criteria")
        if not requirements or not criteria:
            raise WorkflowError("no approved requirement artifacts")
        result=invoke(self.harness,"solution_architect",{"requirements":requirements["body"],"criteria":criteria["body"]})
        self.store.add_artifact(run_id,"design",result["design"])
        return self.store.artifact(run_id,"design")

    def propose_tests(self, run_id: str) -> list:
        criteria=self.store.artifact(run_id,"criteria")
        if not criteria:
            raise WorkflowError("criteria missing")
        result=invoke(self.harness,"test_engineer",{"criteria":criteria["body"]})
        return result["tests"]  # Proposals only; never count as passed executed tests.

    def propose_code(self, run_id: str, workspace: str | Path) -> dict:
        design=self.store.artifact(run_id,"design")
        if not design:
            raise WorkflowError("approved design missing")
        result=invoke(self.harness,"developer",{"design":design["body"],"writable_paths":["app/main.py"]})
        changed=result["changed_paths"]
        if not isinstance(changed,list) or not validate_candidate_paths(Path(workspace),changed,{"app/main.py"}):
            raise WorkflowError("harness proposed forbidden or unsafe paths")
        # The revision is initially just a proposal; a sandbox verifier must
        # independently compare actual workspace contents before validation.
        self.store.add_artifact(run_id,"code",{"changed_paths":changed,
                                                "diff_sha256":result["diff_sha256"],
                                                "source":"UNVERIFIED_AGENT_PROPOSAL"},
                                revision=result["revision"])
        return result

    def inspect(self, run_id: str, diff_metadata: dict) -> list[dict]:
        findings=[]
        for name in ("code_reviewer","security_reviewer"):
            result=invoke(self.harness,name,{"run_id":run_id,"diff":diff_metadata})
            for issue in result["findings"]:
                if not isinstance(issue,dict) or not all(key in issue for key in ("severity","evidence","detail")):
                    raise WorkflowError("reviewer produced malformed finding")
                findings.append({**issue,"source":name})
        return findings

    def summarize(self, run_id: str, assessment: dict) -> str:
        response=invoke(self.harness,"release_assurance",{"run_id":run_id,"assessment":assessment})
        return str(response["summary"])

    def validate_in_docker(self, run_id: str, *, image: str, workspace: str | Path, revision: str,
                           frozen_hashes: dict[str,str]) -> dict:
        """Run fixed tools. Requires separate trusted preflight and image preparation.

        This does not provide all mandatory tools; dependency audit and secret
        scanning must be attached independently by a trusted bootstrap/runner.
        """
        snap=self.store.snapshot(run_id)
        if snap["stage"]!="VALIDATING":
            raise WorkflowError("code must be submitted before validation")
        verify_source_revision(Path(workspace), revision)
        verify_frozen_inputs(Path(workspace), frozen_hashes)
        runner=DockerRunner(image,workspace)
        results={}
        for tool in ("pytest","ruff","bandit"):
            outcome=runner.validate(tool)
            self.store.record_evidence(run_id,tool,revision,status=outcome.status,
                                       exit_code=outcome.exit_code,parsed=outcome.parsed,
                                       report=outcome.report,trusted_runner=True)
            results[tool] = {"status":outcome.status,"parsed":outcome.parsed,
                             "output_sha256":outcome.output_digest}
        return results
