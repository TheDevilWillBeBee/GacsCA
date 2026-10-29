#!/usr/bin/env python3
"""Finite checks supporting the all-time conditional flag-pulse proofs.

These are exhaustive Boolean/local interval checks, not noisy simulations.
The arbitrary-time and separation arguments are given in ROBUSTNESS §10.
No transition rule or candidate is changed.
"""
from itertools import combinations
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from gacsca import candidates, maintenance
from gacsca.netlist import Net, Compiled, const_word


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def threshold(words, count):
    """Bitwise Boolean threshold; each integer bit is an independent site."""
    out = 0
    for chosen in combinations(words, count):
        result = chosen[0]
        for word in chosen[1:]:
            result &= word
        out |= result
    return out


def flag2(word):
    left = [word << j for j in range(1, 6)]
    return threshold(left, 4) | (word & threshold(left, 1))


def flag1(word):
    right = [word >> j for j in range(1, 6)]
    return threshold(right, 3) | (word & threshold(right, 2))


def interval(a, b):
    return 0 if b < a else ((1 << (b - a + 1)) - 1) << a


def interval_check(width, holes):
    a, b = 12, 11 + width
    word = interval(a, b)
    for hole in holes:
        word &= ~(1 << (a + hole))
    # Definitions use only faults actually in each boundary window.
    l2 = any(0 <= hole <= 3 for hole in holes)
    r2 = any(width - 5 <= hole <= width - 1 for hole in holes)
    lo2, hi2 = a + 1 + 4 * l2, b + 2 - 2 * r2
    wanted2 = interval(lo2, hi2)
    require(flag2(word) & wanted2 == wanted2, ("Flag2 interval", width, holes))
    l1 = any(0 <= hole <= 2 for hole in holes)
    r1 = any(width - 3 <= hole <= width - 1 for hole in holes)
    lo1, hi1 = a - 3 + 2 * l1, b - 2 - 2 * r1
    wanted1 = interval(lo1, hi1)
    require(flag1(word) & wanted1 == wanted1, ("Flag1 interval", width, holes))


def actual_maintenance_check(p, field, address=200, uniform_invalid=False):
    """Check independent count formulas against the actual generated gates.

    Fixed geometry specializes the main rule, but all six relevant raw flag
    bits and the extra source bit remain arbitrary. Several Address cases
    test actual colony ends, unused words, and nonexistent right majorities.
    """
    net = Net()
    old = net.input(("old",))
    side = [net.input(("side", j)) for j in range(1, 6)]
    source = net.input(("source",))
    in_colony = [j for j in range(-5, 6) if 0 <= address + j < p.Q]
    commanded = set(in_colony[:3])
    cells = {}
    for j in range(-5, 6):
        if uniform_invalid:
            a = address
            age = [source] * 4 + [0] * (p.m - 4)
        else:
            # Exact raw linear values for the two noncanonical address cases.
            a = (address + j) % p.Q if address < p.Q else address + j
            age = const_word(p.age_code(2000), p.m)
        f1 = (old if j == 0 else side[j - 1] if j > 0 else 0) if field == "f1" else 0
        f2 = (old if j == 0 else side[-j - 1] if j < 0 else 0) if field == "f2" else 0
        if uniform_invalid:
            wf1 = wf2 = 0
        else:
            wf1 = ((1 if field == "f2" else source) if j in commanded else 0)
            wf2 = source if field == "f2" and j in commanded else 0
        cells[j] = dict(addr=const_word(a, p.k), age=age, f1=f1, f2=f2, wf1=wf1, wf2=wf2)
    # For noncanonical addresses the inside-left sites are all present,
    # despite an empty [address-5,address+5] intersection with [0,Q).
    if field == "f2" and not uniform_invalid and address >= p.Q:
        for j in (-5, -4, -3):
            cells[j]["wf1"] = 1
            cells[j]["wf2"] = source
    out = maintenance.build(net, cells, p.k, p.m, Q=p.Q, nb=p.nb,
                            radix=p.R, pos_bits=p.PB)
    net.set_output(("flag",), out[field])
    net.set_output(("computed_f1",), out["f1"])
    compiled = Compiled(net)
    require(len(compiled.inputs) == 7, "seven independent flag variables")
    for assignment in range(128):
        values = {name: (assignment >> i) & 1 for i, name in enumerate(compiled.inputs)}
        actual = compiled.evaluate_scalar(values)
        count = sum(values["side", j] for j in range(1, 6))
        reference = (values["source",] or count >= (4 if field == "f2" else 3)
                     or (values["old",] and count >= (1 if field == "f2" else 2)))
        require(actual["flag",] == bool(reference), ("actual maintenance", field, address, assignment))
        if field == "f2":
            require(actual["computed_f1",] == 1, "Flag2 precondition was not established")
    return 128


