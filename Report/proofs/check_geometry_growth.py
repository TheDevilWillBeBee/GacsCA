#!/usr/bin/env python3
"""Finite and symbolic support for ROBUSTNESS §7's geometry-growth bound.

Checks whole-word dominance for arbitrary faulty words using actual Boolean
gates, local infection envelopes, and an admissible envelope packing example.
The unbounded-time proof and its limits are in ROBUSTNESS.md.
"""
from itertools import combinations
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from gacsca import candidates
from gacsca.netlist import Net, const_word, majority_word


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def threshold(words, count):
    result = 0
    for selected in combinations(words, count):
        term = selected[0]
        for word in selected[1:]:
            term &= word
        result |= term
    return result


def interval(a, b):
    return 0 if a > b else ((1 << (b - a + 1)) - 1) << a


def majority_certificates():
    checks = 0
    for width in (9, 16):
        patterns = (0, (1 << width) - 1,
                    sum(1 << bit for bit in range(0, width, 2)))
        for value in patterns:
            for bad in combinations(range(5), 2):
                net = Net()
                words = []
                for slot in range(5):
                    words.append([net.input(("bad", slot, bit)) for bit in range(width)]
                                 if slot in bad else const_word(value, width))
                default = [net.input(("default", bit)) for bit in range(width)]
                voted, exists = majority_word(net, words, default)
                # Literal constant nodes certify every assignment of all
                # two faulty words and the default, without enumeration.
                require(exists == 1 and voted == const_word(value, width),
                        ("whole-word majority", width, value, bad))
                checks += 1
    return checks


def local_check(width, noise):
    a, b = 24, 23 + width
    bad = interval(a, b)
    for offset in noise:
        bad |= 1 << (a + offset)
    left = [bad << j for j in range(1, 6)]
    right = [bad >> j for j in range(1, 6)]
    computed = threshold(left, 3) | threshold(right, 3)
    lcount = sum(-4 <= offset <= -1 for offset in set(noise))
    rcount = sum(width <= offset <= width + 3 for offset in set(noise))
    require(lcount <= 2 and rcount <= 2, "E0 density")
    wanted = interval(a - 3 - lcount, b + 3 + rcount)
    require(computed & ~wanted == 0, ("infection envelope", width, noise))


def packing_check():
    # A cycle of three adjacent-pair groups with time gaps 7,8,8. Their
    # closest sites are 24 apart. This attains 75/23 for the count envelope,
    # and is not a claim of attaining it in an actual repairing island.
    offsets, gaps = (1, 3, 2), (7, 8, 8)
    frontier = 100
    tick = 0
    events = []
    for index in range(31):
        point = frontier + offsets[index % 3]
        events.append((tick, (point, point + 1), frontier))
        if index < 30:
            delta = gaps[index % 3]
            frontier += 3*delta + 2
            tick += delta
    for old, new in combinations(events, 2):
        require(new[0] - old[0] >= 24 or new[1][0] - old[1][1] >= 24,
                ("packing separation", old, new))
    require(tick == 230 and frontier - 100 == 750, "packing cycle")
    require(Fraction(frontier - 100, tick) == Fraction(75, 23), "packing speed")
    return dict(events=len(events), cycles=10, elapsed_ticks=tick,
                envelope_displacement=frontier - 100,
                scope="sharp for the scalar count envelope, not an island lifetime")


def main():
    c = candidates.load("G17")
    require(c.digest() == "23a14aab4d3dc4fde5562cf3e26a4536b05456f84e65850fcb3bd95a104d8ceb",
            "candidate changed: re-audit")
    majority_checks = majority_certificates()
    local_checks = 0
    for width in range(1, 65):
        groups = [(x,) for x in range(-12, width + 12)]
        groups += [(x, x + 1) for x in range(-12, width + 11)]
        local_check(width, ())
        local_checks += 1
        for group in groups:
            local_check(width, group)
            local_checks += 1
        for g, h in combinations(groups, 2):
            if min(abs(x - y) for x in g for y in h) >= 24:
                local_check(width, g + h)
                local_checks += 1
    packing = packing_check()
    require(Fraction(75, 23) < 4, "growth below four")
    require(Fraction(3) + Fraction(6, 23) == Fraction(75, 23), "packing formula")
    # For (22,23) footprints the same proof gives 3+6/(22-1)=23/7.
    require(Fraction(3) + Fraction(6, 21) == Fraction(23, 7), "reduced spacing")
    receipt = dict(candidate="G17", **candidates.digests(c),
                   checker_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                   helpers_sha256=hashlib.sha256((ROOT / "gacsca/netlist.py").read_bytes()).hexdigest(),
                   result="symbolic and local support for the geometry growth theorem",
                   symbolic_majority_cases=majority_checks,
                   checked_interval_cases=local_checks, checked_widths=[1,64],
                   frontier_growth_rate="75/23", startup_allowance_per_front=2,
                   E0_space_time_separation=[24,24], packing_example=packing,
                   reduced_spacing=dict(separation=[22,23], rate="23/7"),
                   not_proved=["Flag1 generation or boundary crossing",
                               "damage-island erosion, lifetime or colony confinement",
                               "simulation-field recovery or all-time reliability"])
    out = ROOT / "figs/robustness/geometry_growth_certificate.json"
    out.write_text(json.dumps(receipt, indent=2)+"\n")
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()
