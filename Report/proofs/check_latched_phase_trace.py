#!/usr/bin/env python3
"""Exact conditional GF/Flag trace with a held physical Flag2 source.

Only one specified phase/flag pattern and prescribed exterior/source
inputs are covered. Simulation data, correct command computation, actual
Workspace1 absence and general islands are separate proof obligations.
"""
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
import numpy as np
from gacsca.netlist import Net,Compiled,mixed_age_increment
from check_fast_flag_proposal import invoke
import proposed_sparse_latched448 as proposed


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
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
    source_steps = 896
    steps = 1400
    offsets = np.arange(-5,9)
    coordinates = np.arange(p.Q)[None,:]+offsets[:,None]
    first_correct = first_quiet = first_Flag1_quiet = None
    for step in range(steps+1):
        canonical = np.array_equal(address,np.arange(p.Q))
        quiet = canonical and not f1.any() and not f2.any()
        if canonical and first_correct is None:
            first_correct = step
        if quiet and first_quiet is None:
            first_quiet = step
        if canonical and not f1.any() and first_Flag1_quiet is None:
            first_Flag1_quiet = step
        trace.append(dict(step=step,canonical_Address_sites=int((address==np.arange(p.Q)).sum()),
                          Flag1_sites=int(f1.sum()),Flag2_sites=int(f2.sum())))
        states.append(np.stack([address,f1.astype(np.int64),f2.astype(np.int64)]))
        if step == steps:
            break
        assert np.all((address==np.arange(p.Q))|(address==(np.arange(p.Q)-1)%p.Q))
        clamped = np.clip(coordinates,0,p.Q-1)
        inside = (coordinates>=0)&(coordinates<p.Q)
        A = np.where(inside,address[clamped],np.where(coordinates<0,(coordinates-1)%p.Q,coordinates%p.Q))
        F1 = inside & f1[clamped]
        F2 = inside & f2[clamped]
        WF2 = (step<source_steps)&(coordinates>=1)&(coordinates<=5)
        inputs = {}
        for key in compiled.inputs:
            if key[0] == 'clock':
                inputs[key] = np.repeat(((age_assignments>>key[1])&1).astype(bool),p.Q)
                continue
            _,offset,field,bit = key
            index = offset+5
            value = ((A[index]>>bit)&1).astype(bool) if field == 'addr' else F1[index] if field == 'f1' else F2[index] if field == 'f2' else WF2[index] if field == 'wf2' else np.zeros(p.Q,dtype=bool)
            inputs[key] = np.tile(value,16)
        outputs = compiled.evaluate(inputs,bool)
        new_address = sum(outputs['y','addr',bit].astype(np.int64)<<bit for bit in range(p.k)).reshape(16,p.Q)
        new_f1 = outputs['y','f1',0].reshape(16,p.Q)
        new_f2 = outputs['y','f2',0].reshape(16,p.Q)
        assert np.all(new_address==new_address[:1]) and np.all(new_f1==new_f1[:1]) and np.all(new_f2==new_f2[:1]),step
        address,f1,f2 = new_address[0],new_f1[0],new_f2[0]
    assert first_correct is not None and first_Flag1_quiet is not None and first_Flag1_quiet < source_steps
    assert first_quiet is not None and first_quiet <= source_steps+(p.Q+1)//2
    assert np.array_equal(address,np.arange(p.Q)) and not f1.any() and not f2.any()
    out = ROOT/'figs/robustness'
    asset = out/'SP7_latched_phase_trace.npz'
    np.savez_compressed(asset,states=np.stack(states))
    receipt = dict(proposal='SP7',proposed_rule_change=True,active_G17_modified=False,
                   proposed_candidate_sha256=candidate.digest(),proposed_netlist_sha256=candidate.comp.digest,
                   proposal_source_sha256=digest(Path(proposed.__file__)),checker_sha256=digest(Path(__file__)),
                   local_correction_helper_sha256=digest(ROOT/'Report/proofs/check_fast_flag_proposal.py'),
                   helpers_sha256=digest(ROOT/'gacsca/netlist.py'),
                   actual_maintenance_source_sha256=hashlib.sha256(source.encode()).hexdigest(),
                   source_latch_receipt_sha256=digest(out/'SP6_SP7_source_latch_certificate.json'),
                   build_receipt_sha256=digest(out/'SP7_program_build.json'),
                   tracking_asset_sha256=digest(asset),phase=-1,Q=p.Q,
                   source_physical_holders=[1,2,3,4,5],source_steps=source_steps,
                   Workspace1_prescribed_zero=True,all_other_Workspace2_prescribed_zero=True,
                   left_exterior_GF_phase=-1,right_exterior_GF_phase=0,exterior_flags_Workspace_zero=True,
                   common_raw_Age_bits_free=p.m,GF_and_flag_live_clock_bits=list(range(4)),
                   clock_assignments_per_update=16,checked_updates=steps,
                   GF_all_ticks_one_of_two_address_phases=True,all_clock_assignments_identical=True,
                   first_all_canonical_step=first_correct,first_all_GF_and_two_flags_quiet_step=first_quiet,
                   first_all_GF_and_Flag1_quiet_step=first_Flag1_quiet,
                   trace=trace,actual_full_rule_capture_provenance_established=False,
                   arbitrary_island_eroder_established=False,global_reliability_established=False,
                   scope='exact finite conditional maintenance trace with a prescribed held source; not a full physical/noisy repair theorem')
    (out/'SP7_latched_phase_certificate.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(dict(first_canonical=first_correct,first_quiet=first_quiet,clock_assignments=16,steps=steps)))


if __name__ == '__main__':
    main()
