#!/usr/bin/env python3
"""Exact source-free flag clearing on canonical SP11 geometry.

The universal full encoded self-simulation proof is in ROBUSTNESS J76.
This checks its new local flag-clearing premises; it is not a noisy repair
certificate or a simulation relation through partial damaged encodings.
"""
import hashlib
import json
from pathlib import Path
import sys
import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from gacsca.netlist import Net,const_word,mixed_age_increment
from check_fast_flag_proposal import invoke
import proposed_sparse_liveness448 as sp5
import proposed_sparse_modal_clock448 as sp8


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def flag_case(p,build,address,gap,field):
    n = Net()
    age = [n.input(('common_age',bit)) for bit in range(p.m)]
    cells = {}
    for offset in range(-5,9):
        position = address+offset
        flags = {}
        for flag in ('f1','f2'):
            zero = (field == 'f1' and flag == 'f1' and position >= address+gap
                    or field == 'f2' and flag == 'f1'
                    or field == 'f2' and flag == 'f2' and position <= address-gap)
            flags[flag] = 0 if zero else n.input((offset,flag))
        cells[offset] = dict(addr=const_word(position%p.Q,p.k),age=age,
                             **flags,wf1=0,wf2=n.input((offset,'wf2')) if field=='f1' else 0)
    result = invoke(build,n,cells,p)
    assert result['addr'] == const_word(address,p.k)
    assert result['age_now'] == age
    assert result['age'] == mixed_age_increment(n,age,p.PB,p.R,p.nb)
    assert result[field] == 0,(field,address,gap)


def main():
    out = ROOT/'figs/robustness'
    result = dict(checker_sha256=digest(Path(__file__)),
                  liveness_maintenance_checker_sha256=digest(ROOT/'Report/proofs/check_sparse_liveness448_maintenance.py'),
                  local_correction_helper_sha256=digest(ROOT/'Report/proofs/check_fast_flag_proposal.py'),
                  rules={},global_reliability_established=False,
                  scope='canonical-GF source-free flag clearing; complete-encoding theorem proved separately in ROBUSTNESS J76')
    for proposed in (sp8,):
        candidate = proposed.load_artifact()
        p = candidate.p
        build,maintenance_source = proposed.proposed_build(symbolic=True)
        assert all(x not in set(candidate.layout) for x in (3,p.lo,p.hi-1,p.Q-3))
        assert np.array_equal(candidate.layout,sp5.layout(p))
        counts = {}
        for field in ('f1','f2'):
            count = 0
            for address in range(p.Q):
                for gap in (1,2):
                    flag_case(p,build,address,gap,field)
                    count += 1
            counts[field] = count
        source1_free = p.T_wf+2*p.Q+1
        source2_free = p.T_wf+4*p.Q+1
        flag1_quiet = source1_free+(p.Q+1)//2
        flags_quiet = max(flag1_quiet,source2_free)+(p.Q+1)//2
        assert source1_free == 26242 and flag1_quiet == 26466 and source2_free == 27138
        assert flags_quiet == 27362 < p.U-1
        proposal = proposed.identity(p)['proposal']
        result['rules'][proposal] = dict(
            proposed_rule_change=True,active_G17_modified=False,
            proposed_candidate_sha256=candidate.digest(),proposed_netlist_sha256=candidate.comp.digest,
            proposal_source_sha256=digest(Path(proposed.__file__)),
            full_generated_source_sha256=hashlib.sha256(proposed.actual_net(p)[1].encode()).hexdigest(),
            actual_maintenance_source_sha256=hashlib.sha256(maintenance_source.encode()).hexdigest(),
            build_receipt_sha256=digest(out/(proposal+'_program_build.json')),
            schedule_receipt_sha256=digest(out/(proposal+'_symbolic_schedule.json')),
            front_receipt_sha256=digest(out/(proposal+'_front_certificate.json')),
            common_raw_clock_bits_free=p.m,Flag1_suffix_local_identities=counts['f1'],
            Flag2_prefix_local_identities=counts['f2'],
            virtual_right_Flag1_and_left_Flag2_boundaries_clipped=True,
            Workspace1_source_free_clock=source1_free,Workspace2_source_free_clock=source2_free,Flag1_quiet_by_clock=flag1_quiet,all_four_flags_quiet_by_clock=flags_quiet,
            arbitrary_Flag2_and_Workspace2_during_Flag1_erasure=True,arbitrary_stored_Flag2_during_Flag2_erasure=True,
            complete_encoded_noiseless_simulation_proof='ROBUSTNESS J76',
            noisy_partial_encoding_simulation_established=False,global_reliability_established=False)
    (out/'SP11_encoded_closure_certificate.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({key:{f:row[f] for f in ('Flag1_suffix_local_identities','Flag2_prefix_local_identities','all_four_flags_quiet_by_clock')}
                      for key,row in result['rules'].items()}))


if __name__ == '__main__':
    main()
