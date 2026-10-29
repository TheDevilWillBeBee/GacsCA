#!/usr/bin/env python3
"""Exact SF5/SP11 maintenance equality when three left GF words align.

All other fields and neighboring Address words are free. This proves the
modal fallback is inactive on the aligned geometry used by the complete
encoding/E0 induction, not repair from arbitrary damaged geometry.
"""
from itertools import combinations
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from gacsca.netlist import Net,const_word
from check_fast_flag_proposal import invoke
import proposed_sparse_liveness448 as original
import proposed_sparse_modal_clock448 as proposed


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    candidate = proposed.load_artifact()
    p = candidate.p
    old,old_source = original.proposed_build(symbolic=True)
    new,new_source = proposed.proposed_build(symbolic=True)
    count = 0
    for address in range(p.Q):
        for cohort in combinations(range(-5,0),3):
            n = Net()
            cells = {}
            for off in range(-5,9):
                cells[off] = dict(
                    addr=const_word((address+off)%p.Q,p.k) if off in cohort
                         else [n.input((off,'addr',b)) for b in range(p.k)],
                    age=[n.input((off,'age',b)) for b in range(p.m)],
                    **{field:n.input((off,field)) for field in ('f1','f2','wf1','wf2')})
            before = invoke(old,n,cells,p)
            after = invoke(new,n,cells,p)
            assert before == after,(address,cohort)
            count += 1
    out = ROOT/'figs/robustness'
    result = dict(proposal='SP11',proposed_rule_change=True,active_G17_modified=False,
        proposed_candidate_sha256=candidate.digest(),proposed_netlist_sha256=candidate.comp.digest,
        proposal_source_sha256=digest(Path(proposed.__file__)),checker_sha256=digest(Path(__file__)),
        local_correction_helper_sha256=digest(ROOT/'Report/proofs/check_fast_flag_proposal.py'),
        majority_shortcut_sha256=digest(ROOT/'Report/proofs/check_right_barrier.py'),
        SP5_proposal_source_sha256=digest(Path(original.__file__)),
        modal_clock_proposal_source_sha256=digest(ROOT/'Report/proofs/proposed_modal_clock.py'),
        old_maintenance_source_sha256=hashlib.sha256(old_source.encode()).hexdigest(),
        actual_maintenance_source_sha256=hashlib.sha256(new_source.encode()).hexdigest(),
        build_receipt_sha256=digest(out/'SP11_program_build.json'),
        modal_clock_receipt_sha256=digest(out/'modal_clock_certificate.json'),
        aligned_left_three_cohort_cases=count,
        every_maintenance_output_identical=True,
        every_Age_flag_Workspace_and_unconstrained_Address_input_free=True,
        condition='three left adjusted Address words equal a valid Address',
        general_damaged_GF_transfer_established=False,global_reliability_established=False,
        scope='universal local equality under the stated aligned-left-GF premise; ROBUSTNESS J76')
    (out/'SP11_maintenance_transfer_certificate.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(local_equality_cases=count,all_outputs_equal=True)))


if __name__=='__main__':
    main()
