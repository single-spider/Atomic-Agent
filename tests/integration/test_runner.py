import hashlib
import shutil
from pathlib import Path
from unittest.mock import patch

import pytest

from atomic_agent.core import WorkflowError
from atomic_agent.runner import DockerRunner, parse_junit, parse_tool, parse_trusted_dependency_audit

IMAGE='atomic/validation@sha256:'+'a'*64


def test_docker_runner_fails_without_pinned_image_or_daemon(tmp_path):
    with pytest.raises(WorkflowError,match='pinned'):
        DockerRunner('python:3.12',tmp_path)
    with patch('atomic_agent.runner.shutil.which',return_value=None):
        with pytest.raises(WorkflowError,match='Docker unavailable'):
            DockerRunner(IMAGE,tmp_path).validate('pytest')


def test_docker_command_has_required_isolation_flags(tmp_path):
    def fake_run(command,**kw):
        assert '--network=none' in command
        assert '--read-only' in command
        assert '--cap-drop=ALL' in command
        assert '--user=65534:65534' in command
        assert '--security-opt=no-new-privileges' in command
        assert command[-1]=='app'
        class R:
            returncode=0
            stdout='[]'
            stderr=''
        return R()
    with patch('atomic_agent.runner.shutil.which',return_value='/usr/bin/docker'):
        with patch('atomic_agent.runner.subprocess.run',side_effect=fake_run):
            result=DockerRunner(IMAGE,tmp_path).validate('ruff')
    assert result.exit_code==0 and result.parsed


def test_junit_parser_maps_only_real_passing_tests(tmp_path):
    xml=tmp_path/'report.xml'
    xml.write_text('<testsuite><testcase name="test_ac001_owner_updates_profile_and_persists"/>'
                   '<testcase name="test_ac003_other_owner_forbidden_and_storage_unchanged"><failure/></testcase></testsuite>')
    r=parse_junit(xml)
    assert r['passing_ac_ids']==['AC-001']
    assert r['failed']==1
    xml.write_text('<testsuite><testcase name="same"/><testcase name="same"/></testsuite>')
    with pytest.raises(WorkflowError,match='duplicate'):
        parse_junit(xml)


def test_unrecognized_security_findings_fail_closed(tmp_path):
    parsed, data=parse_tool('bandit',0,'{"results":[{"issue_severity":"SOMETHING"}]}',tmp_path)
    assert parsed and data['unknown_count']==1
    parsed, data=parse_tool('ruff',0,'not json',tmp_path)
    assert not parsed


def test_dependency_audit_is_bound_to_lock(tmp_path):
    h='a'*64
    record={'lock_sha256':h,'complete':True,'advisory_snapshot_sha256':'b'*64,
            'dependencies':[{'name':'httpx','version':'0.28.1','vulns':[]}]}
    assert parse_trusted_dependency_audit(record,h)[0]
    assert not parse_trusted_dependency_audit(record,'c'*64)[0]
    record['dependencies'][0]['vulns']=[{'id':'CVE-SYNTHETIC'}]
    assert not parse_trusted_dependency_audit(record,h)[0]
