#!/usr/bin/env python3
"""New unregistered GE1 actual native-history lift through the sixth pulse.

No accepted source or receipt is rewritten. Whole own beta, final layout,
and literal final-computed Workspace completion remain explicit premises.
"""
from pathlib import Path
from bisect import bisect_right
from itertools import product
from dataclasses import replace
import hashlib,json,subprocess,sys,tempfile,time

ROOT=Path(__file__).resolve().parents[4]
SOURCE=Path(__file__).resolve().parent
REGISTERED=SOURCE.parent
DIRECTORY=ROOT/'figs/gray_counterexamples/unregistered_ge4'
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(REGISTERED))
import literal_maintenance as literal
import gray_early_native_flags as e
import gray_moving_word_kernel as h
import gray_raw_gather as g
import gray_native_writeback_ge1 as w
import check_gray_global_first_flags as first
import check_gray_early_native_flags as early_check

Q=8192;U=1048576;START=96*Q-2;END=100*Q
FIELDS=('addr','age','f1','f2','wf1','wf2')
INDEX={name:i for i,(name,_) in enumerate(g.FIELDS)}
ZERO={name:0 for name in FIELDS}


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def background(receiver,evaluation):
    return dict(addr=receiver%Q,age=evaluation,f1=0,f2=0,wf1=0,wf2=0)


def word(state,receiver):
    return state['deviations'].get(receiver,background(receiver,state['evaluation']))


def crossed(receiver,offset,barriers):
    return tuple(b for b in barriers if min(receiver,receiver+offset)<=b<=max(receiver,receiver+offset))


def bank(state,receiver,barriers):
    return {d:word(state,receiver+d) if d==0 or not crossed(receiver,d,barriers) else ZERO
        for d in range(-5,6)}


def initial_state():
    return dict(evaluation=1,deviations={receiver:dict(background(receiver,1),f1=1)
        for receiver in first.FLAG1_SUPPORT})


def evaluate(state,barriers):
    """Exact finite deviations plus proved homogeneous infinite exteriors.

    Receiver outside radius5 of a deviation or barrier has eleven actual
    homogeneous records. The literal next state is background(n+1).
    """
    affected={y+d for y in tuple(state['deviations'])+tuple(barriers) for d in range(-5,6)}
    rows=[];deviations={};n=state['evaluation']+1
    for receiver in sorted(affected):
        records=bank(state,receiver,barriers)
        computed=literal.scalar(records)
        # GE0 EarlyOut's two Workspace outputs are reset0; GE1 mirrors those0.
        out={k:computed[k] for k in ('addr','age','f1','f2')};out.update(wf1=0,wf2=0)
        assert out['addr']==receiver%Q and 0<=out['age']<=n
        assert out['f2']==0
        if out!=background(receiver,n):deviations[receiver]=out
        rows.append(dict(receiver=receiver,actual_native_bank=records,native_output=out))
    return dict(evaluation=n,deviations=deviations),rows


def commands(state):return sorted(y for y,v in state['deviations'].items() if v['f1'])


