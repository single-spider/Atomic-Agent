"""Trusted-workspace evidence checks for the synthetic harness fixture."""
from __future__ import annotations

import hashlib
import re
from pathlib import Path

from .core import WorkflowError


HASH_RE = re.compile(r"[a-f0-9]{64}\Z")


def verify_source_revision(workspace: Path, revision: str) -> None:
    if not HASH_RE.fullmatch(revision):
        raise WorkflowError("code revision must be exact sha256 source digest")
    path=workspace / "app" / "main.py"
    if path.is_symlink() or not path.is_file() or not path.resolve().is_relative_to(workspace.resolve()):
        raise WorkflowError("missing or unsafe expected source file")
    observed=hashlib.sha256(path.read_bytes()).hexdigest()
    if observed!=revision:
        raise WorkflowError("declared revision does not match source bytes")


def verify_frozen_inputs(workspace: Path, hashes: dict[str,str]) -> None:
    """Hashes must originate from the trusted control plane, not agent workspace."""
    if not hashes:
        raise WorkflowError("trusted frozen test/hash manifest missing")
    root=workspace.resolve()
    for relative,expected in hashes.items():
        if (not isinstance(relative,str) or relative.startswith("/") or ".." in relative.split("/")
            or not isinstance(expected,str) or not HASH_RE.fullmatch(expected)):
            raise WorkflowError("malformed frozen input declaration")
        path=workspace/relative
        if path.is_symlink() or not path.is_file() or not path.resolve().is_relative_to(root):
            raise WorkflowError("missing or unsafe frozen artifact")
        if hashlib.sha256(path.read_bytes()).hexdigest()!=expected:
            raise WorkflowError(f"frozen input modified: {relative}")
