#!/usr/bin/env python3
"""Finite support for the conditional intact-colony startup proof.

The arbitrary-duration and arbitrary-width proofs are in ROBUSTNESS §10.
This checks local Boolean identities, interval steps and G17 arithmetic.
It does not assert damaged-colony command delivery or reliability.
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


def require(test, message):
    if not test:
        raise RuntimeError(message)


def threshold(words, count):
    out = 0
    for chosen in combinations(words, count):
        product = chosen[0]
        for word in chosen[1:]:
            product &= word
        out |= product
    return out


def interval(a, b):
    return 0 if b < a else ((1 << (b - a + 1)) - 1) << a


def t20(word):
    left = [word << j for j in range(1, 6)]
    return threshold(left, 4) | (word & threshold(left, 2))


def clear_flag1(zeros):
    right = [zeros >> j for j in range(1, 6)]
    return threshold(right, 4) | (zeros & threshold(right, 3))


def flag1(word):
    right = [word >> j for j in range(1, 6)]
    return threshold(right, 3) | (word & threshold(right, 2))


def check_step(width, holes):
    a, b = 12, 11 + width
    word = interval(a, b)
    for hole in holes:
        word &= ~(1 << (a + hole))
    left_event = any(0 <= hole <= 3 for hole in holes)
    right_event = any(width - 5 <= hole <= width - 1 for hole in holes)
    expected = interval(a + 2 + 3 * left_event, b + 2 - 2 * right_event)
    require(t20(word) & expected == expected, ("unanchored Flag2", width, holes))
    # Finite right tail: discard the last five outputs, whose inputs would
    # require the unspecified extension. The proof uses an infinite tail.
    expected = interval(a - 2 + 2 * left_event, b - 5)
    require(clear_flag1(word) & expected == expected, ("clearing Flag1", width, holes))
    expected = interval(a, b + 2 - 2 * right_event)
    source = interval(a, a + 5)
    require((t20(word) | source) & expected == expected, ("anchored Flag2", width, holes))
    lead_event = any(0 <= hole <= 2 for hole in holes)
    expected = interval(a - 3 + 2 * lead_event, b)
    source = interval(b - 5, b)
    require((flag1(word) | source) & expected == expected, ("anchored Flag1", width, holes))


def actual_flag1_boundary(p, address):
    net = Net()
    raw = {j: net.input(("f1", j)) for j in range(6)}
    cells = {}
    for j in range(-5, 6):
        cells[j] = dict(addr=const_word((address + j) % p.Q, p.k),
                        age=const_word(p.age_code(2000), p.m),
                        f1=raw[j] if j >= 0 else 0, f2=0, wf1=0, wf2=0)
    out = maintenance.build(net, cells, p.k, p.m, Q=p.Q,
                            nb=p.nb, radix=p.R, pos_bits=p.PB)
    net.set_output(("f1",), out["f1"])
    compiled = Compiled(net)
    require(len(compiled.inputs) == 6, "six flag variables")
    for assignment in range(64):
        values = {name: (assignment >> i) & 1 for i, name in enumerate(compiled.inputs)}
        counted = sum(values["f1", j] for j in range(1, 6)
                      if address + j < p.Q)
        expected = counted >= 3 or (values["f1", 0] and counted >= 2)
        require(compiled.evaluate_scalar(values)["f1",] == bool(expected),
                ("actual boundary", address, assignment))
    return 64


def main():
    c = candidates.load("G17")
    require(c.digest() == "23a14aab4d3dc4fde5562cf3e26a4536b05456f84e65850fcb3bd95a104d8ceb",
            "candidate changed: re-audit")
    actual_checks = sum(actual_flag1_boundary(c.p, a)
                        for a in (200, 379, 380, 381, 382, 383))
    dual_checks = 0
    for old in (0, 1):
        for side in range(32):
            ones = side.bit_count()
            zeros = 5 - ones
            f1 = ones >= 3 or (old and ones >= 2)
            clear = zeros >= 4 or ((1 - old) and zeros >= 3)
            require(bool(clear) == (not f1), ("dual", old, side))
            dual_checks += 1
    local_checks = 0
    for width in range(6, 65):
        groups = [(x,) for x in range(-2, width + 2)]
        groups += [(x, x + 1) for x in range(-2, width + 1)]
        check_step(width, ())
        local_checks += 1
        for group in groups:
            check_step(width, group)
            local_checks += 1
        for g, h in combinations(groups, 2):
            if min(abs(x - y) for x in g for y in h) >= 24:
                check_step(width, g + h)
                local_checks += 1
    require(all(2 * d + 1 < 24 for d in range(1, 12)), "clearing event gap 12")
    require(all(2 * d + 6 < 24 for d in range(1, 9)), "T20 trailing event gap 9")
    require(all(2 * d + 2 < 24 for d in range(1, 11)), "Flag2 leading event gap 11")
    require(all(3 * d < 24 for d in range(1, 8)), "anchored Flag1 event gap 8")
    ceil = lambda n, d: (n + d - 1) // d
    clearing_steps = min(t for t in range(1000)
                         if c.p.Q - 2*t + 2*ceil(t, 12) <= 0)
    require(clearing_steps == 210, "clearing arithmetic")
    require(c.p.Q - 10 - 5*(64 - 2) > 4, "first five quiet through tick 64")
    f2_b65 = 5 + 2*63 - 2*ceil(63, 11)
    require(f2_b65 == 119, "Flag2 lower interval at tick 65")
    require(c.p.Q - 6 - 3*138 + 2*ceil(138, 8) <= 0,
            "Flag1 covers colony by tick 140")
    f2_a140 = 2*75 + 3*ceil(75, 9)
    f2_b140 = f2_b65 + 2*75 - 2*ceil(75, 11)
    require((f2_a140, f2_b140) == (177, 255), "Flag2 lower interval at tick 140")
    require(f2_b140 - f2_a140 + 1 == 79, "surviving width")
    # The recurrences are valid throughout this finite transition interval.
    for t in range(76):
        require(120 - 3*ceil(t, 9) - 2*ceil(t, 11) >= 79, "interval bootstrap")
    receipt = dict(
        candidate="G17", **candidates.digests(c),
        checker_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        maintenance_sha256=hashlib.sha256((ROOT / "gacsca/maintenance.py").read_bytes()).hexdigest(),
        result="finite support for conditional intact-colony startup proofs",
        actual_flag1_boundary_assignments=actual_checks, dual_assignments=dual_checks,
        checked_interval_cases=local_checks, checked_widths=[6, 64],
        arbitrary_flag1_clearing=dict(event_gap=12, erasure_updates=210,
                                     include_initial_Wf1_reset_and_next_computed_flag=212),
        quiet_start_both_commands=dict(first_five_quiet_through_tick=64,
                                      flag2_interval_tick65=[0, 119],
                                      computed_flag1_everywhere_from_tick=140,
                                      flag2_interval_tick140=[177, 255],
                                      flag2_width_tick140=79),
        not_proved=["faulty command installation", "damaged/partial-colony startup",
                    "cross-boundary island retreat", "all-time reliability"])
    path = ROOT / "figs/robustness/flag_startup_certificate.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()
