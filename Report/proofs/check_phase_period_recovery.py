#!/usr/bin/env python3
"""Finite support for coherent-pair repair and its period/footprint corollary.

Initial clean state has two complete boundary encodings. A block receives
arbitrary replacement bits subject to J16's coherent geometry/flag
hypotheses. No later faults. CUDA and NumPy reference comparisons only.
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
from gacsca import candidates, codec, gpu, machine
import proposed_sparse_quiet as proposed
from check_sparse_quiet_physical import augmented
from check_coherent_phase_physical import replace_bits


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def check_variant(name):
    started = time.monotonic()
    out = ROOT / "figs/robustness"
    candidate = candidates.load("G17") if name == "G17" else proposed.load_artifact()
    p = candidate.p
    width, geometry_bound = (62, 588) if name == "G17" else (141, 631)
    proof = json.loads((out / "paired_phase_certificate.json").read_text())
    Bmax = proof["results"][name]["quiet_clocks"]["maximum_initial_bad_clock_tick"]
    seed = 1083000+int(name == "SP2")
    rng = np.random.default_rng(seed)
    top = codec.random_upper(candidate, 1, rng)
    upper = augmented(candidate, top)
    lower = augmented(candidate, upper)
    execution = copy.copy(candidate)
    execution.rom = np.pad(candidate.rom, ((0, (1 << p.k)-p.Q), (0, 0)))
    expected_upper = execution.step_numpy(upper)
    expected = machine.CKernel.pack(augmented(candidate, expected_upper))
    cases = [(position, shift, Bmax if (index+int(shift == 160)) % 2 else 0)
             for index, position in enumerate((0, 1, 240, 383)) for shift in (3, 160)]
    base = machine.CKernel.pack(lower)
    states = np.broadcast_to(base, (len(cases)+1,)+base.shape).copy()
    replacements = np.zeros((len(cases), candidate.W, width), dtype=np.uint8)
    for i, (position, shift, B) in enumerate(cases):
        sites = p.Q**2//2+position+np.arange(width)
        replacement = rng.integers(0, 2, (candidate.W, width), dtype=np.uint8)
        candidate.set_field(replacement, "addr", (sites-shift) % p.Q)
        candidate.set_field(replacement, "age", p.age_code(B))
        for field in ("f2", "wf1", "wf2"):
            candidate.set_field(replacement, field, 0)
        if i % 2 == 0:
            candidate.set_field(replacement, "f1", 1)
        replacements[i] = replacement
        for row in range(candidate.W):
            replace_bits(states[i+1], row, sites, replacement[row])
    asset = out / (name+"_phase_period_inputs.npz")
    np.savez_compressed(asset, seed=seed, top=top, cases=np.asarray(cases, dtype=np.int32),
                        width=width, replacements=replacements, initial_packed_base=base)
    result = dict(rule=name, proposed_rule_change=name == "SP2", active_G17_modified=False,
                  driver_sha256=digest(Path(__file__)),
                  augmented_helper_sha256=digest(ROOT / "Report/proofs/check_sparse_quiet_physical.py"),
                  physical_helper_sha256=digest(ROOT / "Report/proofs/check_coherent_phase_physical.py"),
                  proof_receipt_sha256=digest(out / "paired_phase_certificate.json"),
                  input_asset_sha256=digest(asset), seed=seed, Q=p.Q, U=p.U,
                  width=width, physical_cells=p.Q**2, cases=len(cases), geometry_bound=geometry_bound,
                  continuing_noise=False, native_C_comparison=False,
                  completion="execution-only zero padding of unused ROM rows",
                  global_reliability_established=False, checks=[],
                  scope="finite whole-period recovery of J16 seeds at physical Age zero; not arbitrary level-1 errors")
    if name == "G17":
        result.update(candidates.digests(candidate))
    else:
        result.update(proposed_candidate_sha256=candidate.digest(),
                      proposed_netlist_sha256=candidate.comp.digest,
                      proposal_source_sha256=digest(Path(proposed.__file__)))
    sim = gpu.GpuSim(execution, len(cases)+1, p.Q, mode="grid")
    sim.set_state(states, t=0)
    del states, lower
    result["kernel_sha256"] = sim.source_sha256
    result["completed_rom_sha256"] = hashlib.sha256(execution.rom.tobytes()).hexdigest()
    try:
        sim.run(geometry_bound)
        got = sim.state()
        repaired_upper = []
        for ring, (position, shift, B) in enumerate(cases, start=1):
            repaired = codec.decode(candidate, machine.CKernel.unpack(got[ring], p.Q**2))
            differing = np.any(repaired != upper, axis=0)
            start = p.Q**2//2+position
            allowed = list(range((start-5)//p.Q, (start+width-1)//p.Q+1))
            assert len(allowed) <= 2
            outside = differing.copy()
            outside[allowed] = False
            assert not np.any(outside), "upper support escapes the proved two colonies"
            upper_next = execution.step_numpy(repaired)
            assert np.array_equal(upper_next, expected_upper), "boundary-encoding upper pair failed to correct"
            repaired_upper.append(repaired)
            result["checks"].append(dict(position=position, shift=shift, bad_clock_tick=B,
                                         changed_upper_cells=np.flatnonzero(differing).tolist(),
                                         allowed_upper_cells=allowed,
                                         upper_next_equals_clean=True))
        del got
        sim.run(p.U-geometry_bound)
        got = sim.state()
        for ring in range(len(cases)+1):
            unequal = int(np.count_nonzero(got[ring] ^ expected))
            assert unequal == 0, (ring, "whole boundary differs", unequal)
        result.update(result="measured: all eight seeds and clean twin exactly recover the full first-period boundary",
                      full_boundary_comparisons=len(cases)+1)
        data = out / (name+"_phase_period_decoded.npz")
        np.savez_compressed(data, original_upper=upper, repaired_upper=np.stack(repaired_upper),
                            expected_upper=expected_upper)
        result["decoded_asset_sha256"] = digest(data)
    except Exception:
        failure = out / (name+"_phase_period_failure.npz")
        np.savez_compressed(failure, got=sim.state(), gpu_tick=sim.t, expected=expected)
        result.update(result="failed finite period-recovery comparison", failure_asset_sha256=digest(failure))
        raise
    finally:
        result["elapsed_seconds"] = time.monotonic()-started
        (out / (name+"_phase_period_physical.json")).write_text(json.dumps(result, indent=2)+"\n")
    print(json.dumps({key: result[key] for key in ("rule", "result", "elapsed_seconds")}), flush=True)


if __name__ == "__main__":
    for variant in ("G17", "SP2"):
        check_variant(variant)
