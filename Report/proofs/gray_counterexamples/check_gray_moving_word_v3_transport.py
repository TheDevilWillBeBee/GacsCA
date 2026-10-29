#!/usr/bin/env python3
"""GMW3 fast transport obstruction and full-vote restoration component.

This does not certify an own beta, Gray refinement or an intact hierarchy.
All raw payloads are covered in the written transport/three-vote argument;
finite packet replays are retained separately as measured checks.
"""
from pathlib import Path
from dataclasses import replace
from itertools import combinations
import hashlib,json,random,sys,time
import numpy as np
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT))
import gray_moving_word_v3 as k
from gacsca import gray_errors


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def visible_mask(s,delta):
    return tuple(abs(s+delta-t)<=5 for t in k.SLOTS)


def transport_identities():
    masks={}
    for delta in (-3,-2,-1,0,1,2,3):
        masks[str(delta)]=[list(visible_mask(s,delta)) for s in k.SLOTS]
        assert min(sum(m) for m in masks[str(delta)])>=3
    bitcases=0
    for correct in (0,1):
        for count in range(3):
            for faults in combinations(range(5),count):
                for assignment in range(1<<count):
                    source=[correct]*5
                    for i,j in enumerate(faults):source[j]=(assignment>>i)&1
                    for delta in (-3,3):
                        result=[k.old.vote([v if seen else 0 for v,seen in zip(source,visible_mask(s,delta))]) for s in k.SLOTS]
                        assert sum(v==correct for v in result)>=3
                        assert k.old.vote(result)==correct
                        # No false1 is possible from <=2 overwritten holders.
                        assert all(v<=correct for v in result)
                        bitcases+=1
    # Abstract control covers arbitrary clipped payloads, via Q bitwise<=P.
    # For p=1 source movement m, clipped movement can be any submask of m;
    # clipped metadata may request any stride1..3. Full votes are exact.
    # Different clipped slots may choose different submasks/strides.
    controlcases=0
    for move in range(4):
        for actual_stride in (1,2,3):
            actual_dest=actual_stride if move==1 else -actual_stride if move==2 else 0
            for clipped_move in range(4):
                if clipped_move&~move:continue
                for clipped_p in (0,1):
                    for clipped_stride in (1,2,3):
                        for dest in range(-3,4):
                            correctslots=0
                            for s in k.SLOTS:
                                full=all(visible_mask(s,-dest))
                                m=move if full else clipped_move
                                p=1 if full else clipped_p
                                stride=actual_stride if full else clipped_stride
                                accepted=bool(p and ((dest==0 and m in (0,3)) or
                                    (dest>0 and m==1 and stride==dest) or
                                    (dest<0 and m==2 and stride==-dest)))
                                # Only the opaque payload can be wrong at a
                                # clipped vote; all full slots are exact.
                                if (accepted==(dest==actual_dest)) and (full or not accepted):correctslots+=1
                                controlcases+=1
                            assert correctslots>=3
    # Arbitrary source words/collisions: at least three destination slots
    # have ALL seven prospective packet votes exact, simultaneously.
    supports=0
    for count in range(3):
        for faults in combinations(range(-5,6),count):
            good=[s for s in k.SLOTS if all(sum(delta-t not in faults
                for t in k.SLOTS if abs(s+delta-t)<=5)>=3 for delta in range(-3,4))]
            assert len(good)>=3,(faults,good)
            supports+=1
    assert supports==67
    return masks,bitcases,controlcases,supports


