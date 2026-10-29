#!/usr/bin/env python3
"""Finite independent NumPy validation of the native E0 observer masks.

This tests the numerical observation hook, not Gray's recovery theorem.
Raw inputs are deliberately arbitrary, so this is not a Workspace-zero
restriction certificate for every tested input.
"""
from pathlib import Path
import hashlib,json,sys,time
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
sys.path.insert(0,str(ROOT/'Report/proofs'))
import numpy as np
from gacsca import gpu
import periodic_ever_gpu as observer
import corrected_native_rule as native
from check_corrected_native_operator import pack,unpack


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    started=time.monotonic(); out=ROOT/'figs/gray_counterexamples'
    cand=native.candidate(); N=cand.p.Q
    rng=np.random.default_rng(20261012)
    initial=rng.integers(0,2,(cand.W,N),dtype=np.uint8).astype(bool)
    positions=(0,31,63,4095,4096,N-2)
    state=np.broadcast_to(initial,(len(positions)+1,cand.W,N)).copy()
    sim=observer.sim(cand,len(positions)+1,1)
    sim.set_state(pack(state),t=0)
    rows=[cand.row[f,b] for f,w in (('addr',cand.p.k),('age',cand.p.m)) for b in range(w)]
    sim.track(rows)
    expected_ever=np.zeros((len(positions)+1,N),dtype=bool)
    first=np.full(len(positions)+1,-1,dtype=np.int64)
    last=first.copy(); retained_states=[state.copy()]; replacements=[]
    for T in range(1,5):
        cfgs=[gpu.noise()]+[gpu.noise(boxes=[(x,2,T-1,1,1)],mode='zero')
                            if T in (1,3) else gpu.noise() for x in positions]
        expected=np.stack([cand.step_numpy(ring) for ring in state])
        fresh=np.zeros_like(expected_ever)
        for case,x in enumerate(positions,1):
            if T in (1,3):
                fresh[case,x:x+2]=True; expected[case,:,x:x+2]=False
            mask=sim.error_masks(cfgs[case],case,T-1,1)[0]
            assert np.array_equal(mask,fresh[case])
        sim.set_noise(cfgs); sim.run(1)
        assert np.array_equal(unpack(sim.state(),N),expected)
        for case in range(1,len(positions)+1):
            observed=np.any(expected[case,rows]^expected[0,rows],axis=0)&~fresh[case]
            expected_ever[case]|=observed
            if np.any(observed):
                if first[case]<0:
                    first[case]=T
                last[case]=T
        assert np.array_equal(observer.ever_sites(sim),expected_ever)
        # The mixed campaign performs a host replacement at the same masked
        # locations. Repeat that convention with retained arbitrary values.
        custom=np.zeros((len(positions),cand.W,2),dtype=bool)
        if T in (1,3):
            for case,x in enumerate(positions,1):
                custom[case-1]=rng.integers(0,2,(cand.W,2),dtype=np.uint8).astype(bool)
                expected[case,:,x:x+2]=custom[case-1]
            sim.set_state(pack(expected),t=T)
        replacements.append(custom); state=expected
        retained_states.append(state.copy())
    tracked=sim.tracking()
    assert np.array_equal(tracked['first_rows'][:,0],first)
    assert np.array_equal(tracked['last_rows'][:,0],last)
    asset=out/'native_observer_mask_inputs.npz'
    np.savez_compressed(asset,states=np.stack(retained_states),positions=np.array(positions),
                        custom_replacements=np.stack(replacements),geometry_ever=expected_ever,**tracked)
    result=dict(Q=cand.p.Q,U=cand.p.U,cases=len(positions),full_numpy_CUDA_updates=28,
        observed_ticks=4,masked_pair_states=[1,3],random_seed=20261012,
        checker_sha256=digest(__file__),asset_sha256=digest(asset),
        corrected_native_source_sha256=digest(native.__file__),
        observer_source_sha256=digest(observer.__file__),cuda_kernel_sha256=sim.source_sha256,
        candidate_sha256=cand.digest(),netlist_sha256=cand.comp.digest,
        gpu_backend_source_sha256=digest(ROOT/'gacsca/gpu.py'),
        masks_match_exact_requested_sites=True,ever_and_first_last_match_independent_numpy=True,
        measured_only=True,universal_backend_equivalence_proved=False,
        recovery_counterexample=False,global_reliability_established=False,
        elapsed_seconds=time.monotonic()-started)
    (out/'native_observer_mask_certificate.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))


if __name__=='__main__':
    main()
