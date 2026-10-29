#!/usr/bin/env python3
"""GE0 actual-history native prefix/courier certificate, not an own beta."""
from pathlib import Path
from dataclasses import replace
from itertools import combinations,product
import hashlib,json,random,sys,time,types
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
import gray_early_native_flags as e
import gray_moving_word_kernel as h
import gray_raw_gather as g
import literal_maintenance


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def fixture(x,old_age,position,packet,tape,out=None,left=None,right=None,lower_f1=0,receiver=None):
    """Actual raw copies of the derived logical bank, with arbitrary H1.

    This retained finite local context is used to replay the copy induction;
    the mathematical theorem obtains H2/H3 from the pinned GT0 history.
    H1 is deliberately different and is not an independently chosen error.
    """
    out={} if out is None else out
    left={} if left is None else left;right={} if right is None else right
    packed=h.pack(packet);result={}
    for j in range(-5,6):
        raw=[]
        for field,width in g.FIELDS:
            values=[]
            for slot in e.SLOTS:
                y=x+j+slot
                word=(911*y+17)&2047 if field=='history1' else tape.get(y,0) if field in ('history2','history3') else 0
                values.extend((word>>bit)&1 for bit in range(width))
            raw.append(tuple(values))
        absolute=None if receiver is None else receiver*e.Q+x+j
        label=lambda y:int(0<=y<17*e.Q)
        age=old_age if absolute is None else (old_age+label(absolute)-label(receiver*e.Q))%e.U
        flag=lower_f1 if absolute is None else int(-e.Q<=absolute<0 or 16*e.Q<=absolute<17*e.Q)
        result[j]=e.Cell(addr=(x+j)%e.Q,age=age,f1=flag,data=tuple(raw),
            heads=tuple(packed if x+j+s==position else 0 for s in e.SLOTS),
            early_out=tuple(out.get(x+j+s,0) for s in e.SLOTS),
            courierL=tuple(left.get(x+j+s,0) for s in e.SLOTS),
            courierR=tuple(right.get(x+j+s,0) for s in e.SLOTS))
    return result


def programme_audit(beta,listing):
    assert (e.Q,e.U,e.LAMBDA,e.ERROR_SEPARATION)==(8192,1048576,24,104)
    assert (e.FRAME_BITS,e.PRIMARY_START,e.ENTRY)==(2462,2865,2929)
    assert len(e.layout())==e.FRAME_BITS and 2*e.FRAME_BITS<=e.Q
    assert all(5<=a<=e.Q-5 for start,width in e.NATIVE_COLUMNS.values() for a in range(start,start+width))
    assert len(listing)==107 and sum(r['bits'] for r in listing)==2346
    assert listing[-1]['address']+listing[-1]['bits']==5275
    for r in listing:
        raw=sum(beta[r['address']+i]<<i for i in range(r['bits']))
        assert h.decode_instruction(raw)==(r['opcode'],tuple(r['operands']))
    excursions=[];branches=[]
    for r in listing:
        name,args=r['opcode'],r['operands']
        if name in ('BNZ','JMP'):
            target=args[-1];assert target>r['address']
            crossed=[q for q in listing if r['address']<q['address']<target]
            assert all(q['opcode'] not in ('LOAD5','LOADC','LOADCOL','WRITE','HLT') for q in crossed)
            branches.append(dict(address=r['address'],target=target,no_IO_skipped=True))
        if name not in ('LOAD5','LOADC','LOADCOL','WRITE'):continue
        start,width=(args[0],args[1]) if name=='LOAD5' else (args[1],1) if name=='LOADCOL' else (args[1],args[2])
        end=r['address']+r['bits']-1;ret=end+1
        extra=abs(end-start)+width-1+abs(start+width-1-ret)-1
        excursions.append(dict(opcode=name,end=end,start=start,width=width,return_pc=ret,extra_ticks=extra))
    runtime=2346+sum(r['extra_ticks'] for r in excursions)
    assert runtime==34396
    assert e.BIRTH+runtime==599648 and e.SEED-e.BIRTH-1==49147
    assert (e.SEED+e.LEFT_DISTANCE,e.SEED+e.RIGHT_DISTANCE)==(617296,619691)
    assert g.FLAG_DELIVERY-(e.SEED+e.RIGHT_DISTANCE)==35668
    return dict(code_bits=2346,code_start=e.ENTRY,code_end_exclusive=5275,
        instructions=107,excursions=excursions,branches=branches,
        runtime=runtime,reset_age=e.RESET,birth_age=e.BIRTH,first_execution_age=e.BIRTH+1,
        halt_age=e.BIRTH+runtime,available_execution_updates=e.SEED-e.BIRTH-1,
        halt_to_last_execution_slack=e.SEED-e.BIRTH-1-runtime,
        courier_seed=e.SEED,left_arrival=e.SEED+e.LEFT_DISTANCE,
        right_arrival=e.SEED+e.RIGHT_DISTANCE,delivery_age=g.FLAG_DELIVERY,
        delivery_slack=g.FLAG_DELIVERY-e.SEED-e.RIGHT_DISTANCE,
        native_primaries=e.NATIVE_COLUMNS,physical_frame_bits=e.FRAME_BITS,
        frame_start=e.PRIMARY_START,frame_end=e.PRIMARY_START+e.FRAME_BITS)


