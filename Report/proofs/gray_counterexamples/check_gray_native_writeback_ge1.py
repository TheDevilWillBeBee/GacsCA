#!/usr/bin/env python3
"""GE1 native fifth stores and actual next-bank conditional certificate."""
from pathlib import Path
from dataclasses import replace
from itertools import product
import hashlib,json,random,sys,time
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
import gray_native_writeback_ge1 as w
import gray_early_native_flags as e
import gray_raw_gather as g
import check_gray_global_first_flags as first
import literal_maintenance as literal

BARRIERS=(-1,19)
WIDTHS=dict(g.FIELDS)
INDEX={name:i for i,(name,_) in enumerate(g.FIELDS)}
SOURCE_DEPENDENCIES=('gray_native_writeback_ge1.py','gray_early_native_flags.py',
    'gray_moving_word_kernel.py','gray_raw_gather.py','literal_maintenance.py',
    'check_gray_global_first_flags.py','GE0_EARLY_NATIVE_FLAGS.md',
    'GE0_GLOBAL_FIRST_FLAGS.md','GE0_FIRST_WORKSPACE_NATIVE.md',
    'GT0_CLOCK_ERASURE_BANK.md')
RECEIPT_DEPENDENCIES=('GE0_early_native_flags_certificate.json',
    'GE0_global_first_flags_certificate.json','GE0_first_workspace_native_certificate.json',
    'GT0_clock_erasure_bank_certificate.json')


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def phase(receiver):return int(0<=receiver<20)


def z1(receiver):
    return dict(addr=receiver%e.Q,age=1,f1=int(receiver in first.FLAG1_SUPPORT),
        f2=0,wf1=0,wf2=0)


def primary_bit(receiver,residue):
    for field,(start,width) in e.NATIVE_COLUMNS.items():
        if start<=residue<start+width:return (z1(receiver)[field]>>(residue-start))&1
    return 0