def actual_transition(value,receiver,offset,stage,slot,beta,state,barriers,phase):
    """Pinned local History capture over the route's actual derived old word."""
    residue=e.NATIVE_COLUMNS[value][0]
    local_age=g.capture_age(stage,offset+5)
    x=residue-slot;physical=(state['evaluation'])*U+local_age-phase(receiver)
    records=bank(state,receiver,barriers)
    def bit(v,p):
        for key,(start,width) in e.NATIVE_COLUMNS.items():
            if start<=p<start+width:return (v[key]>>(p-start))&1
        return 0
    cells={}
    for j in range(-5,6):
        values=[]
        for field,width in g.FIELDS:
            slots=[]
            for s in e.SLOTS:
                y=receiver*Q+x+j+s;col,p=divmod(y,Q)
                b=bit(word(state,col),p) if field=='simbit' else bit(bank(state,col,barriers)[offset],p) if field in ('mailL','mailR') else 1
                slots.extend([b]*width)
            values.append(tuple(slots))
        absolute=receiver*Q+x+j
        cells[j]=e.Cell(addr=(x+j)%Q,age=(physical+phase(absolute//Q)-1)%U,
            f1=int(absolute//Q in barriers),data=tuple(values))
    actual=w.local_transition(cells,beta)
    index=e.SLOTS.index(slot)*11+offset+5
    expected=bit(records[offset],residue)
    assert actual.data[INDEX['history'+str(stage+1)]][index]==expected
    return [receiver,value,offset,stage,slot,local_age,physical,expected]


def routing_and_captures(state,L,R,beta):
    barriers=(L-1,R-1);phase=lambda y:int(L<=y<R)
    receivers=sorted(set((L-2,L-1,L,L+1,R-2,R-1,R,R+1)) | {0})
    route_sig=hashlib.sha256();affine=0;actual=0
    for receiver,d,stage in product(receivers,range(-5,6),(1,2)):
        S=32*Q if stage==1 else 64*Q
        cap=state['evaluation']*U+S+(1 if d==0 else 2+abs(d)*Q)-phase(receiver)
        assert cap<=state['evaluation']*U+69*Q+2
        for p in (5,Q-5):
            walls=crossed(receiver,d,barriers)
            if not d:kind='held-direct-self'
            elif walls:
                kind='actual-flagged-Mailbox-erasure'
                y=receiver*Q+p
                candidates=[]
                for b in walls:
                    z=y if b==receiver else b*Q if d>0 else (b+1)*Q-1
                    steps=abs(z-y);row=cap-1-steps
                    assert 0<=steps<=abs(d)*Q
                    assert row>=state['evaluation']*U+S
                    candidates.append([steps,z,row])
                assert candidates
            else:
                kind='same-phase-held-committed-primary'
                assert phase(receiver)==phase(receiver+d)
                snapshot=state['evaluation']*U+S+1-phase(receiver+d)
                assert cap-1-snapshot==abs(d)*Q
            route_sig.update(json.dumps([receiver,d,stage,p,cap,kind]).encode());affine+=1
    for receiver,key,d,stage,slot in product(receivers,e.NATIVE_COLUMNS,range(-5,6),(1,2),e.SLOTS):
        row=actual_transition(key,receiver,d,stage,slot,beta,state,barriers,phase)
        route_sig.update(json.dumps(row).encode());actual+=1
    return dict(actual_quiet_clock_interval_colonies=[L,R],actual_full_Flag1_barriers=barriers,
        committed_previous_native_evaluation=state['evaluation'],affine_route_endpoint_checks=affine,
        actual_GE1_History2_History3_holder_capture_checks=actual,
        route_and_capture_sha256=route_sig.hexdigest(),
        both_later_banks_from_same_physical_history=True,
        no_independently_selected_upper_state_or_History=True)


def get(segments,x):
    i=bisect_right([a for a,b,v in segments],x)-1
    return segments[i][2] if i>=0 and x<segments[i][1] else 0


def cuts(segments,lo,hi):
    result={lo,hi}
    for a,b,v in segments:
        result.update(z-d for z in (a,b) for d in range(-5,6) if lo<=z-d<=hi)
    for c in range(lo//Q,hi//Q+1):
        result.update(c*Q-d for d in range(-5,6) if lo<=c*Q-d<=hi)
        if lo<=c*Q+Q-5<=hi:result.add(c*Q+Q-5)
    return sorted(result)


def scalar_point(segments,x,t,source_support):
    raw={j:dict(addr=(x+j)%Q,age=t+(get(segments,x+j)&1),
        f1=(get(segments,x+j)>>1)&1,f2=0,wf1=(get(segments,x+j)>>2)&1,wf2=0)
        for j in range(-5,6)}
    new=literal.scalar(raw);assert new['addr']==x%Q and new['f2']==0
    label=new['age']-(t+1);assert label in (0,1)
    wf1=int(x//Q in source_support and x%Q>=Q-5 and 96*Q<=new['age']<98*Q)
    return label+2*new['f1']+4*wf1


def kernel_pulse(binary,state,width):
    support=commands(state)
    argv=[str(binary),str(width),*map(str,support)]
    result=json.loads(subprocess.run(argv,check=True,capture_output=True,text=True).stdout)
    lo,hi=result['domain'];expected_L=7 if state['evaluation']==6 else 0
    expected_R=width+3
    expected=[[lo,(expected_L-1)*Q,0],[(expected_L-1)*Q,expected_L*Q,2],
        [expected_L*Q,(expected_R-1)*Q,1],[(expected_R-1)*Q,expected_R*Q,3],
        [expected_R*Q,hi,0]]
    assert result['retained_rows'][-1]['segments']==expected
    rows=result['retained_rows'];checks=0;next_checks=0;sig=hashlib.sha256()
    for i,row in enumerate(rows):
        t=row['relative_period_row'];segments=row['segments']
        assert segments[0][0]==lo and segments[-1][1]==hi
        assert all(b==segments[j+1][0] for j,(a,b,v) in enumerate(segments[:-1]))
        for a,b in zip(cuts(segments,lo,hi),cuts(segments,lo,hi)[1:]):
            for x in (a,b-1):
                value=scalar_point(segments,x,t,support);checks+=1
                if i+1<len(rows) and rows[i+1]['relative_period_row']==t+1:
                    assert get(rows[i+1]['segments'],x)==value;next_checks+=1
                sig.update(json.dumps([t,x,value]).encode())
    return dict(evaluation=state['evaluation'],actual_derived_Flag1_source_support=support,
        all_integer_Flag2_sources_zero=True,initial_actual_quiet_clock_interval=[0,width],
        final_actual_quiet_clock_interval=[expected_L,expected_R],
        all_row_event_partition=result,literal_actual_native_endpoint_checks=checks,
        consecutive_retained_update_checks=next_checks,endpoint_sha256=sig.hexdigest(),
        argv_without_binary=argv[1:])


def programme_runs(beta,state,rows):
    """Emitted generic instruction execution on derived banks, not host dispatch."""
    chosen=sorted(set((0,-1,6,7,state['evaluation']*3+13)) & {r['receiver'] for r in rows})
    outrows=[]
    for receiver in chosen:
        row=next(r for r in rows if r['receiver']==receiver)
        out,ticks,packet,trace=e.execute(beta,e.tape_from_native(row['actual_native_bank']),record=True)
        actual=e.native_output(out)
        assert actual=={k:row['native_output'][k] for k in ('addr','age','f1','f2')}
        assert ticks==34396 and packet.mode==h.HALT
        sig=hashlib.sha256()
        for position,before,after,write in trace:
            assert e.PRIMARY_START<=position<5275
            sig.update(position.to_bytes(2,'little'))
            sig.update(h.pack(after).to_bytes((h.HEAD_BITS+7)//8,'little'))
            sig.update(bytes([2 if write is None else write]))
        meta=dict(ticks=ticks,halt_mode=packet.mode,head_residue_bounds=[
            min(t[0] for t in trace),max(t[0] for t in trace)],trace_sha256=sig.hexdigest())
        outrows.append(dict(receiver=receiver,actual_derived_bank=row['actual_native_bank'],
            emitted_native_output=actual,execution=meta))
    return outrows


def calculate():
    beta,listing,_=e.native_programme()
    schedule=early_check.programme_audit(beta,listing)
    state=initial_state();L=0;R=20
    # GE1 first commit is Z1 after the accepted first pulse; GE2's second
    # complete prefix is the accepted anchor. Recalculate its exact bank.
    state2,rows2=evaluate(state,(L-1,R-1))
    assert commands(state2)==list(range(-4,0))+list(range(10,23))
    state=state2;R=23
    stages=[]
    kernel=SOURCE/'ge4_native_workspace_pulse.c'
    with tempfile.TemporaryDirectory(prefix='GE4_reachable_left_') as temp:
        binary=Path(temp)/'pulse'
        compile_argv=['gcc','-std=c11','-O3','-Wall','-Wextra','-Werror',str(kernel),'-o',str(binary)]
        subprocess.run(compile_argv,check=True,capture_output=True,text=True)
        binary_sha=digest(binary)
        for evaluation in range(3,7):
            routing=routing_and_captures(state,L,R,beta)
            new,rows=evaluate(state,(L-1,R-1))
            assert new['evaluation']==evaluation
            if evaluation<6:
                assert 0 not in commands(new)
            else:assert commands(new)==list(range(-16,35))
            execution=programme_runs(beta,new,rows)
            pulse=kernel_pulse(binary,new,R)
            stages.append(dict(evaluation=evaluation,actual_bank_route_and_holder_checks=routing,
                derived_all_integer_native_state=new,finite_exception_outputs=rows,
                emitted_native_programme_replays=execution,late_native_Workspace_pulse=pulse,
                first_old_offset_colony_command=int(0 in commands(new))))
            L,R=pulse['final_actual_quiet_clock_interval'];state=new
    assert (L,R)==(7,35)
    next_routes=routing_and_captures(state,L,R,beta)
    next_state,next_rows=evaluate(state,(L-1,R-1))
    return dict(same_unchanged_GE1_equations_and_schedule=True,
        native_programme_schedule=schedule,event_binary_sha256=binary_sha,
        compile_argv_without_temporary_binary=compile_argv[:-1],stages=stages,
        next_actual_bank_B6_route_and_holder_checks=next_routes,
        actual_derived_next_native_state_Z7=next_state,
        actual_derived_Z7_Flag1_source_support=commands(next_state),
        first_left_command_evaluation=6,sixth_quiet_clock_interval_colonies=[7,35],
        hypothetical_fixed_left_growth_sequence_rejected=True,
        exact_next_bank_and_native_function_outputs=next_rows,
        next_seventh_late_pulse_proved=False,
        full_own_beta_layout_final_source_completion_proved=False,
        faithful_Gray_refutation_iid_or_shorter_U_proved=False)


def receipt():
    manifest=DIRECTORY/'GE4_initial_compile_failure_manifest.json'
    retained=json.loads(manifest.read_text())
    for name,sha in retained['assets_sha256'].items():assert digest(DIRECTORY/name)==sha
    sources=('literal_maintenance.py','gray_native_writeback_ge1.py','gray_early_native_flags.py',
        'gray_moving_word_kernel.py','gray_raw_gather.py','check_gray_global_first_flags.py',
        'check_gray_early_native_flags.py','GE0_EARLY_NATIVE_FLAGS.md',
        'GE1_NATIVE_WRITEBACK_SECOND_BANK.md','GE2_SECOND_NATIVE_PREFIX.md')
    receipts=('GE1_native_writeback_second_bank_certificate.json',
        'GE2_second_native_prefix_certificate.json','GE0_early_native_flags_certificate.json')
    return dict(name='GE4 conditional actual GE1 history through first left-command pulse',
        Q=Q,U=U,lambda_original=24,c_original=104,
        checker_sha256=digest(__file__),kernel_sha256=digest(SOURCE/'ge4_native_workspace_pulse.c'),
        proof_sha256=digest(SOURCE/'GE4_REACHABLE_LEFT_PULSE.md'),
        source_dependencies_sha256={name:digest(REGISTERED/name) for name in sources},
        receipt_dependencies_sha256={name:digest(ROOT/'figs/gray_counterexamples'/name) for name in receipts},
        GE3_conditional_right_template_proof_sha256=digest(REGISTERED/'unregistered_ge3/GE3_RIGHT_TEMPLATE.md'),
        GE3_conditional_right_template_receipt_sha256=digest(ROOT/'figs/gray_counterexamples/unregistered_ge3/GE3_right_template_certificate.json'),
        retained_initial_compile_failure_manifest_sha256=digest(manifest),
        retained_initial_compile_failure_assets_sha256=retained['assets_sha256'],
        primary_Gray_text_sha256=digest(ROOT/'papers_txt/gray_readers_guide.txt'),
        same_shared_row0_Age_only_real2_support=[0,17*Q],no_later_errors=True,
        fixed_left_later_widths_assumed=False,global_common_upper_Age_assumed=False,
        native_only_fifth_writer_departure_and_completion_premises_unchanged=True,
        own_beta_final_layout_literal_final_computed_source_completion_remain_premises=True,
        mathematical_result_is_conditional_component_history_not_a_Gray_refutation=True,
        registered_main_or_old_component_modified=False,results=calculate())


if __name__=='__main__':
    started=time.monotonic();result=receipt();result['elapsed_seconds']=time.monotonic()-started
    path=DIRECTORY/'GE4_reachable_left_pulse_certificate.json'
    path.write_text(json.dumps(result,sort_keys=True,indent=2)+'\n')
    print(json.dumps(dict(receipt=str(path),receipt_sha256=digest(path),
        elapsed_seconds=result['elapsed_seconds'],actual_native_history_proved_conditionally=True,
        sixth_quiet_interval_colonies=[7,35],faithful_Gray_refutation=False)))
