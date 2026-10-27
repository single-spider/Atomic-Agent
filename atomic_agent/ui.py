"""No-build, single-operator SDLC dashboard; client stores token only in memory."""
from __future__ import annotations

PAGE = r'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Atomic-Agent | SDLC Control Plane</title>
<style>
:root{color-scheme:dark;font-family:ui-sans-serif,system-ui,Arial;background:#0b101a;color:#eff5ff}
*{box-sizing:border-box}body{margin:0;background:radial-gradient(circle at 78% 1%,#182840,transparent 50%),#0b101a}
header{padding:26px max(22px,calc((100vw - 1080px)/2));border-bottom:1px solid #2b384a;display:flex;justify-content:space-between;gap:20px;align-items:center}
h1{font-size:23px;letter-spacing:-.04em;margin:0}header p,small{color:#93a8c2}header p{font-size:13px;margin:7px 0 0}
main{max-width:1080px;margin:26px auto;padding:0 18px;display:grid;grid-template-columns:330px minmax(0,1fr);gap:18px}
section{background:#121c2b;border:1px solid #2a3b52;border-radius:14px;padding:20px;margin-bottom:18px;box-shadow:0 12px 25px #060c1533}
h2{font-size:15px;font-weight:700;margin:0 0 15px}label{display:block;font-size:12px;color:#b8cce5;margin:13px 0 6px}
input,textarea,select{background:#0a1321;border:1px solid #334a66;color:#f4f7ff;padding:10px 11px;border-radius:8px;width:100%;font:13px inherit;outline:none}
textarea{font-family:ui-monospace,monospace;min-height:94px;resize:vertical}button{color:#eff8ff;cursor:pointer;background:#24405d;border:1px solid #456387;border-radius:8px;padding:10px 12px;font-weight:650}
button:hover{background:#315676}button.primary{background:#416ee8;border-color:#6f9cff}button.primary:hover{background:#587ef0}
.buttons{display:flex;flex-wrap:wrap;gap:8px;margin-top:14px}.row{display:flex;align-items:center;justify-content:space-between;gap:12px}.mono{font-family:ui-monospace,monospace;overflow-wrap:anywhere;font-size:12px}
.pill{padding:5px 9px;border:1px solid #53728b;border-radius:99px;color:#caebff;font-size:11px}
.timeline{display:flex;flex-direction:column;gap:10px;max-height:340px;overflow:auto}.event{border-left:2px solid #486bb5;padding:2px 10px}.event b{font-size:12px}.event p{color:#94abc8;font-size:11px;margin:6px 0 2px}
#message{padding:10px 14px;background:#1a3043;border-radius:8px;min-height:38px;white-space:pre-wrap;overflow-wrap:anywhere}
#artifacts .item{padding:10px 0;border-bottom:1px solid #283950;font-size:12px}#artifacts .item:last-child{border:0}
footer{color:#8ea7c7;text-align:center;font-size:12px;padding:24px}
@media(max-width:800px){main{display:block}header{padding:22px}section{padding:16px}}
</style></head><body>
<header><div><h1>◈ Atomic-Agent</h1><p>Engineering control plane · Human-governed SDLC · Experimental MVP</p></div><span class="pill">No automatic deployment</span></header>
<main><div>
<section><h2>Operator session</h2><label for="token">Local operator token</label><input id="token" type="password" autocomplete="off" placeholder="Enter ATOMIC_OPERATOR_TOKEN"><small>Kept in page memory only. Do not expose this server publicly.</small>
<label for="actor">Operator ID</label><input id="actor" placeholder="Same as ATOMIC_OPERATOR_ID"></section>
<section><h2>New feature request</h2><label for="title">Title</label><input id="title" placeholder="Update contact API"><label for="requirement">Structured feature JSON</label><textarea id="requirement">{"feature":"Allow authenticated customers to update their own contact fields"}</textarea>
<div class="buttons"><button class="primary" id="create">Create run</button></div></section>
<section><h2>Open an existing run</h2><label for="runid">Run ID</label><input id="runid" class="mono" placeholder="32-character run ID"><div class="buttons"><button id="refresh">Load / Refresh</button><button id="copy">Copy ID</button></div></section>
</div><div>
<section><div class="row"><h2>Run status</h2><span id="stage" class="pill">No run loaded</span></div><p id="message">Create a run or enter an existing ID to begin.</p><div id="summary" class="mono"></div></section>
<section><h2>Submit reviewable artifact</h2><label for="kind">SDLC artifact</label><select id="kind"><option>requirements</option><option>stories</option><option>criteria</option><option>design</option><option>code</option></select>
<label for="body">Artifact JSON (proposal)</label><textarea id="body">{"functional":["Update only the requester's profile"]}</textarea><label for="revision">Code revision (code artifact only)</label><input id="revision" placeholder="Verified Git commit / worktree hash"><div class="buttons"><button id="submit">Save artifact</button><button id="approve">Approve current stage</button><button id="assess">Evaluate release gates</button></div><div class="buttons"><button id="analyze">Agent: Analyze</button><button id="design">Agent: Design</button><button id="tests">Agent: Propose tests</button></div><small>Agent-generated proposals require human review. Validation passes only on real trusted tool evidence.</small></section>
<section><h2>Artifact versions</h2><div id="artifacts"><small>None loaded.</small></div></section>
<section><h2>Workflow events</h2><div id="timeline" class="timeline"><small>None loaded.</small></div></section>
</div></main><footer>Local prototype · No anonymous approvals · No trusted tool-results upload API</footer>
<script>
const E=id=>document.getElementById(id);
const state={run:null};
async function call(path,method='GET',body){const token=E('token').value; const options={method,headers:{'X-Atomic-Operator-Token':token}};
if(body!==undefined){options.headers['Content-Type']='application/json';options.body=JSON.stringify(body)}
const response=await fetch(path,options);let data;try{data=await response.json()}catch{data={detail:'Unexpected server response'}}
if(!response.ok)throw Error(typeof data.detail==='string'?data.detail:JSON.stringify(data.detail));return data;}
function msg(text){E('message').textContent=text}
function line(container,text,cls='item'){let d=document.createElement('div');d.className=cls;d.textContent=text;container.appendChild(d)}
async function refresh(){const id=E('runid').value.trim();if(!id)return msg('Enter a run ID');const data=await call('/runs/'+encodeURIComponent(id));state.run=data;
E('stage').textContent=data.stage;E('summary').textContent='Run '+data.id+' · version '+data.version+' · '+data.artifacts.length+' artifacts';
const artifacts=E('artifacts');artifacts.replaceChildren();for(const a of data.artifacts){line(artifacts,a.kind+' · '+a.content_hash.slice(0,16)+'…'+(a.revision?' · rev '+a.revision:''))}
const timeline=E('timeline');timeline.replaceChildren();for(const event of data.events.slice().reverse()){let node=document.createElement('div');node.className='event';let h=document.createElement('b');h.textContent=event.type;node.appendChild(h);
let p=document.createElement('p');p.textContent=event.created_at+' · '+JSON.stringify(event.data);node.appendChild(p);timeline.appendChild(node)}msg('Loaded '+data.title)}
function handle(fn){return async()=>{try{await fn()}catch(e){msg('Error: '+e.message)}}}
E('create').onclick=handle(async()=>{const data=await call('/runs','POST',{title:E('title').value,requirement:JSON.parse(E('requirement').value)});E('runid').value=data.id;await refresh()});
E('refresh').onclick=handle(refresh);
E('copy').onclick=handle(async()=>{await navigator.clipboard.writeText(E('runid').value);msg('Run ID copied')});
E('submit').onclick=handle(async()=>{const kind=E('kind').value;const body=JSON.parse(E('body').value);await call('/runs/'+E('runid').value+'/artifacts','POST',{kind,body,revision:kind==='code'?E('revision').value:null});await refresh()});
E('approve').onclick=handle(async()=>{if(!state.run)throw Error('Load a run first');const stage=state.run.stage;
const kind=stage==='REQUIREMENTS'?'requirements':stage==='DESIGN_APPROVAL'?'design':stage==='RELEASE_APPROVAL'?'release':null;
if(!kind)throw Error('Current stage does not accept approval');const wanted=kind==='release'?'assessment':kind;
const a=state.run.artifacts.filter(x=>x.kind===wanted).at(-1);if(!a)throw Error('Required artifact missing');
await call('/runs/'+E('runid').value+'/approvals','POST',{kind,actor:E('actor').value,artifact_hash:a.content_hash,decision:'APPROVED'});await refresh()});
E('analyze').onclick=handle(async()=>{await call('/runs/'+E('runid').value+'/agent/analyze','POST');await refresh()});
E('design').onclick=handle(async()=>{await call('/runs/'+E('runid').value+'/agent/design','POST');await refresh()});
E('tests').onclick=handle(async()=>{const v=await call('/runs/'+E('runid').value+'/agent/propose-tests','POST');msg('Generated test proposals: '+JSON.stringify(v.proposals))});
E('assess').onclick=handle(async()=>{const r=await call('/runs/'+E('runid').value+'/assess','POST');await refresh();msg(r.status+' · '+(r.problems.length?r.problems.join('; '):'Mandatory gates passed'))});
</script></body></html>'''
