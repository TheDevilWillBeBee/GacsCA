#!/usr/bin/env python3
"""Compile/replay the conditional first authentic Workspace native prefix."""
from pathlib import Path
from bisect import bisect_right
import hashlib,json,subprocess,time,sys,tempfile
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
import literal_maintenance as literal
import check_gray_global_first_flags as first

Q=8192;U=128*Q;START=96*Q-2;END=100*Q


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def at(segments,x):
    i=bisect_right([s[0] for s in segments],x)-1
    return segments[i][2] if i>=0 and x<segments[i][1] else 0


def native(segments,x,t):
    v=at(segments,x)
    return dict(addr=x%Q,age=(t+(v&1))%U,f1=(v>>1)&1,f2=0,wf1=(v>>2)&1,wf2=0)


def actual_next(segments,x,t):
    raw={j:native(segments,x+j,t) for j in range(-5,6)}
    n=literal.scalar(raw);assert n['addr']==x%Q and n['f2']==0
    label=(n['age']-(t+1))%U;assert label in (0,1)
    colony=x//Q
    wf1=int(colony in first.FLAG1_SUPPORT and x%Q>=Q-5 and 96*Q<=n['age']<98*Q)
    return label+2*n['f1']+4*wf1


def cuts(segments):
    lo=min(-2*Q-5,segments[0][0]-5);hi=max(20*Q,segments[-1][1]+5)
    points={lo,hi}
    for a,b,_ in segments:
        points.update(z-d for z in (a,b) for d in range(-5,6) if lo<=z-d<=hi)
    for colony in range(lo//Q-1,hi//Q+2):
        points.update(colony*Q-d for d in range(-5,6) if lo<=colony*Q-d<=hi)
        if lo<=colony*Q+Q-5<=hi:points.add(colony*Q+Q-5)
    return sorted(points)


def python_next(segments,t):
    points=cuts(segments);result=[];checks=0
    for a,b in zip(points,points[1:]):
        v=actual_next(segments,a,t)
        # Independently test the right endpoint of each integer interval.
        assert actual_next(segments,b-1,t)==v
        if result and result[-1][2]==v:result[-1][1]=b
        else:result.append([a,b,v])
        checks+=2
    while result and result[0][2]==0:result.pop(0)
    while result and result[-1][2]==0:result.pop()
    return result,checks


def calculate():
    source=Path(__file__).parent
    with tempfile.TemporaryDirectory(prefix='ge0_first_workspace_') as d:
        binary=Path(d)/'native'
        compile_args=['gcc','-std=c11','-O3','-Wall','-Wextra','-Werror',str(source/'ge0_first_workspace_native.c'),'-o',str(binary)]
        proc=subprocess.run(compile_args,check=True,capture_output=True,text=True)
        run=subprocess.run([str(binary)],check=True,capture_output=True,text=True)
        result=json.loads(run.stdout)
        binary_digest=digest(binary)
    assert (result['Q'],result['start_row'],result['end_row'])==(Q,START,END)
    assert result['all_updated_rows']==END-START
    assert result['final_matches_20Q_stationary_native_form']
    retained={r['physical_row']:r['segments'] for r in result['retained_rows']}
    assert retained[START]==[[-Q,0,2],[0,16*Q,1],[16*Q,17*Q,3]]
    assert retained[END]==[[-Q,0,2],[0,19*Q,1],[19*Q,20*Q,3]]
    checks=0;checksums=hashlib.sha256()
    for t,segments in retained.items():
        following,c=python_next(segments,t);checks+=c
        if t+1 in retained:assert following==retained[t+1]
        checksums.update(json.dumps((t,following),sort_keys=True).encode())
    return dict(compilation_flags=['-std=c11','-O3','-Wall','-Wextra','-Werror'],
        compiler_version=subprocess.run(['gcc','--version'],capture_output=True,text=True,check=True).stdout.splitlines()[0],
        emitted_native_event_binary_sha256=binary_digest,finite_native_prefix=result,
        literal_native_endpoint_checks=checks,retained_row_count=len(retained),
        independent_literal_next_row_signature_sha256=checksums.hexdigest(),
        infinite_line_exterior_zero_and_event_partition_proved_in_written_argument=True,
        original_Flag2_printed_and_h1_trajectories_coincide=True,
        full_own_rule_or_later_period_or_Gray_refutation_proved=False)


def main():
    started=time.monotonic();source=Path(__file__).parent;directory=ROOT/'figs/gray_counterexamples'
    results=calculate()
    r=dict(name='Conditional first GE0 authentic Workspace/native pulse on the infinite line',
        Q=Q,U=U,lambda_original=24,c_original=104,checker_sha256=digest(__file__),
        proof_sha256=digest(source/'GE0_FIRST_WORKSPACE_NATIVE.md'),
        source_dependencies_sha256={name:digest(source/name) for name in
            ('ge0_first_workspace_native.c','literal_maintenance.py','check_gray_global_first_flags.py',
             'GE0_GLOBAL_FIRST_FLAGS.md','GE0_EARLY_NATIVE_FLAGS.md','gray_raw_gather.py')},
        receipt_dependencies_sha256={name:digest(directory/name) for name in
            ('GE0_global_first_flags_certificate.json','GE0_early_native_flags_certificate.json',
             'GT0_clock_erasure_bank_certificate.json')},
        primary_Gray_text_sha256=digest(ROOT/'papers_txt/gray_readers_guide.txt'),results=results,
        same_original_real2_error_row0_support=[0,17*Q],no_later_errors=True,
        intact_final_GE0_completion_own_beta_and_literal_late_Workspace_equations_remain_premises=True,
        actual_p41_computed_final_SimBit_held_on_this_prefix=True,
        first_pulse_conditional_native_clock_expansion_17Q_to20Q_proved=True,
        first_pulse_recovers_common_clock=False,
        full_faithful_Gray_rule_or_counterexample_or_iid_memory_result=False,
        shorter_U_or_active_rule_or_registered_component_changes=False,
        elapsed_seconds=time.monotonic()-started)
    path=directory/'GE0_first_workspace_native_certificate.json'
    path.write_text(json.dumps(r,indent=2)+'\n')
    print(json.dumps(dict(receipt_sha256=digest(path),retained_rows=results['retained_row_count'],
        first_exact_20Q_clock_row=results['finite_native_prefix']['first_exact_20Q_clock_row'],
        first_exact_quiet_native_row=results['finite_native_prefix']['first_exact_quiet_20Q_native_row'],
        elapsed_seconds=time.monotonic()-started)))


if __name__=='__main__':main()
