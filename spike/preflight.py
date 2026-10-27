"""Static configuration linter, NOT an executable security-boundary attestation.

This module cannot grant permission to run an external harness. Even a
configuration-complete result still requires separately evidenced OS-level
sandbox, cancellation, authorization, egress and cost controls.
"""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

from spike.policy import DesignApproval, approval_allows_dispatch

SHA256 = re.compile(r"[a-f0-9]{64}\Z")


def looks_sha(value: Any) -> bool:
    return isinstance(value, str) and bool(SHA256.fullmatch(value))


def check_configuration(config: dict[str, Any]) -> list[str]:
    problems = []
    operator = config.get("operator")
    if not isinstance(operator, str) or not operator.strip():
        problems.append("named operator missing")
    for key in ("contract_sha256", "design_sha256", "policy_sha256", "fixture_lock_sha256"):
        if not looks_sha(config.get(key)):
            problems.append(f"missing or invalid {key}")
    approval_data = config.get("design_approval")
    try:
        approval = DesignApproval(
            actor=approval_data["actor"],
            role=approval_data["role"],
            approved=approval_data["approved"] is True,
            design_sha256=approval_data["design_sha256"],
            policy_sha256=approval_data["policy_sha256"],
            writable_paths=tuple(approval_data["writable_paths"]),
        )
    except (KeyError, TypeError, ValueError):
        approval = None
    if approval is not None and approval.actor != operator:
        problems.append("design approver is not the named operator")
    if not approval_allows_dispatch(
        approval,
        current_design_hash=config.get("design_sha256", ""),
        current_policy_hash=config.get("policy_sha256", ""),
        requested_paths=("app/main.py",),
    ):
        problems.append("human design approval missing, stale or overbroad")
    model = config.get("model", {})
    if not isinstance(model, dict):
        model = {}
    for key in ("provider", "model_id", "version_or_alias", "pricing_manifest_sha256"):
        if not model.get(key):
            problems.append(f"model.{key} missing")
    for key in ("data_transfer_approved", "spend_approved"):
        if model.get(key) is not True:
            problems.append(f"model.{key} not approved")
    controls = config.get("controls", {})
    if not isinstance(controls, dict):
        controls = {}
    # The listed digests are evidence references for manual/runtime verification,
    # NOT evidence that the enforcement boundaries were actually exercised.
    for key in ("sandbox_image_digest", "egress_probe_sha256", "path_probe_sha256",
                "cancel_probe_sha256", "budget_probe_sha256", "redaction_probe_sha256",
                "trusted_dependency_audit_sha256"):
        if not isinstance(controls.get(key), str) or not controls.get(key):
            problems.append(f"controls.{key} missing")
    return problems


def main() -> int:
    p = argparse.ArgumentParser(description="Check planned spike configuration (not live-run authorization)")
    p.add_argument("manifest", type=Path)
    args = p.parse_args()
    try:
        config = json.loads(args.manifest.read_text(encoding="utf-8"))
        if not isinstance(config, dict):
            raise ValueError("not a JSON object")
    except (OSError, ValueError) as exc:
        print(f"BLOCKED invalid manifest: {exc}")
        return 2
    problems = check_configuration(config)
    if problems:
        print(json.dumps({"status": "BLOCKED", "reasons": problems}, indent=2))
        return 2
    print(json.dumps({"status": "CONFIG_COMPLETE_REQUIRES_RUNTIME_VERIFICATION",
                      "note": "No harness execution or security approval is granted."}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
