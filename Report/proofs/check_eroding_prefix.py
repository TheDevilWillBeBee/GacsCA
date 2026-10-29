#!/usr/bin/env python3
"""Boolean-envelope certificate for the conditional eroding-prefix lemma.

The proof and explicit Flag1/Workspace-source hypotheses are in ROBUSTNESS.
This does not certify that a damaged G17 hierarchy supplies those hypotheses.
"""
from fractions import Fraction
from itertools import combinations
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from gacsca import candidates


def interval(a, b):
    return 0 if a > b else ((1 << (b - a + 1)) - 1) << a


def threshold(words, count):
    result = 0
    for selected in combinations(words, count):
        term = selected[0]
        for word in selected[1:]:
            term &= word
        result |= term
    return result


def endpoint(B, noise, halo, phase):
    if phase:
        J = any(B - 3 <= x <= B for x in noise)
        K = any(B - 2 <= x <= B for x in halo)
        assert not (J and K)
        return B - 3 - 2*J - K
    blocked = any(B - 4 <= x <= B for x in noise + halo)
    return B + 1 - blocked


def next_halo(noise, Bnew):
    return (noise[-1],) if len(noise) == 2 and noise[-1] <= Bnew else ()


def local_check(B, noise, previous, phase):
    halo = (previous[-1],) if previous and previous[-1] <= B else ()
    if previous and noise:
        assert min(abs(x - y) for x in noise for y in previous) >= 24
    raw = interval(B + 1, B + 32)
    for x in noise + halo:
        raw |= 1 << x
    left = [raw << j for j in range(1, 6)]
    right = [raw >> j for j in range(1, 6)]
    # Missing right Address majority requires >=3 incorrect right inputs.
    periodic_source = threshold(right, 3) if phase else 0
    flag2 = periodic_source | threshold(left, 4) | (raw & threshold(left, 1))
    geometric_left, geometric_right = threshold(left, 3), threshold(right, 3)
    controlled = interval(B - 4, B + 1)
    geometric = ((geometric_left | geometric_right) & ~controlled)
    geometric |= (geometric_left | (flag2 & geometric_right)) & controlled
    Bnew = endpoint(B, noise, halo, phase)
    halo_new = next_halo(noise, Bnew)
    allowed = sum(1 << x for x in halo_new)
    prefix = interval(0, Bnew)
    assert not ((flag2 | geometric) & prefix & ~allowed), (B, noise, previous, phase, Bnew)


def main():
    c = candidates.load("G17")
    assert c.digest() == "23a14aab4d3dc4fde5562cf3e26a4536b05456f84e65850fcb3bd95a104d8ceb"
    truth_cases = 0
    for old in (0, 1):
        for left in range(32):
            for inside in range(32):
                total, counted = left.bit_count(), (left & inside).bit_count()
                for flag1 in (0, 1):
                    for source in (0, 1):
                        if old:
                            actual = bool(source or (total >= 1 if flag1 else counted >= 2))
                        else:
                            actual = bool(source or counted >= 4 or (flag1 and total >= 4))
                        upper = bool(source or total >= 4 or (old and total >= 1))
                        assert actual <= upper
                        truth_cases += 1
    B = 64
    groups = [()] + [(x,) for x in range(B - 24, B + 13)]
    groups += [(x, x + 1) for x in range(B - 24, B + 12)]
    previous_groups = [()] + [(x, x + 1) for x in range(B - 24, B + 1)]
    local_cases = 0
    for noise in groups:
        for previous in previous_groups:
            if noise and previous and min(abs(x - y) for x in noise for y in previous) < 24:
                continue
            for phase in (False, True):
                local_check(B, noise, previous, phase)
                local_cases += 1
    charge_cases = 0
    for noise in groups:
        for clock in range(16):
            B1 = endpoint(B, noise, (), clock == 15)
            H1 = next_halo(noise, B1)
            B2 = endpoint(B1, (), H1, (clock + 1) % 16 == 15)
            baseline = (B - 3 if clock == 15 else B + 1)
            baseline += -3 if (clock + 1) % 16 == 15 else 1
            loss = baseline - B2
            assert 0 <= loss <= 2
            if not any(B - 7 <= x <= B for x in noise):
                assert loss == 0
            charge_cases += 1
    # Consecutive affecting groups have no intervening extra loss; the
    # first can charge at most two. Their offsets from B are -7,...,0.
    packing_cases = 0
    for duration in range(1, 17):
        for clock in range(16):
            phases = sum((clock + t) % 16 == 15 for t in range(duration))
            for loss in range(3):
                displacement = duration - 4*phases - loss
                assert -5 <= displacement <= duration
                assert abs(displacement) + 7 < 24
                packing_cases += 1
    rate = Fraction(1) - Fraction(4, 16) - Fraction(2, 17)
    assert rate == Fraction(43, 68) > Fraction(1, 2)
    receipt = dict(candidate="G17", **candidates.digests(c),
                   checker_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                   maintenance_sha256=hashlib.sha256((ROOT / "gacsca/maintenance.py").read_bytes()).hexdigest(),
                   result="finite support for the proved conditional eroding-prefix lemma",
                   Flag2_upper_truth_cases=truth_cases, local_prefix_cases=local_cases,
                   two_update_noise_charge_cases=charge_cases, packing_cases=packing_cases,
                   source_period=16, affecting_error_event_gap=17,
                   maximum_extra_loss_per_E0_group=2,
                   minimum_prefix_speed=str(rate), startup_allowance=6,
                   temporary_halo="right endpoint of an adjacent pair from the previous tick",
                   hypotheses=["computed Flag1=1 in [B_t-4,B_t+1]",
                               "no computed Workspace.Flag2 source at x<=B_t+1",
                               "initial canonical Address/common Age and Flag2=0 on x<=B_0, apart from N_0",
                               "mutually (24,24)-separated singleton/adjacent-pair overwrites"],
                   not_proved=["the island supplies the Flag1/source hypotheses",
                               "apparent-boundary stall deadline",
                               "full G17 level-1 repair or all-time reliability"])
    output = ROOT / "figs/robustness/eroding_prefix_certificate.json"
    output.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()
