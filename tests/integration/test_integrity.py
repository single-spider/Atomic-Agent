import hashlib
import json
import shutil

import pytest

from atomic_agent.core import WorkflowError
from atomic_agent.demo import FIXTURE
from atomic_agent.integrity import verify_source_revision, verify_frozen_inputs


def test_expected_fixture_passes_revision_and_golden_hashes(tmp_path):
    work=tmp_path/'fixture'
    shutil.copytree(FIXTURE,work,ignore=shutil.ignore_patterns('__pycache__','.pytest_cache'))
    rev=hashlib.sha256((work/'app/main.py').read_bytes()).hexdigest()
    manifest=json.loads((FIXTURE/'FROZEN.json').read_text())['sha256']
    verify_source_revision(work,rev)
    verify_frozen_inputs(work,manifest)


def test_source_and_golden_tampering_fail_closed(tmp_path):
    work=tmp_path/'fixture'
    shutil.copytree(FIXTURE,work,ignore=shutil.ignore_patterns('__pycache__','.pytest_cache'))
    rev=hashlib.sha256((work/'app/main.py').read_bytes()).hexdigest()
    manifest=json.loads((FIXTURE/'FROZEN.json').read_text())['sha256']
    (work/'app/main.py').write_text('# modified')
    with pytest.raises(WorkflowError,match='does not match'):
        verify_source_revision(work,rev)
    (work/'tests/golden/test_acceptance.py').write_text('# test overwritten')
    with pytest.raises(WorkflowError,match='frozen input modified'):
        verify_frozen_inputs(work,manifest)
    with pytest.raises(WorkflowError,match='manifest missing'):
        verify_frozen_inputs(work,{})
