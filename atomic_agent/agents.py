"""Typed agent roles and a replaceable harness boundary.

No default provider/model is silently selected. The deterministic demonstration
adapter is test-only and cannot produce release tool evidence.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Protocol

from .core import WorkflowError


@dataclass(frozen=True)
class Profile:
    name: str
    goal: str
    output_keys: tuple[str, ...]
    may_edit_code: bool = False


PROFILES = {
    "business_analyst": Profile("business_analyst", "Extract explicit requirements, assumptions, stories, acceptance criteria and ambiguities. Do not silently invent missing requirements.", ("requirements", "stories", "criteria", "questions")),
    "solution_architect": Profile("solution_architect", "Create an API, data, component, validation and security design consistent with approved requirements.", ("design",)),
    "developer": Profile("developer", "Implement only an approved design within allowed source paths and report the actual change for independent verification.", ("changed_paths", "revision", "diff_sha256"), True),
    "test_engineer": Profile("test_engineer", "Propose tests for positive, negative, boundary, authorization and exception cases. Map them to acceptance criteria.", ("tests",)),
    "code_reviewer": Profile("code_reviewer", "Review diff and code against acceptance criteria and flag evidence-backed issues.", ("findings",)),
    "security_reviewer": Profile("security_reviewer", "Analyze authentication, authorization, injection, dependencies, sensitive logs and configurations; never waive findings.", ("findings",)),
    "defect_resolver": Profile("defect_resolver", "Use failure evidence to propose a minimal scoped correction; require fresh validation.", ("changed_paths", "revision", "diff_sha256"), True),
    "release_assurance": Profile("release_assurance", "Summarize deterministic gate evidence and residual risk without altering release outcomes.", ("summary",)),
}


class HarnessAdapter(Protocol):
    def invoke(self, profile: Profile, context: dict[str, Any]) -> dict[str, Any]: ...


def invoke(adapter: HarnessAdapter, role: str, context: dict) -> dict:
    if role not in PROFILES:
        raise WorkflowError("unknown agent role")
    result=adapter.invoke(PROFILES[role],context)
    if not isinstance(result,dict):
        raise WorkflowError(f"{role}: expected object output")
    missing=[key for key in PROFILES[role].output_keys if key not in result]
    if missing:
        raise WorkflowError(f"{role}: missing structured keys {missing}")
    return result


class NoHarness:
    """Explicit default: live execution is unavailable until approved and configured."""
    def invoke(self, profile: Profile, context: dict) -> dict:
        raise WorkflowError("harness unavailable: select approved runtime and pass required preflight")


class SyntheticAgentForTests:
    """Deterministic demo stand-in. Never call this an LLM or use for release proof."""
    def invoke(self, profile: Profile, context: dict) -> dict:
        match profile.name:
            case "business_analyst":
                return {
                    "requirements": {"functional": ["The owner can update profile contact information"],
                                     "nonfunctional": ["Reject unauthorized edits and avoid contact data in audit"]},
                    "stories": [{"id": "ST-001", "text": "As a customer I can safely update my own contact fields"}],
                    "criteria": [{"id": f"AC-{i:03}", "text": text} for i,text in enumerate((
                        "Allowed owner update", "Unauthenticated denied", "Other owner's profile denied",
                        "Invalid input rejected", "Value-free audit", "Storage error is generic"),1)],
                    "questions": []}
            case "solution_architect":
                return {"design": {"endpoint":"PATCH /profiles/{profile_id}","storage":"SQLite",
                                   "security":"Authenticate token and match owner_id before writes"}}
            case "test_engineer":
                return {"tests": [{"acceptance_id": f"AC-{i:03}","proposal": "Golden test required"} for i in range(1,7)]}
            case "code_reviewer" | "security_reviewer":
                return {"findings": []}
            case "release_assurance":
                return {"summary": "Run is subject to deterministic gates and human approval."}
            case _:
                raise WorkflowError("synthetic demo agent does not implement coding/remediation")
