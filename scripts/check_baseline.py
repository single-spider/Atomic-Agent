"""Run golden Pytest and confirm the intentionally broken baseline fails only AC-003.

This script is for trusted fixture authoring and does not implement the
untrusted-code sandbox, version pinning, or the ADR-012 live preflight.
"""
from __future__ import annotations

import argparse
import subprocess
import sys
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
GOLDEN = ROOT / "fixtures/customer_profile/tests/golden"
EXPECTED_CASES = {
    "test_ac001_owner_updates_profile_and_persists",
    "test_ac002_missing_or_invalid_identity_denied",
    "test_ac003_other_owner_forbidden_and_storage_unchanged",
    "test_ac004_invalid_payload_rejected_without_partial_write",
    "test_ac005_audit_contains_metadata_without_contact_values",
    "test_ac006_storage_failure_is_generic_and_atomic",
    "test_openapi_contract_and_missing_resource",
}


def main() -> int:
    parser = argparse.ArgumentParser(description="Check fixture baseline or repaired outcome")
    parser.add_argument("--repaired", action="store_true", help="All golden cases must pass")
    args = parser.parse_args()
    with tempfile.TemporaryDirectory() as temp:
        xml = Path(temp) / "golden.xml"
        result = subprocess.run(
            [sys.executable, "-m", "pytest", "-q", str(GOLDEN), f"--junitxml={xml}"],
            cwd=ROOT,
            check=False,
            capture_output=True,
            text=True,
            timeout=120,
        )
        if not xml.exists():
            print("FAIL no machine-readable test report")
            print(result.stdout[-1600:])
            return 1
        try:
            tree = ET.parse(xml)
        except ET.ParseError:
            print("FAIL malformed JUnit XML")
            return 1
        cases = list(tree.iter("testcase"))
        names = {c.attrib.get("name") for c in cases}
        failed = {
            c.attrib.get("name")
            for c in cases if c.find("failure") is not None or c.find("error") is not None
        }
        skipped = {c.attrib.get("name") for c in cases if c.find("skipped") is not None}
        expected_failed = set() if args.repaired else {"test_ac003_other_owner_forbidden_and_storage_unchanged"}
        okay = names == EXPECTED_CASES and failed == expected_failed and not skipped
        okay &= result.returncode == (0 if args.repaired else 1)
        if not okay:
            print(f"FAIL actual_cases={sorted(names)} failed={sorted(failed)} skipped={sorted(skipped)}")
            print(result.stdout[-1600:])
            return 1
        print(f"PASS {'repaired' if args.repaired else 'intentionally failing baseline'}: "
              f"{len(cases) - len(failed)} pass / {len(failed)} expected failure")
        return 0


if __name__ == "__main__":
    raise SystemExit(main())
