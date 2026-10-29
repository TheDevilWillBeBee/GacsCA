#!/usr/bin/env python3
"""GT0 conditional native-prefix/erased-bank certificate, not a full Gray rule."""
from pathlib import Path
from itertools import product
import hashlib,json,sys,time
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
from gacsca.netlist import Net,const_word,at_least
import gray_raw_gather as p
import literal_maintenance as literal

B=17*p.Q;F=(-p.Q,0,16*p.Q,17*p.Q)


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def clock(x):return int(0<=x<B)


def flagged(x):return int(-p.Q<=x<0 or 16*p.Q<=x<17*p.Q)


def native(x,t):
    assert t>=2731
    return dict(addr=x%p.Q,age=t+clock(x),f1=flagged(x),f2=0,wf1=0,wf2=0)


def phase_classes():
    low=32*p.Q-2;high=70*p.Q+3
    points={low,high}
    for event in p.clock_boundaries():
        for e in (0,1):
            v=event-e
            if low<=v<=high:points.add(v)
    return sorted(points)[:-1]


def native_and_component_factor():
    phases=phase_classes();centres=[b+j for b in F for j in range(-3,4)]
    signature=hashlib.sha256();groups=holder_controls=copy_identities=0
    for y,nrow in product(centres,phases):
        net=Net();raw={(x,f,q*w+b):net.input(('raw',x,f,q*w+b))
            for x in range(y-7,y+8) for f,w in p.FIELDS for q in range(5) for b in range(w)}
        widths=dict(p.FIELDS)
        def value(z,f,b):return at_least(net,[raw[z-s,f,q*widths[f]+b]
            for q,s in enumerate(p.SLOTS)],3)
        def expression(command):
            if command[0]=='zero':return 0
            if command[0]=='majority3':
                a,b,c=[expression(item) for item in command[1:]]
                return net.OR(net.AND(a,b),net.AND(c,net.OR(a,b)))
            assert command[0] not in ('flag1_port','flag2_port','write_port')
            f,off,b=command;return value(y+off,f,b)
        output=[]
        for q,s in enumerate(p.SLOTS):
            x=y-s;controls=literal.scalar({j:native(x+j,nrow-1) for j in range(-5,6)})
            assert controls['addr']==x%p.Q and controls['age']==nrow+clock(x)
            assert controls['f1']==flagged(x) and controls['f2']==0
            cells={j:{f:[raw[x+j,f,b] for b in range(5*w)] for f,w in p.FIELDS}
                for j in range(-5,6)}
            future1=net.input(('futureFlag1',x));future2=net.input(('futureFlag2',x))
            writes={s:(net.input(('futureEnable',x,s)),net.input(('futureValue',x,s))) for s in p.SLOTS}
            actual=p.build(net,cells,const_word(controls['addr'],p.K),const_word(controls['age'],p.M),
                controls['f1'],0,future1,future2,writes)
            output.append(actual);holder_controls+=1
        for f,w in p.FIELDS:
            if f not in ('mailR','mailL','history1','history2','history3'):continue
            for b in range(w):
                expected=expression(p.scalar_plan(nrow+clock(y),y%p.Q,0,f,b))
                if f in ('mailR','mailL') and flagged(y):expected=0
                good=0
                for q,s in enumerate(p.SLOTS):
                    x=y-s
                    usable=(flagged(x) if flagged(y) else not flagged(x) and clock(x)==clock(y)) \
                        if f in ('mailR','mailL') else clock(x)==clock(y)
                    if usable:
                        assert output[q][f,s,b]==expected,(y,nrow,f,b,x)
                        good+=1;copy_identities+=1
                assert good>=3,(y,nrow,f,b,good)
                signature.update(f'{y}/{nrow}/{f}/{b}/{good};'.encode())
        groups+=1
    return dict(physical_output_clock_classes=phases,boundary_centres=centres,
        complete_saturated_Mailbox_and_History_event_groups=groups,
        actual_literal_native_holder_controls=holder_controls,
        raw_free_bit_actual_GT0_copy_identities=copy_identities,
        input_native_Field2_zero_printed_and_h1_agree=True,
        factor_signature_sha256=signature.hexdigest(),arbitrary_raw_copy_extension_proved=True,
        all_integer_centres_extension_from_four_separated_boundaries_proved=True)


