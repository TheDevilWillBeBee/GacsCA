#!/usr/bin/env python3
"""All-receiver first actual GT0 banks, scoped to the GE0 prefix premises."""
from pathlib import Path
from itertools import product
import hashlib,json,sys,time
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
import gray_early_native_flags as e
import gray_raw_gather as g
import literal_maintenance as literal

BARRIERS=(-1,16)
FLAG1_SUPPORT=(-3,-2,-1,13,14,15,16,17,18,19)


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def phase(receiver):return int(0<=receiver<17)


def crossed_barriers(receiver,offset):
    return tuple(f for f in BARRIERS if min(receiver,receiver+offset)<=f<=max(receiver,receiver+offset))


def bank(receiver):
    return {d:dict(addr=(receiver+d)%e.Q if d==0 or not crossed_barriers(receiver,d) else 0,
        age=0,f1=0,f2=0,wf1=0,wf2=0) for d in range(-5,6)}


def wall_origin(receiver,offset,residue,start):
    """Nearest actual flagged coordinate on the backward Mailbox path."""
    y=receiver*e.Q+residue
    capture=start+2+abs(offset)*e.Q-phase(receiver)
    candidates=[]
    for f in crossed_barriers(receiver,offset):
        if receiver==f:wall=y
        elif offset>0:wall=f*e.Q
        else:wall=(f+1)*e.Q-1
        steps=abs(wall-y)
        assert 0<=steps<=abs(offset)*e.Q
        assert f*e.Q<=wall<(f+1)*e.Q
        candidates.append((steps,wall,capture-1-steps))
    return min(candidates) if candidates else None


def route_classes():
    rows=[];signature=hashlib.sha256();endpoint_checks=0;erased=surviving=0
    # All noncanonical banks lie in the following finite receiver range.
    # Each path row is affine in p; these are the endpoints of p in[5,Q-5].
    for receiver,offset,start in product(range(-6,22),range(-5,6),(32*e.Q,64*e.Q)):
        walls=crossed_barriers(receiver,offset)
        kind='self' if offset==0 else 'erased' if walls else 'exact-held-source'
        endpoints=[]
        for residue in (5,e.Q-5):
            capture=start+2+abs(offset)*e.Q-phase(receiver) if offset else start+1-phase(receiver)
            assert start-1<capture<70*e.Q
            if offset==0:origin=('self',receiver*e.Q+residue)
            elif walls:
                steps,wall,row=wall_origin(receiver,offset,residue,start)
                assert row>=start>2731
                origin=('permanent_flagged_mailbox',wall,row,steps);erased+=1
            else:
                assert phase(receiver+offset)==phase(receiver)
                assert capture-1-(start+1-phase(receiver+offset))==abs(offset)*e.Q
                assert all(not crossed_barriers(receiver,d) for d in range(min(0,offset),max(0,offset)+1))
                origin=('held_exact_same_residue', (receiver+offset)*e.Q+residue);surviving+=1
            endpoints.append(dict(residue=residue,capture=capture,origin=origin));endpoint_checks+=1
        item=dict(receiver=receiver,offset=offset,start=start,kind=kind,barrier_colonies=walls,
            affine_residue_endpoints=endpoints)
        rows.append(item);signature.update(json.dumps(item,sort_keys=True).encode())
    # Any receiver outside this union has no barrier in any nonself path.
    affected=set(range(-6,5))|set(range(11,22))
    derived=set(f-d for f in BARRIERS for d in range(-5,6))
    assert derived==affected
    assert all((crossed_barriers(r,d)!=()) <= (r in affected)
        for r,d in product(range(-7,23),range(-5,6)))
    return dict(affected_receivers=sorted(affected),route_classes=rows,
        all_interior_residues=[5,e.Q-5],affine_endpoint_checks=endpoint_checks,
        actual_erased_wall_endpoint_checks=erased,exact_source_endpoint_checks=surviving,
        no_surviving_path_crosses_a_clock_jump=True,
        route_signature_sha256=signature.hexdigest())


