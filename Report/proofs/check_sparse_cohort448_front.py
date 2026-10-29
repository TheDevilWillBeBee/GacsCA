#!/usr/bin/env python3
"""SP12 verifier/build copy of check_sparse_front.py; distinct source and receipt pins."""
"""All-raw-word front uniqueness and completion certificate for proposed SP12.

This rechecks the literal timing/addition gates at SP12's constants. It
does not prove noisy restoration or an all-time threshold. G17 is unchanged.
"""
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
import numpy as np
import proposed_sparse_cohort448 as proposed
from gacsca.netlist import Net, Compiled, w_add_const_mod
from gacsca.rule import front_timing_dwell


def main():
    p = proposed.parameters()
    assert (p.k, p.PB, p.dlog, p.fronts, p.delta) == (9, 9, 0, 5, 5)
    assert (p.lo, p.hi, p.H, p.E0b) == (58, 390, 20, 32)
    net = Net()
    address = [net.input(("addr", i)) for i in range(p.k)]
    age = [net.input(("age", i)) for i in range(p.m)]
    for slot in proposed.SLOTS:
        xa = w_add_const_mod(net, address, slot % p.Q, p.Q)
        cell = dict(age=age, addr=xa, reg=[0] * p.L)
        pseudo = {-1: dict(reg=[0] * p.L), 0: cell, 1: dict(reg=[0] * p.L)}
        _, _, arrive, _ = front_timing_dwell(net, p, cell, pseudo)
        net.set_output(("arr", slot), arrive)
        for i, bit in enumerate(xa):
            net.set_output(("xa", slot, i), bit)
    comp = Compiled(net)
    cases = 2 * (1 << (2 * p.k))
    histogram = [0, 0]
    outside = invalid = 0
    for begin in range(0, cases, 4096):
        number = np.arange(begin, min(begin + 4096, cases), dtype=np.uint32)
        A = number & 511
        position = (number >> 9) & 511
        direction = number >> 18
        raw_age = ((p.E0b + direction) << p.PB) | position
        values = {("addr", i): ((A >> i) & 1).astype(bool) for i in range(p.k)}
        values.update({("age", i): ((raw_age >> i) & 1).astype(bool) for i in range(p.m)})
        got = comp.evaluate(values, bool)
        base = np.where(direction, p.hi - 1 - position.astype(np.int64), p.lo - p.H + position) & 511
        arrivals = []
        for slot in proposed.SLOTS:
            value = A.astype(np.int64) + slot % p.Q
            xa = np.where(value >= p.Q, value - p.Q, value) & 511
            actual_xa = sum(got["xa", slot, i].astype(np.uint32) << i for i in range(p.k))
            assert np.array_equal(actual_xa, xa)
            expected = np.isin((xa - base) & 511, [0, 5, 10, 15, 20])
            assert np.array_equal(got["arr", slot], expected)
            arrivals.append(expected)
            outside += int(np.count_nonzero(expected & ((xa < p.lo) | (xa >= p.hi))))
            invalid += int(np.count_nonzero(expected & (xa >= p.Q)))
        count = np.stack(arrivals).sum(axis=0)
        assert np.all(count <= 1)
        for i in (0, 1):
            histogram[i] += int(np.count_nonzero(count == i))
    all_words = np.arange(512, dtype=np.int64)
    slot_words = []
    for slot in proposed.SLOTS:
        value = all_words + slot % p.Q
        slot_words.append(np.where(value >= p.Q, value - p.Q, value) & 511)
    forbidden = {5, 10, 15, 20, 492, 497, 502, 507}
    for i in range(5):
        for j in range(i):
            difference = (slot_words[i] - slot_words[j]) & 511
            assert np.all(difference != 0)
            assert not (set(difference.tolist()) & forbidden)
    result = dict(
        proposal="SP12", proposed_rule_change=True, active_G17_modified=False,
        checker_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        proposal_source_sha256=hashlib.sha256(Path(proposed.__file__).read_bytes()).hexdigest(),
        timing_sha256=hashlib.sha256((ROOT / "gacsca/rule.py").read_bytes()).hexdigest(),
        helpers_sha256=hashlib.sha256((ROOT / "gacsca/netlist.py").read_bytes()).hexdigest(),
        address_position_direction_cases=cases, arrival_count_histogram=histogram,
        arriving_cases_outside_work=outside, arriving_cases_outside_ROM=invalid,
        maximum_simultaneous_arrivals=1, raw_Age_words=1 << p.m,
        result="proved local uniqueness; window/direction factorization covers all raw Age words",
        consequence="outside-work arriving keys have inside false and instruction-independent outputs; I=0 is a total output completion",
        scope="local timing/addition certificate with unchanged mux-front gating; not physical restoration",
        global_reliability_established=False)
    (ROOT / "figs/robustness/SP12_front_certificate.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
