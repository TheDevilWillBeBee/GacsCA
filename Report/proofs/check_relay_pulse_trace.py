#!/usr/bin/env python3
"""Continue the saved SP6 one-core run to inspect its next repair pulse.

Exact retained finite driven experiment, measured only. No replayed rule
source or boundary choice is changed relative to the parent receipt.
"""
import copy
import hashlib
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
import numpy as np
from gacsca import machine,codec
import proposed_sparse_relay448 as proposed
import asymmetric_ghost_gpu as ghost


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def cohort(candidate,raw,field,primary):
    width = proposed.logical_width(field,candidate.p)
    holders = np.arange(primary-2,primary+3)
    bits = [raw[candidate.row[field,(primary-int(holder)+2)*width],holder] for holder in holders]
    return dict(primary=primary,holders=holders.tolist(),copies=[int(v) for v in bits],majority=int(sum(bits)>=3))


def main():
    started = time.monotonic()
    out = ROOT/'figs/robustness'
    parent_path = out/'SP6_relay_one_core_physical.json'
    parent = json.loads(parent_path.read_text())
    candidate = proposed.load_artifact()
    p = candidate.p
    assert parent['completed_periods'] == 20 and parent['proposed_candidate_sha256'] == candidate.digest()
    input_asset = out/'SP6_relay_one_core_tracking.npz'
    with np.load(input_asset,allow_pickle=False) as saved:
        initial = saved['final_packed'].copy()
    execution = copy.copy(candidate)
    execution.rom = np.pad(candidate.rom,((0,512-p.Q),(0,0)))
    sim = ghost.sim(execution,4,p.Q)
    sim.set_state(initial,t=20*p.U)
    clocks = sorted({0,20050,22529,25288,25289,25344,25345,25346,25400,25500,25600,
                     25700,25800,25900,26000,26100,26200,26241,26242,26690,p.U})
    ticks = [period*p.U for period in range(21,32)]+[31*p.U+clock for clock in clocks if clock]
    rows,snapshots = [],[]
    gf_rows = [candidate.row[field,bit] for field,width in (('addr',p.k),('age',p.m)) for bit in range(width)]
    result = dict(proposal='SP6',proposed_rule_change=True,active_G17_modified=False,
                  proposed_candidate_sha256=candidate.digest(),proposed_netlist_sha256=candidate.comp.digest,
                  proposal_source_sha256=digest(Path(proposed.__file__)),driver_sha256=digest(Path(__file__)),
                  asymmetric_ghost_helper_sha256=digest(Path(ghost.__file__)),
                  parent_physical_receipt_sha256=digest(parent_path),input_asset_sha256=digest(input_asset),
                  build_receipt_sha256=digest(out/'SP6_program_build.json'),
                  start_tick=20*p.U,target_period=32,extra_overwrites=0,rings=4,rows=rows,
                  changed_boundary_condition=True,noisy_rings_are_periodic_CA_trajectories=False,
                  source_copy_provenance_proved=False,universal_repair_established=False,
                  global_reliability_established=False,scope='finite saved-state continuation; measured only')
    try:
        for tick in ticks:
            sim.run(tick-sim.t)
            packed = sim.state()
            reference = machine.CKernel.unpack(packed[0],p.Q*p.Q)
            raw = machine.CKernel.unpack(packed[3],p.Q*p.Q)
            gf_bad = np.any(raw[gf_rows]!=reference[gf_rows],axis=0)
            address = candidate.field(raw,'addr')[:p.Q]
            aligned = codec.decode(candidate,np.roll(raw,-1,axis=1))
            clock = tick%p.U
            primary = 60-(clock-25288) if 25289 <= clock <= 25344 else (59 if clock == 25288 else 4)
            rows.append(dict(tick=tick,period=tick//p.U,clock=clock,
                             physical_GF_bad_sites=int(gf_bad.sum()),
                             first_colony_GF_bad_sites=int(gf_bad[:p.Q].sum()),
                             canonical_Address_sites_first_colony=int((address==np.arange(p.Q)).sum()),
                             phase_minus_one_Address_sites_first_colony=int((address==(np.arange(p.Q)-1)%p.Q).sum()),
                             first_colony_Flag_counts={field:int(candidate.field(raw,field)[:p.Q].sum()) for field in ('f1','f2','wf1','wf2')},
                             first_colony_Flag2_indices=np.flatnonzero(candidate.field(raw,'f2')[:p.Q]).tolist(),
                             source_Hold=cohort(candidate,raw,'hold',59),
                             moving_ML=cohort(candidate,raw,'ml',primary),
                             special_Info=cohort(candidate,raw,'info',4),
                             aligned_parent_GF_flags={field:candidate.field(aligned,field)[:3].tolist() for field in ('addr','age','f1','f2')}))
            snapshots.append(packed[:,:,:8*(p.Q//64)].copy())
            print(json.dumps(dict(period=tick//p.U,clock=clock,canonical_Address=rows[-1]['canonical_Address_sites_first_colony'],
                                  flags=rows[-1]['first_colony_Flag_counts'],
                                  Hold2=rows[-1]['source_Hold']['majority'],ML=rows[-1]['moving_ML']['majority'],
                                  Info3=rows[-1]['special_Info']['majority'])),flush=True)
        result['completed_tick'] = sim.t
    finally:
        asset = out/'SP6_relay_pulse_trace.npz'
        np.savez_compressed(asset,ticks=[row['tick'] for row in rows],first_eight_colonies_packed=np.stack(snapshots),final_packed=sim.state())
        result.update(tracking_asset_sha256=digest(asset),elapsed_seconds=time.monotonic()-started)
        (out/'SP6_relay_pulse_trace.json').write_text(json.dumps(result,indent=2)+'\n')
        print(json.dumps(dict(completed_tick=sim.t,seconds=result['elapsed_seconds'])),flush=True)


if __name__ == '__main__':
    main()
