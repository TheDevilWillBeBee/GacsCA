#!/usr/bin/env python3
"""Exact source/front certificate for J121's changed SP22 native transition.

The all-time native reconstruction induction is written in ROBUSTNESS.
The own ROM is loaded for identity. Complete encoding is certified
separately; no full upper map, confinement or iid theorem is proved here.
"""
from itertools import combinations
import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from gacsca.netlist import Net,Compiled,const_word,mixed_age_increment,w_eq_const
from check_right_barrier import dominant_majority
import proposed_sparse_backward_fitted448 as proposed


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def cells(n,p,address,faults,clock,source=False):
    result={}
    for j in range(-6,9):
        y=address+j
        good=j not in faults
        result[j]=dict(addr=const_word(y%p.Q,p.k) if good else [n.input((j,'addr',b)) for b in range(p.k)],
            age=const_word(p.age_code(clock),p.m) if good else [n.input((j,'age',b)) for b in range(p.m)],
            backward_pressure=[1 if good else n.input((j,'backward_pressure',0))],
            packet_tag=const_word(y-1,4) if source and 1<=y<=5 and good else [n.input((j,'packet_tag',b)) for b in range(4)],
            packet_count=[n.input(('common_count',b)) for b in range(11)] if source and 1<=y<=5 and good else [n.input((j,'packet_count',b)) for b in range(11)],
            packet_valid=[1 if source and 1<=y<=5 and good else n.input((j,'packet_valid',0))],
            wf2=[1 if source and 1<=y<=5 and good else n.input((j,'wf2',0))],
            **{f:n.input((j,f)) for f in ('f1','f2','wf1')})
    return result


