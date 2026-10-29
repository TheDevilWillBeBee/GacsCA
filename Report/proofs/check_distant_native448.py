#!/usr/bin/env python3
"""Exact local/native certificate; real1 geometry proof is ROBUSTNESS J125.

No full own-ROM, higher-island, simulation-data or iid theorem. Proof
shortcuts are justified by literal primitive truth tables and word
identities, not by sampled GF/Age trajectories.
"""
from itertools import combinations
import hashlib,json
from pathlib import Path
import sys,time
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
import numpy as np
from gacsca.netlist import (Net,Compiled,const_word,mixed_age_increment,
                           w_eq_const)
from check_right_barrier import dominant_majority,check_dominance_primitive
import proposed_distant_native448 as proposed


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dominant_quorum(n,values,default):
    # If three existing words literally agree, the 3/4 bitwise vote is
    # that word and at least three valid equality tests are true.
    for word,valid in values:
        if valid==1 and sum(other==word and flag==1 for other,flag in values)>=3:
            return word,1
    return proposed.block_quorum(n,values,default)


def quorum_truth():
    checks=0
    for bad in range(4):
        n=Net();common=n.input(('common',));fault=n.input(('fault',))
        default=n.input(('default',));valid=n.input(('valid',))
        values=[([fault],valid) if j==bad else ([common],1) for j in range(4)]
        value,exists=proposed.block_quorum(n,values,[default])
        n.set_output(('value',),value[0]);n.set_output(('exists',),exists)
        patterns=np.arange(16,dtype=np.uint32)
        inputs={(name,):((patterns>>b)&1).astype(bool)
                for b,name in enumerate(('common','fault','default','valid'))}
        got=Compiled(n).evaluate(inputs,bool)
        assert np.array_equal(got['value',],inputs['common',]) and got['exists',].all()
        checks+=len(patterns)
    return checks


def one_bad_block(p,address,bad):
    n=Net();common=[n.input(('common_Age',b)) for b in range(p.m)]
    cells={}
    corrupt={proposed.CENTERS[bad]+u for u in range(-2,3)}
    for j in range(-32,33):
        cells[j]=dict(
            addr=[n.input(('arbitrary_GF',j,b)) for b in range(p.k)] if j in corrupt or j==0 else const_word((address+j)%p.Q,p.k),
            age=[n.input(('arbitrary_Age',j,b)) for b in range(p.m)] if j in corrupt or j==0 else common)
    out,exists=proposed.refine_one(n,cells,p,0,dominant_majority,dominant_quorum)
    assert exists==1 and out['addr']==const_word(address,p.k) and out['age']==common


def native_cofactor(p,address):
    n=Net();common=[n.input(('common_Age',b)) for b in range(p.m)]
    cells={j:dict(addr=const_word((address+j)%p.Q,p.k),age=common,
        **{f:n.input((j,f)) for f in ('f1','f2','wf1','wf2')}) for j in range(-37,38)}
    force=n.input(('arbitrary_service_force',))
    out=proposed.previous.proposed_build(symbolic=True)[0](n,cells,p.k,p.m,
        Q=p.Q,nb=p.nb,radix=p.R,pos_bits=p.PB,service_force=force)
    assert out['addr']==const_word(address,p.k) and out['age_now']==common
    assert out['age']==mixed_age_increment(n,common,p.PB,p.R,p.nb)


