#!/usr/bin/env python3
"""Exact singleton-GF native-wipe wake in GR1's broad encoded family.

This is not a refutation from Gray's intact all-level initialization. The
upper raw Workspace.Flag1 starts1, which the broad noiseless encoding
theorem permits. SF heals on the next update; no memory failure follows.
"""
from pathlib import Path
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT)); sys.path.insert(0,str(ROOT/'Report/proofs'))
from gacsca import maintenance,gray_errors
from gacsca.netlist import Net,const_word
from check_g17_schedule import Terms
import gray_staged_rule as proposed


def digest(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    out=ROOT/'figs/gray_counterexamples'; candidate=proposed.load_artifact()
    p=candidate.p; comp=candidate.comp; terms=Terms()
    y=p.Q-3; rawtime=96*p.Q+1
    phases=sorted({0,p.Q}|set(range(1,6))|set(range(p.Q-5,p.Q)))[:-1]
    for phase in phases:
        n=Net(); cells={j:dict(addr=const_word((phase+j)%p.Q,p.k),age=const_word(0,p.m),
            f1=0,f2=0,wf1=1,wf2=0) for j in range(-5,6)}
        got=maintenance.build(n,cells,p.k,p.m)
        assert (got['f1'],got['f2'])==(1,0)
    def initial(site,field,bit,punctured):
        phase=site%p.Q
        if field=='addr': return ((((site+1)%p.Q) if punctured and site==y else phase)>>bit)&1
        if field=='age': return (rawtime>>bit)&1
        if field=='f1': return int(phase>=p.Q-8)
        if field=='f2' or field=='wf2': return 0
        if field=='wf1': return int(phase>=p.Q-5)
        if field=='reg': return 0
        width=proposed.logical_width(field,p); slot,b=divmod(bit,width)
        logical=site+slot-2
        if field=='info': return int(logical%p.Q!=3)
        if field in ('h1','h2','h3'): return terms.var(('coherent_history',field,logical,b))
        return 0
    def update(site,punctured,old=None):
        nodes=[0,1]
        for name in comp.inputs:
            if name[0]=='I': value=terms.var(('irrelevant_I',site,old is not None,name[1]))
            else:
                _,x,field,bit=name
                value=(initial(site+x,field,bit,punctured) if old is None else
                       old[site+x]['y',field,bit])
            nodes.append(value)
        for op,a,b in comp.gates: nodes.append(terms.op(op,nodes[a],nodes[b]))
        return {name:nodes[index] for name,index in comp.outputs.items()}
    first={punctured:{site:update(site,punctured) for site in range(y-10,y+11)}
           for punctured in (False,True)}
    differences=[]
    for site in range(y-10,y+11):
        changed=[name for name in comp.outputs if first[False][site][name]!=first[True][site][name]]
        if changed: differences.append(dict(site=site,outputs=[list(name) for name in changed]))
    assert len(differences)==1 and differences[0]['site']==y
    changed=differences[0]['outputs']
    assert len(changed)==171
    for b in range(5):
        assert first[False][y]['y','info',b]==1 and first[True][y]['y','info',b]==0
    assert first[False][y]['y','wf1',0]==1 and first[True][y]['y','wf1',0]==0
    for field,width in (('addr',p.k),('age',p.m),('f1',1),('f2',1)):
        assert all(first[False][y]['y',field,b]==first[True][y]['y',field,b] for b in range(width))
    restored=0
    for site in range(y-5,y+6):
        clean=update(site,False,first[False]); noisy=update(site,True,first[True])
        assert clean==noisy,site
        restored+=len(clean)
    locations=[(y,rawtime)]
    classification=gray_errors.classify(locations,Q=p.Q,U=p.U,sep=104)
    assert gray_errors.level0_points(locations)==set(locations)
    assert classification['level0']==1 and not classification['level1']
    result=dict(candidate='GR1',Q=p.Q,U=p.U,width=candidate.W,
        candidate_sha256=candidate.digest(),netlist_sha256=comp.digest,
        error_lambda=24,error_separation_c=104,error_set=locations,
        error_classification=classification,
        overwrite=dict(site=y,time=rawtime,field='addr',old=p.Q-3,new=p.Q-2),
        raw_geometry_corrected_next_tick=True,
        native_Flag1_and_Flag2_equal_next_tick=True,
        clean_primary_Info_next_tick=1,noisy_primary_Info_next_tick=0,
        raw_simulation_difference_at_clean_time=rawtime+1,
        raw_simulation_difference_sites=[y],
        first_tick_changed_outputs=changed,
        histories_symbolic_and_fivefold_coherent=True,
        upper_flag_seed_native_cofactors=len(phases),
        full_compiled_net_cofactors=64,second_tick_exact_restoration_equalities=restored,
        all_local_outputs_restored_by_time=rawtime+2,
        clean_encoded_context='Choose upper s with canonical GF/common Age0, raw Workspace.Flag1=1 at every upper cell, Flag1/Flag2/Workspace.Flag2=0, and all other upper fields0. Encode s in the broad E family with unrepresented initial logicalInfo1. The universal prefix gives upper newFlags(1,0), so at80Q−1 Info(Q−3)=1 and Info(3)=0. At96Q Workspace.Flag1 pulses on the last five cells of every colony. At96Q+1 native Flag1 is1 exactly in the last eight cells, every native Flag2 is0, represented and unrepresented Info is unchanged except the courier cells, and all private fields except the retained coherent histories are0.',
        full_GR1_broad_E_context_reachability_proved=True,
        clean_period_receipt_sha256=digest(out/'GR1_noiseless_period_certificate.json'),
        raw_self_GF_wipe_wake_proved=True,
        unconditional_one_step_raw_copy_transparency_refuted=True,
        proof_scope='The singleton is genuine E0 and its mandatory GF-mismatch/Flag1 wipe changes primaryInfo on the following clean tick. In this full GR1 broad-E encoded context every local output recovers one tick later. This refutes only unconditional one-step raw-field transparency; the earlier conditional primitive theorem requires unchanged wipe controls and is unaffected.',
        gray_intact_all_level_initialization_reachability_proved=False,
        gray_Proposition2_or4_refuted=False,corrected_gray_refuted=False,
        whole_encoded_period_memory_failure_proved=False,iid_unreliability_proved=False,
        checker_sha256=digest(__file__),proposal_sha256=digest(proposed.__file__),
        active_native_source_sha256=digest(maintenance.__file__),
        classifier_sha256=digest(gray_errors.__file__),
        term_library_sha256=digest(ROOT/'Report/proofs/check_g17_schedule.py'),
        gray_verbatim_simulation=False,global_reliability_established=False,measured_only=False)
    (out/'GR1_wipe_wake_certificate.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({key:result[key] for key in ('raw_self_GF_wipe_wake_proved',
        'full_GR1_broad_E_context_reachability_proved','raw_simulation_difference_at_clean_time',
        'all_local_outputs_restored_by_time','second_tick_exact_restoration_equalities',
        'gray_intact_all_level_initialization_reachability_proved','iid_unreliability_proved')}))


if __name__=='__main__': main()