def native_outputs():
    beta,listing,labels=e.native_programme();rows=[];signature=hashlib.sha256()
    for receiver in range(-6,22):
        words=bank(receiver);actual=literal.scalar(words)
        expected=dict(addr=receiver%e.Q,age=1,f1=int(receiver in FLAG1_SUPPORT),f2=0)
        assert {field:actual[field] for field in expected}==expected
        out,ticks,packet,_=e.execute(beta,e.tape_from_native(words))
        assert ticks==34396 and packet.mode==e.head.HALT
        assert e.native_output(out)==expected
        row=dict(receiver=receiver,records=words,literal_native_output=expected,
            actual_emitted_programme_output=e.native_output(out),physical_head_ticks=ticks,
            physical_delivery_row=80*e.Q-1-phase(receiver))
        rows.append(row);signature.update(json.dumps(row,sort_keys=True).encode())
    # Pin the two subtle boundary calculations, including the coincident
    # adjusted zero record that creates a right majority at receiver-4.
    minus4=bank(-4)
    adjusted={d:(minus4[d]['addr']-d)%e.Q for d in range(1,6)}
    assert [d for d in adjusted if adjusted[d]==e.Q-4]==[1,2,4]
    assert literal.scalar(minus4)['f1']==0
    assert literal.scalar(bank(-3))['f1']==1
    assert literal.scalar(bank(19))['f1']==1 and literal.scalar(bank(20))['f1']==0
    assert all(word['age']==word['f1']==word['f2']==word['wf1']==word['wf2']==0
        for receiver in range(-6,22) for word in bank(receiver).values())
    return dict(all_noncanonical_receiver_classes=rows,Flag1_command_support=FLAG1_SUPPORT,
        all_integer_Gf_correct_and_Age_one=True,all_integer_Flag2_commands_zero=True,
        actual_emitted_native_executions=len(rows),actual_head_ticks=sum(row['physical_head_ticks'] for row in rows),
        minus4_adjusted_right_Gf=adjusted,minus4_correct_majority_offsets=[1,2,4],
        native_result_signature_sha256=signature.hexdigest(),latest_physical_delivery_row=80*e.Q-1,
        canonical_outside_affected_intervals_argument_reused=True,
        actual_late_Workspace_or_future_period_proved=False)


def calculate():return dict(routes=route_classes(),native_and_GE0_outputs=native_outputs())


def main():
    started=time.monotonic();source=Path(__file__).parent;directory=ROOT/'figs/gray_counterexamples'
    results=calculate()
    receipt=dict(name='GE0 all-receiver actual first three-history native flags, conditional prefix',
        Q=e.Q,U=e.U,lambda_original=e.LAMBDA,c_original=e.ERROR_SEPARATION,
        proof_sha256=digest(source/'GE0_GLOBAL_FIRST_FLAGS.md'),checker_sha256=digest(__file__),
        source_dependencies_sha256={name:digest(source/name) for name in
            ('gray_early_native_flags.py','gray_raw_gather.py','literal_maintenance.py',
             'GE0_EARLY_NATIVE_FLAGS.md','GT0_CLOCK_ERASURE_BANK.md')},
        receipt_dependencies_sha256={name:digest(directory/name) for name in
            ('GE0_early_native_flags_certificate.json','GT0_clock_erasure_bank_certificate.json')},
        primary_Gray_text_sha256=digest(ROOT/'papers_txt/gray_readers_guide.txt'),results=results,
        same_shared_clock_only_row0_fault=[0,17*e.Q],no_later_errors=True,
        original_real2_error_geometry_reused=True,full_intact_GE0_completion_and_own_beta_are_premises=True,
        all_integer_actual_first_GT0_banks_and_GE0_delivery_proved_conditionally=True,
        no_preloaded_bank_or_independent_upper_history=True,
        positive_actual_Flag2_command_or_late_Workspace_repair_proved=False,
        full_Gray_or_Gacs_refutation_or_iid_theorem=False,
        new_rule_or_shorter_U_or_registered_component_edits=False,
        elapsed_seconds=time.monotonic()-started)
    path=directory/'GE0_global_first_flags_certificate.json'
    path.write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(dict(receipt_sha256=digest(path),first_Flag1_support=FLAG1_SUPPORT,
        first_Flag2_zero=True,actual_emitted_executions=results['native_and_GE0_outputs']['actual_emitted_native_executions'],
        elapsed_seconds=time.monotonic()-started)))


if __name__=='__main__':main()
