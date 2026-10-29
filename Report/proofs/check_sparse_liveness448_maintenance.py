#!/usr/bin/env python3
"""SP5 local GF preservation, quiet correction and blank-clock liveness.

These are conditional Boolean identities, not a damaged-island eroder.
The all-raw-clock test concerns externally blank neighbor inputs only.
"""
import hashlib
from itertools import combinations
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
import numpy as np
from gacsca.netlist import Net,Compiled,const_word,mixed_age_increment
import proposed_sparse_liveness448 as proposed
from check_fast_flag_proposal import invoke,pristine_symbolic
from check_sparse_prefix448_localization import closed_colony_case


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_arbitrary_flags(p,build,address,faults=()):
    n = Net()
    age = [n.input(('common_age',bit)) for bit in range(p.m)]
    cells = {}
    for offset in range(-5,9):
        if offset >= 6:
            cells[offset] = dict(f1=n.input((offset,'f1')))
            continue
        faulty = offset in faults
        cells[offset] = dict(addr=[n.input((offset,'addr',bit)) for bit in range(p.k)] if faulty
                             else const_word((address+offset)%p.Q,p.k),
                             age=[n.input((offset,'age',bit)) for bit in range(p.m)] if faulty else age,
                             **{field:n.input((offset,field)) for field in ('f1','f2','wf1','wf2')})
    result = invoke(build,n,cells,p)
    assert result['addr'] == const_word(address,p.k)
    assert result['age_now'] == age
    assert result['age'] == mixed_age_increment(n,age,p.PB,p.R,p.nb)


def blank_clock(p,build):
    n = Net()
    own = dict(addr=[n.input(('own_addr',bit)) for bit in range(p.k)],
               age=[n.input(('own_age',bit)) for bit in range(p.m)],
               **{field:n.input(('own',field)) for field in ('f1','f2','wf1','wf2')})
    cells = {offset:(own if offset == 0 else dict(addr=const_word(0,p.k),age=const_word(0,p.m),
                                                f1=0,f2=0,wf1=0,wf2=0)) for offset in range(-5,9)}
    result = invoke(build,n,cells,p)
    assert result['addr'] == own['addr'] and result['age_now'] == own['age']
    assert result['age'] == mixed_age_increment(n,own['age'],p.PB,p.R,p.nb)
    assert result['f1'] == 1
    for bit,node in enumerate(result['age']):
        n.set_output(('age',bit),node)
    n.set_output(('f2',),result['f2'])
    compiled = Compiled(n)
    words = np.arange(1 << p.m,dtype=np.int64)
    pos_mask = (1 << p.PB)-1
    block_mask = (1 << (p.m-p.PB))-1
    pos,block = words & pos_mask,words >> p.PB
    newpos = np.where(pos == p.R-1,0,(pos+1) & pos_mask)
    newblock = np.where(pos == p.R-1,np.where(block == p.nb-1,0,(block+1) & block_mask),block)
    expected = (newblock << p.PB) | newpos
    for flag in (0,1):
        values = {key:((words >> key[1]) & 1).astype(bool) if key[0] == 'own_age'
                  else np.full(len(words),bool(flag if key == ('own','f2') else 0)) for key in compiled.inputs}
        got = compiled.evaluate(values,bool)
        age = sum(got['age',bit].astype(np.int64) << bit for bit in range(p.m))
        assert np.array_equal(age,expected)
        assert np.array_equal(age & 15,(words+1) & 15)
        assert np.array_equal(got['f2',],(words & 15) == 15)
    return dict(raw_Age_words=len(words),old_Flag2_assignments=2,
                checked_cases=2*len(words),low_four_bits_advance_modulo16=True,
                computed_Flag2_iff_old_low_bits15=True,
                all_neighbors_externally_clamped_to_blank=True)


def main():
    candidate = proposed.load_artifact()
    p = candidate.p
    build,source = proposed.proposed_build(symbolic=True)
    masks = list(combinations(range(-5,9),2))
    extra = [faults for count in (3,4) for faults in combinations(range(-5,9),count)
             if all(sum(start <= x < start+11 for x in faults) <= 2 for start in range(-5,-1))]
    assert len(masks) == 91 and len(extra) == 70
    gf_cases = quiet_cases = 0
    for address in range(p.Q):
        canonical_arbitrary_flags(p,build,address)
        gf_cases += 1
        for faults in masks:
            canonical_arbitrary_flags(p,build,address,faults)
            gf_cases += 1
            pristine_symbolic(p,build,address,faults)
            quiet_cases += 1
        if address % 112 == 111:
            print(json.dumps(dict(through_Address=address,GF_cases=gf_cases,quiet_cases=quiet_cases)),flush=True)
    edge_cases = 0
    for address in (*range(5),*range(p.Q-8,p.Q)):
        for faults in masks+extra:
            closed_colony_case(p,build,address,faults)
            edge_cases += 1
    raw_clock = blank_clock(p,proposed.proposed_build()[0])
    out = ROOT/'figs/robustness'
    result = dict(proposal='SP5',proposed_rule_change=True,active_G17_modified=False,SP4_modified=False,
                  proposed_candidate_sha256=candidate.digest(),proposed_netlist_sha256=candidate.comp.digest,
                  checker_sha256=digest(Path(__file__)),proposal_source_sha256=digest(Path(proposed.__file__)),
                  majority_shortcut_sha256=digest(ROOT/'Report/proofs/check_right_barrier.py'),
                  helpers_sha256=digest(ROOT/'gacsca/netlist.py'),
                  local_correction_helper_sha256=digest(ROOT/'Report/proofs/check_fast_flag_proposal.py'),
                  boundary_correction_helper_sha256=digest(ROOT/'Report/proofs/check_sparse_prefix448_localization.py'),
                  liveness_helper_sha256=digest(ROOT/'Report/proofs/check_blank_neighbor_clock.py'),
                  actual_maintenance_source_sha256=hashlib.sha256(source.encode()).hexdigest(),
                  build_receipt_sha256=digest(out/'SP5_program_build.json'),
                  GF_preservation_cases_arbitrary_flags=gf_cases,quiet_two_fault_cases=quiet_cases,
                  quiet_boundary_density_cases=edge_cases,common_raw_Age_bits_free=p.m,
                  canonical_GF_ignores_arbitrary_flags_with_two_GF_faults=True,
                  blank_clock=raw_clock,actual_Flag2_geometry_override=True,
                  arbitrary_island_repair_established=False,
                  higher_island_eroder_established=False,global_reliability_established=False,
                  scope='exact local canonical-GF/quiet correction and blank-input liveness; no general damaged-region trajectory claim')
    (out/'SP5_maintenance_certificate.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(GF_cases=gf_cases,quiet_cases=quiet_cases,boundary_cases=edge_cases,
                          blank_clock_cases=raw_clock['checked_cases'])),flush=True)


if __name__ == '__main__':
    main()