def main():
    p=proposed.parameters()
    candidate=proposed.load_artifact()
    n,comp=proposed.cached(p)
    assert candidate.comp.digest==comp.digest
    source=proposed.generated_source(p)
    # Literal actual full-output wiring, with I and all raw fields free.
    read=lambda j,f,b:n.input(('x',j,f,b))
    cc={j:{f:[read(j,f,b) for b in range(w)] for f,w in proposed.schema(p)} for j in range(-12,13)}
    sig=proposed.pulse(n,cc,p)
    epoch=proposed.base.starter.epoch(n,cc,p)
    service=proposed.service.build(n,{j:dict(packet_tag=cc[j]['packet_tag'],packet_count=cc[j]['packet_count'],
        packet_valid=cc[j]['packet_valid'][0],wf2=cc[j]['wf2'][0],
        flag_valid=cc[j]['service_valid'][0],flag_position=cc[j]['service_position'],flag_count=cc[j]['service_count']) for j in range(-5,6)})
    native={j:dict(addr=cc[j]['addr'],age=cc[j]['age'],**{f:cc[j][f][0] for f in ('f1','f2','wf1','wf2')}) for j in range(-12,13)}
    mt=proposed.proposed_build()[0](n,native,p.k,p.m,Q=p.Q,nb=p.nb,radix=p.R,pos_bits=p.PB,
        service_force=n.any([service['service_force'],epoch['force'],sig['signal']]))
    commit=w_eq_const(n,mt['age_now'],p.age_code(p.U-1))
    assert n.outputs['y','backward_pressure',0]==n.AND(sig['signal'],n.NOT(commit))
    identities=1
    for field in ('addr','age'):
        for b,node in enumerate(mt[field]):
            assert n.outputs['y',field,b]==node
            identities+=1
    assert identities==27
    front=0
    for address in range(p.Q-1):
        for faults in combinations(range(1,6),2):
            q=Net()
            cc=cells(q,p,address,faults,p.T_wf+449)
            cut=lambda n,c:n.input(('arbitrary_packet_force',))
            out=proposed.pulse(q,cc,p,dominant_majority,cut)
            assert out['signal']==1 and out['addr']==const_word(address,p.k)
            assert out['age']==const_word(p.age_code(p.T_wf+449),p.m)
            native_cells={j:dict(c,wf2=c['wf2'][0]) for j,c in cc.items()}
            native=proposed.proposed_build(symbolic=True)[0](q,native_cells,p.k,p.m,Q=p.Q,nb=p.nb,radix=p.R,pos_bits=p.PB,service_force=out['signal'])
            assert native['addr']==const_word(address,p.k)
            assert native['age']==const_word(p.age_code(p.T_wf+450),p.m)
            front+=1
    source_checks=0
    for address in range(-1,8):
        for faults in combinations(range(-6,7),2):
            q=Net()
            cc=cells(q,p,address,faults,p.T_wf+1,source=True)
            out=proposed.pulse(q,cc,p,dominant_majority)
            assert out['packet']==1 and out['signal']==1,(address,faults)
            source_checks+=1
    assert (front,source_checks)==(4470,702)
    boundaries=0
    for clock in range(p.T_wf+1,p.T_wf+1793):
        q=Net()
        cc=cells(q,p,p.Q-1,(),clock)
        for j in range(1,6):
            cc[j]['backward_pressure']=[1]
        out=proposed.pulse(q,cc,p,dominant_majority,lambda n,c:0)
        assert out['window']==1
        assert out['signal']==0
        assert mixed_age_increment(q,const_word(p.age_code(clock),p.m),p.PB,p.R,p.nb)==const_word(p.age_code(clock+1),p.m)
        boundaries+=1
    assert 2+(p.Q-1)==449 <898<1150<1792<p.U-p.T_wf
    outdir=ROOT/'figs/robustness'
    receipt=dict(proposal='SP22',proposed_rule_change=True,standalone_unincorporated_module=False,
        active_G17_modified=False,SP18_modified=False,
        inherited_checker_source_sha256=digest(ROOT/'Report/proofs/check_backward_pressure448.py'),
        checker_sha256=digest(Path(__file__)),proposal_source_sha256=digest(Path(proposed.__file__)),
        base_source_sha256=digest(Path(proposed.base.__file__)),packet_detector_source_sha256=digest(Path(proposed.detector.__file__)),
        helpers_sha256=digest(ROOT/'gacsca/netlist.py'),
        module_raw_netlist_sha256=comp.digest,module_generated_source_sha256=hashlib.sha256(source.encode()).hexdigest(),
        actual_maintenance_source_sha256=hashlib.sha256(proposed.proposed_build()[1].encode()).hexdigest(),
        epoch_receipt_sha256=digest(outdir/'right_epoch_starter_certificate.json'),
        incorporation_receipt_sha256=digest(outdir/'SP18_incorporation_encoded_certificate.json'),
        proposed_candidate_sha256=candidate.digest(),initial_epoch_clock=p.T_wf,NPe=p.NPe,MP=p.MP,
        Q=p.Q,U=p.U,width=317,radius=12,history_ranks=12,
        actual_native_pressure_GF_Age_output_wiring_identities=identities,
        right_five_arbitrary_two_word_front_and_native_cofactors=front,
        source_injection_readers=[-1,7],source_injection_arbitrary_two_word_cofactors=source_checks,
        source_free_GF447_valve_clock_checks=boundaries,
        proper_packet_source_states=[1,1792],previous_colony_GF_Age_reconstruction_state=449,
        previous_colony_Flag1_WF1_quiet_deadline=1150,
        expanded_native_halfline_initial_boundary=0,expanded_native_halfline_boundary=-448,
        initial_positive_GF_Age_epoch_halfline_required=True,initial_negative_GF_Age_flags_work_arbitrary=True,
        global_E0_required=True,future_right_native_boundary_prescribed=False,
        native_column_reconstruction_and_post_quiet_preservation_proved=True,
        first_previous_colony_structural_workspace_reset_state=p.U-p.T_wf,
        own_ROM_or_self_simulating_candidate_built=True,
        healthy_complete_encoding_self_simulation_proved=False,
        left_damage_confinement_or_finite_island_erosion_established=False,
        represented_Info_or_full_upper_error_map_established=False,
        iid_threshold_established=False,global_reliability_established=False,
        scope='ROBUSTNESS J122 (J121 equations at NPe65/MP75): explicit one-bit backward-pressure full local transition with I free; reconstruct previous colony from correct positive epoch GF/Age and global E0; native theorem for the actual own ROM; confinement/data map/iid remain unproved')
    (outdir/'SP22_backward_native_certificate.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(dict(front=front,injection=source_checks,reconstructed=449,quiet=1150,own_ROM=True,iid=False)),flush=True)


if __name__=='__main__':
    main()
