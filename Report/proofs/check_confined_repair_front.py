#!/usr/bin/env python3
"""Exact maintenance identities supporting SP10's conditional front proof.

The theorem assumes two-phase raw GF, common clocks, a bootstrapped packet
and WF2-only replacements with at most two per eleven sites. General whole-
cell mixed-noise islands and the upper capture map are not covered.
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
import proposed_sparse_confined_source448 as proposed


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def case(p,build,x,phase,kind,source=()):
    n = Net()
    age = [n.input(('common_age',bit)) for bit in range(p.m)]
    cells = {}
    for off in range(-5,9):
        # Three exact right words determine RF, regardless of the other
        # two right words or any left/central Address. Local F1 diagnostics
        # remain free but NF2's conclusion is independent of their value.
        addr = const_word((x+off+phase)%p.Q,p.k) if off in (1,2,3) else [n.input((off,'addr',b)) for b in range(p.k)]
        f2 = 1 if (kind=='keep' and off in (0,-1,-2)
                   or kind=='advance1' and off in (-1,-2,-3,-4)
                   or kind=='advance2' and off in (-2,-3,-4,-5)) else n.input((off,'f2'))
        wf2 = 1 if x+off in source else n.input((off,'wf2'))
        cells[off] = dict(addr=addr,age=age,f1=n.input((off,'f1')),f2=f2,
                          wf1=n.input((off,'wf1')),wf2=wf2)
    result = invoke(build,n,cells,p)
    assert result['f2'] == 1,(x,phase,kind,source)
    assert result['addr'] == const_word((x+phase)%p.Q,p.k)
    assert result['age_now'] == age
    assert result['age'] == mixed_age_increment(n,age,p.PB,p.R,p.nb)


def quiet(p,build,x,gap,field):
    n = Net()
    age = [n.input(('common_age',bit)) for bit in range(p.m)]
    cells = {}
    for off in range(-5,9):
        position = x+off
        inside = 0<=position<p.Q
        addr = const_word(position%p.Q,p.k) if position>=0 else [n.input((off,'addr',b)) for b in range(p.k)]
        f1_zero = inside and (field=='f2' or position>=x+gap)
        f2_zero = inside and field=='f2' and position<=x-gap
        cells[off] = dict(addr=addr,age=age,
            f1=0 if f1_zero else n.input((off,'f1')),
            f2=0 if f2_zero else n.input((off,'f2')),
            wf1=0 if inside else n.input((off,'wf1')),
            wf2=0 if field=='f2' else n.input((off,'wf2')))
    result = invoke(build,n,cells,p)
    assert result['f1'] == 0
    if field=='f2':
        assert result['f2'] == 0
    assert result['addr'] == const_word(x,p.k)
    assert result['age_now'] == age
    assert result['age'] == mixed_age_increment(n,age,p.PB,p.R,p.nb)


def main():
    candidate = proposed.load_artifact()
    p = candidate.p
    build,source = proposed.proposed_build(symbolic=True)
    counts = dict(packet=0,canonical_zero_holder=0,front=0,Flag1_suffix=0,Flag2_prefix=0)
    for x in range(1,7):
        for phase in (-1,0):
            for holders in combinations(range(1,6),3):
                case(p,build,x,phase,'packet',holders)
                counts['packet'] += 1
    for holders in combinations(range(1,6),3):
        case(p,build,0,0,'packet',holders)
        counts['canonical_zero_holder'] += 1
    for x in range(7,p.Q):
        for phase in (-1,0):
            for kind in ('keep','advance1','advance2'):
                case(p,build,x,phase,kind)
                counts['front'] += 1
        if x in (7,200,p.Q-1):
            print(json.dumps(dict(through_holder=x,identities=counts)),flush=True)
    for x in range(p.Q):
        for gap in (1,2):
            for field in ('f1','f2'):
                quiet(p,build,x,gap,field)
                counts['Flag1_suffix' if field=='f1' else 'Flag2_prefix'] += 1
    f2_front_updates = 1+(p.Q-1-6+1)//2
    gf_retreat_updates = (p.Q+2)//3
    gf_deadline = f2_front_updates+gf_retreat_updates
    assert (f2_front_updates,gf_retreat_updates,gf_deadline)==(222,150,372)
    out = ROOT/'figs/robustness'
    receipt = dict(proposal='SP10',proposed_rule_change=True,active_G17_modified=False,
                   proposed_candidate_sha256=candidate.digest(),proposed_netlist_sha256=candidate.comp.digest,
                   proposal_source_sha256=digest(Path(proposed.__file__)),checker_sha256=digest(Path(__file__)),
                   local_correction_helper_sha256=digest(ROOT/'Report/proofs/check_fast_flag_proposal.py'),
                   helpers_sha256=digest(ROOT/'gacsca/netlist.py'),
                   actual_maintenance_source_sha256=hashlib.sha256(source.encode()).hexdigest(),
                   source_certificate_sha256=digest(out/'SP10_confined_source_certificate.json'),
                   build_receipt_sha256=digest(out/'SP10_program_build.json'),
                   local_identities=counts,right_majority_fixed_by_three_matching_words=True,
                   all_remaining_raw_Address_and_flag_Workspace_bits_free=True,
                   common_raw_Age_bits_free=p.m,Q=p.Q,
                   NF2_positive_prefix_all_one_by_update=f2_front_updates,
                   canonical_GF_suffix_advances_three_per_update_after_NF2_prefix=True,
                   conditional_canonical_GF_by_update=gf_deadline,
                   Workspace1_source_free_relative_update=896,
                   conditional_GF_and_Flag1_quiet_by_update=1120,
                   Workspace2_source_free_relative_update=1792,
                   conditional_all_computed_flags_quiet_by_update=2016,
                   initial_GF_each_holder_independently_phase_minus_one_or_canonical=True,
                   right_exterior_GF_canonical_and_all_clocks_common_prescribed=True,
                   overwrites_preserve_every_field_except_WF2=True,
                   WF2_overwrite_density_at_most_two_per_eleven_site_row_required=True,
                   full_rule_bootstrap_and_exterior_provenance_established=False,
                   arbitrary_whole_cell_mixed_noise_repair_established=False,
                   global_reliability_established=False,
                   scope='universal local maintenance identities plus the monotone source/prefix/suffix induction ROBUSTNESS J73; limited to stated structural and WF2-only noise premises')
    (out/'SP10_repair_front_certificate.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(dict(counts=counts,GF_deadline=gf_deadline)))


if __name__ == '__main__':
    main()
