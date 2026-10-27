import pytest

from atomic_agent.agents import NoHarness, PROFILES, SyntheticAgentForTests, invoke
from atomic_agent.core import Store, WorkflowError
from atomic_agent.orchestrator import Orchestrator


def test_eight_specialized_agent_roles():
    assert len(PROFILES)==8
    assert sum(profile.may_edit_code for profile in PROFILES.values())==2
    with pytest.raises(WorkflowError,match='unavailable'):
        invoke(NoHarness(),'business_analyst',{'request':'update profile'})


def test_deterministic_demo_moves_only_to_human_requirement_approval(tmp_path):
    store=Store(tmp_path/'agent.sqlite')
    run=store.create_run('Update contact details',{'feature':'profile edit'})
    workflow=Orchestrator(store,SyntheticAgentForTests())
    hashes=workflow.analyze(run,{'feature':'profile edit'})
    assert set(hashes)=={'requirements','stories','criteria'}
    assert store.snapshot(run)['stage']=='REQUIREMENTS'
    with pytest.raises(WorkflowError,match='cannot be submitted'):
        workflow.design(run)
    store.approve(run,'requirements','operator',hashes['requirements'],'APPROVED')
    design=workflow.design(run)
    assert design['body']['endpoint']=='PATCH /profiles/{profile_id}'
    assert store.snapshot(run)['stage']=='DESIGN_APPROVAL'
    tests=workflow.propose_tests(run)
    assert len(tests)==6
    assert workflow.summarize(run,{'status':'NOT_READY'})


def test_agent_endpoints_require_token_and_no_provider_enabled_by_default(tmp_path, monkeypatch):
    from fastapi.testclient import TestClient
    from atomic_agent.api import create_app
    monkeypatch.setenv('ATOMIC_OPERATOR_ID','operator')
    monkeypatch.setenv('ATOMIC_OPERATOR_TOKEN','development-token-for-tests')
    client=TestClient(create_app(tmp_path/'api.sqlite'))
    page=client.get('/')
    assert page.status_code==200 and 'Atomic-Agent' in page.text
    assert 'localStorage' not in page.text
    assert client.post('/runs',json={'title':'X','requirement':{'feature':'y'}}).status_code==401
    client.headers.update({'X-Atomic-Operator-Token':'development-token-for-tests'})
    run=client.post('/runs',json={'title':'X','requirement':{'feature':'y'}}).json()
    assert client.post('/runs/'+run['id']+'/agent/analyze').status_code==409
    client.close()
