#!/usr/bin/env python3
"""Age-free NF2/GF front and noisy correct-clock RF suffix identities.

These pin the conditional maintenance theorem in ROBUSTNESS J82 for a
separately bootstrapped timed packet. No full timed own-ROM rule is built;
GF/Flag2 noise and general higher-island projection remain unproved.
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
import proposed_sparse_cohort448 as proposed
import proposed_timed_cohort_packet as timed


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def case(p,build,x,phase,kind,source=()):
    n = Net()
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
        cells[off] = dict(addr=addr,age=[n.input((off,'age',b)) for b in range(p.m)],f1=n.input((off,'f1')),f2=f2,
                          wf1=n.input((off,'wf1')),wf2=wf2)
    result = invoke(build,n,cells,p)
    assert result['f2'] == 1,(x,phase,kind,source)
    assert result['addr'] == const_word((x+phase)%p.Q,p.k)


def clock_suffix(p,build,x,age_cohort,source=()):
    n = Net()
    age = [n.input(('reference_age',b)) for b in range(p.m)]
    cells = {}
    for off in range(-5,9):
        cells[off] = dict(
            addr=const_word((x+off)%p.Q,p.k) if off in range(1,6) else [n.input((off,'addr',b)) for b in range(p.k)],
            age=age if off in age_cohort else [n.input((off,'age',b)) for b in range(p.m)],
            f1=n.input((off,'f1')),f2=1 if x>=7 and off in (0,-1,-2) else n.input((off,'f2')),
            wf1=n.input((off,'wf1')),wf2=1 if x+off in source else n.input((off,'wf2')))
    result = invoke(build,n,cells,p)
    assert result['f2']==1,(x,age_cohort,source)
    assert result['addr']==const_word(x,p.k),(x,'addr')
    assert result['age_now']==age,(x,'age_now')
    assert result['age']==mixed_age_increment(n,age,p.PB,p.R,p.nb),(x,'age')


def main():
    candidate = proposed.load_artifact()
    p = candidate.p
    build,source = proposed.proposed_build(symbolic=True)
    counts = dict(packet=0,canonical_zero_holder=0,front=0,clock_suffix=0)
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
    for x in range(p.Q):
        for cohort in combinations(range(1,6),3):
            sources = combinations(range(1,6),3) if x<7 else ((),)
            for holders in sources:
                clock_suffix(p,build,x,cohort,holders)
                counts['clock_suffix'] += 1
    prefix = 1+(p.Q-1-6+1)//2
    deadline = prefix+(p.Q-1)+2
    assert (prefix,deadline)==(222,671) and deadline<timed.LIFETIME
    out = ROOT/'figs/robustness'
    receipt = dict(proposed_rule_change=True,unincorporated_timed_composition=True,active_G17_modified=False,
        SP12_modified=False,checker_sha256=digest(Path(__file__)),
        proposal_source_sha256=digest(Path(proposed.__file__)),
        timed_packet_proposal_source_sha256=digest(Path(timed.__file__)),
        timed_packet_certificate_sha256=digest(out/'timed_cohort_packet_certificate.json'),
        local_correction_helper_sha256=digest(ROOT/'Report/proofs/check_fast_flag_proposal.py'),
        actual_maintenance_source_sha256=hashlib.sha256(source.encode()).hexdigest(),
        proposed_candidate_sha256=candidate.digest(),proposed_netlist_sha256=candidate.comp.digest,
        build_receipt_sha256=digest(out/'SP12_program_build.json'),
        local_identities=counts,Q=p.Q,NF2_positive_prefix_by_update=prefix,
        canonical_GF_and_correct_computed_Age_by_update=deadline,
        initial_binary_phase_GF_and_bootstrapped_timed_packet_required=True,
        initial_Age_on_colony_arbitrary=True,every_other_Age_word_free_in_front_identities=True,
        right_canonical_GF_and_reference_clock_prescribed=True,
        continuing_faults_preserve_GF_Flag1_Flag2_and_other_data=True,
        at_most_two_Age_faults_per_five_site_row_and_packet_faults_per_eleven_required=True,
        packet_lifetime=timed.LIFETIME,actual_timed_own_ROM_incorporation_established=False,
        general_GF_or_Flag2_faults_covered=False,command_birth_or_upper_map_established=False,
        global_reliability_established=False,
        scope='exact local maintenance identities and conditional binary-GF/arbitrary-Age eroder with a bootstrapped timed source; ROBUSTNESS J82')
    (out/'timed_packet_age_eroder_certificate.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(dict(local_identities=counts,GF_Age_deadline=deadline)))


if __name__=='__main__':
    main()
