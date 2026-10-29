#!/usr/bin/env python3
"""Finite premises for the cohort module's arbitrary-seed support bound.

The universal induction is in ROBUSTNESS J77b. No source birth, full-rule
island map or iid conclusion is claimed.
"""
from itertools import combinations
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
import numpy as np
from gacsca.netlist import Net,Compiled,const_word,w_add_const
import proposed_cohort_packet as proposed


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    n = Net()
    for tag in range(5):
        for offset in range(-5,6):
            word = w_add_const(n,const_word(tag,4),(-offset)%16)
            actual = sum(bit<<b for b,bit in enumerate(word))
            assert actual == (tag-offset)%16
            for selected in range(5):
                if actual == selected:
                    assert selected == tag-offset
    masks = np.arange(1<<11,dtype=np.uint16)
    alive = ((masks[:,None]>>np.arange(11))&1).astype(bool)
    certificate_cases = 0
    for faults in combinations(range(11),2):
        good = [j for j in range(11) if j not in faults]
        assert not np.any((alive.sum(axis=1)>=3) & ~alive[:,good].any(axis=1))
        certificate_cases += len(masks)
    out = ROOT/'figs/robustness'
    receipt = dict(proposed_rule_change=True,unincorporated_module=True,active_G17_modified=False,
        SP11_modified=False,checker_sha256=digest(Path(__file__)),
        proposal_source_sha256=digest(Path(proposed.__file__)),helpers_sha256=digest(ROOT/'gacsca/netlist.py'),
        packet_module_certificate_sha256=digest(out/'cohort_packet_certificate.json'),
        modulo_tag_offset_selected_tag_cases=5*11*5,
        three_vote_nonfault_witness_assignments=certificate_cases,
        raw_initial_packet_components_arbitrary_on_finite_K=True,
        every_clock_gate_can_be_arbitrary_per_site_and_tick=True,
        at_most_two_raw_packet_faults_per_eleven_site_window_required=True,
        computed_nonzero_support_within_initial_K_plus_minus_nine=True,
        future_computed_origins_subset_first_computed_origin_set=True,
        closed_gate_everywhere_clears_all_computed_components=True,
        packet_birth_or_full_CA_incorporation_established=False,
        full_GF_or_simulation_field_support_bound_established=False,
        global_reliability_established=False,
        scope='exact local arithmetic/counting premises and arbitrary-seed packet-component induction ROBUSTNESS J77b')
    (out/'cohort_packet_ancestry_certificate.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(dict(integer_origin_cases=275,nonfault_witness_assignments=certificate_cases,all_passed=True)))


if __name__=='__main__':
    main()
