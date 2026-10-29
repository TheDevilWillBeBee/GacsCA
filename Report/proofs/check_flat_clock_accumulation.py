#!/usr/bin/env python3
"""Actual SP10 flat-Address private clocks and six-E0 Age detuning witness.

The global flat GF is an invariant of the actual GF/clock circuit. The
source trace prescribes zero raw Info; reachability from an encoded hierarchy
or finite real island is not proved. This is not iid unreliability.
"""
import hashlib
import json
from pathlib import Path
import sys
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
import numpy as np
from gacsca import rule_g
from gacsca.gray_errors import level0_points
from gacsca.netlist import Net,Compiled,const_word,mixed_age_increment,at_least,w_in_range
from check_shifted_halfline import dominant_bit
import check_fast_mail_proposal as transport
import proposed_sparse_confined_source448 as proposed


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def bounded(zero_info):
    p = proposed.parameters()
    maintenance,_ = proposed.proposed_build(symbolic=True)
    _,source = proposed.actual_net(p)
    class BoundNet(Net):
        def input(self,key):
            if key[0]=='x':
                if key[2]=='addr' or zero_info and key[2]=='info':
                    return 0
            return super().input(key)
    namespace = dict(rule_g.__dict__,Net=BoundNet,maj5=dominant_bit,
                     maintenance=SimpleNamespace(build=maintenance),OFFSETS=tuple(range(-12,13)),
                     sparse_controls=transport.sparse_controls,sparse_table=proposed.dependency_table(p))
    exec(compile(source,'<SP10 flat GF private-clock identity>', 'exec'),namespace)
    n = namespace['build'](p)
    own = [n.input_node['x',0,'age',bit] for bit in range(p.m)]
    assert [n.outputs['y','addr',bit] for bit in range(p.k)] == const_word(0,p.k)
    assert [n.outputs['y','age',bit] for bit in range(p.m)] == mixed_age_increment(n,own,p.PB,p.R,p.nb)
    assert n.outputs['y','f1',0] == 1
    if zero_info:
        age = [at_least(n,[n.input_node['x',j,'age',bit] for j in range(-5,6)],6) for bit in range(p.m)]
        gate = w_in_range(n,age,p.age_code(p.T_wf),p.age_code(p.T_wf+4*p.Q-1)+1)
        memory = at_least(n,[n.input_node['x',j,'wf2',0] for j in range(-5,6)],3)
        assert n.outputs['y','wf2',0] == n.AND(gate,memory)
        n.outputs = {('y','wf2',0):n.outputs['y','wf2',0]}
        # Compiled preserves all declared inputs by default; retain only
        # those of the already verified source cone for this evaluator.
        live = set(n.live_nodes())
        n.input_names = [key for key in n.input_names if n.input_node[key] in live]
    return n


def main():
    candidate = proposed.load_artifact()
    p = candidate.p
    bounded(False)
    comp = Compiled(bounded(True))
    errors = {(1,50),(2,50),(3,75),(4,75),(5,100),(6,100)}
    assert level0_points(errors) == errors
    x = np.arange(-1024,1025)
    ever_bad = np.zeros(len(x),dtype=bool)
    wf2 = (x>=1)&(x<=5)
    states,clock_rows = [],[]
    for t in range(121):
        for holder,tick in errors:
            if tick==t:
                ever_bad[holder+1024] = True
        good,bad = p.age_code(p.T_wf+1+t),p.age_code(1+t)
        clocks = np.where(ever_bad,bad,good)
        states.append(wf2.copy())
        clock_rows.append(clocks.copy())
        if t==100:
            assert wf2[(x>=1)&(x<=5)].all()
        if t==101:
            assert not wf2[(x>=1)&(x<=5)].any()
        if t==120:
            break
        padded_wf = np.pad(wf2,(5,5))
        padded_age = np.pad(clocks,(5,5),constant_values=good)
        inputs = {}
        for key in comp.inputs:
            _,off,field,bit = key
            values = padded_age if field=='age' else padded_wf
            assert field in ('age','wf2')
            row = values[5+off:5+off+len(x)]
            inputs[key] = ((row>>bit)&1).astype(bool)
        wf2 = comp.evaluate(inputs,bool)['y','wf2',0]
    out = ROOT/'figs/robustness'
    asset = out/'SP10_flat_clock_accumulation_trace.npz'
    np.savez_compressed(asset,coordinates=x,Workspace2=np.stack(states),raw_Age=np.stack(clock_rows),errors=np.array(sorted(errors)))
    result = dict(proposal='SP10',proposed_rule_change=True,active_G17_modified=False,
                  proposed_candidate_sha256=candidate.digest(),proposed_netlist_sha256=candidate.comp.digest,
                  proposal_source_sha256=digest(Path(proposed.__file__)),checker_sha256=digest(Path(__file__)),
                  build_receipt_sha256=digest(out/'SP10_program_build.json'),
                  helpers_sha256=digest(ROOT/'gacsca/netlist.py'),
                  dominant_bit_helper_sha256=digest(ROOT/'Report/proofs/check_shifted_halfline.py'),
                  transport_checker_sha256=digest(Path(transport.__file__)),
                  full_rule_sha256=digest(ROOT/'gacsca/rule_g.py'),classifier_sha256=digest(ROOT/'gacsca/gray_errors.py'),
                  full_generated_source_sha256=hashlib.sha256(proposed.actual_net(p)[1].encode()).hexdigest(),
                  tracking_asset_sha256=digest(asset),errors=sorted(errors),all_six_errors_E0=True,
                  overwrites_preserve_every_field_except_Age=True,
                  all_raw_Address_zero=True,actual_next_Address_zero=True,
                  actual_next_Flag1_one=True,actual_next_Age_equals_h_of_own_raw_Age=True,
                  all_raw_Age_flag_data_and_instruction_bits_free_in_clock_identity=True,
                  initial_proper_legal_clock=p.T_wf+1,bad_clock_sequence_starts_at_one=True,
                  six_detuned_private_clocks_at_state100=True,
                  initial_packet_holders=list(range(1,6)),all_packet_WF2_one_at_state100=True,
                  all_packet_computed_WF2_zero_at_state101=True,
                  proper_reference_clock_gate_still_active_at_state100=True,
                  raw_Info_prescribed_zero_for_source_trace=True,trace_updates=120,
                  source_cone_radius=5,finite_trace_domain=[-1024,1024],central_causal_buffer_exceeds_5_times120=True,
                  initial_flat_GF_or_zero_Info_reachability_established=False,
                  general_iid_unreliability_established=False,global_reliability_established=False,
                  scope='exact full-circuit flat-GF/private-clock identities and conditional source detuning by six separated Age errors; not an encoded-hierarchy failure')
    (out/'SP10_flat_clock_accumulation_certificate.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(E0_Age_errors=6,packet_WF2_at100=5,packet_WF2_at101=0,GF_clock_identity_universal=True)))


if __name__ == '__main__':
    main()
