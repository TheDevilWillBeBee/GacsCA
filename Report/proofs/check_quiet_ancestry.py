#!/usr/bin/env python3
"""Local and arithmetic certificate for the conditional quiet-ancestry lemmas.

The unbounded path proof and its noise-free recovery-window consequence
are stated in ROBUSTNESS §7. A four-site burst supports the exact joint
ancestry obstruction; it is not a sampled reliability claim.
"""
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
import numpy as np
from gacsca import candidates, codec, gpu, maintenance
from gacsca.gray_errors import classify
from gacsca.netlist import Net, Compiled, const_word, w_add_const_mod


def actual_flag_cases(p, address):
    net = Net()
    flag = {j: net.input(("flag", j)) for j in range(6)}
    cells = {j: dict(addr=const_word((address + j) % p.Q, p.k),
                     age=const_word(p.age_code(2000), p.m),
                     f1=flag[j] if j >= 0 else 0, f2=0, wf1=0, wf2=0)
             for j in range(-5, 6)}
    out = maintenance.build(net, cells, p.k, p.m, Q=p.Q,
                            nb=p.nb, radix=p.R, pos_bits=p.PB)
    net.set_output(("flag",), out["f1"])
    comp = Compiled(net)
    assert set(comp.inputs) == set(flag_name for flag_name in (("flag", j) for j in range(6)))
    words = np.arange(64, dtype=np.uint32)
    result = comp.evaluate({("flag", j): ((words >> j) & 1).astype(bool)
                            for j in range(6)}, bool)["flag",]
    expected = np.array([sum((int(word) >> j) & 1 for j in range(1, 6)) >= 3 or
                         ((int(word) & 1) and sum((int(word) >> j) & 1 for j in range(1, 6)) >= 2)
                         for word in words])
    assert np.array_equal(result, expected)
    assert np.all([sum((int(word) >> j) & 1 for j in range(1, 6)) <= 2
                   for word in words[~result]])
    return len(words)


def joint_obstruction(p):
    # Right Address support {1,2,3}, wrong Age support {3,4,5}, quiet
    # right Flag1 support {1,4,5}; the triple intersection is empty.
    net = Net()
    alpha, beta = p.age_code(2000), p.age_code(2001)
    cells = {}
    for j in range(-5, 6):
        address = j % p.Q if j <= 3 else 375 + j
        age = beta if j in (3, 4, 5) else alpha
        cells[j] = dict(addr=const_word(address, p.k), age=const_word(age, p.m),
                        f1=int(j in (2, 3)), f2=0, wf1=0, wf2=0)
    out = maintenance.build(net, cells, p.k, p.m, Q=p.Q,
                            nb=p.nb, radix=p.R, pos_bits=p.PB)
    assert out["addr"] == const_word(0, p.k)
    assert out["age_now"] == const_word(beta, p.m)
    assert out["age"] == const_word(p.age_code(2002), p.m)
    assert out["f1"] == out["f2"] == 0
    address_support, age_support, quiet_support = {1, 2, 3}, {3, 4, 5}, {1, 4, 5}
    assert not (address_support & age_support & quiet_support)
    return dict(reference_Address=0, correct_Age=alpha, wrong_selected_Age=beta,
                computed_Flag1=0, computed_Flag2=0,
                right_Address_support=sorted(address_support),
                right_wrong_Age_support=sorted(age_support),
                right_quiet_support=sorted(quiet_support),
                quiet_joint_support=[],
                scope="exact local snapshot; corresponding admissible burst checked separately; not a reliability counterexample")