def main():
    started=time.monotonic();p=proposed.parameters();base=proposed.previous.load_artifact()
    n,comp,source=proposed.cached(p)
    raw={j:{f:[n.input(('x',j,f,b)) for b in range(w)]
             for f,w in proposed.schema(p)} for j in proposed.OFFSETS}
    refined=proposed.refine(n,raw,p)
    cells={j:dict(value,**refined[j]) if j in refined else value for j,value in raw.items()}
    previous=proposed.previous
    epoch=previous.base.starter.epoch(n,cells,p)
    pressure=previous.pulse(n,cells,p)
    service=previous.service.build(n,{j:dict(packet_tag=cells[j]['packet_tag'],packet_count=cells[j]['packet_count'],
        packet_valid=cells[j]['packet_valid'][0],wf2=cells[j]['wf2'][0],
        flag_valid=cells[j]['service_valid'][0],flag_position=cells[j]['service_position'],
        flag_count=cells[j]['service_count']) for j in range(-5,6)})
    native={j:dict(addr=cells[j]['addr'],age=cells[j]['age'],
        **{f:cells[j][f][0] for f in ('f1','f2','wf1','wf2')}) for j in proposed.OFFSETS}
    mt=previous.proposed_build()[0](n,native,p.k,p.m,Q=p.Q,nb=p.nb,radix=p.R,pos_bits=p.PB,
        service_force=n.any([service['service_force'],epoch['force'],pressure['signal']]))
    wiring=0
    for field in ('addr','age'):
        for b,node in enumerate(mt[field]):
            assert n.outputs['y',field,b]==node
            wiring+=1
    assert wiring==26
    five=check_dominance_primitive();four=quorum_truth()
    checks=0
    for address in range(p.Q):
        for bad in range(4):
            one_bad_block(p,address,bad);checks+=1
        native_cofactor(p,address)
    # Every pair of sample blocks is c16 separated, and all four lie
    # in an interval of spatial diameter64, below real1's24Q radius.
    separation_checks=0
    for a,b in combinations(proposed.CENTERS,2):
        for x in range(a-2,a+3):
            for y in range(b-2,b+3):
                assert abs(x-y)>=16
                separation_checks+=1
    assert 64<24*p.Q and max(abs(x) for x in proposed.OFFSETS)==37
    # The gate-level mixed-radix clock identity, on all legal clocks.
    clock=Net();bits=[clock.input(('age',b)) for b in range(p.m)]
    after=mixed_age_increment(clock,bits,p.PB,p.R,p.nb)
    for b,node in enumerate(after): clock.set_output(('age',b),node)
    all_ages=np.arange(p.U,dtype=np.uint32)
    codes=np.array([p.age_code(int(t)) for t in all_ages],dtype=np.uint32)
    inputs={('age',b):((codes>>b)&1).astype(bool) for b in range(p.m)}
    got=Compiled(clock).evaluate(inputs,bool)
    expected=np.array([p.age_code(int((t+1)%p.U)) for t in all_ages],dtype=np.uint32)
    assert all(np.array_equal(got['age',b],((expected>>b)&1).astype(bool)) for b in range(p.m))
    profile={}
    live=set(n.live_nodes())
    for key,node in n.input_node.items():
        if key[0]=='x' and node in live:
            _,offset,field,bit=key
            profile.setdefault((field,bit),set()).add(offset)
    rank=max(len(offsets-{0}) for offsets in profile.values())
    assert all(len(offsets-{0})==64 for (field,_),offsets in profile.items()
               if field in ('addr','age'))
    details={field:dict(nonzero_offsets=sorted(set.union(*(offsets-{0} for (f,_),offsets in profile.items() if f==field))),
                       max_rank=max(len(offsets-{0}) for (f,_),offsets in profile.items() if f==field))
             for field in ('addr','age')}
    outdir=ROOT/'figs/robustness'
    receipt=dict(proposal='distant_native448_local_module',proposed_rule_change=True,
        standalone_unincorporated_module=True,active_G17_modified=False,SP22_modified=False,
        checker_sha256=digest(Path(__file__)),proposal_source_sha256=digest(Path(proposed.__file__)),
        parent_proposal_source_sha256=digest(Path(previous.__file__)),
        parent_candidate_sha256=base.digest(),parent_netlist_sha256=base.comp.digest,
        helpers_sha256=digest(ROOT/'gacsca/netlist.py'),
        majority_proof_helper_sha256=digest(ROOT/'Report/proofs/check_right_barrier.py'),
        parent_local_source_sha256=digest(Path(previous.local.__file__)),
        module_raw_netlist_sha256=comp.digest,module_generated_source_sha256=hashlib.sha256(source.encode()).hexdigest(),
        actual_maintenance_source_sha256=hashlib.sha256(previous.proposed_build()[1].encode()).hexdigest(),
        Q=p.Q,U=p.U,width=proposed.width(p),radius_change=[12,37],sample_centers=list(proposed.CENTERS),
        refined_logical_offsets=list(proposed.REFINED),joint_pair_bits=p.k+p.m,
        full_output_native_wiring_identities=wiring,five_word_dominance_truth_assignments=five,
        four_block_dominance_truth_assignments=four,one_bad_block_free_word_cofactors=checks,
        all_phase_native_maintenance_free_common_Age_and_flags_cofactors=p.Q,
        sample_block_point_separation_checks=separation_checks,all_legal_clock_increment_cases=p.U,
        initial_GF_and_common_Age_canonical_required=True,all_other_initial_fields_and_I_arbitrary=True,
        global_error_set_E0_union_actual_real1_required=True,higher_errors_allowed=False,
        at_most_one_dense_faulted_sample_block_geometry_proof='ROBUSTNESS J125',
        all_time_computed_GF_Age_under_E0_plus_real1_proved=True,
        raw_current_error_sites_can_still_have_wrong_native_fields=True,
        full_net_live_gates=len(comp.gates),actual_dependency_max_nonzero_rank=rank,
        actual_native_dependency_profile=details,old_capture_rank=12,
        old_capture_layout_covers_new_rule=False,own_programme_built=False,
        represented_Info_copy_keep_GF_equality_changed=True,
        self_simulation_complete_encoding_or_upper_error_map_proved=False,
        iid_threshold_or_global_reliability_established=False,global_reliability_established=False,
        seconds=time.monotonic()-started,
        scope='exact unincorporated joint distant native refinement and E0+actual-real1 native induction; no own ROM, higher-island or data-map theorem')
    (outdir/'distant_native448_certificate.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(dict(native_wiring=wiring,cofactors=checks,radius=37,required_rank=rank,
                         old_rank=12,own_ROM=False,seconds=receipt['seconds'])),flush=True)


if __name__=='__main__':
    main()
