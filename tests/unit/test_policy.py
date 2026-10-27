import hashlib
from pathlib import Path

from spike.policy import (
    DesignApproval,
    approval_allows_dispatch,
    can_reserve_cost,
    redact_fixture_canaries,
    tool_passes,
    validate_candidate_paths,
)


def approval():
    return DesignApproval("local-operator", "design-approver", True, "d123", "p123", ("app/main.py",))


def test_design_approval_version_bound_and_human():
    assert approval_allows_dispatch(approval(), current_design_hash="d123", current_policy_hash="p123", requested_paths=("app/main.py",))
    assert not approval_allows_dispatch(None, current_design_hash="d123", current_policy_hash="p123", requested_paths=("app/main.py",))
    assert not approval_allows_dispatch(approval(), current_design_hash="stale", current_policy_hash="p123", requested_paths=("app/main.py",))
    assert not approval_allows_dispatch(approval(), current_design_hash="d123", current_policy_hash="changed", requested_paths=("app/main.py",))
    assert not approval_allows_dispatch(approval(), current_design_hash="d123", current_policy_hash="p123", requested_paths=("tests/golden/test_acceptance.py",))


def test_paths_reject_escape_and_symlink(tmp_path):
    (tmp_path / "app").mkdir()
    (tmp_path / "app" / "main.py").write_text("ok")
    assert validate_candidate_paths(tmp_path, ["app/main.py"], {"app/main.py"})
    assert not validate_candidate_paths(tmp_path, ["../host.py"], {"../host.py"})
    assert not validate_candidate_paths(tmp_path, ["tests/golden.py"], {"app/main.py"})
    outside = tmp_path.parent / "outside-file.py"
    outside.write_text("outside")
    (tmp_path / "link").symlink_to(outside)
    assert not validate_candidate_paths(tmp_path, ["link"], {"link"})
    outside.unlink()


def test_budget_is_fail_closed():
    assert can_reserve_cost("5", "4.99")
    for remaining, reservation in [("5", "5.01"), ("", "1"), ("nan", "1"), ("-1", "1"), ("3", "inf")]:
        assert not can_reserve_cost(remaining, reservation)


def test_tool_reports_cannot_fake_pass_or_use_stale_revision():
    good = dict(revision="sha-new", status="COMPLETED", exit_code=0, parsed=True, evidence_sha256=hashlib.sha256(b"ok").hexdigest())
    assert tool_passes(good, revision="sha-new")
    assert not tool_passes(good, revision="sha-old")
    assert not tool_passes(dict(good, exit_code=1), revision="sha-new")
    assert not tool_passes(dict(good, parsed=False), revision="sha-new")
    assert not tool_passes(dict(good, exit_code=False), revision="sha-new")
    assert not tool_passes(None, revision="sha-new")


def test_canary_redaction():
    result = redact_fixture_canaries("value=CANARY-LOCAL and again CANARY-LOCAL", ("CANARY-LOCAL",))
    assert "CANARY-LOCAL" not in result and result.count("[REDACTED]") == 2


def test_static_preflight_blocks_absent_authorization():
    from spike.preflight import check_configuration
    assert any("operator" in item for item in check_configuration({}))
    assert any("model.spend_approved" in item for item in check_configuration({}))
