"""Verify SHA-256 of golden fixture files; no agent may update FROZEN.json."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FROZEN = ROOT / "fixtures/customer_profile/FROZEN.json"


def verify() -> list[str]:
    document = json.loads(FROZEN.read_text(encoding="utf-8"))
    errors: list[str] = []
    for name, expected in document["sha256"].items():
        path = ROOT / "fixtures/customer_profile" / name
        if not path.exists():
            errors.append(f"missing: {name}")
            continue
        observed = hashlib.sha256(path.read_bytes()).hexdigest()
        if observed != expected:
            errors.append(f"hash mismatch: {name}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.parse_args()
    failures = verify()
    if failures:
        for failure in failures:
            print(f"FAIL {failure}")
        return 1
    print("PASS frozen fixture content hashes verified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