def reachable_obstruction(c):
    p, C = c.p, c.c_backend()
    upper = codec.encode(c, np.zeros((c.W, 1), dtype=bool))
    sim = gpu.GpuSim(c, 1, p.Q, mode="grid")
    sim.set_state(C.pack(codec.encode(c, upper)))
    sim.run(2000)
    baseline = sim.state()[0]
    X = C.unpack(baseline, p.Q**2)
    assert np.all(c.field(X, "addr") == np.arange(p.Q**2) % p.Q)
    assert np.all(c.field(X, "age") == p.age_code(2000))
    assert not any(X[c.row[field, 0]].any() for field in ("f1", "f2", "wf1", "wf2"))
    center = (p.Q // 2)*p.Q
    for j in (2, 3, 4, 5):
        if j in (2, 3):
            X[c.row["f1", 0], center + j] = 1
        if j in (3, 4, 5):
            code = p.age_code(2001)
            for bit in range(p.m):
                X[c.row["age", bit], center + j] = (code >> bit) & 1
        if j in (4, 5):
            word = 375 + j
            for bit in range(p.k):
                X[c.row["addr", bit], center + j] = (word >> bit) & 1
    bad = C.pack(X)
    expected = C.run_packed(bad.copy(), 1)
    sim.set_state(bad)
    sim.run(1)
    got = sim.state()[0]
    assert np.array_equal(got, expected)
    next_X = C.unpack(got, p.Q**2)
    assert c.field(next_X, "addr")[center] == 0
    assert c.field(next_X, "age")[center] == p.age_code(2002)
    assert not next_X[c.row["f1", 0], center]
    assert not next_X[c.row["f2", 0], center]
    faults = {(center + j, 2000) for j in (2, 3, 4, 5)}
    certificate = classify(faults, Q=p.Q, U=p.U, sep=16)
    assert certificate["level1"] and certificate["level0"] == 0
    output = ROOT / "figs/robustness/quiet_ancestry_burst.npz"
    np.savez_compressed(output, center=center, baseline=baseline, burst_state=bad, output=got)
    return dict(physical_sites=p.Q**2, baseline_updates=2000,
                direct_fault_offsets=[2, 3, 4, 5], class_certificate=certificate,
                unaffected_center_Address=0, wrong_center_Age=int(c.field(next_X, "age")[center]),
                expected_clean_center_Age=p.age_code(2001), center_Flag1=0, center_Flag2=0,
                C_CUDA_full_output_equal=True, kernel_sha256=sim.source_sha256,
                asset_sha256=hashlib.sha256(output.read_bytes()).hexdigest(),
                scope="exact reachable one-update obstruction; no unreliability or recovery-lifetime claim")


def main():
    c = candidates.load("G17")
    p = c.p
    assert c.digest() == "23a14aab4d3dc4fde5562cf3e26a4536b05456f84e65850fcb3bd95a104d8ceb"
    inverse_cases = 0
    raw = np.arange(1 << p.k, dtype=np.uint32)
    for j in range(1, 6):
        net = Net()
        word = [net.input(("word", bit)) for bit in range(p.k)]
        adjusted = w_add_const_mod(net, word, (-j) % p.Q, p.Q)
        for bit, value in enumerate(adjusted):
            net.set_output(("adjusted", bit), value)
        result = Compiled(net).evaluate({("word", bit): ((raw >> bit) & 1).astype(bool)
                                        for bit in range(p.k)}, bool)
        values = sum(result["adjusted", bit].astype(np.uint32) << bit for bit in range(p.k))
        for address in range(p.Q - 5):
            assert np.array_equal(np.flatnonzero(values == address), [address + j])
            inverse_cases += 1
    intersections = 0
    for majority in range(32):
        if majority.bit_count() < 3:
            continue
        for quiet in range(32):
            if quiet.bit_count() < 3:
                continue
            assert majority & quiet
            intersections += 1
    flag_cases = sum(actual_flag_cases(p, address) for address in range(p.Q - 5))
    obstruction = joint_obstruction(p)
    reachable = reachable_obstruction(c)
    # A quiet path starting at a<=4 cannot terminate at Address >=Q-5
    # before travelling D=Q-5-a sites and at least ceil(D/5) updates.
    # The noise-free right damage envelope is b_s<=b_0+3s.
    windows = {}
    arithmetic_cases = 0
    for width in range(1, 151):
        upper = (600 - width) // 3
        assert upper >= width
        for tick in range(width, upper + 1):
            for address in range(5):
                distance = p.Q - 5 - address
                steps = (distance + 4) // 5
                assert width - 1 + 3*(tick - steps) < distance
                assert tick > width - 1
                arithmetic_cases += 1
        windows[str(width)] = [width, upper]
    assert windows["141"] == [141, 153]
    assert windows["150"] == [150, 150]
    assert (600 - 151) // 3 < 151
    receipt = dict(candidate="G17", **candidates.digests(c),
                   checker_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                   helpers_sha256=hashlib.sha256((ROOT / "gacsca/netlist.py").read_bytes()).hexdigest(),
                   maintenance_sha256=hashlib.sha256((ROOT / "gacsca/maintenance.py").read_bytes()).hexdigest(),
                   result="local/arithmetic certificate for proved conditional quiet-ancestry lemmas",
                   actual_modular_inverse_cases=inverse_cases,
                   support_intersection_cases=intersections,
                   actual_Flag1_gate_cases=flag_cases,
                   quiet_Address_path_step_range=[1, 5],
                   terminal_Address_range=[p.Q - 5, p.Q - 1],
                   quiet_clock_path_requires_aligned_Address=True,
                   joint_vote_snapshot=obstruction,
                   admissible_burst_obstruction=reachable,
                   noise_free_window_arithmetic_cases=arithmetic_cases,
                   noise_free_seed_widths_proved=list(range(1, 151)),
                   noise_free_width141_window=windows["141"],
                   noise_free_width150_window=windows["150"],
                   scope="quiet output lineage; noise-free forbidden window for x at or right of initial seed left endpoint",
                   not_proved=["mixed E0 boundary escape", "Flag2/D4 control",
                               "noisy island erosion", "reliability"],
                   rule_change=False)
    output = ROOT / "figs/robustness/quiet_ancestry_certificate.json"
    output.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()
