#!/usr/bin/env python3
"""Finite SP22 NumPy/CUDA comparison and exact observation-hook check.

This is measured backend evidence, not a universal backend theorem.
No rule, ROM artifact, compiler or active backend is changed.
"""
import copy,hashlib,json
from pathlib import Path
import sys,time
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
import numpy as np
from gacsca import machine
import proposed_sparse_backward_fitted448 as proposed
import periodic_ever_gpu as observer


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    started=time.monotonic()
    candidate=proposed.load_artifact(); p=candidate.p
    execution=copy.copy(candidate)
    execution.rom=np.pad(candidate.rom,((0,(1<<p.k)-p.Q),(0,0)))
    rng=np.random.default_rng(1084494)
    states=rng.random((5,candidate.W,p.Q))<0.5
    states[3]=False;states[4]=True
    out=ROOT/'figs/robustness'
    asset=out/'SP22_periodic_operator_inputs.npz'
    np.savez_compressed(asset,initial=states)
    sim=observer.sim(execution,5,1)
    sim.set_state(np.stack([machine.CKernel.pack(s) for s in states]))
    rows=[candidate.row[f,b] for f,w in (('addr',p.k),('age',p.m)) for b in range(w)]
    sim.track(rows)
    ever=np.zeros((5,p.Q),dtype=bool)
    checks=[]
    for tick in range(4):
        expected=np.stack([execution.step_numpy(s) for s in states])
        for ring in range(1,5):
            ever[ring]|=np.any(expected[ring,rows]!=expected[0,rows],axis=0)
        sim.run(1)
        got=np.stack([machine.CKernel.unpack(s,p.Q) for s in sim.state()])
        assert np.array_equal(expected,got),tick
        assert np.array_equal(ever,observer.ever_sites(sim)),tick
        checks.append(dict(input_tick=tick,full_word_comparisons=5,ever_site_mask_exact=True))
        states=got
    result=dict(proposal='SP22',proposed_rule_change=True,active_G17_modified=False,
        proposed_candidate_sha256=candidate.digest(),proposed_netlist_sha256=candidate.comp.digest,
        proposal_source_sha256=digest(Path(proposed.__file__)),checker_sha256=digest(Path(__file__)),
        observer_helper_sha256=digest(Path(observer.__file__)),gpu_backend_sha256=digest(ROOT/'gacsca/gpu.py'),
        build_receipt_sha256=digest(out/'SP22_program_build.json'),input_asset_sha256=digest(asset),
        kernel_sha256=sim.source_sha256,completed_rom_sha256=hashlib.sha256(execution.rom.tobytes()).hexdigest(),
        ticks=4,rings=5,full_word_periodic_comparisons=20,union_mask_comparisons=4,checks=checks,
        measured_only=True,global_reliability_established=False,elapsed_seconds=time.monotonic()-started,
        scope='twenty finite literal NumPy/CUDA periodic updates and four selected-row union-mask checks; no universal backend or iid proof')
    (out/'SP22_periodic_operator_certificate.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(updates=20,union_masks=4,all_equal=True,seconds=result['elapsed_seconds'])),flush=True)


if __name__=='__main__':
    main()
