#!/usr/bin/env python3
"""Measured full-own-programme SP18 source-core probe; no repair theorem.

Two periodic reference rings feed left/right halos of two driven rings.
Ring 2 is boundary-only; ring 3 gets one 16x16 kernel plus one singleton.
The core spans physical source sites 1..16 during clock T_wf-8..T_wf+7.
This is an explicitly changed boundary condition, not a noisy periodic CA.
"""
import argparse
import copy
import hashlib
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
import numpy as np
from gacsca import codec, machine
import proposed_sparse_epoch448 as proposed
from check_sparse_prefix448_physical import augmented
from check_coherent_phase_physical import replace_bits
import asymmetric_ghost_gpu as ghost


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--periods', type=int, default=20)
    args = parser.parse_args()
    assert args.periods >= 2
    started = time.monotonic()
    out = ROOT/'figs/robustness'
    stem = 'SP18_epoch_source_core'
    candidate = proposed.load_artifact()
    p = candidate.p
    cells = p.Q*p.Q
    top = np.zeros((candidate.W, 1), dtype=bool)
    upper = augmented(candidate, top)
    lower = augmented(candidate, upper)
    shifted = np.roll(lower, 1, axis=1)
    initial = np.stack([machine.CKernel.pack(s) for s in (lower, shifted, lower, lower)])
    input_asset = out/(stem+'_inputs.npz')
    tau, begin = p.T_wf-8, 1
    np.savez_compressed(input_asset, top=top, upper=upper, initial_packed=initial,
                        core_begin=begin, core_tau=tau)
    del upper, lower, shifted
    events = {tau+step: np.arange(begin, begin+16) if step < 16 else np.array([begin+15])
              for step in list(range(16))+[38]}
    execution = copy.copy(candidate)
    execution.rom = np.pad(candidate.rom, ((0, (1 << p.k)-p.Q), (0, 0)))
    sim = ghost.sim(execution, 4, p.Q)
    sim.set_state(initial, t=0)
    del initial
    gf_rows = [candidate.row[f,b] for f,w in (('addr',p.k),('age',p.m)) for b in range(w)]
    flag_rows = [candidate.row[f,0] for f in ('f1','f2','wf1','wf2')]
    sim.track(gf_rows)
    checks, pulses, snapshots, snapshot_ticks = [], [], [], []
    overwrite_ticks, overwrite_sites, overwrite_values = [], [], []
    clocks = sorted({p.T_wf-8,p.T_wf-1,p.T_wf,p.T_wf+1,p.T_wf+8,
                     p.T_wf+39,p.T_wf+443,p.T_wf+898,p.T_wf+1150,
                     p.T_wf+1792,p.T_wf+1793,p.T_wf+2304,p.T_wf+10788})
    pulse_ticks = {n*p.U+c for n in range(args.periods) for c in clocks}
    checkpoints = {n*p.U for n in range(1,args.periods+1)}
    result = dict(proposal='SP18', proposed_rule_change=True, active_G17_modified=False,
        proposed_candidate_sha256=candidate.digest(), proposed_netlist_sha256=candidate.comp.digest,
        proposal_source_sha256=digest(Path(proposed.__file__)), driver_sha256=digest(Path(__file__)),
        asymmetric_ghost_helper_sha256=digest(Path(ghost.__file__)),
        ghost_operator_checker_sha256=digest(ROOT/'Report/proofs/check_sparse_epoch448_ghost_operator.py'),
        ghost_operator_receipt_sha256=digest(out/'SP18_asymmetric_ghost_certificate.json'),
        inherited_operator_checker_sha256=digest(ROOT/'Report/proofs/check_sparse_framed448_ghost_operator.py'),
        augmented_helper_sha256=digest(ROOT/'Report/proofs/check_sparse_prefix448_physical.py'),
        physical_helper_sha256=digest(ROOT/'Report/proofs/check_coherent_phase_physical.py'),
        build_receipt_sha256=digest(out/'SP18_program_build.json'), input_asset_sha256=digest(input_asset),
        kernel_sha256=sim.source_sha256, completed_rom_sha256=hashlib.sha256(execution.rom.tobytes()).hexdigest(),
        completion='execution-only zero rows 448..511; mathematical I=0 completion',
        Q=p.Q,U=p.U,width=candidate.W,physical_cells=cells,upper_cells=p.Q,rings=4,
        requested_periods=args.periods,completed_periods=0,periodic_reference_rings=[0,1],
        boundary_only_control_ring=2,one_core_ring=3,left_reference_phase_shift=-1,
        core_begin=begin,core_tau=tau,overwrite_batches=17,total_overwrites=257,
        overwrite_rule='copy the evolving one-site-shifted periodic reference, all physical bits',
        classification='one 16x16 kernel plus its right-end singleton at relative tick38; all errors in this one finite level1 cluster',
        changed_boundary_condition=True,noisy_rings_are_periodic_CA_trajectories=False,
        continuing_E0=False,initial_pristine_infinite_hierarchy=False,
        infinite_line_equivalence_established=False,universal_core_repair_established=False,
        global_reliability_established=False,checks=checks,pulses=pulses,
        scope='finite full-upper-colony driven probe, measured only; boundary and overwrite values explicitly retained')
    try:
        for tick in sorted(set(events)|checkpoints|pulse_ticks):
            sim.run(tick-sim.t)
            packed = sim.state()
            reference = machine.CKernel.unpack(packed[0],cells)
            if tick in checkpoints:
                assert np.array_equal(candidate.field(reference,'addr'),np.arange(cells)%p.Q)
                assert np.all(candidate.field(reference,'age') == p.age_code(0))
                assert all(not candidate.field(reference,f).any() for f in ('f1','f2','wf1','wf2'))
                ref_upper = codec.decode(candidate,reference)
                row = dict(period=tick//p.U,tick=tick,rings=[])
                for ring in (2,3):
                    raw = machine.CKernel.unpack(packed[ring],cells)
                    gf_bad = np.any(raw[gf_rows]!=reference[gf_rows],axis=0)
                    flags_bad = np.any(raw[flag_rows]!=reference[flag_rows],axis=0)
                    full_bad = np.any(raw!=reference,axis=0)
                    decoded = codec.decode(candidate,raw)
                    row['rings'].append(dict(ring=ring,geometry_sites=int(gf_bad.sum()),
                        flags_sites=int(flags_bad.sum()),full_word_sites=int(full_bad.sum()),
                        geometry_first_eight_colonies=[int(s.sum()) for s in np.split(gf_bad[:8*p.Q],8)],
                        full_word_first_eight_colonies=[int(s.sum()) for s in np.split(full_bad[:8*p.Q],8)],
                        upper_GF_changed_cells=np.flatnonzero(np.any(decoded[gf_rows]!=ref_upper[gf_rows],axis=0)).tolist(),
                        upper_full_word_changed_cells=np.flatnonzero(np.any(decoded!=ref_upper,axis=0)).tolist()))
                checks.append(row)
                result['completed_periods']=row['period']
                print(json.dumps(dict(period=row['period'],rings=row['rings'],
                      seconds=round(time.monotonic()-started,3))),flush=True)
            if tick in pulse_ticks:
                raw = machine.CKernel.unpack(packed[3],cells)
                addr = candidate.field(raw,'addr')[:8*p.Q]
                age = candidate.field(raw,'age')[:8*p.Q]
                valid = candidate.field(raw,'packet_valid') & candidate.field(raw,'wf2')
                tags, counts = candidate.field(raw,'packet_tag'),candidate.field(raw,'packet_count')
                live = np.flatnonzero((valid & (tags<5))[:8*p.Q])
                coded = np.flatnonzero(candidate.field(raw,'service_valid')[:8*p.Q])
                positions, cc = candidate.field(raw,'service_position'),candidate.field(raw,'service_count')
                pulses.append(dict(tick=tick,period=tick//p.U,clock=tick%p.U,
                    canonical_GF_first_eight=[int(np.count_nonzero(a==np.arange(p.Q))) for a in np.split(addr,8)],
                    reference_Age_first_eight=[int(np.count_nonzero(a==b)) for a,b in zip(np.split(age,8),np.split(candidate.field(reference,'age')[:8*p.Q],8))],
                    F1_first_eight=[int(s.sum()) for s in np.split(candidate.field(raw,'f1')[:8*p.Q],8)],
                    F2_first_eight=[int(s.sum()) for s in np.split(candidate.field(raw,'f2')[:8*p.Q],8)],
                    packet_sites=live.tolist(),packet_tags=tags[live].tolist(),packet_counts=counts[live].tolist(),
                    packet_origins=(live-tags[live].astype(np.int64)-1).tolist(),
                    code_count=len(coded),code_origins=np.unique(coded-positions[coded].astype(np.int64)).tolist(),
                    code_counter_range=[int(cc[coded].min()),int(cc[coded].max())] if len(coded) else None))
            if tick in pulse_ticks or tick in checkpoints:
                snapshots.append(packed[:,:,:8*(p.Q//64)].copy())
                snapshot_ticks.append(tick)
            if tick in events:
                sites=events[tick]
                shifted_reference=machine.CKernel.unpack(packed[1],cells)
                values=shifted_reference[:,sites].copy()
                for bit in range(candidate.W):
                    replace_bits(packed[3],bit,sites,values[bit])
                padded_values=np.zeros((candidate.W,16),dtype=bool)
                padded_values[:,:len(sites)]=values
                padded_sites=np.full(16,-1,dtype=np.int64)
                padded_sites[:len(sites)]=sites
                overwrite_ticks.append(tick)
                overwrite_sites.append(padded_sites)
                overwrite_values.append(padded_values)
                sim.set_state(packed,t=tick)
        result['result']='measured: requested finite driven boundaries completed'
    finally:
        asset=out/(stem+'_tracking.npz')
        tracked=sim.tracking()
        np.savez_compressed(asset,snapshot_ticks=snapshot_ticks,
            first_eight_colonies_packed=np.stack(snapshots) if snapshots else np.empty((0,)),
            final_packed=sim.state(),overwrite_ticks=overwrite_ticks,
            overwrite_sites=np.stack(overwrite_sites) if overwrite_sites else np.empty((0,)),
            overwrite_values=np.stack(overwrite_values) if overwrite_values else np.empty((0,)),
            **{'every_tick_'+key:value for key,value in tracked.items()})
        result.update(tracking_asset_sha256=digest(asset),elapsed_seconds=time.monotonic()-started,
            recorded_overwrite_batches=len(overwrite_ticks),
            final_GF_last_difference_first_eight=tracked['last_rows'][3,:8].tolist(),
            final_full_word_last_difference_first_eight=tracked['last_any'][3,:8].tolist())
        (out/(stem+'_physical.json')).write_text(json.dumps(result,indent=2)+'\n')
        print(json.dumps(dict(result=result.get('result','incomplete'),
              completed_periods=result['completed_periods'],seconds=result['elapsed_seconds'])),flush=True)


if __name__=='__main__':
    main()
