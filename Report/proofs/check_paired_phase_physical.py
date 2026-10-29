#!/usr/bin/env python3
"""Finite CUDA comparisons for J16's coherent Address/clock pair theorem.

The extreme legal clock ranges are included. No later errors; no native
C comparison; data restoration and arbitrary iid reliability not tested.
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
from check_coherent_phase_physical import replace_bits


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_variant(name):
    started = time.monotonic()
    out = ROOT / "figs/robustness"
    candidate = candidates.load("G17") if name == "G17" else proposed.load_artifact()
    p = candidate.p
    seed = 1082800+int(name == "SP2")
    rng = np.random.default_rng(seed)
    proof = json.loads((out / "paired_phase_certificate.json").read_text())
    clocks = proof["results"][name]["quiet_clocks"]
    Amax = clocks["maximum_initial_good_clock_tick"]
    Bmax = clocks["maximum_initial_bad_clock_tick"]
    columns = 40
    N = columns*p.Q
    width, geometry_bound, flag_bound, radius = (62, 588, 800, 5) if name == "G17" else (141, 631, 847, 8)
    assert N//2-radius*flag_bound > 0 and N//2+383+width+radius*flag_bound < N
    patterns = ("zero", "one", "alternating", "random")
    cases = list(itertools.product((0, 1, 2, 5, 128, 240, 380, 383),
                                   (1, 2, 3, 4, 8, 64, 160, 383),
                                   patterns, (0, 1, Amax, Bmax)))
    execution = copy.copy(candidate)
    execution.rom = np.pad(candidate.rom, ((0, (1 << p.k)-p.Q), (0, 0)))
    geometry_rows = [candidate.row[field, bit] for field, length in (("addr", p.k), ("age", p.m))
                     for bit in range(length)]
    flag_rows = [candidate.row[field, 0] for field in ("f1", "f2", "wf1", "wf2")]
    C = machine.CKernel  # static packing helpers only
    fixture = dict(seed=seed, columns=columns, width=width,
                   cases=np.asarray([(pos, shift, patterns.index(pattern), B)
                                     for pos, shift, pattern, B in cases], dtype=np.int32))
    result = dict(rule=name, proposed_rule_change=name == "SP2", active_G17_modified=False,
                  driver_sha256=digest(Path(__file__)),
                  physical_helper_sha256=digest(ROOT / "Report/proofs/check_coherent_phase_physical.py"),
                  proof_receipt_sha256=digest(out / "paired_phase_certificate.json"),
                  Q=p.Q, U=p.U, raw_width=candidate.W, seed=seed,
                  physical_cells_per_ring=N, width=width, cases_per_batch=len(cases),
                  batches=2, total_cases=2*len(cases), good_clock_ticks=(0, Amax),
                  bad_clock_ticks=(0, 1, Amax, Bmax), geometry_bound=geometry_bound,
                  Flag1_bound=flag_bound, native_C_comparison=False, continuing_noise=False,
                  periodic_edge_outside_maintenance_cone=True, global_reliability_established=False,
                  completion="execution-only zero padding of unused ROM rows; no active source change",
                  completed_rom_sha256=hashlib.sha256(execution.rom.tobytes()).hexdigest(),
                  scope="finite paired-clock support for J16 only", comparisons=[])
    if name == "G17":
        result.update(candidates.digests(candidate))
    else:
        result.update(proposed_candidate_sha256=candidate.digest(),
                      proposed_netlist_sha256=candidate.comp.digest,
                      proposal_source_sha256=digest(Path(proposed.__file__)))
    tracks = {}
    for batch, A in enumerate((0, Amax)):
        baseline = rng.integers(0, 2, (candidate.W, N), dtype=np.uint8)
        candidate.set_field(baseline, "addr", np.arange(N) % p.Q)
        candidate.set_field(baseline, "age", p.age_code(A))
        for field in ("f1", "f2", "wf1", "wf2"):
            candidate.set_field(baseline, field, 0)
        base = C.pack(baseline)
        del baseline
        states = np.broadcast_to(base, (len(cases)+1,)+base.shape).copy()
        flags = np.zeros((len(cases), width), dtype=np.uint8)
        for i, (position, shift, pattern, B) in enumerate(cases):
            sites = N//2+position+np.arange(width)
            address = (sites-shift) % p.Q
            for bit in range(p.k):
                replace_bits(states[i+1], candidate.row["addr", bit], sites, (address >> bit) & 1)
            for bit in range(p.m):
                replace_bits(states[i+1], candidate.row["age", bit], sites, (p.age_code(B) >> bit) & 1)
            if pattern == "one":
                flags[i] = 1
            elif pattern == "alternating":
                flags[i] = np.arange(width) % 2
            elif pattern == "random":
                flags[i] = rng.integers(0, 2, width, dtype=np.uint8)
            replace_bits(states[i+1], candidate.row["f1", 0], sites, flags[i])
        fixture[f"baseline_{batch}"] = base
        fixture[f"Flag1_patterns_{batch}"] = flags
        print(f"{name}: paired-clock batch A={A}, {len(cases)} cases", flush=True)
        sim = gpu.GpuSim(execution, len(cases)+1, columns, mode="grid")
        sim.set_state(states, t=0)
        del states
        result["kernel_sha256"] = sim.source_sha256
        sim.track(geometry_rows)
        sim.run(geometry_bound)
        tracking = sim.tracking()
        got = sim.state()
        unequal = np.count_nonzero(got[:, geometry_rows] ^ got[0, geometry_rows], axis=(1, 2))
        expected = base.copy()
        for bit in range(p.m):
            expected[candidate.row["age", bit]] = (np.uint64(2**64-1)
                                                    if (p.age_code(A+geometry_bound) >> bit) & 1 else 0)
        assert np.array_equal(got[0, geometry_rows], expected[geometry_rows]), "reference clock"
        assert not np.any(unequal), "paired-clock geometric bound"
        del got
        sim.track(flag_rows)
        sim.run(flag_bound-geometry_bound)
        got = sim.state()
        assert not np.any(got[:, flag_rows]), "paired-clock flag bound"
        assert not np.any(got[:, geometry_rows] ^ got[0, geometry_rows]), "persistent geometry"
        for kind, tracked in (("geometry", tracking), ("flags", sim.tracking())):
            tracks.update({f"{batch}_{kind}_{key}": value for key, value in tracked.items()})
        comparison = dict(good_clock_tick=A, last_geometry_difference=int(tracking["last_rows"].max()),
                          all_geometry_equal=True, all_flags_zero=True,
                          final_all_field_difference_words=int(np.count_nonzero(got[1:] ^ got[0])))
        result["comparisons"].append(comparison)
        print(json.dumps(comparison), flush=True)
        del got, sim
    asset = out / (name+"_paired_phase_inputs.npz")
    data = out / (name+"_paired_phase_tracking.npz")
    np.savez_compressed(asset, **fixture)
    np.savez_compressed(data, **tracks)
    result.update(input_asset_sha256=digest(asset), tracking_asset_sha256=digest(data),
                  elapsed_seconds=time.monotonic()-started,
                  result="measured: all 2048 paired phase cases meet J16 bounds")
    (out / (name+"_paired_phase_physical.json")).write_text(json.dumps(result, indent=2)+"\n")


if __name__ == "__main__":
    for variant in ("G17", "SP2"):
        check_variant(variant)
