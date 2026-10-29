#!/usr/bin/env python3
"""Unregistered conditional three-colony right-template certificate."""
from pathlib import Path
from bisect import bisect_right
import hashlib,json,subprocess,sys,tempfile,time
ROOT=Path(__file__).resolve().parents[4]
SOURCE=Path(__file__).resolve().parent
REGISTERED=SOURCE.parent
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(REGISTERED))
import literal_maintenance as literal

Q=8192;U=1048576;START=96*Q-2;END=100*Q


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def get(segments,x):
    if x<0:return 1
    if x>=3*Q:return 0
    i=bisect_right([a for a,b,v in segments],x)-1
    assert i>=0 and segments[i][0]<=x<segments[i][1]
    return segments[i][2]


def point(segments,x,t):
    a={j:get(segments,x+j) for j in range(-5,6)}
    r=x%Q
    L=int(sum(a[-j]&1 for j in range(1,6))>=3)
    R=int(sum(a[j]&1 for j in range(1,6))>=3)
    inside=[j for j in range(-5,6) if 0<=r+j<Q]
    I=sum((a[j]&1)!=R for j in inside if j<0)
    H=sum((a[j]>>1)&1 for j in inside if j>0)
    W=sum((a[j]>>2)&1 for j in inside)
    F=int(I>=3 or W>=3 or H>=3 or ((a[0]>>1)&1 and H>=2))
    label=L if F else R
    age=t+1+label
    nextW=int(r>=Q-5 and 96*Q<=age<98*Q)
    return label+2*F+4*nextW


def scalar_point(segments,x,t):
    raw={}
    for j in range(-5,6):
        value=get(segments,x+j)
        raw[j]=dict(addr=(x+j)%Q,age=(t+(value&1))%U,
            f1=(value>>1)&1,f2=0,wf1=(value>>2)&1,wf2=0)
    new=literal.scalar(raw)
    assert new['addr']==x%Q and new['f2']==0
    label=new['age']-(t+1)
    assert label in (0,1)
    nextW=int(new['addr']>=Q-5 and 96*Q<=new['age']<98*Q)
    return label+2*new['f1']+4*nextW


def cuts(segments):
    c={0,3*Q}
    for a,b,v in segments:
        for e in (a,b):
            c.update(e-d for d in range(-5,6) if 0<=e-d<=3*Q)
    for b in range(4):
        c.update(b*Q-d for d in range(-5,6) if 0<=b*Q-d<=3*Q)
    c.update(b*Q+Q-5 for b in range(3))
    return sorted(c)


def calculate():
    kernel=SOURCE/'ge3_right_three_colony_pulse.c'
    with tempfile.TemporaryDirectory(prefix='GE3_right_template_') as temp:
        binary=Path(temp)/'right_template'
        command=['cc','-O2','-std=c11',str(kernel),'-o',str(binary)]
        subprocess.run(command,check=True,capture_output=True)
        output=subprocess.run([str(binary)],check=True,capture_output=True,text=True).stdout
        result=json.loads(output);binary_sha=digest(binary)
    assert result['all_updated_rows']==4*Q+2
    assert result['first_complete_clock_row']==797352
    assert result['first_quiet_native_row']==806911
    assert result['final_quiet_right_template']
    rows=result['retained_rows'];checks=0;consecutive=0;signature=hashlib.sha256()
    for i,row in enumerate(rows):
        t=row['relative_period_row'];segments=row['segments']
        assert segments[0][0]==0 and segments[-1][1]==3*Q
        assert all(0<=a<b<=3*Q and 0<=v<8 for a,b,v in segments)
        assert all(b==segments[k+1][0] for k,(a,b,v) in enumerate(segments[:-1]))
        partition=cuts(segments)
        for a,b in zip(partition,partition[1:]):
            for x in (a,b-1):
                expected=point(segments,x,t)
                actual=scalar_point(segments,x,t)
                assert actual==expected,(t,x,actual,expected)
                if i+1<len(rows) and rows[i+1]['relative_period_row']==t+1:
                    assert get(rows[i+1]['segments'],x)==expected
                    consecutive+=1
                signature.update(json.dumps((t,x,actual)).encode());checks+=1
    assert rows[-1]['segments']==[[0,2*Q,1],[2*Q,3*Q,3]]
    horizon=END-START
    assert 13*Q-5>3*horizon
    return dict(native_event_kernel=result,kernel_binary_sha256=binary_sha,
        compile_argv_without_temporary_binary=command[:-1],
        native_scalar_endpoint_checks=checks,consecutive_retained_update_checks=consecutive,
        endpoint_trace_sha256=signature.hexdigest(),
        H=horizon,sufficient_width_m_minimum_for_stated_shield_bound=13,
        width13_right_guard_margin=13*Q-5-3*horizon,
        universal_minimum_width_or_unchanged_left_endpoint_proved=False)


def receipt():
    directory=ROOT/'figs/gray_counterexamples/unregistered_ge3'
    manifest=directory/'GE3_right_template_initial_failure_manifest.json'
    retained=json.loads(manifest.read_text())
    for name,value in retained['assets_sha256'].items():assert digest(directory/name)==value
    return dict(Q=Q,U=U,lambda_original=24,c_original=104,
        checker_sha256=digest(__file__),kernel_sha256=digest(SOURCE/'ge3_right_three_colony_pulse.c'),
        proof_sha256=digest(SOURCE/'GE3_RIGHT_TEMPLATE.md'),
        native_scalar_sha256=digest(REGISTERED/'literal_maintenance.py'),
        accepted_quotient_proof_sha256=digest(REGISTERED/'GE0_FIRST_WORKSPACE_NATIVE.md'),
        accepted_quotient_receipt_sha256=digest(ROOT/'figs/gray_counterexamples/GE0_first_workspace_native_certificate.json'),
        retained_initial_checker_failure_manifest_sha256=digest(manifest),
        retained_initial_checker_failure_assets_sha256=retained['assets_sha256'],
        results=calculate(),
        conditional_right_local_pulse_theorem=True,
        exact_new_right_commands_and_held_final_sources_are_premises=True,
        left_commands_and_left_boundary_evolution_not_suppressed=True,
        later_actual_bank_mirror_head_or_positive_Flag2_history_proved=False,
        full_Gray_own_beta_iid_or_shorter_U_result_proved=False,
        registered_artifacts_changed=False)


if __name__=='__main__':
    started=time.monotonic();r=receipt();r['elapsed_seconds']=time.monotonic()-started
    path=ROOT/'figs/gray_counterexamples/unregistered_ge3/GE3_right_template_certificate.json'
    path.parent.mkdir(exist_ok=True);path.write_text(json.dumps(r,sort_keys=True,indent=2)+'\n')
    print(json.dumps(dict(receipt=str(path),receipt_sha256=digest(path),
        scalar_checks=r['results']['native_scalar_endpoint_checks'],
        elapsed_seconds=r['elapsed_seconds'],only_conditional_right_template=True)))
