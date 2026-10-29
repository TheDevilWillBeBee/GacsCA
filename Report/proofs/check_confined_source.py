#!/usr/bin/env python3
"""SP10 actual source identities and shifted/canonical anchor truth table.

Packet persistence and the seven-site band require their stated raw GF
and clock premises. This is not an arbitrary-island or iid theorem.
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
from gacsca.netlist import Net,Compiled,at_least,w_in_range,w_add_const_mod
from check_shifted_halfline import dominant_bit
import check_fast_mail_proposal as transport
import proposed_sparse_confined_source448 as proposed


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def bounded(kind):
    p = proposed.parameters()
    maintenance,_ = proposed.proposed_build(symbolic=True)
    _,source = proposed.actual_net(p)
    class BoundNet(Net):
        def input(self,key):
            if key[0]=='x':
                _,off,field,bit = key
                if kind=='zero_command' and field=='info':
                    return 0
                if kind=='three_sources' and field=='wf2' and off in (-2,0,4):
                    return 1
            return super().input(key)
    namespace = dict(rule_g.__dict__,Net=BoundNet,maj5=dominant_bit,
                     maintenance=SimpleNamespace(build=maintenance),
                     OFFSETS=tuple(range(-12,13)),sparse_controls=transport.sparse_controls,
                     sparse_table=proposed.dependency_table(p))
    exec(compile(source,'<SP10 actual source identities>', 'exec'),namespace)
    n = namespace['build'](p)
    age = [at_least(n,[n.input_node['x',j,'age',bit] for j in range(-5,6)],6)
           for bit in range(p.m)]
    gate = w_in_range(n,age,p.age_code(p.T_wf),p.age_code(p.T_wf+4*p.Q-1)+1)
    anchor = at_least(n,[w_in_range(n,w_add_const_mod(n,
                        [n.input_node['x',j,'addr',bit] for bit in range(p.k)],(-j)%p.Q,p.Q),0,6)
                        for j in range(-5,6)],6)
    if kind=='three_sources':
        expected = n.AND(gate,anchor)
    else:
        memory = at_least(n,[n.input_node['x',j,'wf2',0] for j in range(-5,6)],3)
        expected = n.all([gate,anchor,memory])
    assert n.outputs['y','wf2',0] == expected
    return dict(all_raw_Address_flags_Ages_other_data_and_instructions_free=True,
                three_preset_WF2_offsets=[-2,0,4] if kind=='three_sources' else None,
                all_raw_Info_inputs_zero=kind=='zero_command',
                actual_WF2_equals_clock_gate_AND_anchor=kind=='three_sources',
                actual_WF2_equals_clock_gate_AND_anchor_AND_memory=kind=='zero_command')


def anchor_truth(p):
    n = Net()
    for j in range(-5,6):
        a = [n.input(('raw',j,bit)) for bit in range(p.k)]
        n.set_output(('qualifier',j),w_in_range(n,w_add_const_mod(n,a,(-j)%p.Q,p.Q),0,6))
    comp = Compiled(n)
    x = np.repeat(np.arange(p.Q),2)
    phase = np.tile([-1,0],p.Q)
    raw = {j:(x+j+phase)%p.Q for j in range(-5,6)}
    y = comp.evaluate({('raw',j,bit):((raw[j]>>bit)&1).astype(bool)
                       for j in range(-5,6) for bit in range(p.k)},bool)
    expected = (x+phase)%p.Q < 6
    for j in range(-5,6):
        assert np.array_equal(y['qualifier',j],expected)
    assert all(expected[(x==a)].all() for a in range(1,6))
    assert all(not expected[(x==a)].any() for a in range(7,p.Q))
    return dict(valid_Address_offset_phase_cases=2*p.Q*11,
                both_phases_qualify_at_residues=list(range(1,6)),
                neither_phase_qualifies_at_residues=list(range(7,p.Q)),
                union_possible_anchor_residues=list(range(7)),
                each_neighbor_phase_can_be_chosen_independently=True,
                min_qualifiers_with_two_faults_on_packet_holders=9,
                max_qualifiers_with_two_faults_outside_band=2)


def main():
    out = ROOT/'figs/robustness'
    candidate = proposed.load_artifact()
    p = candidate.p
    prior = out/'SP9_corrected_source_certificate.json'
    prior_receipt = json.loads(prior.read_text())
    assert prior_receipt['primitive_truth_table']['complete_Boolean_assignments']==2048
    assert prior_receipt['legal_clock_gate_assignments']==p.U
    result = dict(proposal='SP10',proposed_rule_change=True,active_G17_modified=False,
                  proposed_candidate_sha256=candidate.digest(),proposed_netlist_sha256=candidate.comp.digest,
                  proposal_source_sha256=digest(Path(proposed.__file__)),checker_sha256=digest(Path(__file__)),
                  build_receipt_sha256=digest(out/'SP10_program_build.json'),
                  helpers_sha256=digest(ROOT/'gacsca/netlist.py'),
                  dominant_bit_helper_sha256=digest(ROOT/'Report/proofs/check_shifted_halfline.py'),
                  transport_checker_sha256=digest(Path(transport.__file__)),
                  full_rule_sha256=digest(ROOT/'gacsca/rule_g.py'),
                  full_generated_source_sha256=hashlib.sha256(proposed.actual_net(p)[1].encode()).hexdigest(),
                  SP9_threshold_and_clock_receipt_sha256=digest(prior),
                  identities={kind:bounded(kind) for kind in ('zero_command','three_sources')},
                  anchor_truth_table=anchor_truth(p),Q=p.Q,U=p.U,source_active_legal_input_ticks=4*p.Q,
                  conditional_physical_packet_holders=list(range(1,6)),
                  conditional_computed_source_band_per_true_colony=list(range(7)),
                  clock_cohort_and_anchor_premises_in_arbitrary_GF_established=False,
                  general_island_repair_established=False,global_reliability_established=False,
                  scope='actual full-rule source identities and exact phase/anchor truth table; conditional packet and confinement proof ROBUSTNESS J71')
    (out/'SP10_confined_source_certificate.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(actual_cofactors=2,anchor_cases=2*p.Q*11,conditional_band=list(range(7)))))


if __name__ == '__main__':
    main()