def physical_witness(beta,rest_period=0):
    start=k.HEAD_ADDRESS;lo=start-75;hi=start+150;sites=np.arange(lo,hi+1)
    payload=k.Packet(p=1,move=1,mode=k.SEEK,start=start+120,width=1,index=0,kind=1,lane=5)
    initialage=112*k.Q+1
    def baseline(x,age):
        return k.Cell(addr=x%k.Q,age=age,program=tuple(beta[(x+s)%k.Q] for s in k.SLOTS))
    state={x:replace(baseline(x,initialage),heads=tuple(k.pack(payload) if x+s==start else 0 for s in k.SLOTS)) for x in sites}
    reference=dict(state);points=[(start-1,0),(start,0),(start+24,8)];replacement=[]
    def overwrite(t):
        for x,tt in points:
            if tt==t:
                state[x]=replace(state[x],heads=(0,)*5)
                replacement.append((x,t,k.cell_bits(state[x])))
    overwrite(0);rows=[];clean=[]
    for t in range(10):
        rows.append(np.array([k.cell_bits(state[x]) for x in sites],np.uint8))
        clean.append(np.array([k.cell_bits(reference[x]) for x in sites],np.uint8))
        if t==9:break
        age=initialage+t
        def advance(old):
            return {x:k.local_transition({j:old.get(x+j,baseline(x+j,age)) for j in range(-5,6)},beta,rest_period) for x in sites}
        state=advance(state);reference=advance(reference);overwrite(t+1)
    if rest_period==0:
        for t in range(1,9):
            logical=start+3*t
            actual=[k.cell_from_bits(rows[t][logical-s-lo].tolist()).heads[q] for q,s in enumerate(k.SLOTS)]
            if t<8:assert actual==[k.pack(payload),0,0,k.pack(payload),k.pack(payload)]
            else:assert actual==[0,0,0,k.pack(payload),k.pack(payload)]
        assert all(not any(c.heads) for c in state.values())
        assert any(any(c.heads) for c in reference.values())
        assert not np.array_equal(rows[-1],clean[-1])
    else:
        # Same shared admissible history causes no disagreement after tick9:
        # its second singleton is far from the slower reference head.
        assert np.array_equal(rows[-1],clean[-1])
    classified=gray_errors.classify(points,Q=k.Q,U=k.U,sep=104)
    assert classified['level0']==3 and not classified['candidate_level1']
    groups=(points[:2],points[2:])
    assert all(abs(x-y)>=24 or abs(t-s)>=24 for x,t in groups[0] for y,s in groups[1])
    assert min(abs(x-y) for x,t in groups[0] for y,s in groups[1])==24
    assert lo+5*9<start-1 and start+3*9<hi-5*9
    return dict(sites=sites,actual=np.array(rows),reference=np.array(clean),
        errors=np.array(points,np.int32),replacements=np.array([a[2] for a in replacement],np.uint8)),classified


def main():
    started=time.monotonic();directory=ROOT/'figs/gray_counterexamples'
    beta=(0,)*65536
    masks,bits,controls,supports=transport_identities()
    witness,classification=physical_witness(beta,0)
    restored,_=physical_witness(beta,2)
    asset=directory/'GMW3_unpaused_E0_transport_witness.npz'
    np.savez_compressed(asset,**witness,restored_actual=restored['actual'],restored_reference=restored['reference'])
    bpath=directory/'GMW3_transport_zero_beta.bin';bpath.write_bytes(bytes(8192))
    result=dict(name='GMW3 padded three-site travel E0 loss and paired restoration component',Q=k.Q,U=k.U,
        lambda_original=24,c_original=104,frame_bits=k.FRAME_BITS,raw_transport_radius=5,
        unavailable_source_copies_zero_padded=True,visible_masks=masks,
        transport_bit_cofactors=bits,opaque_head_control_cofactors=controls,
        arbitrary_source_fault_supports=supports,
        unpaused_one_step_five_copy_closure_refuted=True,
        unpaused_original_E0_history_head_loss_proved=True,actual_error_points=witness['errors'].tolist(),
        error_tick_origin=112*k.Q+1,absolute_error_points=[
            [int(x),int(t)+112*k.Q+1] for x,t in witness['errors']],
        original_error_classification=classification,error_separation_minimum_spatial_distance=24,
        first_wake_logical_copy_presence=[1,0,0,1,1],lost_all_five_copies_on_output_tick=9,
        immutable_zero_beta_is_own_programme=False,input_is_prepared_SEEK_head=True,
        initial_context_is_intact_recursive_hierarchy=False,
        same_error_history_rest_period2_finite_recovery_checked=True,
        paired_fast_then_one_site_restore_proof_uses_diameter20_less_than_lambda24=True,
        arbitrary_packet_replacement_universal_transport_proof_in_written_argument=True,
        arbitrary_word_replacement_covered_bitwise=True,
        no_false_presence_from_two_fault_sites_by_threshold3=True,
        longer_restoration_periods_proved=False,universal_own_recompiled_beta_identity_proved=False,
        physical_gather_flag_special_write_whole_period_completed=False,
        faithful_Gray_or_iid_failure_proved=False,faster_U_used=False,
        active_rule_modified=False,global_reliability_established=False,
        kernel_sha256=digest(k.__file__),base_GMW2_kernel_sha256=digest(k.base.__file__),
        checker_sha256=digest(__file__),asset_sha256=digest(asset),beta_sha256=digest(bpath),
        proof_sha256=digest(Path(__file__).with_name('GMW3_FAST_TRANSPORT.md')),
        classifier_sha256=digest(ROOT/'gacsca/gray_errors.py'),wall_seconds=time.monotonic()-started)
    (directory/'GMW3_fast_transport_certificate.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))


if __name__=='__main__':main()
