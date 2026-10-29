#!/usr/bin/env python3
"""Actual-gate and mask certificates for the conditional left-edge repair lemma."""
from itertools import combinations
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
import numpy as np
from gacsca import candidates, maintenance
from gacsca.netlist import Net, const_word


def age_next(p, age):
    pos, block = age & ((1 << p.PB) - 1), age >> p.PB
    return (((0 if block == p.nb - 1 else (block + 1) % (1 << (p.m - p.PB))) << p.PB)
            if pos == p.R - 1 else (block << p.PB) | ((pos + 1) % (1 << p.PB)))


def symbolic(p, A, V, alpha, beta, good, no_right_majority=False):
    n = Net()
    cells = {}
    def free_word(j, field, width):
        return [n.input((j, field, bit)) for bit in range(width)]
    for j in range(-5, 6):
        if j < 0 and -j in good:
            addr, age = const_word((A + j) % p.Q, p.k), const_word(alpha, p.m)
        elif j > 0:
            addr = const_word(500 if no_right_majority else
                              ((V + j) % p.Q if V < p.Q else V + j), p.k)
            age = (free_word(j, "age", p.m) if no_right_majority
                   else const_word(beta, p.m))
        else:
            addr, age = free_word(j, "addr", p.k), free_word(j, "age", p.m)
        cells[j] = dict(addr=addr, age=age, f1=n.input((j, "f1")),
                        wf1=n.input((j, "wf1")),
                        f2=n.input((j, "f2")) if no_right_majority else 0,
                        wf2=n.input((j, "wf2")) if no_right_majority else 0)
    out = maintenance.build(n, cells, p.k, p.m, Q=p.Q,
                            nb=p.nb, radix=p.R, pos_bits=p.PB)
    assert out["addr"] == const_word(A, p.k), (A, V, alpha, beta, good, "addr")
    assert out["age_now"] == const_word(alpha, p.m), (A, V, alpha, beta, good, "age")
    assert out["age"] == const_word(age_next(p, alpha), p.m)
    assert out["f1"] == 1
    if not no_right_majority:
        assert out["f2"] == 0


def sharp_case(p, V, fault_pair):
    n, A = Net(), 100
    alpha, beta = p.age_code(2000), p.age_code(2001)
    cells = {}
    for j in range(-5, 6):
        wrong = j >= 0 or (fault_pair and j in (-1, -2))
        cells[j] = dict(addr=const_word((V + j if wrong else A + j) % p.Q, p.k),
                        age=const_word(beta if wrong else alpha, p.m),
                        f1=0, f2=0, wf1=0, wf2=0)
    out = maintenance.build(n, cells, p.k, p.m, Q=p.Q,
                            nb=p.nb, radix=p.R, pos_bits=p.PB)
    assert out["addr"] == const_word(V, p.k)
    assert out["age_now"] == const_word(beta, p.m)
    assert out["f1"] == out["f2"] == 0
    return dict(right_vote=V, reference_address=A, left_fault_sites=[-2, -1] if fault_pair else [],
                computed_Flag1=0, computed_Flag2=0, incorrect_vote_selected=True)


def main():
    cand = candidates.load("G17")
    assert cand.digest() == "23a14aab4d3dc4fde5562cf3e26a4536b05456f84e65850fcb3bd95a104d8ceb"
    p = cand.p
    A = np.arange(p.Q)[:, None]
    V = np.arange(1 << p.k)[None, :]
    wrong_phase = V % p.Q != A
    mismatch = []
    for d in range(1, 6):
        expected = V + p.Q - d
        expected = np.where(expected >= p.Q, expected - p.Q, expected)
        mismatch.append((V >= d) & (expected != (A - d) % p.Q))
    mask_cases, symbolic_cases = 0, 0
    good_sets = list(combinations(range(1, 6), 3))
    for good in good_sets:
        count = sum(mismatch[d - 1] for d in good)
        assert np.all(count[(V >= 5) & wrong_phase] >= 3)
        mask_cases += p.Q * (1 << p.k)
    for reference in (0, 5, 100, 383):
        for alpha in (0, p.age_code(2000), 65535):
            for good in good_sets:
                symbolic(p, reference, None, alpha, None, good, no_right_majority=True)
                symbolic_cases += 1
                if reference >= 5:
                    symbolic(p, reference, reference, alpha, alpha ^ 1, good)
                    symbolic_cases += 1
                for right in (5, 127, 383, 384, 500, 506):
                    if right % p.Q != reference:
                        symbolic(p, reference, right, alpha, alpha, good)
                        symbolic_cases += 1
    sharp = [sharp_case(p, 2, False), sharp_case(p, 4, True)]
    receipt = dict(candidate="G17", **candidates.digests(cand),
                   checker_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                   helpers_sha256=hashlib.sha256((ROOT / "gacsca/netlist.py").read_bytes()).hexdigest(),
                   maintenance_sha256=hashlib.sha256((ROOT / "gacsca/maintenance.py").read_bytes()).hexdigest(),
                   result="finite/symbolic support for the proved conditional left-front repair lemma",
                   exact_mask_cases=mask_cases, symbolic_all_assignment_cases=symbolic_cases,
                   sharp_snapshot_examples=sharp,
                   hypotheses=["at least three of five left neighbors have correct canonical Address/common Age",
                               "computed Flag2 is zero when a right Address majority exists"],
                   exceptional_right_Address_votes=[0, 1, 2, 3, 4],
                   noise_free_exceptional_votes=[0, 1, 2],
                   not_proved=["control of Flag2 at the moving frontier",
                               "escape from apparent-colony boundary exceptions",
                               "island lifetime, all-field recovery or reliability"])
    output = ROOT / "figs/robustness/left_boundary_certificate.json"
    output.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()