def main():
    c = candidates.load("G17")
    require(c.digest() == "23a14aab4d3dc4fde5562cf3e26a4536b05456f84e65850fcb3bd95a104d8ceb",
            "candidate changed: re-audit")
    f2_checks = 0
    for old in (0, 1):
        for left in range(32):
            total = left.bit_count()
            for inside in range(32):
                counted = (left & inside).bit_count()
                for source in (0, 1):
                    # The actual candidate-B fragment when computed Flag1=1.
                    on = counted >= 4 or total >= 4 or source
                    erase = total == 0
                    actual = bool(source or not erase) if old else bool(on)
                    reference = bool(source or total >= 4 or (old and total >= 1))
                    require(actual == reference, ("Flag2 truth table", old, left, inside, source))
                    # With Flag1=0, G17 uses the inside-only threshold 2.
                    without_f1 = bool(source or counted >= 2) if old else bool(source or counted >= 4)
                    require(actual >= without_f1, "Flag1 raising must not reduce Flag2")
                    f2_checks += 1
    actual_f1_checks = actual_maintenance_check(c.p, "f1")
    actual_f2_checks = sum(actual_maintenance_check(c.p, "f2", address)
                          for address in (0, 1, 2, 3, 4, 5, 200, 378, 379, 380, 381, 382, 383, 388, 500))
    actual_f2_checks += actual_maintenance_check(c.p, "f2", 500, uniform_invalid=True)

    local_checks = 0
    for width in range(10, 129):
        groups = [(x,) for x in range(-2, width + 2)]
        groups += [(x, x + 1) for x in range(-2, width + 1)]
        interval_check(width, ())
        local_checks += 1
        for group in groups:
            interval_check(width, group)
            local_checks += 1
        # Multiple widely separated groups test concurrent interior holes and
        # faults on different edges. The proof covers any number of groups.
        for left_group, right_group in combinations(groups, 2):
            if min(abs(x - y) for x in left_group for y in right_group) >= 24:
                interval_check(width, left_group + right_group)
                local_checks += 1
    # The minimum event gaps follow solely from pair separation and these
    # upper bounds on the distance between successive affecting faults.
    for delta in range(1, 17):
        require(delta + 7 < 24 and delta < 24, "Flag2 trailing event gap")
    for delta in range(1, 11):
        require(2 * delta + 2 < 24 and delta < 24, "Flag2 leading event gap")
    for delta in range(1, 8):
        require(3 * delta < 24 and delta < 24, "Flag1 leading event gap")
    for delta in range(1, 10):
        require(2 * delta + 4 < 24 and delta < 24, "Flag1 trailing event gap")
    receipt = dict(
        candidate="G17", **candidates.digests(c),
        checker_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        maintenance_sha256=hashlib.sha256((ROOT / "gacsca/maintenance.py").read_bytes()).hexdigest(),
        result="finite support checks for the conditional proofs in ROBUSTNESS §10",
        hypotheses={
            "Flag2": "computed Flag1 is 1 on the required output interval at each tick",
            "Flag1": "the five right neighbors are inside the computed colony at each required output",
            "noise": "distinct singleton/adjacent-pair groups are (24,24)-separated"},
        not_proved=["trickle-down establishes/maintains those hypotheses",
                    "pulse supply and synchronization across partial colonies",
                    "damage-island edge retreat or all-time memory"],
        flag2_truth_assignments=f2_checks, flag1_truth_assignments=actual_f1_checks,
        actual_maintenance_flag1_assignments=actual_f1_checks,
        actual_maintenance_flag2_assignments=actual_f2_checks,
        checked_interval_cases=local_checks, checked_widths=[10, 128],
        flag2=dict(initial_width_at_least=16, trailing_event_gap=17, leading_event_gap=11,
                   leading_minimum_speed="20/11", trailing_maximum_speed="21/17",
                   width_growth_lower_bound="109/187", width_startup_allowance=6),
        flag1=dict(initial_width_at_least=14, leading_event_gap=8, trailing_event_gap=10,
                   leading_minimum_speed="11/4", trailing_maximum_speed="11/5",
                   width_growth_lower_bound="11/20", width_startup_allowance=4))
    path = ROOT / "figs/robustness/flag_pulse_certificate.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()
