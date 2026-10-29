#!/usr/bin/env python3
"""Check local arithmetic/counting premises of the timed packet theorem.

This does not exhaust all full-width neighborhoods. The word-cohort
selection, restoration and all-time erasure proof is ROBUSTNESS J81.
"""
from itertools import combinations
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
import numpy as np
from gacsca.netlist import Net,Compiled,w_add_const,w_ult_const
import proposed_timed_cohort_packet as proposed


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    n = Net()
    count = [n.input(('count',b)) for b in range(proposed.COUNTER_BITS)]
    n.set_output(('retain',),w_ult_const(n,count,proposed.LIFETIME-1))
    for b,node in enumerate(w_add_const(n,count,1)):n.set_output(('increment',b),node)
    words = np.arange(1<<proposed.COUNTER_BITS,dtype=np.uint32)
    actual = Compiled(n).evaluate({('count',b):((words>>b)&1).astype(bool)
                                  for b in range(proposed.COUNTER_BITS)},bool)
    increment = sum(actual['increment',b].astype(np.uint32)<<b for b in range(proposed.COUNTER_BITS))
    assert np.array_equal(actual['retain',],words<proposed.LIFETIME-1)
    assert np.array_equal(increment,(words+1)%(1<<proposed.COUNTER_BITS))
    assert np.array_equal(increment[actual['retain',]],words[actual['retain',]]+1)
    masks = np.arange(1<<11,dtype=np.uint16)
    matching = ((masks[:,None]>>np.arange(11))&1).astype(bool)
    witness_cases = 0
    for faults in combinations(range(11),2):
        good = [j for j in range(11) if j not in faults]
        assert not np.any((matching.sum(axis=1)>=3)&~matching[:,good].any(axis=1))
        witness_cases += len(masks)
    # Every retained integer increases without overflow and is <=T-1.
    for old in range(proposed.LIFETIME-1):
        new = old+1
        assert 1<=new<=proposed.LIFETIME-1 and new>old
    out = ROOT/'figs/robustness'
    receipt = dict(proposed_rule_change=True,unincorporated_module=True,active_G17_modified=False,
        SP12_modified=False,checker_sha256=digest(Path(__file__)),
        proposal_source_sha256=digest(Path(proposed.__file__)),helpers_sha256=digest(ROOT/'gacsca/netlist.py'),
        tag_ancestry_receipt_sha256=digest(out/'cohort_packet_ancestry_certificate.json'),
        counter_bits=proposed.COUNTER_BITS,lifetime=proposed.LIFETIME,
        added_state_bits=4+1+proposed.COUNTER_BITS,WF2_reused=True,
        all_counter_word_assignments=len(words),nonfault_witness_assignments=witness_cases,
        retained_integer_counter_assignments=proposed.LIFETIME-1,
        full_width_neighborhoods_exhausted=False,
        proof='ROBUSTNESS J81; word matching/counting and counter lower-bound induction',
        correct_initialized_packet_restored_with_counter_increment_under_two_fault_bound=True,
        arbitrary_initial_packet_component_erased_by_lifetime_updates=True,
        every_GF_Age_flag_data_input_ignored=True,
        at_most_two_packet_faults_per_eleven_site_input_window_required=True,
        no_external_births_required_for_erasure_theorem=True,
        birth_or_own_program_incorporation_established=False,
        full_GF_or_simulation_repair_established=False,global_reliability_established=False,
        scope='exact finite arithmetic/counting premises for the universal timed-packet module proof; not full-neighborhood enumeration or a CA reliability theorem')
    (out/'timed_cohort_packet_certificate.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(dict(counter_words=len(words),witness_assignments=witness_cases,lifetime=proposed.LIFETIME,all_passed=True)))


if __name__=='__main__':
    main()
