"""Deterministic policy contract helpers; not an execution sandbox.

These functions cannot enforce OS-level network, filesystem, process or credential
isolation. Runtime boundary verification remains mandatory under ADR-012.
"""
from __future__ import annotations

import re
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from pathlib import Path, PurePosixPath
from typing import Any


@dataclass(frozen=True)
class DesignApproval:
    actor: str
    role: str
    approved: bool
    design_sha256: str
    policy_sha256: str
    writable_paths: tuple[str, ...]


def approval_allows_dispatch(
    approval: DesignApproval | None,
    *,
    current_design_hash: str,
    current_policy_hash: str,
    requested_paths: tuple[str, ...],
) -> bool:
    return bool(
        approval
        and approval.approved
        and approval.actor.strip()
        and approval.role == "design-approver"
        and approval.design_sha256 == current_design_hash
        and approval.policy_sha256 == current_policy_hash
        and set(requested_paths).issubset(set(approval.writable_paths))
        and all(is_clean_relative_path(p) for p in requested_paths)
    )


def is_clean_relative_path(value: str) -> bool:
    if not value or "\\" in value or "\x00" in value:
        return False
    path = PurePosixPath(value)
    return not path.is_absolute() and all(part not in ("..", ".") for part in value.split("/"))


def validate_candidate_paths(root: Path, changed_paths: list[str], allowed_paths: set[str]) -> bool:
    """Advisory path validator. The runtime must separately deny filesystem writes."""
    base = root.resolve()
    for relative in changed_paths:
        if not is_clean_relative_path(relative) or relative not in allowed_paths:
            return False
        candidate = (base / relative).resolve(strict=False)
        if not candidate.is_relative_to(base):
            return False
    return True


def can_reserve_cost(remaining_usd: str, worst_case_usd: str) -> bool:
    try:
        remaining = Decimal(remaining_usd)
        reservation = Decimal(worst_case_usd)
    except (InvalidOperation, TypeError):
        return False
    return all(x.is_finite() for x in (remaining, reservation)) and remaining >= reservation >= 0


def tool_passes(report: dict[str, Any] | None, *, revision: str) -> bool:
    """Fail closed on absent, stale, nonzero, malformed, or misleading reports."""
    if not isinstance(report, dict) or not revision:
        return False
    return (
        report.get("revision") == revision
        and report.get("status") == "COMPLETED"
        and type(report.get("exit_code")) is int
        and report["exit_code"] == 0
        and report.get("parsed") is True
        and isinstance(report.get("evidence_sha256"), str)
        and bool(re.fullmatch(r"[a-f0-9]{64}", report["evidence_sha256"]))
    )


def redact_fixture_canaries(text: str, canaries: tuple[str, ...]) -> str:
    """Redact configured test canaries; use separate redaction tooling for real runs."""
    redacted = text
    for canary in canaries:
        if not canary:
            raise ValueError("Canary may not be empty")
        redacted = redacted.replace(canary, "[REDACTED]")
    return redacted
