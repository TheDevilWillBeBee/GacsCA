#!/usr/bin/env python3
"""Exhaustive actual-gate certificate for arbitrary-word G17 front arrivals.

Every possible holder Address, Age position and sweep direction is checked.
The proof in ROBUSTNESS also factors out the Age window and all registers.
This establishes a local lemma, not noisy simulation or reliability.
"""
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
import numpy as np
from gacsca import candidates
from gacsca.netlist import Net, Compiled, w_add_const_mod
from gacsca.rule import front_timing_dwell


def main():
    c = candidates.load("G17")
    p = c.p
    assert c.digest() == "23a14aab4d3dc4fde5562cf3e26a4536b05456f84e65850fcb3bd95a104d8ceb"
    assert (p.k, p.PB, p.dlog, p.fronts, p.delta) == (9, 9, 0, 5, 5)
    assert (p.lo, p.hi, p.H, p.E0b) == (58, 326, 20, 34)
    net = Net()
    address = [net.input(("addr", i)) for i in range(p.k)]
    age = [net.input(("age", i)) for i in range(p.m)]
    slots = tuple(range(-2, 3))
    for d in slots:
        xa = w_add_const_mod(net, address, d % p.Q, p.Q)
        cell = dict(age=age, addr=xa, reg=[0]*p.L)
        pseudo = {-1: dict(reg=[0]*p.L), 0: cell, 1: dict(reg=[0]*p.L)}
        _, _, arrive, _ = front_timing_dwell(net, p, cell, pseudo)
        net.set_output(("arr", d), arrive)
        for i, bit in enumerate(xa):
            net.set_output(("xa", d, i), bit)
    comp = Compiled(net)
    cases = 2 * (1 << (2*p.k))
    histogram = [0, 0]
    outside = invalid = 0
    for begin in range(0, cases, 4096):
        number = np.arange(begin, min(begin + 4096, cases), dtype=np.uint32)
        A = number & 511
        position = (number >> 9) & 511
        direction = number >> 18
        packed_age = ((34 + direction) << 9) | position
        result = comp.evaluate({
            **{("addr", i): ((A >> i) & 1).astype(bool) for i in range(p.k)},
            **{("age", i): ((packed_age >> i) & 1).astype(bool) for i in range(p.m)}}, bool)
        base = np.where(direction, 325 - position.astype(np.int64), 38 + position) & 511
        arrivals = []
        for d in slots:
            value = A.astype(np.int64) + d % p.Q
            expected_xa = np.where(value >= p.Q, value - p.Q, value) & 511
            actual_xa = sum(result["xa", d, i].astype(np.uint32) << i for i in range(p.k))
            assert np.array_equal(actual_xa, expected_xa)
            difference = (expected_xa - base) & 511
            expected_arrival = np.isin(difference, [0, 5, 10, 15, 20])
            assert np.array_equal(result["arr", d], expected_arrival)
            arrivals.append(expected_arrival)
            outside += int(np.count_nonzero(expected_arrival & ((actual_xa < p.lo) | (actual_xa >= p.hi))))
            invalid += int(np.count_nonzero(expected_arrival & (actual_xa >= p.Q)))
        count = np.stack(arrivals).sum(axis=0)
        assert np.all(count <= 1)
        for i in (0, 1):
            histogram[i] += int(np.count_nonzero(count == i))
    # Every nonzero difference of two comb targets is +/-5,10,15,20
    # modulo 512. Compare all actual slot words independently of clock.
    A = np.arange(512, dtype=np.int64)
    values = []
    for d in slots:
        value = A + d % p.Q
        values.append(np.where(value >= p.Q, value - p.Q, value) & 511)
    forbidden = {5, 10, 15, 20, 492, 497, 502, 507}
    for i in range(5):
        for j in range(i):
            difference = (values[i] - values[j]) & 511
            assert np.all(difference != 0)
            assert not (set(difference.tolist()) & forbidden)
    receipt = dict(candidate="G17", **candidates.digests(c),
                   checker_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                   helpers_sha256=hashlib.sha256((ROOT / "gacsca/netlist.py").read_bytes()).hexdigest(),
                   timing_sha256=hashlib.sha256((ROOT / "gacsca/rule.py").read_bytes()).hexdigest(),
                   result="proved local front-arrival uniqueness for every raw Address/Age",
                   address_position_direction_cases=cases,
                   arrival_count_histogram=histogram,
                   maximum_simultaneous_arrivals=1,
                   arriving_cases_outside_work=outside,
                   arriving_cases_outside_ROM=invalid,
                   scope="all 512 Address words and 512 Age positions in both directions; window factor gives all 65536 Ages",
                   rule_change=False,
                   not_proved=["simulation through damaged physical boundary states", "reliability"])
    output = ROOT / "figs/robustness/front_arrival_certificate.json"
    output.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()
