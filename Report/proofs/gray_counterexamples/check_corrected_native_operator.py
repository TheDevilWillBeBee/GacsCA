#!/usr/bin/env python3
"""Finite C/CUDA/NumPy agreement for the isolated corrected native rule."""
from pathlib import Path
import hashlib,json,sys,time
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
import numpy as np
from gacsca import gpu
import corrected_native_rule as native


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def pack(state):
    return np.ascontiguousarray(np.packbits(state,axis=-1,bitorder='little').view(np.uint64))


def unpack(state,N):
    return np.unpackbits(state.view(np.uint8),axis=-1,bitorder='little')[...,:N].astype(bool)


def main():
    started=time.monotonic()
    out=ROOT/'figs/gray_counterexamples'
    cand=native.candidate()
    rng=np.random.default_rng(20261010)
    initial=rng.integers(0,2,size=(4,cand.W,cand.p.Q),dtype=np.uint8).astype(bool)
    initial[2]=False
    initial[3]=True
    sim=gpu.GpuSim(cand,4,1,mode='grid')
    sim.set_state(pack(initial))
    sim.set_noise([gpu.noise() for _ in range(4)])
    state=initial.copy()
    cb=cand.c_backend()
    checks=0
    states=[state.copy()]
    for tick in range(4):
        expected=np.stack([cand.step_numpy(ring) for ring in state])
        cresult=np.stack([cb.run(ring.copy(),1) for ring in state])
        sim.run(1)
        cuda=unpack(sim.state(),cand.p.Q)
        assert np.array_equal(cresult,expected)
        assert np.array_equal(cuda,expected)
        checks+=4
        state=expected
        states.append(state.copy())
    asset=out/'corrected_native_operator_inputs.npz'
    np.savez_compressed(asset,states=np.stack(states))
    result=dict(Q=cand.p.Q,U=cand.p.U,width=cand.W,radius=5,
        corrected_native_source_sha256=digest(native.__file__),checker_sha256=digest(__file__),
        active_maintenance_sha256=digest(ROOT/'gacsca/maintenance.py'),
        c_backend_source_sha256=digest(ROOT/'gacsca/machine.py'),gpu_backend_source_sha256=digest(ROOT/'gacsca/gpu.py'),
        cuda_kernel_sha256=sim.source_sha256,candidate_sha256=cand.digest(),
        netlist_sha256=cand.comp.digest,asset_sha256=digest(asset),
        random_seed=20261010,full_numpy_C_CUDA_updates=checks,
        measured_only=True,universal_backend_equivalence_proved=False,
        full_gray_simulation_rule=False,global_reliability_established=False,
        elapsed_seconds=time.monotonic()-started)
    (out/'corrected_native_operator_certificate.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))


if __name__=='__main__':
    main()
