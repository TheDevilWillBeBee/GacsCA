#!/usr/bin/env python3
"""SP3 physical checker: NumPy/CUDA references, with static packing helpers."""
"""Finite physical checks of the EXPLICIT SP3 proposal, not reliability.

Four arbitrary upper contexts, ordinary/augmented encodings, and four E0
overwrite modes are checked for two periods. The universal copy argument
is separate. Execution-only zero padding realizes the proved completion.
"""
import copy
import hashlib
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
import numpy as np
from gacsca import codec, gpu, machine
import proposed_sparse_prefix as proposed


def augmented(candidate, upper):
    state = codec.encode(candidate, upper)
    for address, flag in ((candidate.p.lo, "f2"), (candidate.p.hi - 1, "f1")):
        assert address not in candidate.layout
        for bit, offset in candidate.p.fam().info_copies(candidate.p):
            sites = (np.arange(upper.shape[1]) * candidate.p.Q + address + offset) % state.shape[1]
            state[candidate.row["info", bit], sites] = upper[candidate.row[flag, 0]]
    return state


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    started = time.monotonic()
    out = ROOT / "figs/robustness"
    candidate = proposed.load_artifact()
    p = candidate.p
    front = json.loads((out / "SP3_front_certificate.json").read_text())
    assert front["maximum_simultaneous_arrivals"] == 1
    assert front["proposal_source_sha256"] == digest(Path(proposed.__file__))
    execution = copy.copy(candidate)
    execution.rom = np.pad(candidate.rom, ((0, (1 << p.k) - p.Q), (0, 0)))
    print("Preparing the isolated SP3 NumPy and CUDA comparisons.", flush=True)
    C = machine.CKernel  # static packing helpers; no C backend is compiled
    seed = 1083203
    rng = np.random.default_rng(seed)
    cases = {"random_all_words": codec.random_upper(candidate, p.Q, rng)}
    invalid = codec.random_upper(candidate, p.Q, rng)
    candidate.set_field(invalid, "addr", 500)
    candidate.set_field(invalid, "age", 17868)
    cases["invalid_fetch"] = invalid
    active = codec.random_upper(candidate, p.Q, rng)
    candidate.set_field(active, "age", (rng.integers(p.E0b, p.E0b + p.NP, p.Q) << p.PB) |
                         rng.integers(0, 512, p.Q))
    cases["active_raw_clocks"] = active
    staggered = codec.random_upper(candidate, p.Q, rng)
    candidate.set_field(staggered, "addr", 384 + np.arange(p.Q) % 128)
    candidate.set_field(staggered, "age", ((p.E0b + np.arange(p.Q) % 2) << p.PB) |
                         ((7 * np.arange(p.Q)) % 512))
    cases["unused_staggered_words"] = staggered
    asset = out / "SP3_physical_inputs.npz"
    np.savez_compressed(asset, seed=seed, **cases)
    contexts, states, cfgs = [], [], []
    for name, upper in cases.items():
        for encoding in ("ordinary", "augmented"):
            lower = codec.encode(candidate, upper) if encoding == "ordinary" else augmented(candidate, upper)
            states.append(C.pack(lower))
            contexts.append(dict(case=name, encoding=encoding, noise="none"))
            cfgs.append(gpu.noise())
    for mode in ("random", "one", "invert", "copy"):
        upper = cases["random_all_words"]
        encoding = "ordinary" if mode in ("random", "invert") else "augmented"
        lower = codec.encode(candidate, upper) if encoding == "ordinary" else augmented(candidate, upper)
        states.append(C.pack(lower))
        contexts.append(dict(case="random_all_words", encoding=encoding, noise=mode))
        cfg = gpu.noise(seed=seed + len(cfgs), e0_grid=26, e0_pair=1,
                        mode=mode, shift_sites=p.Q if mode == "copy" else 0)
        cfg.e0_pair16 = 65536
        cfgs.append(cfg)
    sim = gpu.GpuSim(execution, len(states), p.Q, mode="grid")
    initial_tick = (1 - p.U) % 26
    assert (initial_tick + p.U - 1) % 26 == 0
    sim.set_state(np.stack(states), t=initial_tick)
    sim.set_noise(cfgs)
    del states
    upper_states = {name: upper.copy() for name, upper in cases.items()}
    checks = []
    result = dict(
        proposal="SP3", proposed_rule_change=True, active_G17_modified=False,
        proposed_candidate_sha256=candidate.digest(), proposed_netlist_sha256=candidate.comp.digest,
        driver_sha256=digest(Path(__file__)), proposal_source_sha256=digest(Path(proposed.__file__)),
        build_receipt_sha256=digest(out / "SP3_program_build.json"),
        front_receipt_sha256=digest(out / "SP3_front_certificate.json"),
        input_asset_sha256=digest(asset), seed=seed,
        Q=p.Q, U=p.U, raw_width=candidate.W, radius=12,
        upper_cells=p.Q, physical_cells=p.Q ** 2, rings=len(contexts), periods=2,
        initial_gpu_tick=initial_tick, E0_grid=26, E0_pair_integer_threshold=65536,
        completed_rom_sha256=hashlib.sha256(execution.rom.tobytes()).hexdigest(),
        completion="execution-only padding of rows 384,...,511; proved output completion",
        kernel_sha256=sim.source_sha256,
        scope="finite physical comparisons; universal theorem rests on separate arguments",
        global_reliability_established=False, checks=checks)
    try:
        upper_sim = gpu.GpuSim(execution, len(cases), 1, mode="grid")
        for period in (1, 2):
            upper_sim.set_state(np.stack([C.pack(upper) for upper in upper_states.values()]))
            upper_sim.run(1)
            upper_native = upper_sim.state()
            for ring, (name, upper) in enumerate(upper_states.items()):
                expected = execution.step_numpy(upper)
                native = C.unpack(upper_native[ring], p.Q)
                assert np.array_equal(expected, native), name
                upper_states[name] = expected
            sim.run(p.U)
            got = sim.state()
            for ring, context in enumerate(contexts):
                expected = C.pack(augmented(candidate, upper_states[context["case"]]))
                current = sim.error_masks(cfgs[ring], ring, sim.t - 1, 1)[0]
                error_words = np.packbits(current, bitorder="little").view(np.uint64)
                indirect = (got[ring] ^ expected) & ~error_words[None, :]
                check = dict(context, period=period, current_overwrite_sites=int(current.sum()),
                             unequal_words_outside_current_overwrites=int(np.count_nonzero(indirect)),
                             state_sha256=hashlib.sha256(got[ring].tobytes()).hexdigest(),
                             expected_sha256=hashlib.sha256(expected.tobytes()).hexdigest(),
                             upper_CUDA_numpy_equal=True, gpu_ms=sim.last_ms)
                checks.append(check)
                print(json.dumps(check), flush=True)
                if np.any(indirect):
                    failure = out / "SP3_physical_failure.npz"
                    np.savez_compressed(failure, context=json.dumps(context), period=period,
                                        initial=cases[context["case"]], got=got[ring],
                                        expected=expected, current_errors=error_words)
                    result.update(result="failed finite comparison", failure_asset_sha256=digest(failure))
                    raise AssertionError(check)
        result["result"] = "measured: all boundary states exact outside current overwrites in 24 finite runs"
    finally:
        result["elapsed_seconds"] = time.monotonic() - started
        (out / "SP3_physical.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(dict(result=result["result"], comparisons=len(checks), seconds=result["elapsed_seconds"])))


if __name__ == "__main__":
    main()
