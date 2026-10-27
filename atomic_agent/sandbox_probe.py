"""Development-only real Docker boundary probes, never a certification claim."""
from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import tempfile
import uuid
from pathlib import Path

from .core import WorkflowError
from .runner import DockerRunner

PROBE_CODE = '''import os,socket
from pathlib import Path
assert not Path('/var/run/docker.sock').exists(), 'docker socket exposed'
assert not any(k in os.environ for k in ('DEEPSEEK_API_KEY','LLM_API_KEY','OPENAI_API_KEY'))
try:
    Path('/work/app/main.py').write_text('overwrite attempt')
except (OSError,PermissionError):
    pass
else:
    raise AssertionError('read-only mount allowed modification')
try:
    socket.socket().connect(('1.1.1.1',443))
except OSError:
    pass
else:
    raise AssertionError('network egress allowed')
print('BOUNDARY_DENIALS_VERIFIED')
'''


def docker_command(image: str, workspace: Path, *command: str) -> list[str]:
    """Reproduce the worker restrictions for hard-coded CI probes."""
    return ["docker","run","--rm","--network=none","--read-only",
            "--cap-drop=ALL","--security-opt=no-new-privileges",
            "--user=65534:65534","--pids-limit=64","--memory=512m","--cpus=1",
            "--tmpfs=/tmp:rw,noexec,nosuid,nodev,size=64m",
            "--mount",f"type=bind,src={workspace},dst=/work,readonly",
            "--workdir=/work","--env=HOME=/tmp","--env=PYTHONDONTWRITEBYTECODE=1",
            image,*command]


def probe(image: str, workspace: Path) -> dict:
    # DockerRunner validates digest form and real workspace before any command.
    worker=DockerRunner(image,workspace)
    if not shutil.which('docker'):
        raise WorkflowError('Docker unavailable; no host fallback')
    cmd=docker_command(image,worker.workspace,'python','-c',PROBE_CODE)
    p=subprocess.run(cmd,capture_output=True,text=True,timeout=20,check=False)
    if p.returncode or 'BOUNDARY_DENIALS_VERIFIED' not in p.stdout:
        raise WorkflowError('network/filesystem/credential boundary probe failed')
    checks={}
    for tool in ('pytest','ruff','bandit'):
        result=worker.validate(tool,timeout=60)
        checks[tool]={"status":result.status,"exit_code":result.exit_code,
                      "parsed":result.parsed,"report":result.report}
        if not result.parsed:
            raise WorkflowError(f'{tool} report could not be parsed')
    # Baseline must fail authorization deliberately. No false READY allowed.
    junit=checks['pytest']['report']
    if checks['pytest']['exit_code'] != 1 or 'AC-003' in junit.get('passing_ac_ids',[]):
        raise WorkflowError('expected baseline authorization defect not observed')
    if not {'AC-001','AC-002','AC-004','AC-005','AC-006'} <= set(junit.get('passing_ac_ids',[])):
        raise WorkflowError('other mandatory acceptance tests did not pass')
    return {"status":"DEVELOPMENT_BOUNDARY_AND_BASELINE_CHECKED","image":image,
            "tests":checks,"security_probes":["no-network","read-only-source","no-docker-socket","no-model-keys"]}


def main() -> int:
    parser=argparse.ArgumentParser()
    parser.add_argument('--image',required=True,help='immutable Docker image ID or repo digest')
    parser.add_argument('--workspace',default='fixtures/customer_profile')
    args=parser.parse_args()
    result=probe(args.image,Path(args.workspace))
    print(json.dumps(result,indent=2))
    return 0


if __name__=='__main__':
    raise SystemExit(main())
