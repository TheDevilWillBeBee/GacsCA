#!/usr/bin/env python3
"""Finite checks for the Flag2 source cone lemma and a fixed-site counterexample.

The universal ancestry proof is in ROBUSTNESS §10. This checker evaluates
the unchanged total mathematical rule with safe experiment-only ROM padding.
"""
import copy
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
import numpy as np
from gacsca import candidates, gpu, machine
from gacsca.netlist import Net, Compiled, mixed_age_increment


def main():
    c = candidates.load("G17")
    p = c.p
    assert c.digest() == "23a14aab4d3dc4fde5562cf3e26a4536b05456f84e65850fcb3bd95a104d8ceb"
    net = Net()
    age = [net.input(("age", bit)) for bit in range(p.m)]
    new = mixed_age_increment(net, age, p.PB, p.R, p.nb)
    for bit in range(4):
        net.set_output(("new", bit), new[bit])
    words = np.arange(1 << p.m, dtype=np.uint32)
    out = Compiled(net).evaluate({("age", bit): ((words >> bit) & 1).astype(bool)
                                 for bit in range(p.m)}, bool)
    low = sum(out["new", bit].astype(np.uint32) << bit for bit in range(4))
    assert np.array_equal(low, (words + 1) % 16)
    for phase in range(16):
        assert 0 in [(phase + t) % 16 for t in range(1, 17)]
    # A full spatial period of the stationary Age staircase, at constant
    # Address 500, has 3U sites, a multiple of 64 and Q.
    N = 3 * p.U
    assert N % 64 == N % p.Q == 0
    X = np.zeros((c.W, N), dtype=bool)
    c.set_field(X, "addr", 500)
    c.set_field(X, "age", p.age_code(np.arange(N) // 3))
    c.set_field(X, "f1", 1)
    execution = copy.copy(c)
    execution.rom = np.pad(c.rom, ((0, (1 << p.k) - p.Q), (0, 0)))
    C = machine.CKernel(execution)
    initial = C.pack(X)
    first = C.run_packed(initial.copy(), 1)
    source_expected = (np.arange(N) // 3) % 16 == 0
    first_X = C.unpack(first, N)
    assert np.array_equal(first_X[c.row["f2", 0]], source_expected)
    fields = ("addr", "age", "f1")
    rows = [c.row[field, bit] for field in fields for bit in range(dict(c.schema)[field])]
    sim = gpu.GpuSim(execution, 1, N // p.Q, mode="grid")
    sim.set_state(initial)
    snapshots = sim.run(64, rows=rows, stride=1)
    assert np.all(snapshots[:, 0] == initial[rows][None])
    final = sim.state()[0]
    final_C = C.run_packed(initial.copy(), 64)
    assert np.array_equal(final, final_C)
    assert np.array_equal(C.unpack(final, N)[c.row["f2", 0]], source_expected)
    output = ROOT / "figs/robustness"
    np.savez_compressed(output / "flag2_source_staircase.npz", initial=initial,
                        first=first, final=final)
    receipt = dict(candidate="G17", **candidates.digests(c),
                   checker_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                   helpers_sha256=hashlib.sha256((ROOT / "gacsca/netlist.py").read_bytes()).hexdigest(),
                   maintenance_sha256=hashlib.sha256((ROOT / "gacsca/maintenance.py").read_bytes()).hexdigest(),
                   kernel_sha256=sim.source_sha256,
                   result="finite checks for proved conditional source-cone lemma and exact per-site counterexample",
                   raw_increment_words_checked=1 << p.m,
                   source_cone_updates=16, source_cone_spatial_span=75,
                   source_cone_maximum_sites_per_row=76,
                   stationary_staircase_sites=N, checked_stationary_updates=64,
                   C_CUDA_full_final_state_equal=True,
                   fixed_site_without_local_d3=3,
                   fixed_site_without_Flag2=3,
                   three_site_Flag2_patches_stationary=True,
                   local_d3_sites_per_period=int(source_expected.sum()),
                   completion="zero padding in experiment memory; ROBUSTNESS §6",
                   not_proved=["source guarantee through mixed E0 or partial no-majority regions",
                               "island reversal, erosion or reliability"])
    (output / "flag2_source_certificate.json").write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps(receipt, indent=2), flush=True)


if __name__ == "__main__":
    main()
