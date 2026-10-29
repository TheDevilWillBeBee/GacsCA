#!/usr/bin/env python3
"""Local infection certificate for ROBUSTNESS's protected clock strip.

All raw Age words are covered by whole-word majority dominance. The
unbounded induction, hypotheses and error-group packing are in the audit.
"""
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from gacsca import candidates


def interval(a, b):
    return 0 if a > b else ((1 << (b - a + 1)) - 1) << a


def threshold3(bits):
    total = 0
    for i in range(5):
        for j in range(i + 1, 5):
            for k in range(j + 1, 5):
                total |= bits[i] & bits[j] & bits[k]
    return total


def check(width, current, old):
    a, b = 32, 31 + width
    # Model both exterior regions as arbitrary. M has at most the two
    # sites b-4,b-3; its maximal version suffices by monotonicity.
    bad = interval(0, a - 1) | interval(b + 1, b + 16)
    if old is not None:
        bad |= interval(b - 4, b - 3)
    for x in current:
        bad |= 1 << x
    left = threshold3([bad << j for j in range(1, 6)])
    right = threshold3([bad >> j for j in range(1, 6)])
    # All cells except the last three can select either Age vote. No
    # right Address majority in the last three forces the left vote there.
    tail = interval(b - 2, b)
    computed = left | (right & ~tail)
    edge_count = sum(a <= x <= a + 3 for x in current)
    anew = a + 3 + edge_count
    if old is not None:
        assert not current or min(abs(x - y) for x in current for y in old) >= 24
        Mnew = 0
    else:
        Mnew = interval(b - 4, b - 3) if any(b - 3 <= x <= b for x in current) else 0
    forbidden = interval(anew, b) & ~Mnew
    assert not (computed & forbidden), (width, current, old, anew)
    assert not (computed & tail), ("computed clock tail", width, current, old)


def main():
    cand = candidates.load("G17")
    assert cand.digest() == "23a14aab4d3dc4fde5562cf3e26a4536b05456f84e65850fcb3bd95a104d8ceb"
    checks = 0
    for width in (6, 7):
        check(width, (), None)
        checks += 1
    for width in range(8, 129):
        a, b = 32, 31 + width
        currents = [()]
        currents += [(x,) for x in range(a - 12, b + 13)]
        currents += [(x, x + 1) for x in range(a - 12, b + 12)]
        old_groups = [(x,) for x in range(b - 3, b + 1)]
        old_groups += [(x, x + 1) for x in range(b - 4, b + 1)]
        for current in currents:
            check(width, current, None)
            checks += 1
            for old in old_groups:
                if not current or min(abs(x - y) for x in current for y in old) >= 24:
                    check(width, current, old)
                    checks += 1
    def edge_bound(T):
        return 3*T + 2*(1 + (3*T)//23) if T else 0
    for duration, width in ((16, 57), (32, 111)):
        assert width - edge_bound(duration - 1) >= 8
        assert all(width - edge_bound(t) >= 8 for t in range(duration))
    assert 51 - 3*15 == 6
    for phase in range(16):
        source_steps = [s for s in range(1, 33) if (phase + s - 1) % 16 == 15]
        assert len(source_steps) == 2 and source_steps[1] - source_steps[0] == 16
        assert source_steps[0] <= 16
    receipt = dict(candidate="G17", **candidates.digests(cand),
                   checker_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                   result="local support for the proved conditional synchronized clock-source lemma",
                   local_interval_cases=checks, checked_widths=[8, 128],
                   noise_free_clock_strip_width=51,
                   left_front_rate=str(Fraction(75, 23)),
                   boundary_indirect_bad_sites=[-4, -3],
                   boundary_age_hypothesis="last three cells have no computed right Address majority",
                   simultaneous_computed_Flag2_source={"initial_clock_strip_width": 57,
                                                        "within_updates": 16, "cells": 3,
                                                        "stored_ones_at_source_at_least": 1},
                   clean_stored_Flag2_source={"initial_clock_strip_width": 111,
                                              "within_updates": 32, "cells": 3},
                   not_proved=["clock-strip invariant in a damaged physical simulation",
                               "command installation and trickle-down across partial colonies",
                               "island erosion or reliability"])
    output = ROOT / "figs/robustness/clock_strip_certificate.json"
    output.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()
