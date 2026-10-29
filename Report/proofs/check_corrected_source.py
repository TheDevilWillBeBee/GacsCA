#!/usr/bin/env python3
"""Exact SP9 physical-source identities and threshold truth table.

The packet persistence induction is conditional on six agreeing raw clocks
in each eleven-site window. It does not prove that premise in damaged GF,
or a global source envelope, general eroder, or iid theorem.
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
from gacsca.netlist import Net,Compiled,at_least,w_in_range
from check_shifted_halfline import dominant_bit
import check_fast_mail_proposal as transport
import proposed_sparse_corrected_source448 as proposed


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
    exec(compile(source,'<SP9 actual source identities>', 'exec'),namespace)
    n = namespace['build'](p)
    age = [at_least(n,[n.input_node['x',j,'age',bit] for j in range(-5,6)],6)
           for bit in range(p.m)]
    gate = w_in_range(n,age,p.age_code(p.T_wf),p.age_code(p.T_wf+4*p.Q-1)+1)
    if kind=='three_sources':
        expected = gate
    else:
        memory = at_least(n,[n.input_node['x',j,'wf2',0] for j in range(-5,6)],3)
        expected = n.AND(gate,memory)
    assert n.outputs['y','wf2',0] == expected
    return dict(all_raw_Address_flags_Ages_other_data_and_instructions_free=True,
                three_preset_WF2_offsets=[-2,0,4] if kind=='three_sources' else None,
                all_raw_Info_inputs_zero=kind=='zero_command',
                actual_WF2_equals_clock_gate=kind=='three_sources',
                actual_WF2_equals_clock_gate_AND_threshold3_memory=kind=='zero_command')


def primitive():
    n = Net()
    bits = [n.input(('bit',j)) for j in range(11)]
    n.set_output(('threshold',3),at_least(n,bits,3))
    n.set_output(('threshold',6),at_least(n,bits,6))
    comp = Compiled(n)
    words = np.arange(2048)
    inputs = {('bit',j):((words>>j)&1).astype(bool) for j in range(11)}
    y = comp.evaluate(inputs,bool)
    counts = sum(inputs.values())
    assert np.array_equal(y['threshold',3],counts>=3)
    assert np.array_equal(y['threshold',6],counts>=6)
    return dict(complete_Boolean_assignments=2048,
                threshold3_equals_popcount_at_least3=True,
                threshold6_equals_popcount_at_least6=True,
                any_three_ones_force_threshold3=True,
                at_most_two_ones_force_threshold3_zero=True,
                any_six_equal_bits_force_threshold6_to_that_bit=True)


def main():
    out = ROOT/'figs/robustness'
    candidate = proposed.load_artifact()
    p = candidate.p
    n = Net()
    age = [n.input(('age',bit)) for bit in range(p.m)]
    n.set_output(('gate',0),w_in_range(n,age,p.age_code(p.T_wf),p.age_code(p.T_wf+4*p.Q-1)+1))
    ticks = np.arange(p.U)
    encoded = np.array([p.age_code(int(t)) for t in ticks])
    y = Compiled(n).evaluate({('age',bit):((encoded>>bit)&1).astype(bool) for bit in range(p.m)},bool)
    assert np.array_equal(y['gate',0],(ticks>=p.T_wf)&(ticks<p.T_wf+4*p.Q))
    result = dict(proposal='SP9',proposed_rule_change=True,active_G17_modified=False,
                  proposed_candidate_sha256=candidate.digest(),proposed_netlist_sha256=candidate.comp.digest,
                  proposal_source_sha256=digest(Path(proposed.__file__)),checker_sha256=digest(Path(__file__)),
                  build_receipt_sha256=digest(out/'SP9_program_build.json'),
                  helpers_sha256=digest(ROOT/'gacsca/netlist.py'),
                  dominant_bit_helper_sha256=digest(ROOT/'Report/proofs/check_shifted_halfline.py'),
                  transport_checker_sha256=digest(Path(transport.__file__)),
                  full_rule_sha256=digest(ROOT/'gacsca/rule_g.py'),
                  full_generated_source_sha256=hashlib.sha256(proposed.actual_net(p)[1].encode()).hexdigest(),
                  identities={kind:bounded(kind) for kind in ('zero_command','three_sources')},
                  primitive_truth_table=primitive(),source_input_clock_interval=[p.T_wf,p.T_wf+4*p.Q-1],
                  legal_clock_gate_assignments=p.U,
                  source_active_legal_input_ticks=4*p.Q,
                  conditional_five_adjacent_holder_packet_tolerates_two_current_erasures=True,
                  packet_persistence_requires_six_agreeing_raw_Age_words_per_input_window=True,
                  initial_packet_bootstrap_and_damaged_clock_cohort_established=False,
                  global_packet_spread_envelope_established=False,
                  general_island_repair_established=False,global_reliability_established=False,
                  scope='exact actual full-rule source cofactors and complete Boolean threshold truth table; conditional packet induction in ROBUSTNESS J68')
    (out/'SP9_corrected_source_certificate.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(actual_source_cofactors=2,threshold_assignments=2048,active_clocks=4*p.Q)))


if __name__ == '__main__':
    main()
