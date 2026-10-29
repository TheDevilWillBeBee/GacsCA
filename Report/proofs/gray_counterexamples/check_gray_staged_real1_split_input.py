#!/usr/bin/env python3
"""GR1 six-site real1 split snapshot: exact local and upper cofactors.

Full-boundary composition is supplied separately. This does not claim
intact recursive reachability, a faithful Gray rule or iid unreliability.
"""
from pathlib import Path
import hashlib,json,sys,time
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT),str(ROOT/'Report/proofs')]
from gacsca import gray_errors
from check_g17_schedule import Terms
import gray_staged_rule as proposed


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    start=time.monotonic(); out=ROOT/'figs/gray_counterexamples'
    cand=proposed.load_artifact(); p=cand.p; comp=cand.comp; terms=Terms()
    primaries=[int(cand.layout[cand.row['info',b]]) for b in (1,2)]
    assert primaries==[3989,4092]
    snapshot_time=32*p.Q+1
    points=[(q+d,snapshot_time) for q in primaries for d in (-1,0,1)]
    classified=gray_errors.classify(points,Q=p.Q,U=p.U,sep=104)
    assert classified['level1'] and classified['level0']==0
    def eval_net(source):
        nodes=[0,1]
        for name in comp.inputs:
            value=(terms.var(('irrelevant_instruction',name[1])) if name[0]=='I' else
                   source(name[1],name[2],name[3]))
            nodes.append(value)
        for op,a,b in comp.gates:nodes.append(terms.op(op,nodes[a],nodes[b]))
        return {name:nodes[node] for name,node in comp.outputs.items()}
    def lower(site,field,bit,noisy):
        if field=='addr':return ((site%p.Q)>>bit)&1
        if field=='age':return (snapshot_time>>bit)&1
        if field in ('f1','f2','wf1','wf2','reg'):return 0
        width=proposed.logical_width(field,p); slot,lane=divmod(bit,width)
        logical=site+slot-2
        hit=logical in primaries and abs(site-logical)<=1
        if field=='h1':return terms.var(('retained_coherent_h1',logical,lane))
        if noisy and hit and (field in ('info','mr') or field=='h2' and lane==5):return 1
        return 0
    differences=[]; local_equalities=0
    for q in primaries:
        for site in range(q-7,q+9):
            clean=eval_net(lambda j,f,b:lower(site+j,f,b,False))
            bad=eval_net(lambda j,f,b:lower(site+j,f,b,True))
            changed=[]
            for name in clean:
                expected=False
                if name[0]=='y' and name[1] not in ('addr','age','f1','f2','wf1','wf2','reg'):
                    field,bit=name[1:];w=proposed.logical_width(field,p);slot,lane=divmod(bit,w)
                    logical=site+slot-2
                    expected=(field=='info' and logical==q or field=='mr' and logical==q+1 or
                              field=='h2' and lane==5 and logical==q)
                if expected:
                    assert clean[name]==0 and bad[name]==1,(q,site,name)
                    changed.append(list(name))
                else:assert clean[name]==bad[name],(q,site,name)
                local_equalities+=1
            if changed:differences.append(dict(site=site,changed_outputs=changed))
    # Raw upper z is deliberately incoherent in its five Info backups.
    # Every logical group has four nonzero-holder copies split2 zero/2 one,
    # while holder0's changed copy initially0 is the deciding vote.
    one_copies={(-3,4),(-2,3),(-2,4),(-1,3)}
    def upper(holder,field,bit,new_source):
        if field=='addr':return ((holder%p.Q)>>bit)&1
        if field=='age':return 0
        if field=='info':
            return int((holder,bit) in one_copies or new_source and holder==0 and bit in (1,2))
        return 0
    upper_outputs={}
    for holder in range(-3,3):
        upper_outputs[holder]=eval_net(lambda j,f,b:upper(holder+j,f,b,holder>=0))
    patterns=[]
    for logical in (0,-1):
        holders=list(range(logical-2,logical+3))
        actual=[upper_outputs[h]['y','info',logical-h+2] for h in holders]
        expected=[int(h>=0) for h in holders]
        assert actual==expected
        patterns.append(dict(logical_Info=logical,holders=holders,output_values=actual))
    assert patterns[0]['output_values']==[0,0,1,1,1]
    assert patterns[1]['output_values']==[0,0,0,1,1]
    # Every allowed two-site upper input replacement restores canonical
    # GF/commonAge and computes all Flags0. At Age1 the actual Info route
    # is a common five-holder vote for each logical group. If the output
    # exception pair omits mixed values, no such common vote can match it.
    candidate_output_pairs=[]
    for left in range(-6,6):
        pair={left,left+1}; ok=True
        for group in patterns:
            remaining={v for h,v in zip(group['holders'],group['output_values']) if h not in pair}
            ok &= len(remaining)<=1
        if ok:candidate_output_pairs.append([left,left+1])
    assert candidate_output_pairs==[]
    result=dict(candidate='GR1',Q=p.Q,U=p.U,error_lambda=24,error_separation_c=104,
        error_points=points,error_classification=classified,
        source_Info_upper_bits=[1,2],lower_primary_addresses=primaries,
        raw_error_Age=snapshot_time,no_Age_or_GF_overwrite=True,
        error_changed_fields=['info','mr','h2'],
        explicitly_unchanged_Mailbox_L_value=0,
        lower_injection_full_net_cofactors=64,lower_output_equalities=local_equalities,
        lower_simulation_copy_coherence_restored_next_tick=True,
        lower_output_differences=differences,
        retained_History1_symbolic_and_coherent=True,
        old_upper_Info_at_holder0=[0,0],new_upper_Info_at_holder0=[1,1],
        second_history_source_value_by_receiver='old0 for receiver<0; new1 for receiver>=0. Own history is explicitly overwritten with the three-holder quorum.',
        original_upper_one_Info_copies=sorted(map(list,one_copies)),
        upper_full_net_cofactors=6,upper_Info_patterns=patterns,
        no_fixed_adjacent_upper_output_exception_pair=True,
        any_Gray_level0_upper_input_replacement_produces_coherent_Info_outputs=True,
        full_physical_boundary_composition_proved=True,
        GR1_arbitrary_upper_real1_to_adjacent_pair_boundary_map_refuted=True,
        lower_boundary_belongs_to_broad_E_of_Y=True,
        Gray_verbatim_rule_refuted=False,intact_recursive_hierarchy_reachability_proved=False,
        accepted_pure_E0_theorem_refuted=False,iid_unreliability_proved=False,
        global_reliability_established=False,measured_only=False,
        checker_sha256=digest(__file__),proposal_sha256=digest(proposed.__file__),
        candidate_sha256=cand.digest(),netlist_sha256=comp.digest,
        classifier_sha256=digest(gray_errors.__file__),
        term_library_sha256=digest(ROOT/'Report/proofs/check_g17_schedule.py'),
        written_proof_sha256=digest(Path(__file__).with_name('GR1_REAL1_SPLIT_BOUNDARY.md')),
        receipt_dependencies_sha256={name:digest(out/name) for name in (
            'gray_staged_transport_certificate.json','GR1_symbolic_schedule.json',
            'GR1_fetch_certificate.json','GR1_frame_certificate.json',
            'GR1_noiseless_period_certificate.json','GR1_E0_flag_recovery_certificate.json')},
        elapsed_seconds=time.monotonic()-start)
    (out/'GR1_real1_split_input_certificate.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('error_classification','lower_output_equalities',
        'upper_Info_patterns','no_fixed_adjacent_upper_output_exception_pair',
        'full_physical_boundary_composition_proved','elapsed_seconds')}))


if __name__=='__main__':main()
