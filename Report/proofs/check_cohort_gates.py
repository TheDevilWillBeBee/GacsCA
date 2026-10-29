#!/usr/bin/env python3
"""Exact SP12 packet-gate arithmetic and source-free full-rule cofactors."""
from itertools import combinations
import hashlib
import json
from pathlib import Path
import sys
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
import numpy as np
from gacsca import rule_g
from gacsca.netlist import Net,Compiled,w_in_range,w_eq_const
import check_fast_mail_proposal as transport
import proposed_sparse_cohort448 as proposed


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    candidate = proposed.load_artifact()
    p = candidate.p
    n = Net()
    age = [n.input(('age',b)) for b in range(p.m)]
    n.set_output(('gate',),w_in_range(n,age,p.age_code(p.T_wf),p.age_code(p.T_wf+4*p.Q-1)+1))
    n.set_output(('birth',),w_eq_const(n,age,p.age_code(p.T_wf)))
    words = np.arange(1<<p.m,dtype=np.uint32)
    actual = Compiled(n).evaluate({('age',b):((words>>b)&1).astype(bool) for b in range(p.m)},bool)
    assert not np.any(actual['birth',] & ~actual['gate',])
    clocks = np.arange(p.U)
    codes = np.asarray([p.age_code(int(t)) for t in clocks])
    assert np.array_equal(actual['gate',][codes],(clocks>=p.T_wf)&(clocks<p.T_wf+4*p.Q))
    assert np.array_equal(actual['birth',][codes],clocks==p.T_wf)
    _,source = proposed.actual_net(p)
    cases = 0
    for faults in combinations(range(-5,6),2):
        class BoundNet(Net):
            def input(self,key):
                if key[0]=='x' and key[2]=='age' and key[1] not in faults:
                    return (p.age_code(p.T_wf+4*p.Q)>>key[3])&1
                return super().input(key)
        namespace = dict(rule_g.__dict__,Net=BoundNet,
            maintenance=SimpleNamespace(build=proposed.proposed_build()[0]),schema=proposed.schema,
            packet_build=proposed.packet.build,OFFSETS=tuple(range(-12,13)),
            sparse_controls=transport.sparse_controls,sparse_table=proposed.dependency_table(p))
        exec(compile(source,'<SP12 source-free full-rule clock cofactor>','exec'),namespace)
        full = namespace['build'](p)
        assert full.outputs['y','wf2',0] == full.outputs['y','packet_valid',0] == 0
        assert all(full.outputs['y','packet_tag',b]==0 for b in range(4))
        cases += 1
    out = ROOT/'figs/robustness'
    receipt = dict(proposal='SP12',proposed_rule_change=True,active_G17_modified=False,
        proposed_candidate_sha256=candidate.digest(),proposed_netlist_sha256=candidate.comp.digest,
        proposal_source_sha256=digest(Path(proposed.__file__)),checker_sha256=digest(Path(__file__)),
        build_receipt_sha256=digest(out/'SP12_program_build.json'),
        packet_proposal_source_sha256=digest(ROOT/'Report/proofs/proposed_cohort_packet.py'),
        helpers_sha256=digest(ROOT/'gacsca/netlist.py'),
        full_generated_source_sha256=hashlib.sha256(source.encode()).hexdigest(),
        raw_clock_word_assignments=len(words),legal_clock_assignments=p.U,
        legal_birth_input_clock=p.T_wf,legal_retention_input_clocks=4*p.Q,
        birth_gate_implies_retention_gate_at_every_raw_clock_word=True,
        source_free_full_rule_two_Age_fault_cofactors=cases,
        source_free_cofactor_input_clock=p.T_wf+4*p.Q,
        all_six_packet_output_bits_zero=True,every_other_raw_bit_and_instruction_free=True,
        source_gate_off_on_arbitrary_higher_Age_islands_established=False,
        global_reliability_established=False,scope='universal clock-gate arithmetic and actual full-rule source-free cofactors; ROBUSTNESS J79/J80')
    (out/'SP12_packet_gate_certificate.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(dict(raw_clock_words=len(words),legal_clocks=p.U,source_free_cofactors=cases,all_passed=True)))


if __name__=='__main__':
    main()
