from pathlib import Path
from unittest.mock import patch

from atomic_agent.demo import FIXTURE, reference_repair, run_fixture_demo, source_sha
from atomic_agent.runner import ToolResult


def test_reference_fix_is_scoped_to_copy_and_preserves_original(tmp_path):
    import shutil
    directory=tmp_path/'fixture'
    shutil.copytree(FIXTURE,directory,ignore=shutil.ignore_patterns('__pycache__','.pytest_cache'))
    before=source_sha(directory)
    original_hash=source_sha(FIXTURE)
    reference_repair(directory)
    assert source_sha(directory)!=before
    assert source_sha(FIXTURE)==original_hash
    assert 'status_code=403' in (directory/'app/main.py').read_text()


def test_no_design_approval_does_not_run_code(tmp_path):
    output=run_fixture_demo('sha256:'+'a'*64,'synthetic-operator',design_approved=False)
    assert output['status']=='WAITING_FOR_DESIGN_APPROVAL'


def test_mocked_docker_lifecycle_is_not_ready_without_dependency_audit():
    def fake_validate(self,tool,timeout=120):
        if tool=='pytest':
            source=(self.workspace/'app/main.py').read_text()
            repaired='status_code=403' in source
            passing=[f'AC-{i:03}' for i in range(1,7) if repaired or i!=3]
            return ToolResult(tool,'COMPLETED' if repaired else 'FAILED',0 if repaired else 1,True,
                              {'passing_ac_ids':passing,'skipped':0,'failed':0 if repaired else 1},'digest')
        return ToolResult(tool,'COMPLETED',0,True,
                          {'high_count':0,'unknown_count':0} if tool=='bandit' else {'violation_count':0},'digest')
    with patch('atomic_agent.runner.DockerRunner.validate',new=fake_validate):
        output=run_fixture_demo('sha256:'+'a'*64,'synthetic-operator',design_approved=True)
    assert output['baseline']['exit_code']==1
    assert output['release_recommendation']['status']=='NOT_READY'
    assert any('dependency_audit' in p for p in output['release_recommendation']['problems'])
