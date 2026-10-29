#!/usr/bin/env python3
"""Local certificate for source-free Flag2 clearing on aligned geometry.

The explicit source/Flag1 hypotheses and all-duration proof are in
ROBUSTNESS §10. This certificate is not a damaged-colony repair theorem.
"""
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from gacsca import candidates, maintenance
from gacsca.netlist import Net, Compiled, const_word


def main():
    c = candidates.load("G17")
    assert c.digest() == "23a14aab4d3dc4fde5562cf3e26a4536b05456f84e65850fcb3bd95a104d8ceb"
    actual_cases = 0
    for address in (0, 1, 2, 3, 4, 5, 200, 383):
        net = Net()
        flag = {j: net.input(("f2", j)) for j in range(-5, 1)}
        cells = {j: dict(addr=const_word((address + j) % c.p.Q, c.p.k),
                         age=const_word(c.p.age_code(2000), c.p.m),
                         f1=0, f2=flag[j] if j <= 0 else 0, wf1=0, wf2=0)
                 for j in range(-5, 6)}
        out = maintenance.build(net, cells, c.p.k, c.p.m, Q=c.p.Q,
                                nb=c.p.nb, radix=c.p.R, pos_bits=c.p.PB)
        net.set_output(("f2",), out["f2"])
        comp = Compiled(net)
        for bits in range(64):
            values = {("f2", j): (bits >> (j + 5)) & 1 for j in range(-5, 1)}
            counted = sum(values["f2", j] for j in range(-5, 0) if address + j >= 0)
            expected = counted >= 4 or (values["f2", 0] and counted >= 2)
            assert comp.evaluate_scalar(values)["f2",] == bool(expected)
            actual_cases += 1
    local_cases = 0
    for B in range(1, 32):
        groups = [()] + [(x,) for x in range(-5, B + 8)]
        groups += [(x, x + 1) for x in range(-5, B + 7)]
        for group in groups:
            # Zero prefix punctured by the current group; all other cells
            # inside the colony set to one, the worst monotone input.
            def old(x):
                return int(x in group or x > B) if x >= 0 else 0
            count = sum(B - 4 <= x <= B for x in group)
            Bnew = B + 2 - count
            for x in range(Bnew + 1):
                left = sum(old(x - j) for j in range(1, 6))
                actual = left >= 4 or (old(x) and left >= 2)
                assert not actual, (B, group, x, Bnew)
                local_cases += 1
    # Every possible pair of groups relevant at the advancing edge can
    # be tested independently of the local flag values. For gaps d<=10,
    # previous extra loss r is 1 or 2 and offsets belong to -4,...,0.
    packing_cases = 0
    for duration in range(1, 11):
        for prior_loss in (1, 2):
            displacement = 2*duration - prior_loss
            for a in range(-4, 1):
                for b in range(-4, 1):
                    assert abs(displacement + b - a) < 24
                    packing_cases += 1
    ceil = lambda n, d: (n + d - 1) // d
    clearing = min(t for t in range(1000) if 1 + 2*t - 2*ceil(t, 11) >= c.p.Q - 1)
    assert clearing == 211
    assert 1 + 2*clearing - 2*ceil(clearing, 11) == 383
    receipt = dict(candidate="G17", **candidates.digests(c),
                   checker_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                   maintenance_sha256=hashlib.sha256((ROOT / "gacsca/maintenance.py").read_bytes()).hexdigest(),
                   result="finite local certificate for proved conditional source-free Flag2 clearing",
                   actual_boundary_assignments=actual_cases,
                   local_output_cases=local_cases, event_packing_cases=packing_cases,
                   event_gap=11, minimum_prefix_speed="20/11",
                   initial_two_site_reset_updates=1, subsequent_erasure_updates=clearing,
                   total_computed_Flag2_clearing_updates=clearing + 1,
                   hypotheses=["aligned canonical Address/common Age apart from current E0",
                               "computed Flag1=0 and computed D3=D4=0 throughout",
                               "mutually (24,24)-separated singleton/adjacent-pair overwrites"],
                   not_proved=["quieting on damaged geometry", "reliability"])
    path = ROOT / "figs/robustness/flag2_quiet_certificate.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()