def fixture(receiver,primary,slot,computed_age,next_mode):
    """Raw local holders of the proved coherent native Out, not extra noise.

    The scalar fixtures instrument the stated conditional copy induction.
    Full physical first-bank/early execution is a pinned dependency.
    """
    x=receiver*e.Q+primary-slot;result={}
    for j in range(-5,6):
        raw=[]
        for field,width in g.FIELDS:
            values=[]
            for s in e.SLOTS:
                y=x+j+s;col,p=divmod(y,e.Q)
                for bit in range(width):
                    v=(primary_bit(col,p) if next_mode=='z1' else int(next_mode)) if field=='nextbit' else int(field=='simbit')
                    values.append(v)
            raw.append(tuple(values))
        outputs=[]
        for s in e.SLOTS:
            col,p=divmod(x+j+s,e.Q);outputs.append(primary_bit(col,p))
        result[j]=e.Cell(addr=(x+j)%e.Q,age=(computed_age-1)%e.U,
            f1=int((x+j)//e.Q in BARRIERS),data=tuple(raw),early_out=tuple(outputs))
    return result


def writeback_checks(beta):
    modes=((112*e.Q,'1','reset',0),(112*e.Q+1,'1','write',None),
        (120*e.Q-1,'1','write',None),(120*e.Q,'z1','hold',None),
        (126*e.Q,'z1','hold',None),(e.U-1,'z1','hold',None),
        (0,'z1','commit',0),(1,'0','postcommit',0))
    checks=0;signature=hashlib.sha256();first_commit={}
    for receiver,primary,slot,(age,old_next,kind,next_expected) in product(
            (-1,0,18,19,20,23),range(w.NATIVE_PRIMARY_BEGIN,w.NATIVE_PRIMARY_END),e.SLOTS,modes):
        i=e.SLOTS.index(slot);bit=primary_bit(receiver,primary)
        cells=fixture(receiver,primary,slot,age,old_next)
        conflicts={s:(1,1-primary_bit(receiver,(primary-slot+s)%e.Q)) for s in e.SLOTS}
        actual=w.local_transition(cells,beta,other_fifth_stores=conflicts)
        expected=bit if next_expected is None else next_expected
        assert actual.data[INDEX['nextbit']][i]==expected,(receiver,primary,slot,age,'nextbit')
        assert actual.data[INDEX['simbit']][i]==(bit if kind=='commit' else 1)
        assert actual.early_out[i]==bit
        assert actual.addr==(primary-slot)%e.Q and actual.age==age
        assert actual.f2==actual.wf1==actual.wf2==0
        row=(receiver,primary,slot,age,kind,bit,expected,actual.data[INDEX['simbit']][i])
        signature.update(json.dumps(row).encode());checks+=1
        if kind=='commit':first_commit[str(receiver)]=e.U-phase(receiver)
    # All payload assignments at the actual five distinct raw EarlyOut holders.
    vote_checks=0;p=e.NATIVE_COLUMNS['age'][0]
    for bits,slot in product(product((0,1),repeat=5),e.SLOTS):
        cells=fixture(18,p,slot,112*e.Q+1,'1')
        for i,t in enumerate(e.SLOTS):
            offset=slot-t;values=list(cells[offset].early_out);values[i]=bits[i]
            cells[offset]=replace(cells[offset],early_out=tuple(values))
        actual=w.local_transition(cells,beta,other_fifth_stores={s:(1,0) for s in e.SLOTS})
        assert actual.data[INDEX['nextbit']][e.SLOTS.index(slot)]==int(sum(bits)>=3)
        signature.update(bytes(bits)+bytes([e.SLOTS.index(slot)]));vote_checks+=1
    # At a non-native logical primary the declared port remains real and gated.
    p=2700;cells=fixture(21,p,0,112*e.Q+1,'0')
    actual=w.local_transition(cells,beta,other_fifth_stores={0:(1,1)})
    assert actual.data[INDEX['nextbit']][0]==1
    stores=w.native_fifth_stores(cells,{0:(1,1)})
    assert stores[0]==(1,1)
    return dict(native_primary_copy_phase_and_gate_checks=checks,
        all32_raw_five_holder_payload_checks=vote_checks,non_native_port_preserved=True,
        actual_native_EarlyOut_vs_Nextbit_vs_commit_distinguished=True,
        five_holder_first_commit_rows=first_commit,
        trace_sha256=signature.hexdigest())


def arbitrary_raw_checks(beta):
    rng=random.Random(2008192);checks=0;signature=hashlib.sha256()
    for case in range(48):
        cells={}
        for j in range(-5,6):
            data=tuple(tuple(rng.randrange(2) for _ in range(5*width)) for _,width in g.FIELDS)
            address=rng.randrange(e.Q) if case%2 else (e.PRIMARY_START+17+j)%e.Q
            cells[j]=e.Cell(address,rng.randrange(1<<20),*(rng.randrange(2) for _ in range(4)),
                data=data,heads=tuple(rng.getrandbits(e.HEAD_BITS) for _ in e.SLOTS),
                early_out=tuple(rng.randrange(2) for _ in e.SLOTS),
                courierL=tuple(rng.randrange(2) for _ in e.SLOTS),
                courierR=tuple(rng.randrange(2) for _ in e.SLOTS))
        ports={s:(rng.randrange(2),rng.randrange(2)) for s in e.SLOTS}
        actual=w.local_transition(cells,beta,(case&1,(case>>1)&1),ports)
        assert 0<=actual.addr<e.Q and 0<=actual.age<e.U
        assert all(flag in (0,1) for flag in (actual.f1,actual.f2,actual.wf1,actual.wf2))
        assert all(v in (0,1) for bits in actual.data for v in bits)
        assert all(0<=v<(1<<e.HEAD_BITS) for v in actual.heads)
        assert all(v in (0,1) for name in ('early_out','courierL','courierR') for v in getattr(actual,name))
        signature.update(repr(actual).encode());checks+=1
    return dict(retained_arbitrary_raw_state_and_finite_port_checks=checks,
        raw_Age_full_20_bit_range_used=True,trace_sha256=signature.hexdigest(),
        universal_noisy_extension_proved=False)


def crossed_barriers(receiver,offset):
    return tuple(f for f in BARRIERS if min(receiver,receiver+offset)<=f<=max(receiver,receiver+offset))


def bank(receiver):
    return {d:z1(receiver+d) if d==0 or not crossed_barriers(receiver,d) else
        dict(addr=0,age=0,f1=0,f2=0,wf1=0,wf2=0) for d in range(-5,6)}


def route_checks():
    rows=[];signature=hashlib.sha256();endpoint_checks=0
    affected=set(range(-6,5))|set(range(14,25))
    assert affected==set(f-d for f in BARRIERS for d in range(-5,6))
    for receiver,offset,start in product(range(-6,25),range(-5,6),(32*e.Q,64*e.Q)):
        walls=crossed_barriers(receiver,offset);endpoints=[]
        kind='self' if offset==0 else 'erased' if walls else 'exact-held-committed-source'
        for residue in (5,e.Q-5):
            capture=e.U+start+(2+abs(offset)*e.Q if offset else 1)-phase(receiver)
            assert e.U+start-1<capture<=e.U+69*e.Q+2
            if offset==0:origin=('direct_committed_SimBit',receiver*e.Q+residue)
            elif walls:
                y=receiver*e.Q+residue;candidates=[]
                for f in walls:
                    wall=y if f==receiver else f*e.Q if offset>0 else (f+1)*e.Q-1
                    steps=abs(wall-y);row=capture-1-steps
                    assert 0<=steps<=abs(offset)*e.Q and e.U+start<=row<capture
                    assert f*e.Q<=wall<(f+1)*e.Q
                    candidates.append((steps,wall,row))
                origin=('permanent_flagged_mailbox',min(candidates))
            else:
                assert phase(receiver+offset)==phase(receiver)
                assert capture-1-(e.U+start+1-phase(receiver+offset))==abs(offset)*e.Q
                assert e.U-phase(receiver+offset)<e.U+start+1-phase(receiver+offset)
                origin=('actual_held_Z1_same_primary', (receiver+offset)*e.Q+residue)
            endpoints.append(dict(residue=residue,capture=capture,origin=origin));endpoint_checks+=1
            # The actual scalar route names and zero/reset priority are retained.
            local_age=g.capture_age(1 if start==32*e.Q else 2,offset+5)
            expected=('simbit' if offset==0 else 'mailR' if offset<0 else 'mailL',0,0)
            assert g.scalar_plan(local_age,residue,0,'history2' if start==32*e.Q else 'history3',offset+5)==expected
        row=dict(receiver=receiver,offset=offset,start_after_U=start,kind=kind,
            barrier_colonies=walls,affine_residue_endpoints=endpoints)
        rows.append(row);signature.update(json.dumps(row,sort_keys=True).encode())
    return dict(barrier_colonies=BARRIERS,erased_record_receiver_classes=sorted(affected),
        routes=rows,affine_endpoint_checks=endpoint_checks,interior_residue_interval=[5,e.Q-5],
        all_native_primaries_in_checked_interval=True,
        no_surviving_route_crosses_a_clock_jump=True,
        bank_ready_physical_row=e.U+70*e.Q,route_signature_sha256=signature.hexdigest())


def actual_history_captures(beta):
    """Instrument the proven old-mail origin with actual raw holder accesses.

    These local fixtures are derived from B1, rather than independently
    supplied upper states. The preceding route proof supplies their old
    Mailbox values; this check certifies the local capture interface.
    """
    primaries=tuple(start for start,_ in e.NATIVE_COLUMNS.values())
    checks=0;signature=hashlib.sha256();resets=0
    for receiver,primary,slot,age in product((-1,0,18,19,20,23),primaries,e.SLOTS,
            (0,32*e.Q,64*e.Q)):
        cells=fixture(receiver,primary,slot,age,'0')
        for j,cell in list(cells.items()):
            data=list(cell.data)
            for field in ('history1','history2','history3'):data[INDEX[field]]=(1,)*55
            cells[j]=replace(cell,data=tuple(data))
        actual=w.local_transition(cells,beta)
        assert actual.data[INDEX['history2']]==((1,)*55 if age==64*e.Q else (0,)*55)
        assert actual.data[INDEX['history3']]==(0,)*55
        signature.update(json.dumps(('reset',receiver,primary,slot,age,e.U+age-phase(receiver))).encode())
        resets+=1
    for receiver,primary,offset,stage,slot in product((-1,0,18,19,20,23),
            primaries,range(-5,6),(1,2),e.SLOTS):
        age=g.capture_age(stage,offset+5)
        cells=fixture(receiver,primary,slot,age,'0')
        def bit_from(word,residue):
            for field,(start,width) in e.NATIVE_COLUMNS.items():
                if start<=residue<start+width:return (word[field]>>(residue-start))&1
            return 0
        for j,cell in list(cells.items()):
            data=list(cell.data);sim=[];mail=[]
            for s in e.SLOTS:
                y=receiver*e.Q+primary-slot+j+s;col,p=divmod(y,e.Q)
                sim.append(primary_bit(col,p));mail.append(bit_from(bank(col)[offset],p))
            data[INDEX['simbit']]=tuple(sim)
            data[INDEX['mailL']]=data[INDEX['mailR']]=tuple(mail)
            data[INDEX['history'+str(stage+1)]]=(1,)*55
            cells[j]=replace(cell,data=tuple(data))
        actual=w.local_transition(cells,beta)
        expected=bit_from(bank(receiver)[offset],primary)
        at=e.SLOTS.index(slot)*11+offset+5
        assert actual.data[INDEX['history'+str(stage+1)]][at]==expected
        row=(receiver,primary,offset,stage,slot,age,e.U+age-phase(receiver),expected)
        signature.update(json.dumps(row).encode());checks+=1
    # If the two later histories agree, every H1 bit gives their exact majority.
    for later,h1 in product((0,1),repeat=2):
        assert (h1&later)|(later&(h1|later))==later
    return dict(actual_raw_holder_History2_History3_capture_checks=checks,
        actual_raw_history_reset_or_nonreset_hold_checks=resets,
        checked_lower_colony_clock_phases=[0,1],receiver_classes=[-1,0,18,19,20,23],
        six_representative_native_primary_fields=True,
        both_later_banks_temporal_majority_for_arbitrary_History1_bit=True,
        trace_sha256=signature.hexdigest(),
        old_Mailbox_origin_is_supplied_by_the_proved_actual_route=True)


def derived_native_checks(beta):
    rows=[];signature=hashlib.sha256()
    for receiver in range(-8,25):
        records=bank(receiver);actual=literal.scalar(records)
        out,ticks,packet,_=e.execute(beta,e.tape_from_native(records))
        expected={key:actual[key] for key in ('addr','age','f1','f2')}
        assert e.native_output(out)==expected and ticks==34396 and packet.mode==e.head.HALT
        assert actual['addr']==receiver%e.Q and actual['f2']==0
        row=dict(receiver=receiver,actual_next_History2_History3_native_bank=records,
            literal_native_result=expected,emitted_native_prefix_result=e.native_output(out),
            prepared_native_head_updates=ticks)
        rows.append(row);signature.update(json.dumps(row,sort_keys=True).encode())
    ages={receiver:literal.scalar(bank(receiver))['age'] for receiver in range(18,24)}
    assert ages=={18:2,19:1,20:1,21:1,22:1,23:2}
    assert all(literal.scalar(bank(receiver))['age']==2 for receiver in (-9,25,e.Q-1,e.Q,e.Q+1))
    return dict(finite_next_bank_and_literal_prefix_classes=rows,
        exact_native_programme_executions=len(rows),head_ticks=34396*len(rows),
        derived_native_Ages_18_through23=ages,next_bank_globally_common_Ages=False,
        result_signature_sha256=signature.hexdigest(),
        actual_second_early_run_or_late_Workspace_trajectory_proved=False)


def calculate():
    beta,listing,_=e.native_programme()
    assert len(listing)==107 and sum(row['bits'] for row in listing)==2346
    packed=bytes(sum(beta[i+j]<<j for j in range(8)) for i in range(0,e.Q,8))
    assert digest(ROOT/'figs/gray_counterexamples/GE0_native_prefix_beta.bin')==hashlib.sha256(packed).hexdigest()
    return dict(transition_manifest=w.transition_manifest(),native_writeback=writeback_checks(beta),
        finite_raw_checks=arbitrary_raw_checks(beta),actual_next_gather_routes=route_checks(),
        actual_local_history_capture=actual_history_captures(beta),
        derived_next_bank_native_outputs=derived_native_checks(beta))


def main():
    started=time.monotonic();source=Path(__file__).parent;directory=ROOT/'figs/gray_counterexamples'
    results=calculate()
    receipt=dict(name='GE1 changed native fifth writer and next actual bank, conditional component',
        Q=e.Q,U=e.U,lambda_original=e.LAMBDA,c_original=e.ERROR_SEPARATION,
        proof_sha256=digest(source/'GE1_NATIVE_WRITEBACK_SECOND_BANK.md'),checker_sha256=digest(__file__),
        source_dependencies_sha256={name:digest(source/name) for name in SOURCE_DEPENDENCIES},
        receipt_dependencies_sha256={name:digest(directory/name) for name in RECEIPT_DEPENDENCIES},
        assets_sha256={name:digest(directory/name) for name in ('GE0_native_prefix_beta.bin','GE0_native_prefix_listing.json',
            'GE1_native_writeback_initial_checker.txt','GE1_native_writeback_initial_check.log',
            'GE1_native_writeback_launch_timeout.txt')},
        primary_Gray_text_sha256=digest(ROOT/'papers_txt/gray_readers_guide.txt'),results=results,
        same_shared_clock_only_row0_fault=[0,17*e.Q],no_later_errors=True,
        original_real2_geometry_reused=True,actual_first_native_result_not_preloaded=True,
        explicit_native_only_fifth_store_change=True,remaining_ports_are_declared=True,
        own_beta_final_layout_intact_completion_and_literal_Workspace_are_premises=True,
        conditional_native_first_commit_and_actual_next_bank_proved=True,
        retained_initial_checker_failure='one-byte-per-bit comparison to packed-bit beta; corrected without rule change',
        universal_noisy_extension_or_full_period_or_positive_Flag2_repair=False,
        faithful_Gray_refutation_or_iid_theorem=False,shorter_U_or_active_rule_change=False,
        elapsed_seconds=time.monotonic()-started)
    path=directory/'GE1_native_writeback_second_bank_certificate.json'
    path.write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(dict(receipt_sha256=digest(path),native_commit_and_next_bank_proved_conditionally=True,
        next_native_Ages=results['derived_next_bank_native_outputs']['derived_native_Ages_18_through23'],
        full_Gray_or_iid_result=False,elapsed_seconds=time.monotonic()-started)))


if __name__=='__main__':main()