def route_and_banks():
    signature=hashlib.sha256();routes=walls=0;largest=0
    for stage,g,residue,d in product((1,2),(15,16),range(5,p.Q-4),range(-5,6)):
        start=p.STAGES[stage][0];y=g*p.Q+residue
        capture=p.capture_age(stage,d+5)-clock(y)
        assert start-1<capture<70*p.Q
        largest=max(largest,capture)
        if d==0:origin=('held_own_SimBit',y)
        elif g==16:origin=('permanent_erased_receiver_Mailbox',y,capture-1)
        elif d<0:
            assert 10<=g+d<=14
            source=y+d*p.Q
            assert 0<source<16*p.Q and clock(source)==clock(y)==1
            assert capture-1-(start+1-clock(y))==abs(d)*p.Q
            origin=('unblocked_held_source_SimBit',source)
        else:
            steps=p.Q-residue;wall=16*p.Q;wallrow=capture-1-steps
            assert y+steps==wall and flagged(wall)
            assert wallrow==start+(d-1)*p.Q+residue>=start+5>2731
            assert wallrow>start+1-clock(wall)
            origin=('permanent_erased_colony16_wall',wall,wallrow);walls+=1
        signature.update(f'{stage},{g},{residue},{d},{capture},{origin};'.encode());routes+=1
    records=[]
    names=('addr','age','f1','f2','wf1','wf2')
    for g in (15,16):
        bank={}
        for d in range(-5,6):
            good=d==0 or g==15 and d<0
            bank[d]=dict(addr=(g+d)%p.Q if good else 0,age=0,f1=0,f2=0,wf1=0,wf2=0)
        native_output=literal.scalar(bank)
        assert {name:native_output[name] for name in ('addr','age','f1','f2')}==dict(addr=g,age=1,f1=1,f2=0)
        assert all(bank[d]['addr']==0 for d in range(1,6))
        if g==15:assert [bank[-i]['addr'] for i in range(1,6)]==list(range(14,9,-1))
        else:assert not any(bank[d]['addr'] for d in range(-5,6) if d)
        records.append(dict(receiver=g,lower_Flag1=flagged(g*p.Q+4096),
            stage2_and_stage3_same_exact_native_bank=bank,
            computed_native={name:native_output[name] for name in names if name in native_output}))
    temporal=0
    for first,b in product((0,1),repeat=2):
        assert at_least(Net(),[first,b,b],2)==b;temporal+=1
    preliminary=p.preliminary_layout()
    native_layout=[dict(field=name,bit=b,primary=preliminary[name,b])
        for name,width in p.FRAME_SCHEMA[:6] for b in range(width)]
    assert len(native_layout)==37 and all(5<=item['primary']<=p.Q-5 for item in native_layout)
    return dict(all_interior_native_primary_residues=[5,p.Q-5],stages=[2,3],
        exact_route_or_erasure_identities=routes,actual_wall_origin_identities=walls,
        largest_physical_capture_row=largest,records_available_physical_row=70*p.Q,
        route_signature_sha256=signature.hexdigest(),native_banks=records,
        three_bank_temporal_majority_bit_identities=temporal,
        preliminary_native_bit_layout=native_layout,final_layout_and_beta_existence_assumed_not_proved=True)


def calculate():return dict(native_and_component_factor=native_and_component_factor(),
    routes_and_native_banks=route_and_banks())


def main():
    started=time.monotonic();source=Path(__file__).parent;directory=ROOT/'figs/gray_counterexamples'
    result=calculate()
    previous=json.loads((directory/'GMW7_WF0_clock_island_certificate.json').read_text())['errors']
    assert previous['whole_row_one_original_real2_proved_by_definition']
    receipt=dict(name='GT0 authentic Mailbox-mask conditional clock-prefix native banks',
        Q=p.Q,U=p.U,lambda_original=24,c_original=104,checker_sha256=digest(__file__),
        proof_sha256=digest(source/'GT0_CLOCK_ERASURE_BANK.md'),results=result,
        source_dependencies_sha256={name:digest(source/name) for name in
            ('gray_raw_gather.py','literal_maintenance.py','GT0_RAW_GATHER.md',
                'GMW7_WF0_CLOCK_ISLAND.md','GRAY_FLAG_COMMAND_CONTRACT.md')},
        receipt_dependencies_sha256={name:digest(directory/name) for name in
            ('GT0_raw_gather_certificate.json','GT0_transitions.json','GT0_preliminary_frame_layout.json',
                'GMW7_WF0_clock_island_certificate.json')},
        primary_Gray_text_sha256=digest(ROOT/'papers_txt/gray_readers_guide.txt'),
        error_geometry=dict(physical_input_row=0,half_open_sites=[0,17*p.Q],replacement='Age1 only; other fields unchanged',
            original_real2=True,E0_empty=True,E1_empty=True,no_later_errors=True),
        same_location_set_not_same_GMW7_state_alphabet=True,
        conditional_Gt0_prefix_native_and_actual_blocked_banks_proved=True,
        no_preloaded_bank_or_independent_upper_error=True,
        initial_native_layout_and_intact_full_completion_premises_explicit=True,
        full_Gray_beta_layout_early_evaluation_or_late_repair_proved=False,
        Gray_or_Gacs_refuted_or_iid_memory_failure=False,
        active_rule_or_existing_GT0_modified=False,new_rule_schedule_or_shorter_U_emitted=False,
        elapsed_seconds=time.monotonic()-started)
    path=directory/'GT0_clock_erasure_bank_certificate.json';path.write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(dict(groups=result['native_and_component_factor']['complete_saturated_Mailbox_and_History_event_groups'],
        identities=result['native_and_component_factor']['raw_free_bit_actual_GT0_copy_identities'],
        routes=result['routes_and_native_banks']['exact_route_or_erasure_identities'],
        receipt_sha256=digest(path),elapsed_seconds=time.monotonic()-started)))


if __name__=='__main__':main()
