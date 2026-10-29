#!/usr/bin/env python3
"""Finite CUDA support for J15, separate from its unbounded-line proof.

No later faults. Every case satisfies the common-clock, two-phase and
initial flag hypotheses. Arbitrary other fields are shared with a clean
twin. Neither rule source is changed; SP2 is the isolated proposal.
"""
import copy
import hashlib
import itertools
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
import numpy as np
from gacsca import candidates, gpu, machine
import proposed_sparse_quiet as proposed


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def replace_bits(packed, row, sites, values):
    words = sites // 64
    bits = np.left_shift(np.uint64(1), (sites % 64).astype(np.uint64))
    mask = np.zeros(packed.shape[1], dtype=np.uint64)
    data = np.zeros_like(mask)
    np.bitwise_or.at(mask, words, bits)
    np.bitwise_or.at(data, words, bits * np.asarray(values, dtype=np.uint64))
    packed[row] = (packed[row] & ~mask) | data


def check_variant(name):
    started = time.monotonic()
    out = ROOT / "figs/robustness"
    candidate = candidates.load("G17") if name == "G17" else proposed.load_artifact()
    p = candidate.p
    proposed_change = name == "SP2"
    seed = 1082700 + int(proposed_change)
    rng = np.random.default_rng(seed)
    columns = 40
    N = columns * p.Q
    widths = (1, 3, 5, 8, 16, 62) if name == "G17" else (1, 3, 5, 16, 62, 141)
    positions = (0, 1, 2, 5, 128, 240, 380, 383)
    shifts = (1, 2, 3, 4, 8, 64, 160, 383)
    patterns = ("zero", "one", "alternating", "random")
    cases = list(itertools.product(widths, positions, shifts, patterns))
    geometry_bound, flag_bound = (588, 800) if name == "G17" else (631, 847)
    maintenance_radius = 5 if name == "G17" else 8
    # While sources are off, simulation fields cannot couple back into
    # geometry/Flag1. The maintenance cone cannot reach the periodic edge.
    assert N//2-maintenance_radius*flag_bound > 0
    assert N//2+max(positions)+max(widths)+maintenance_radius*flag_bound < N
    assert flag_bound < p.T_wf
    baseline = rng.integers(0, 2, (candidate.W, N), dtype=np.uint8)
    candidate.set_field(baseline, "addr", np.arange(N) % p.Q)
    candidate.set_field(baseline, "age", 0)
    for field in ("f1", "f2", "wf1", "wf2"):
        candidate.set_field(baseline, field, 0)
    C = machine.CKernel  # static pack/unpack only; no native C is compiled
    base = C.pack(baseline)
    states = np.broadcast_to(base, (len(cases)+1,)+base.shape).copy()
    flags = np.zeros((len(cases), max(widths)), dtype=np.uint8)
    for i, (width, position, shift, pattern) in enumerate(cases):
        sites = N//2+position+np.arange(width)
        address = (sites-shift) % p.Q
        for bit in range(p.k):
            replace_bits(states[i+1], candidate.row["addr", bit], sites, (address >> bit) & 1)
        if pattern == "one":
            flags[i, :width] = 1
        elif pattern == "alternating":
            flags[i, :width] = np.arange(width) % 2
        elif pattern == "random":
            flags[i, :width] = rng.integers(0, 2, width, dtype=np.uint8)
        replace_bits(states[i+1], candidate.row["f1", 0], sites, flags[i, :width])
    asset = out / (name+"_coherent_phase_inputs.npz")
    np.savez_compressed(asset, seed=seed, baseline_packed=base,
                        cases=np.asarray([(w, pos, shift, patterns.index(pattern))
                                          for w, pos, shift, pattern in cases], dtype=np.int32),
                        Flag1_patterns=flags, columns=columns)
    execution = copy.copy(candidate)
    execution.rom = np.pad(candidate.rom, ((0, (1 << p.k)-p.Q), (0, 0)))
    print(f"{name}: {len(cases)} coherent phase cases, {N} sites per ring", flush=True)
    sim = gpu.GpuSim(execution, len(cases)+1, columns, mode="grid")
    sim.set_state(states, t=0)
    del states, baseline
    geometry_rows = [candidate.row[field, bit] for field, length in (("addr", p.k), ("age", p.m))
                     for bit in range(length)]
    sim.track(geometry_rows)
    result = dict(rule=name, proposed_rule_change=proposed_change, active_G17_modified=False,
                  driver_sha256=digest(Path(__file__)),
                  proof_receipt_sha256=digest(out / "SP2_coherent_phase_certificate.json"),
                  input_asset_sha256=digest(asset), kernel_sha256=sim.source_sha256,
                  Q=p.Q, U=p.U, raw_width=candidate.W, seed=seed,
                  cases=len(cases), rings=len(cases)+1, physical_cells_per_ring=N,
                  widths=widths, positions=positions, shifts=shifts, Flag1_patterns=patterns,
                  geometry_bound=geometry_bound, Flag1_bound=flag_bound,
                  periodic_edge_outside_maintenance_cone=True,
                  continuing_noise=False, native_C_comparison=False,
                  scope="finite CUDA support for J15 hypotheses only, not arbitrary bursts or reliability",
                  completed_rom_sha256=hashlib.sha256(execution.rom.tobytes()).hexdigest(),
                  completion="execution-only zero padding; active sources and stored ROM unchanged",
                  global_reliability_established=False)
    if name == "G17":
        result.update(candidates.digests(candidate))
    else:
        result.update(proposed_candidate_sha256=candidate.digest(),
                      proposed_netlist_sha256=candidate.comp.digest,
                      proposal_source_sha256=digest(Path(proposed.__file__)),
                      build_receipt_sha256=digest(out / "SP2_program_build.json"))
    try:
        while sim.t < geometry_bound:
            sim.run(min(64, geometry_bound-sim.t))
            print(f"{name}: geometry checks through state {sim.t}", flush=True)
        tracking = sim.tracking()
        got = sim.state()
        unequal = np.count_nonzero(got[:, geometry_rows] ^ got[0, geometry_rows], axis=(1, 2))
        expected = base.copy()
        for bit in range(p.m):
            expected[candidate.row["age", bit]] = (np.uint64(2**64-1)
                                                    if (p.age_code(geometry_bound) >> bit) & 1 else 0)
        assert np.array_equal(got[0, geometry_rows], expected[geometry_rows]), "reference geometry"
        result.update(unequal_geometry_words_by_case=unequal[1:].tolist(),
                      last_geometry_difference=int(tracking["last_rows"].max()))
        assert not np.any(unequal), "geometric bound failed in finite comparison"
        del got
        flag_rows = [candidate.row[field, 0] for field in ("f1", "f2", "wf1", "wf2")]
        sim.track(flag_rows)
        while sim.t < flag_bound:
            sim.run(min(64, flag_bound-sim.t))
        got = sim.state()
        assert not np.any(got[:, flag_rows]), "flag-clearance bound failed"
        assert not np.any(got[:, geometry_rows] ^ got[0, geometry_rows]), "geometry did not persist"
        data = out / (name+"_coherent_phase_tracking.npz")
        np.savez_compressed(data, **{"geometry_"+key: value for key, value in tracking.items()},
                            **{"flags_"+key: value for key, value in sim.tracking().items()})
        result.update(tracking_asset_sha256=digest(data),
                      final_flags_zero=True, final_geometry_equal=True,
                      final_all_field_difference_words=int(np.count_nonzero(got[1:] ^ got[0])),
                      result="measured: all 1536 coherent phase cases meet J15 bounds")
    except Exception:
        failure = out / (name+"_coherent_phase_failure.npz")
        np.savez_compressed(failure, final=sim.state(), gpu_tick=sim.t)
        result.update(result="failed finite J15 comparison", failure_asset_sha256=digest(failure))
        raise
    finally:
        result["elapsed_seconds"] = time.monotonic()-started
        (out / (name+"_coherent_phase_physical.json")).write_text(json.dumps(result, indent=2)+"\n")
    print(json.dumps({key: result[key] for key in ("rule", "result", "last_geometry_difference",
                                                "final_all_field_difference_words", "elapsed_seconds")}), flush=True)


if __name__ == "__main__":
    for variant in ("G17", "SP2"):
        check_variant(variant)
