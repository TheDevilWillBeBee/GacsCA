#!/usr/bin/env python3
"""Exhaust every local fault word for the isolated five-holder packet.

This is finite exhaustive verification of a fully specified local module,
not a stochastic simulation. Its all-time induction and birth/clock
premises are stated in ROBUSTNESS J77. No complete CA is constructed.
"""
from itertools import combinations
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
import numpy as np
from gacsca.netlist import Net,Compiled,const_word
import proposed_cohort_packet as proposed


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    assignments = np.arange(1<<13,dtype=np.uint16)
    total = cases = 0
    for x in range(-5,11):
        for faults in combinations(range(-5,6),2):
            n = Net()
            cells = {}
            values = {}
            for j in range(-5,6):
                if j in faults:
                    index = faults.index(j)*6
                    cells[j] = dict(tag=[n.input((j,'tag',b)) for b in range(4)],
                                    valid=n.input((j,'valid')),wf2=n.input((j,'wf2')))
                    for b in range(4):
                        values[j,'tag',b] = ((assignments>>(index+b))&1).astype(bool)
                    values[j,'valid'] = ((assignments>>(index+4))&1).astype(bool)
                    values[j,'wf2'] = ((assignments>>(index+5))&1).astype(bool)
                else:
                    holder = 0<=x+j<5
                    cells[j] = dict(tag=const_word(x+j if holder else 0,4),
                                    valid=int(holder),wf2=int(holder))
            gate = n.input(('gate',))
            values['gate',] = ((assignments>>12)&1).astype(bool)
            result = proposed.build(n,cells,gate)
            for field,word in result.items():
                if field=='tag':
                    for b,node in enumerate(word):n.set_output((field,b),node)
                else:n.set_output((field,),word)
            actual = Compiled(n).evaluate(values,bool)
            expected = values['gate',] & (0<=x<5)
            assert np.array_equal(actual['valid',],expected),(x,faults,'valid')
            assert np.array_equal(actual['wf2',],expected),(x,faults,'wf2')
            for b in range(4):
                assert np.array_equal(actual['tag',b],expected & bool((x>>b)&1)),(x,faults,b)
            total += len(assignments)
            cases += 1
        print(json.dumps(dict(through_center=x,local_windows=cases,complete_assignments=total)),flush=True)
    out = ROOT/'figs/robustness'
    receipt = dict(proposed_rule_change=True,unincorporated_module=True,active_G17_modified=False,
        SP11_modified=False,checker_sha256=digest(Path(__file__)),
        proposal_source_sha256=digest(Path(proposed.__file__)),helpers_sha256=digest(ROOT/'gacsca/netlist.py'),
        added_state_bits=5,existing_WF2_bit_reused=True,tag_modulus=16,packet_holders=list(range(5)),
        radius=5,local_window_cases=cases,complete_Boolean_assignments=total,
        arbitrary_fault_words_per_eleven_site_window=2,
        local_outputs_restore_exact_packet_or_clear_under_gate=True,
        every_unmentioned_GF_Age_flag_and_data_field_ignored=True,
        common_correct_clock_gate_is_external_premise=True,
        packet_birth_established=False,own_program_rebuilt_or_certified=False,
        arbitrary_other_cohort_initialization_covered=False,
        higher_error_island_repair_established=False,global_reliability_established=False,
        scope='exhaustive local module certificate and conditional packet persistence/confinement induction ROBUSTNESS J77')
    (out/'cohort_packet_certificate.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(dict(local_windows=cases,complete_assignments=total,all_equal=True)))


if __name__=='__main__':
    main()
