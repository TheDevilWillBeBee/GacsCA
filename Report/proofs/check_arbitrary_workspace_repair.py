#!/usr/bin/env python3
"""Universal-WF1 conditional GF repair for one shifted448-cell colony.

WF2's five physical sources and the exterior GF/flag inputs are prescribed.
This proves a conditional maintenance induction, not its full-rule capture
premises, general islands, continuing-noise recovery or an iid theorem.
"""
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
import numpy as np
from gacsca.netlist import Net,const_word,mixed_age_increment
from check_fast_flag_proposal import invoke
import proposed_sparse_latched448 as proposed


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def core(p,build,address,raw_address,F2,F1mask,WF2,inside,expected_address,expected_F2,require_F1):
    n = Net()
    common = [n.input(('common_age',bit)) for bit in range(p.m)]
    cells = {}
    for index,offset in enumerate(range(-5,9)):
        f1 = n.input((offset,'f1')) if F1mask[index]<0 else int(F1mask[index])
        wf1 = n.input((offset,'wf1')) if inside[index] else 0
        cells[offset] = dict(addr=const_word(int(raw_address[index]),p.k),age=common,
                             f1=f1,f2=int(F2[index]),wf1=wf1,wf2=int(WF2[index]))
    result = invoke(build,n,cells,p)
    assert result['age_now'] == common
    assert result['age'] == mixed_age_increment(n,common,p.PB,p.R,p.nb)
    assert result['addr'] == const_word(int(expected_address),p.k),(address,'Address',raw_address,F2,F1mask)
    assert result['f2'] == int(expected_F2),(address,'Flag2',F2,F1mask)
    if require_F1:
        assert result['f1'] == 1,(address,'bad-site Flag1',raw_address,F1mask)


def quiet_suffix(p,build,address,gap):
    n = Net()
    common = [n.input(('common_age',bit)) for bit in range(p.m)]
    cells = {}
    for offset in range(-5,9):
        position = address+offset
        A = (position-1)%p.Q if position<0 else position%p.Q
        inside = 0<=position<p.Q
        f1 = n.input((offset,'f1')) if inside and position<address+gap else 0
        cells[offset] = dict(addr=const_word(A,p.k),age=common,
                             f1=f1,f2=int(inside),wf1=0,wf2=int(1<=position<=5))
    result = invoke(build,n,cells,p)
    assert result['addr'] == const_word(address,p.k)
    assert result['age_now'] == common
    assert result['f2'] == 1 and result['f1'] == 0


def main():
    out = ROOT/'figs/robustness'
    candidate = proposed.load_artifact()
    p = candidate.p
    build,source = proposed.proposed_build(symbolic=True)
    reference_path = out/'SP7_latched_phase_trace.npz'
    with np.load(reference_path,allow_pickle=False) as saved:
        reference = saved['states'][:370].copy()
    assert np.array_equal(reference[369,0],np.arange(p.Q)) and reference[369,2].all()
    cache = set()
    rows = []
    checked = 0
    for step in range(369):
        A,F2 = reference[step,0],reference[step,2]
        next_A,next_F2 = reference[step+1,0],reference[step+1,2]
        for address in range(p.Q):
            coordinates = address+np.arange(-5,9)
            inside = (coordinates>=0)&(coordinates<p.Q)
            clamped = np.clip(coordinates,0,p.Q-1)
            raw_A = np.where(inside,A[clamped],np.where(coordinates<0,(coordinates-1)%p.Q,coordinates%p.Q))
            F2values = inside*F2[clamped]
            # All still-bad positive sites are flagged; every canonical
            # site's Flag1, and the leading site's Flag1, is free.
            mask = np.where(inside,np.where((A[clamped]!=clamped)&(coordinates>0),1,-1),0)
            WF2 = (coordinates>=1)&(coordinates<=5)
            require_F1 = address>0 and next_A[address]!=address
            key = tuple([address,*raw_A,*F2values,*mask,*WF2,*inside,int(next_A[address]),int(next_F2[address]),int(require_F1)])
            if key not in cache:
                core(p,build,address,raw_A,F2values,mask,WF2,inside,next_A[address],next_F2[address],require_F1)
                cache.add(key)
                rows.append(key)
            checked += 1
        if step in (0,100,200,300,368):
            print(json.dumps(dict(through_step=step,holder_transitions=checked,distinct_symbolic_cases=len(cache))),flush=True)
    invariant = 0
    for address in range(p.Q):
        coordinates = address+np.arange(-5,9)
        inside = (coordinates>=0)&(coordinates<p.Q)
        A = np.where(coordinates<0,(coordinates-1)%p.Q,coordinates%p.Q)
        core(p,build,address,A,inside.astype(np.int64),np.where(inside,-1,0),
             (coordinates>=1)&(coordinates<=5),inside,address,1,False)
        invariant += 1
    erasure = 0
    for address in range(p.Q):
        for gap in (1,2):
            quiet_suffix(p,build,address,gap)
            erasure += 1
    asset = out/'SP8_arbitrary_Workspace1_symbolic_cases.npz'
    np.savez_compressed(asset,cases=np.asarray(rows,dtype=np.int64))
    receipt = dict(checker_sha256=digest(Path(__file__)),active_G17_modified=False,
                   proposed_rule_change=False,maintenance_proposal='SP7/SP8 common maintenance',
                   SP7_proposal_source_sha256=digest(Path(proposed.__file__)),
                   proposed_SP7_candidate_sha256=candidate.digest(),proposed_SP7_netlist_sha256=candidate.comp.digest,
                   actual_maintenance_source_sha256=hashlib.sha256(source.encode()).hexdigest(),
                   local_correction_helper_sha256=digest(ROOT/'Report/proofs/check_fast_flag_proposal.py'),
                   helpers_sha256=digest(ROOT/'gacsca/netlist.py'),
                   reference_receipt_sha256=digest(out/'SP7_latched_phase_certificate.json'),
                   reference_trace_sha256=digest(reference_path),symbolic_cases_asset_sha256=digest(asset),
                   Q=p.Q,GF_repair_updates=369,holder_transitions=checked,
                   distinct_symbolic_local_cases=len(cache),
                   canonical_GF_Flag2_invariant_local_cases=invariant,
                   Flag1_suffix_erasure_local_cases=erasure,common_raw_Age_bits_free=p.m,
                   all_Workspace1_inputs_free_at_each_holder_transition=True,
                   canonical_site_Flag1_inputs_free=True,bad_positive_site_Flag1_one_induction=True,
                   source_physical_holders=[1,2,3,4,5],left_GF_phase=-1,right_GF_phase=0,
                   exterior_flags_Workspace_zero=True,initial_Flag2_zero=True,
                   sufficient_Flag2_held_source_updates=1120,Workspace1_allowed_updates=896,
                   Flag1_erasure_updates=224,Flag2_post_source_erasure_updates=224,
                   GF_and_all_four_flags_quiet_by_update=1344,
                   full_rule_source_and_clock_provenance_established=False,
                   continuing_noise_or_general_island_repair_established=False,
                   global_reliability_established=False,
                   scope='universal Boolean local identities plus explicit fixed-shape induction; conditional held physical source, not a noisy reliability theorem')
    (out/'SP8_arbitrary_Workspace1_certificate.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(dict(symbolic_cases=len(cache),invariant_cases=invariant,Flag1_erasure_cases=erasure)))


if __name__ == '__main__':
    main()
