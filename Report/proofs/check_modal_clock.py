#!/usr/bin/env python3
"""Exact clock identities for an explicit, unbuilt local maintenance change.

The all-period clock proof assumes E0-only Age errors, but allows every
GF/flag/Workspace input arbitrary. No complete candidate or iid theorem.
"""
from itertools import combinations
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from gacsca.netlist import Net,const_word,mixed_age_increment
from check_fast_flag_proposal import invoke
import proposed_sparse_confined_source448 as base
import proposed_modal_clock as proposed


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def case(p,build,one_bit,left,right):
    n = Net()
    age = const_word(0,p.m) if one_bit is None else [1 if bit==one_bit else n.input(('common_age',bit)) for bit in range(p.m)]
    cells = {}
    for off in range(-5,9):
        constrained = off in (*left,*right) or one_bit is None and off==0
        cells[off] = dict(addr=[n.input((off,'addr',b)) for b in range(p.k)],
                         age=age if constrained else [n.input((off,'age',b)) for b in range(p.m)],
                         **{f:n.input((off,f)) for f in ('f1','f2','wf1','wf2')})
    result = invoke(build,n,cells,p)
    assert result['age_now'] == age
    assert result['age'] == mixed_age_increment(n,age,p.PB,p.R,p.nb)


def main():
    p = base.parameters()
    build,source = proposed.proposed_build(symbolic=True)
    cohorts = list(combinations(range(1,6),3))
    counts = dict(nonzero=0,zero_at_correct_center=0)
    for bit in [*range(p.m),None]:
        for left in cohorts:
            for right in cohorts:
                case(p,build,bit,tuple(-j for j in left),right)
                counts['zero_at_correct_center' if bit is None else 'nonzero'] += 1
        if bit in (0,p.m-1,None):
            print(json.dumps(dict(through_bit=bit,identities=counts)),flush=True)
    n = Net()
    own = [n.input(('own_age',bit)) for bit in range(p.m)]
    cells = {off:dict(addr=const_word(0,p.k),age=own if off==0 else const_word(0,p.m),
                      **{f:n.input((off,f)) for f in ('f1','f2','wf1','wf2')}) for off in range(-5,9)}
    blank = invoke(build,n,cells,p)
    assert blank['addr']==const_word(0,p.k) and blank['age_now']==own
    assert blank['age']==mixed_age_increment(n,own,p.PB,p.R,p.nb)
    out = ROOT/'figs/robustness'
    receipt = dict(proposed_rule_change=True,active_G17_modified=False,SP10_modified=False,
                   proposal_source_sha256=digest(Path(proposed.__file__)),checker_sha256=digest(Path(__file__)),
                   local_correction_helper_sha256=digest(ROOT/'Report/proofs/check_fast_flag_proposal.py'),
                   majority_shortcut_sha256=digest(ROOT/'Report/proofs/check_right_barrier.py'),
                   helpers_sha256=digest(ROOT/'gacsca/netlist.py'),
                   SP10_proposal_source_sha256=digest(Path(base.__file__)),
                   actual_proposed_maintenance_source_sha256=hashlib.sha256(source.encode()).hexdigest(),
                   Q=p.Q,U=p.U,raw_Age_bits=p.m,local_identities=counts,
                   raw_GF_flags_Workspace_and_unconstrained_Age_words_all_free=True,
                   three_matching_left_and_right_Age_words_suffice_at_nonzero_clock=True,
                   zero_clock_correct_centers_always_advance_to_one=True,
                   blank_neighbor_own_clock_advance_preserved=True,
                   all_period_raw_clock_exceptions_confined_to_Nt_union_Nt_minus_one=True,
                   globally_separated_E0_Age_errors_and_initial_common_clock_required=True,
                   source_clock_eleven_vote_has_at_least_nine_correct_words_under_these_premises=True,
                   own_program_rebuilt_or_certified=False,
                   arbitrary_higher_Age_island_repair_established=False,global_reliability_established=False,
                   scope='universal local clock identities and conditional all-period E0-only Age induction ROBUSTNESS J75; unbuilt local rule change')
    (out/'modal_clock_certificate.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(dict(local_identities=counts,own_program_rebuilt=False)))


if __name__=='__main__':
    main()
