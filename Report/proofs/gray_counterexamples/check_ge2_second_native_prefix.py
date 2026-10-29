#!/usr/bin/env python3
"""Actual second GE1 early evaluation/couriers and conditional native pulse."""
from pathlib import Path
from bisect import bisect_right
from itertools import product
import hashlib,json,subprocess,sys,tempfile,time
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
import gray_native_writeback_ge1 as w
import gray_early_native_flags as e
import gray_moving_word_kernel as h
import gray_raw_gather as g
import check_gray_native_writeback_ge1 as bridge
import literal_maintenance as literal
import emit_ge2_second_workspace as emitter

Q=e.Q;U=e.U;START=96*Q-2;END=100*Q
COMMAND=emitter.COMMAND


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def fixture(receiver,x,old_age,position,packet,tape,out,left=None,right=None):
    """Actual raw native phase20 geometry and derived native History bits.

    Its native H1 is the stage0 bank derived after GE1 commit. All three
    native banks equal B1; unrepresented History bits are unused by beta.
    This is a local instrumentation of the proved copy induction.
    """
    left={} if left is None else left;right={} if right is None else right
    wall_time=U+old_age-bridge.phase(receiver);packed=h.pack(packet);cells={}
    for j in range(-5,6):
        absolute=receiver*Q+x+j;raw=[]
        for field,width in g.FIELDS:
            values=[]
            for s in e.SLOTS:
                y=x+j+s;word=tape.get(y,0) if field.startswith('history') else 0
                values.extend((word>>bit)&1 for bit in range(width))
            raw.append(tuple(values))
        cells[j]=e.Cell(addr=(x+j)%Q,age=(wall_time+bridge.phase(absolute//Q))%U,
            f1=int(absolute//Q in bridge.BARRIERS),data=tuple(raw),
            heads=tuple(packed if x+j+s==position else 0 for s in e.SLOTS),
            early_out=tuple(out.get(x+j+s,0) for s in e.SLOTS),
            courierL=tuple(left.get(x+j+s,0) for s in e.SLOTS),
            courierR=tuple(right.get(x+j+s,0) for s in e.SLOTS))
    return cells


def physical_head(beta,receiver):
    records=bridge.bank(receiver);tape=e.tape_from_native(records)
    position=e.ENTRY;packet=e.initial_packet();out={};counts=[0]*5
    age=e.BIRTH;sig=hashlib.sha256();minimum=Q;maximum=-1
    for tick in range(34396):
        newpos=position+(1 if packet.move==1 else -1 if packet.move==2 else 0)
        newpacket,write=h.step_packet(packet,newpos,tape.get(newpos,0),beta)
        newout=dict(out)
        if write is not None:newout[newpos]=write
        selected=range(5) if write is not None or tick in (0,34395) else (tick%5,)
        for i in selected:
            x=newpos-e.SLOTS[i]
            actual=w.local_transition(fixture(receiver,x,age,position,packet,tape,out),beta)
            assert actual.heads==tuple(h.pack(newpacket) if x+s==newpos else 0 for s in e.SLOTS)
            assert actual.early_out==tuple(newout.get(x+s,0) for s in e.SLOTS)
            assert actual.courierL==actual.courierR==(0,)*5
            assert (actual.addr,actual.age,actual.f1,actual.f2,actual.wf1,actual.wf2)==(
                x%Q,age+1,int(receiver in bridge.BARRIERS),0,0,0)
            counts[i]+=1
        sig.update(newpos.to_bytes(2,'little'))
        sig.update(h.pack(newpacket).to_bytes((h.HEAD_BITS+7)//8,'little'))
        sig.update(bytes([2 if write is None else write]))
        minimum=min(minimum,newpos);maximum=max(maximum,newpos)
        position,packet,out,age=newpos,newpacket,newout,age+1
    assert packet.mode==h.HALT and age==599648
    expected={key:literal.scalar(records)[key] for key in ('addr','age','f1','f2')}
    assert e.native_output(out)==expected
    assert minimum>=e.PRIMARY_START and maximum<5275
    return out,dict(receiver=receiver,lower_phase=bridge.phase(receiver),
        lower_Flag1=int(receiver in bridge.BARRIERS),actual_native_input_bank=records,
        native_output=expected,all34396_head_updates_instrumented=True,
        actual_local_transition_count=sum(counts),rotating_and_native_write_holder_counts=counts,
        head_residue_bounds=[minimum,maximum],halt_local_age=age,
        halt_physical_row=U+age-bridge.phase(receiver),trace_sha256=sig.hexdigest())


def reset_birth(beta,receiver):
    wild=h.Packet(p=1,mode=h.ERROR,move=3,pc=0,ret=0,target=0,regs=(h.MASK,)*16)
    dirty={p:1 for p in range(e.PRIMARY_START-8,5283)};checks=0
    for slot in e.SLOTS:
        x=e.ENTRY-slot
        actual=w.local_transition(fixture(receiver,x,e.RESET-1,e.ENTRY,wild,{},dirty,dirty,dirty),beta)
        assert actual.heads==actual.early_out==actual.courierL==actual.courierR==(0,)*5
        actual=w.local_transition(fixture(receiver,x,e.BIRTH-1,-1,h.ZERO,{},{}),beta)
        assert actual.heads==tuple(h.pack(e.initial_packet()) if x+s==e.ENTRY else 0 for s in e.SLOTS)
        assert actual.early_out==actual.courierL==actual.courierR==(0,)*5
        checks+=2
    return dict(receiver=receiver,actual_raw_reset_and_unique_birth_holder_checks=checks,
        reset_physical_row=U+e.RESET-bridge.phase(receiver),birth_physical_row=U+e.BIRTH-bridge.phase(receiver))


def couriers(beta,receiver,out):
    sig=hashlib.sha256();count=0;delivery=[]
    for field,source,direction,distance in (
            ('courierL',e.NATIVE_COLUMNS['f2'][0],-1,e.LEFT_DISTANCE),
            ('courierR',e.NATIVE_COLUMNS['f1'][0],1,e.RIGHT_DISTANCE)):
        payload=out.get(source,0);previous=source
        # For a zero source, the global zero induction proves every move;
        # seed/arrival raw checks supplement it. Every one-source move is checked.
        ticks=range(distance+1) if payload else (0,distance)
        for tick in ticks:
            newpos=source+direction*tick
            oldpos=source+direction*(tick-1)
            values={} if tick==0 else {oldpos:payload}
            left=values if field=='courierL' else {};right=values if field=='courierR' else {}
            selected=range(5) if tick in (0,distance) else (tick%5,)
            for i in selected:
                x=newpos-e.SLOTS[i]
                actual=w.local_transition(fixture(receiver,x,e.SEED-1+tick,-1,h.ZERO,{},out,left,right),beta)
                assert getattr(actual,field)==tuple(payload if x+s==newpos else 0 for s in e.SLOTS)
                count+=1
            sig.update(newpos.to_bytes(2,'little'));sig.update(bytes([payload]))
            previous=newpos
        assert previous==source+direction*distance
        values={previous:payload}
        left=values if field=='courierL' else {};right=values if field=='courierR' else {}
        for i in range(5):
            x=previous-e.SLOTS[i]
            actual=w.local_transition(fixture(receiver,x,g.FLAG_DELIVERY-1,-1,h.ZERO,{},out,left,right),beta)
            assert actual.data[bridge.INDEX['simbit']][i]==payload
            delivery.append(dict(field=field,target=previous,holder=x,copy=e.SLOTS[i],value=payload,
                physical_row=U+g.FLAG_DELIVERY-bridge.phase(receiver)));count+=1
    return dict(receiver=receiver,actual_carrier_transition_and_delivery_checks=count,
        delivery=delivery,trace_sha256=sig.hexdigest(),zero_carrier_all_move_induction_in_proof=True)


def derived_sources_and_first_history():
    native_rows=[];sig=hashlib.sha256()
    for receiver in range(-8,25):
        records=bridge.bank(receiver);output=literal.scalar(records)
        native_rows.append(dict(receiver=receiver,output={k:output[k] for k in ('addr','age','f1','f2')}))
        sig.update(json.dumps((receiver,records,output),sort_keys=True).encode())
    assert tuple(row['receiver'] for row in native_rows if row['output']['f1'])==COMMAND
    assert all(row['output']['f2']==0 for row in native_rows)
    route_count=0
    for receiver,offset,p in product(range(-6,25),range(-5,6),(5,Q-5)):
        capture=U+(1 if offset==0 else 2+abs(offset)*Q)-bridge.phase(receiver)
        assert capture>=U-bridge.phase(receiver) and capture<=U+5*Q+2
        if offset and not bridge.crossed_barriers(receiver,offset):
            assert bridge.phase(receiver)==bridge.phase(receiver+offset)
            snapshot=U+1-bridge.phase(receiver+offset)
            assert capture-1-snapshot==abs(offset)*Q
        route_count+=1
    return dict(derived_second_native_commands=native_rows,Flag1_source_support=COMMAND,
        all_integer_Flag2_sources_zero=True,actual_second_stage0_History1_same_bank=B1_description(),
        stage0_affine_route_endpoint_checks=route_count,derived_signature_sha256=sig.hexdigest(),
        latest_all_integer_physical_delivery_row=U+g.FLAG_DELIVERY,
        full_own_beta_or_computed_source_refinement_discharged=False)


def B1_description():
    return 'Z1(g+d) on self or paths avoiding−1/19; zero on other paths'


def at(segments,x):
    i=bisect_right([s[0] for s in segments],x)-1
    return segments[i][2] if i>=0 and x<segments[i][1] else 0


def actual_next(segments,x,local_t):
    physical_t=U+local_t
    raw={j:dict(addr=(x+j)%Q,age=(physical_t+(at(segments,x+j)&1))%U,
        f1=(at(segments,x+j)>>1)&1,f2=0,wf1=(at(segments,x+j)>>2)&1,wf2=0)
        for j in range(-5,6)}
    n=literal.scalar(raw);assert n['addr']==x%Q and n['f2']==0
    label=(n['age']-((physical_t+1)%U))%U;assert label in (0,1)
    wf1=int(x//Q in COMMAND and x%Q>=Q-5 and 96*Q<=n['age']<98*Q)
    return label+2*n['f1']+4*wf1


def cuts(segments):
    lo=min(-3*Q-5,segments[0][0]-5);hi=max(23*Q,segments[-1][1]+5);points={lo,hi}
    for a,b,_ in segments:points.update(z-d for z in (a,b) for d in range(-5,6) if lo<=z-d<=hi)
    for colony in range(lo//Q-1,hi//Q+2):
        points.update(colony*Q-d for d in range(-5,6) if lo<=colony*Q-d<=hi)
        if lo<=colony*Q+Q-5<=hi:points.add(colony*Q+Q-5)
    return sorted(points)


def python_next(segments,t):
    points=cuts(segments);result=[];checks=0
    for a,b in zip(points,points[1:]):
        v=actual_next(segments,a,t);assert actual_next(segments,b-1,t)==v;checks+=2
        if result and result[-1][2]==v:result[-1][1]=b
        else:result.append([a,b,v])
    while result and result[0][2]==0:result.pop(0)
    while result and result[-1][2]==0:result.pop()
    return result,checks


def workspace_prefix():
    source=Path(__file__).parent
    assert (source/'ge2_second_workspace_native.c').read_text()==emitter.generated_source()
    with tempfile.TemporaryDirectory(prefix='ge2_second_workspace_') as directory:
        binary=Path(directory)/'native'
        subprocess.run(['gcc','-std=c11','-O3','-Wall','-Wextra','-Werror',str(source/'ge2_second_workspace_native.c'),'-o',str(binary)],check=True,capture_output=True,text=True)
        run=subprocess.run([str(binary)],check=True,capture_output=True,text=True)
        result=json.loads(run.stdout);binary_sha=digest(binary)
    assert (result['Q'],result['start_row'],result['end_row'])==(Q,START,END)
    retained={row['local_period_row']:row['segments'] for row in result['retained_rows']}
    assert retained[START]==[[-Q,0,2],[0,19*Q,1],[19*Q,20*Q,3]]
    assert retained[END]==[[-Q,0,2],[0,22*Q,1],[22*Q,23*Q,3]]
    sig=hashlib.sha256();checks=0
    for t,segments in retained.items():
        following,count=python_next(segments,t);checks+=count
        if t+1 in retained:assert following==retained[t+1]
        sig.update(json.dumps((U+t,following),sort_keys=True).encode())
    return dict(compilation_flags=['-std=c11','-O3','-Wall','-Wextra','-Werror'],
        compiler_version=subprocess.run(['gcc','--version'],check=True,capture_output=True,text=True).stdout.splitlines()[0],
        event_binary_sha256=binary_sha,relative_row_origin_physical_U=U,
        exact_relative_second_prefix=result,literal_actual_native_endpoint_checks=checks,
        first_exact_23Q_clock_physical_row=U+result['first_exact_23Q_clock_row'],
        first_exact_quiet_23Q_native_physical_row=U+result['first_exact_quiet_23Q_native_row'],
        retained_row_count=len(retained),independent_next_row_sha256=sig.hexdigest(),
        exact_infinite_line_event_partition_reused_with_derived_sources=True)


def calculate():
    beta,_,_=e.native_programme();physical=[];courier=[];birth=[]
    for receiver in (18,19,20):
        birth.append(reset_birth(beta,receiver))
        out,run=physical_head(beta,receiver);physical.append(run)
        courier.append(couriers(beta,receiver,out))
    return dict(actual_second_banks_and_sources=derived_sources_and_first_history(),
        retained_actual_head_runs=physical,retained_actual_couriers=courier,actual_reset_and_birth=birth,
        second_Workspace_native_prefix=workspace_prefix())


def main():
    started=time.monotonic();source=Path(__file__).parent;directory=ROOT/'figs/gray_counterexamples'
    results=calculate()
    r=dict(name='GE2 actual second early delivery and native Workspace prefix, conditional on unchanged GE1',
        Q=Q,U=U,lambda_original=24,c_original=104,checker_sha256=digest(__file__),
        proof_sha256=digest(source/'GE2_SECOND_NATIVE_PREFIX.md'),
        source_dependencies_sha256={name:digest(source/name) for name in (
            'emit_ge2_second_workspace.py','ge2_second_workspace_native.c','gray_native_writeback_ge1.py',
            'check_gray_native_writeback_ge1.py','GE1_NATIVE_WRITEBACK_SECOND_BANK.md',
            'gray_early_native_flags.py','gray_moving_word_kernel.py','gray_raw_gather.py',
            'literal_maintenance.py','GE0_EARLY_NATIVE_FLAGS.md','GE0_FIRST_WORKSPACE_NATIVE.md',
            'ge0_first_workspace_native.c')},
        receipt_dependencies_sha256={name:digest(directory/name) for name in (
            'GE1_native_writeback_second_bank_certificate.json','GE0_early_native_flags_certificate.json',
            'GE0_first_workspace_native_certificate.json')},
        primary_Gray_text_sha256=digest(ROOT/'papers_txt/gray_readers_guide.txt'),results=results,
        same_shared_row0_Age_only_real2_support=[0,17*Q],no_later_errors=True,
        own_beta_final_layout_intact_completion_and_literal_final_computed_Workspace_remain_premises=True,
        GE1_native_only_mirror_departure_unchanged_and_remaining_ports_explicit=True,
        actual_second_native_prefix_and_pulse_proved_conditionally=True,
        global_common_upper_Age_assumed=False,second_Flag2_source_or_repaired_common_clock=False,
        faithful_Gray_refutation_full_period_iid_or_shorter_U_theorem=False,
        accepted_components_or_main_checkpoint_modified=False,elapsed_seconds=time.monotonic()-started)
    path=directory/'GE2_second_native_prefix_certificate.json';path.write_text(json.dumps(r,indent=2)+'\n')
    print(json.dumps(dict(receipt_sha256=digest(path),actual_second_prefix_proved_conditionally=True,
        first23Qphysical=results['second_Workspace_native_prefix']['first_exact_23Q_clock_physical_row'],
        quiet23Qphysical=results['second_Workspace_native_prefix']['first_exact_quiet_23Q_native_physical_row'],
        elapsed_seconds=time.monotonic()-started)))


if __name__=='__main__':main()
