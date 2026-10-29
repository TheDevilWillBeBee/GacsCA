#!/usr/bin/env python3
"""Exact SP10 conditional trace with corrected/anchored source and four E0 erasures.
GF exterior and zero raw Info are prescribed; no iid or capture theorem.
"""
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
import numpy as np
from gacsca.netlist import Net,Compiled,mixed_age_increment,at_least,w_in_range,w_add_const_mod
from check_fast_flag_proposal import invoke
import proposed_sparse_confined_source448 as proposed
from gacsca.gray_errors import level0_points


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check(erased):
    candidate = proposed.load_artifact()
    p = candidate.p
    build,source = proposed.proposed_build(symbolic=True)
    n = Net()
    common = [n.input(('clock',bit)) for bit in range(p.m)]
    cells = {offset:dict(addr=[n.input(('x',offset,'addr',bit)) for bit in range(p.k)],age=common,
                         **{field:n.input(('x',offset,field,0)) for field in ('f1','f2','wf1','wf2')})
             for offset in range(-5,9)}
    result = invoke(build,n,cells,p)
    assert result['age_now'] == common
    assert result['age'] == mixed_age_increment(n,common,p.PB,p.R,p.nb)
    for bit,node in enumerate(result['addr']):
        n.set_output(('y','addr',bit),node)
    for field in ('f1','f2'):
        n.set_output(('y',field,0),result[field])
    source_gate = n.input(('source_gate',))
    anchor = at_least(n,[w_in_range(n,w_add_const_mod(n,cells[j]['addr'],(-j)%p.Q,p.Q),0,6) for j in range(-5,6)],6)
    memory = at_least(n,[cells[j]['wf2'] for j in range(-5,6)],3)
    n.set_output(('y','wf2',0),n.all([source_gate,anchor,memory]))
    compiled = Compiled(n)
    # The only live clock dependence of GF/flags is d3's low-four-bit
    # pulse. Enumerate all16 assignments at every update; all higher
    # common clock bits are absent from this output cone.
    live = set(n.live_nodes())
    assert all(key[1] < 4 for key,node in n.input_node.items() if key[0] == 'clock' and node in live)
    age_assignments = np.arange(16)
    address = (np.arange(p.Q)-1)%p.Q
    f1 = np.arange(p.Q) > 0
    f2 = np.zeros(p.Q,dtype=bool)
    trace = []
    states = []
    wf2 = (np.arange(p.Q)>=1)&(np.arange(p.Q)<=5)
    errors = {(1,400),(2,400),(3,425),(4,425)} if erased else set()
    assert level0_points(errors) == errors
    source_steps = 1792
    steps = 2200
    offsets = np.arange(-5,9)
    coordinates = np.arange(p.Q)[None,:]+offsets[:,None]
    first_correct = first_quiet = first_Flag1_quiet = None
    for step in range(steps+1):
        for x,t in errors:
            if t == step:
                wf2[x] = False
        if step<1792:
            assert wf2[1:6].sum() >= 3
        canonical = np.array_equal(address,np.arange(p.Q))
        quiet = canonical and not f1.any() and not f2.any()
        if canonical and first_correct is None:
            first_correct = step
        if quiet and first_quiet is None:
            first_quiet = step
        if canonical and not f1.any() and first_Flag1_quiet is None:
            first_Flag1_quiet = step
        trace.append(dict(step=step,canonical_Address_sites=int((address==np.arange(p.Q)).sum()),
                          Flag1_sites=int(f1.sum()),Flag2_sites=int(f2.sum()),Workspace2_sites=int(wf2.sum()),packet_surviving_bits=int(wf2[1:6].sum())))
        states.append(np.stack([address,f1.astype(np.int64),f2.astype(np.int64),wf2.astype(np.int64)]))
        if step == steps:
            break
        assert np.all((address==np.arange(p.Q))|(address==(np.arange(p.Q)-1)%p.Q))
        clamped = np.clip(coordinates,0,p.Q-1)
        inside = (coordinates>=0)&(coordinates<p.Q)
        A = np.where(inside,address[clamped],np.where(coordinates<0,(coordinates-1)%p.Q,coordinates%p.Q))
        F1 = inside & f1[clamped]
        F2 = inside & f2[clamped]
        WF2 = inside & wf2[clamped]
        WF1 = (step<896)&(coordinates>=p.Q-5)&(coordinates<p.Q)
        inputs = {}
        for key in compiled.inputs:
            if key[0] == 'source_gate':
                inputs[key] = np.full(16*p.Q,step<1791,dtype=bool)
                continue
            if key[0] == 'clock':
                inputs[key] = np.repeat(((age_assignments>>key[1])&1).astype(bool),p.Q)
                continue
            _,offset,field,bit = key
            index = offset+5
            value = ((A[index]>>bit)&1).astype(bool) if field == 'addr' else F1[index] if field == 'f1' else F2[index] if field == 'f2' else WF2[index] if field == 'wf2' else WF1[index]
            inputs[key] = np.tile(value,16)
        outputs = compiled.evaluate(inputs,bool)
        new_address = sum(outputs['y','addr',bit].astype(np.int64)<<bit for bit in range(p.k)).reshape(16,p.Q)
        new_f1 = outputs['y','f1',0].reshape(16,p.Q)
        new_f2 = outputs['y','f2',0].reshape(16,p.Q)
        assert np.all(new_address==new_address[:1]) and np.all(new_f1==new_f1[:1]) and np.all(new_f2==new_f2[:1]),step
        new_wf2 = outputs['y','wf2',0].reshape(16,p.Q)
        assert np.all(new_wf2==new_wf2[:1]),step
        address,f1,f2,wf2 = new_address[0],new_f1[0],new_f2[0],new_wf2[0]
    assert first_correct <= 372 and first_Flag1_quiet <= 1120 and first_quiet <= 2016
    assert np.array_equal(address,np.arange(p.Q)) and not f1.any() and not f2.any() and not wf2.any()
    out = ROOT/'figs/robustness'
    label = 'erased' if erased else 'control'
    asset = out/f'SP10_confined_phase_{label}_trace.npz'
    np.savez_compressed(asset,states=np.stack(states),errors=np.array(sorted(errors),dtype=np.int64).reshape(-1,2))
    receipt = dict(proposal='SP10',proposed_rule_change=True,active_G17_modified=False,
                   proposed_candidate_sha256=candidate.digest(),proposed_netlist_sha256=candidate.comp.digest,
                   proposal_source_sha256=digest(Path(proposed.__file__)),checker_sha256=digest(Path(__file__)),
                   local_correction_helper_sha256=digest(ROOT/'Report/proofs/check_fast_flag_proposal.py'),
                   helpers_sha256=digest(ROOT/'gacsca/netlist.py'),classifier_sha256=digest(ROOT/'gacsca/gray_errors.py'),
                   actual_maintenance_source_sha256=hashlib.sha256(source.encode()).hexdigest(),
                   source_certificate_sha256=digest(out/'SP10_confined_source_certificate.json'),
                   front_proof_receipt_sha256=digest(out/'SP10_repair_front_certificate.json'),
                   build_receipt_sha256=digest(out/'SP10_program_build.json'),tracking_asset_sha256=digest(asset),
                   label=label,errors=sorted(errors),all_displayed_errors_E0=True,WF2_only_overwrites=True,
                   zero_raw_Info_prescribed=True,initial_common_legal_clock=p.T_wf+1,
                   initial_packet_holders=list(range(1,6)),packet_never_below_three_before_gate_off=True,
                   source_gate_active_remaining_input_ticks=1791,Workspace2_source_free_relative_step=1792,
                   Workspace1_prescribed_one_at_right_five=True,Workspace1_source_steps=896,
                   left_exterior_GF_phase=-1,right_exterior_GF_phase=0,exterior_flags_Workspace_zero=True,
                   common_raw_Age_bits_free_in_GF_subsystem=p.m,clock_assignments_per_update=16,
                   actual_clock_gate_prescribed_by_common_legal_clock_sequence=True,
                   checked_updates=steps,all_GF_flag_and_source_clock_assignments_identical=True,
                   first_all_canonical_step=first_correct,first_all_GF_and_Flag1_quiet_step=first_Flag1_quiet,
                   first_all_GF_and_two_flags_quiet_step=first_quiet,trace=trace,
                   full_rule_bootstrap_or_exterior_provenance_established=False,
                   arbitrary_island_eroder_established=False,global_reliability_established=False,
                   scope='exact corrected-source conditional maintenance trace; exterior GF/flags and zero Info prescribed; not a full encoded trajectory or iid theorem')
    (out/f'SP10_confined_phase_{label}_certificate.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(dict(label=label,first_canonical=first_correct,first_Flag1_quiet=first_Flag1_quiet,first_quiet=first_quiet)))

if __name__ == "__main__":
    for erased in (False,True):
        check(erased)