def retained_inputs():
    receipt=json.loads((ROOT/'figs/gray_counterexamples/GT0_clock_erasure_bank_certificate.json').read_text())
    cases=[]
    for row in receipt['results']['routes_and_native_banks']['native_banks']:
        bank={int(j):word for j,word in row['stage2_and_stage3_same_exact_native_bank'].items()}
        cases.append((str(row['receiver'])+'_actual_GT0_bank',bank,row['lower_Flag1'],True))
    # The following bank is explicitly prepared, not derived from the island.
    bank={j:dict(addr=(15+j)%e.Q if j<=0 else 0,age=15 if j<=0 else 0,
         f1=0,f2=0,wf1=0,wf2=0) for j in range(-5,6)}
    cases.append(('15_prepared_common_Age15',bank,0,False))
    return cases


def physical_run(beta,tape,lower_f1,receiver,complete=False):
    position=e.ENTRY;packet=e.initial_packet();out={}
    trace=hashlib.sha256();holders=[0]*5;minpos=e.Q;maxpos=-1
    age=e.BIRTH
    for tick in range(34396):
        newposition=position+(1 if packet.move==1 else -1 if packet.move==2 else 0)
        newpacket,write=h.step_packet(packet,newposition,tape.get(newposition,0),beta)
        newout=dict(out)
        if write is not None:newout[newposition]=write
        # One rotating holder on every tick; all five at every native store,
        # instruction transition and first/last tick. The proof covers all.
        selected=range(5) if complete or write is not None or tick in (0,34395) else (tick%5,)
        for i in selected:
            x=newposition-e.SLOTS[i]
            actual=e.local_transition(fixture(x,age,position,packet,tape,out,lower_f1=lower_f1,receiver=receiver),beta)
            assert actual.heads==tuple(h.pack(newpacket) if x+s==newposition else 0 for s in e.SLOTS)
            assert actual.early_out==tuple(newout.get(x+s,0) for s in e.SLOTS)
            assert actual.courierL==actual.courierR==(0,)*5
            assert (actual.addr,actual.age,actual.f1,actual.f2,actual.wf1,actual.wf2)==(x%e.Q,age+1,lower_f1,0,0,0)
            holders[i]+=1
        # Exactly which bits are fetched, and which source columns are loaded.
        if newpacket.mode==h.FETCH or packet.mode==h.FETCH:
            assert e.ENTRY<=newposition<5275 or packet.mode==h.SEEK
        if write is not None:assert any(a<=newposition<a+w for f,(a,w) in e.NATIVE_COLUMNS.items() if f not in ('wf1','wf2'))
        trace.update(newposition.to_bytes(2,'little'))
        trace.update(h.pack(newpacket).to_bytes((h.HEAD_BITS+7)//8,'little'))
        trace.update(bytes([2 if write is None else write]))
        minpos=min(minpos,newposition);maxpos=max(maxpos,newposition)
        position,packet,out,age=newposition,newpacket,newout,age+1
    assert packet.mode==h.HALT and age==599648
    return out,dict(all_ticks_actual_local_transition=True,rotating_and_store_holder_counts=holders,
        physical_local_transition_calls=sum(holders),trace_sha256=trace.hexdigest(),
        minimum_head_residue=minpos,maximum_head_residue=maxpos,
        output=e.native_output(out),halt_age=age)


def courier_and_delivery(beta,out,lower_f1,receiver):
    # A retained positive(1,1) context tests both carriers. For the actual
    # derived banks only(Flag1,Flag2)=(1,0) will be promoted by the proof.
    count=0;sig=hashlib.sha256();left={};right={}
    for field,source,direction,distance in (
        ('courierL',e.NATIVE_COLUMNS['f2'][0],-1,e.LEFT_DISTANCE),
        ('courierR',e.NATIVE_COLUMNS['f1'][0],1,e.RIGHT_DISTANCE)):
        payload=out.get(source,0);oldpos=source
        for tick in range(distance+1):
            newpos=source+direction*tick
            oldvalues={} if tick==0 else {oldpos:payload}
            l=oldvalues if field=='courierL' else {}
            r=oldvalues if field=='courierR' else {}
            oldage=e.SEED-1+tick
            selected=range(5) if tick in (0,distance) else (tick%5,)
            for i in selected:
                x=newpos-e.SLOTS[i]
                actual=e.local_transition(fixture(x,oldage,-1,h.ZERO,{},out,l,r,lower_f1,receiver),beta)
                expected=tuple(payload if x+s==newpos else 0 for s in e.SLOTS)
                assert getattr(actual,field)==expected,(field,tick,i)
                count+=1
            sig.update(bytes([payload]));sig.update(newpos.to_bytes(2,'little'))
            oldpos=newpos
        if field=='courierL':left={3:payload}
        else:right={e.Q-3:payload}
    # At the existing GT0 delivery, all actual raw-holder accesses read the
    # courier target. Include both targets and all five central holders.
    writes=[]
    for target,field,values in ((3,'courierL',left),(e.Q-3,'courierR',right)):
        for i in range(5):
            x=target-e.SLOTS[i]
            actual=e.local_transition(fixture(x,g.FLAG_DELIVERY-1,-1,h.ZERO,{},out,left,right,lower_f1,receiver),beta)
            data=actual.data[list(dict(g.FIELDS)).index('simbit')]
            assert data[i]==values[target]
            writes.append(dict(target=target,central_holder=x,slot=e.SLOTS[i],value=data[i]))
    return dict(actual_courier_local_transition_calls=count,
        courier_trace_sha256=sig.hexdigest(),actual_five_holder_GT0_delivery=writes)


def reset_birth_and_hold(beta,tape,lower_f1,receiver):
    checks=0;wild=replace(e.initial_packet(),mode=h.ERROR,move=3,regs=(h.MASK,)*16)
    arbitrary={p:1 for p in range(e.PRIMARY_START-8,5275+8)}
    for i in range(5):
        x=e.ENTRY-e.SLOTS[i]
        reset=e.local_transition(fixture(x,e.RESET-1,e.ENTRY,wild,tape,
            arbitrary,arbitrary,arbitrary,lower_f1,receiver),beta)
        assert reset.heads==(0,)*5 and reset.early_out==reset.courierL==reset.courierR==(0,)*5
        born=e.local_transition(fixture(x,e.BIRTH-1,-1,h.ZERO,tape,{},
            lower_f1=lower_f1,receiver=receiver),beta)
        assert born.heads==tuple(h.pack(e.initial_packet()) if x+s==e.ENTRY else 0 for s in e.SLOTS)
        assert born.early_out==(0,)*5;checks+=2
    # Actual holding after each independent motion deadline is required;
    # stopping the faster left field early must not wait for the right field.
    for field,target,arrival in (('courierL',3,e.SEED+e.LEFT_DISTANCE),
        ('courierR',e.Q-3,e.SEED+e.RIGHT_DISTANCE)):
        for i in range(5):
            x=target-e.SLOTS[i]
            kwargs={field.replace('courierL','left').replace('courierR','right'):{target:1}}
            actual=e.local_transition(fixture(x,arrival,-1,h.ZERO,tape,
                lower_f1=lower_f1,receiver=receiver,**kwargs),beta)
            assert getattr(actual,field)==tuple(int(x+s==target) for s in e.SLOTS);checks+=1
    return dict(actual_all_five_holder_reset_birth_and_independent_courier_hold_checks=checks)


def raw_total_and_source_checks(beta):
    rng=random.Random(0x4541524C59);checks=0
    # Finite raw tests of the total function, not a claimed exhaustive proof.
    for age in (e.RESET,e.BIRTH,e.BIRTH+1,e.SEED,e.SEED+1,g.FLAG_DELIVERY,
                96*e.Q,98*e.Q,112*e.Q+1,e.U-1):
        cells={j:e.Cell(addr=rng.randrange(e.Q),age=age-1,f1=rng.randrange(2),f2=rng.randrange(2),
            wf1=rng.randrange(2),wf2=rng.randrange(2),
            data=tuple(tuple(rng.randrange(2) for _ in range(5*w)) for _,w in g.FIELDS),
            heads=tuple(rng.getrandbits(e.HEAD_BITS) for _ in range(5)),
            early_out=tuple(rng.randrange(2) for _ in range(5)),
            courierL=tuple(rng.randrange(2) for _ in range(5)),
            courierR=tuple(rng.randrange(2) for _ in range(5))) for j in range(-5,6)}
        out=e.local_transition(cells,beta,(1,1),{s:(1,1) for s in e.SLOTS})
        assert 0<=out.addr<e.Q and 0<=out.age<e.U
        assert len(out.data)==len(g.FIELDS) and all(v in (0,1) for values in out.data for v in values)
        assert all(0<=v<1<<e.HEAD_BITS for v in out.heads)
        checks+=1
    # Temporal majority remains exact with every first-history bit.
    temporal=0
    for first,bank in product((0,1),repeat=2):
        assert (first&bank)|(bank&(first|bank))==bank;temporal+=1
    migration=sorted({s+j-t for s in e.SLOTS for j in (-1,0,1) for t in e.SLOTS})
    ordinary=sorted({s-t for s in e.SLOTS for t in e.SLOTS})
    deliveries=sorted({target-address-s for target,addresses in
        ((3,range(1,6)),(e.Q-3,range(e.Q-5,e.Q))) for address in addresses for s in e.SLOTS})
    assert migration==list(range(-5,6))
    assert ordinary==deliveries==list(range(-4,5))
    return dict(finite_raw_state_replays=checks,temporal_majority_boolean_identities=temporal,
        head_raw_offsets=migration,ordinary_and_delivery_raw_offsets=ordinary)


def workspace_endpoint_check(beta):
    """Retain and certify our old port transcription defect, not Gray's."""
    path=ROOT/'figs/gray_counterexamples/GE0_workspace_endpoint_initial_kernel.py.txt'
    name='_GE0_retained_old_endpoint_kernel'
    old=types.ModuleType(name);old.__file__=str(path);sys.modules[name]=old
    exec(compile(path.read_text(),str(path),'exec'),old.__dict__)
    cases=[]
    for computed_age in (96*e.Q-1,96*e.Q,98*e.Q-1,98*e.Q,98*e.Q+1):
        raw={j:e.Cell(addr=(4000+j)%e.Q,age=computed_age-1) for j in range(-5,6)}
        before=old.local_transition(raw,beta,(1,1))
        after=e.local_transition(raw,beta,(1,1))
        expected=int(96*e.Q<=computed_age<98*e.Q)
        assert (after.wf1,after.wf2)==(expected,expected)
        assert (before.wf1,before.wf2)==((1,1) if computed_age==98*e.Q else (expected,expected))
        cases.append(dict(computed_age=computed_age,old_workspace=[before.wf1,before.wf2],
            corrected_workspace=[after.wf1,after.wf2],port_values=[1,1]))
    return dict(primary_interval='[96Q,98Q)',old_closed_upper_endpoint_defect=True,
        early_claim_last_age=g.FLAG_DELIVERY,early_theorem_unchanged=True,cases=cases)


def calculate():
    beta,listing,labels=e.native_programme();programme=programme_audit(beta,listing)
    results=[]
    for name,bank,f1,derived in retained_inputs():
        tape=e.tape_from_native(bank)
        out,ticks,packet,_=e.execute(beta,tape)
        assert ticks==34396 and packet.mode==h.HALT
        expected=literal_maintenance.scalar(bank)
        assert e.native_output(out)=={f:expected[f] for f in ('addr','age','f1','f2')}
        # Only the two banks obtained from the shared actual history receive
        # all-tick physical replays. The prepared Age15 test is clearly scoped.
        physical=None
        if derived:
            physical_out,physical=physical_run(beta,tape,f1,int(name.split('_')[0]))
            assert physical_out==out
        couriers=courier_and_delivery(beta,out,f1,int(name.split('_')[0]))
        special=reset_birth_and_hold(beta,tape,f1,int(name.split('_')[0]))
        alternate=list(beta)
        for p in range(e.Q):
            if not e.ENTRY<=p<5275:alternate[p]=(p*19+7)&1
        alternate_out,alternate_ticks,alternate_packet,_=e.execute(alternate,tape)
        assert alternate_out==out and alternate_ticks==ticks and alternate_packet==packet
        results.append(dict(name=name,bank_derived_from_actual_GT0_history=derived,
            input_native_words=bank,output=e.native_output(out),runtime=ticks,
            physical=physical,couriers=couriers,special=special,
            unused_beta_completion_replay_agrees=True))
    return dict(programme=programme,retained_cases=results,raw_checks=raw_total_and_source_checks(beta),
        retained_workspace_endpoint_transcription=workspace_endpoint_check(beta),
        original_GT0_stage_endpoints_unchanged=[list(s) for s in g.STAGES],
        genuine_own_beta_or_Gray_completion=False)


def main():
    started=time.monotonic();directory=ROOT/'figs/gray_counterexamples'
    beta,listing,labels=e.native_programme();result=calculate()
    beta_path=directory/'GE0_native_prefix_beta.bin'
    beta_path.write_bytes(bytes(sum(beta[i+j]<<j for j in range(8)) for i in range(0,e.Q,8)))
    listing_path=directory/'GE0_native_prefix_listing.json'
    listing_path.write_text(json.dumps(dict(entry=e.ENTRY,code_bits=2346,labels=labels,programme=listing),indent=2)+'\n')
    sources=('gray_early_native_flags.py','gray_moving_word_kernel.py','gray_raw_gather.py',
        'literal_maintenance.py','GMW0_PHYSICAL_NATIVE_PROGRAMME.md','GT0_CLOCK_ERASURE_BANK.md')
    receipts=('GMW0_native_programme_certificate.json','GT0_clock_erasure_bank_certificate.json',
        'GT0_raw_gather_certificate.json')
    r=dict(name='GE0 actual-three-history early native evaluation and flag couriers; conditional prefix',
        Q=e.Q,U=e.U,lambda_original=e.LAMBDA,c_original=e.ERROR_SEPARATION,results=result,
        conditional_actual_GT0_history_native_execution_and_flag_delivery_proved=True,
        native_programme_is_full_own_beta=False,total_component_has_explicit_late_ports=True,
        full_intact_completion_and_final_programme_premises_remain=True,
        actual_island_first_native_Flag2_output_positive=False,
        prepared_Age15_positive_Flag2_reachability_proved=False,
        arbitrary_E0_GF_birth_transparency_proved=False,registered_components_or_active_rule_changed=False,
        early_reset_birth_run_couriers_added_explicit_schedule_change=True,
        full_Gray_or_Gacs_refutation_or_iid_reliability=False,shorter_U_proved=False,
        checker_sha256=digest(__file__),proof_sha256=digest(Path(__file__).with_name('GE0_EARLY_NATIVE_FLAGS.md')),
        source_dependencies_sha256={name:digest(Path(__file__).with_name(name)) for name in sources},
        receipt_dependencies_sha256={name:digest(directory/name) for name in receipts},
        emitted_assets_sha256={p.name:digest(p) for p in (beta_path,listing_path)},
        retained_initial_endpoint_sha256={name:digest(directory/name) for name in (
            'GE0_workspace_endpoint_initial_kernel.py.txt','GE0_workspace_endpoint_initial_proof.md',
            'GE0_workspace_endpoint_initial_checker.py.txt','GE0_workspace_endpoint_initial_validator.py.txt',
            'GE0_workspace_endpoint_initial_certificate.json','GE0_workspace_endpoint_initial_readonly_replay.log')},
        primary_Gray_text_sha256=digest(ROOT/'papers_txt/gray_readers_guide.txt'),
        elapsed_seconds=time.monotonic()-started)
    receipt=directory/'GE0_early_native_flags_certificate.json'
    receipt.write_text(json.dumps(r,indent=2)+'\n')
    print(json.dumps(dict(receipt_sha256=digest(receipt),programme=result['programme'],
        retained_outputs=[c['output'] for c in result['retained_cases']],elapsed_seconds=r['elapsed_seconds'])))


if __name__=='__main__':main()
