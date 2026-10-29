#!/usr/bin/env python3
"""Finite support and class examples for the 141-site geometric seed lemma.

The universal candidate-pair separation and trajectory induction are proved
in ROBUSTNESS §7. These examples are not a repair or reliability campaign.
"""
from itertools import combinations
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from gacsca import candidates
from gacsca.gray_errors import classify


def require(condition, message):
    if not condition:
        raise RuntimeError(message)


def linked(a, b):
    return abs(a[0]-b[0]) < 24 and abs(a[1]-b[1]) < 24


def certify_example(c, points):
    result = classify(points, Q=c.p.Q, U=c.p.U, sep=16)
    require(result["level1"], ("not a real level-1 example", result))
    dangerous = []
    for triple in combinations(points, 3):
        xs, ts = zip(*triple)
        if len(set(ts)) == 1 and max(xs)-min(xs) <= 4:
            dangerous.append(triple)
    require(dangerous, "no geometry-dangerous triple")
    tau = min(triple[0][1] for triple in dangerous)
    triple = next(triple for triple in dangerous if triple[0][1] == tau)
    pair = min(combinations(triple, 2), key=lambda pair: abs(pair[0][0]-pair[1][0]))
    p, q = sorted(point[0] for point in pair)
    require(1 <= q-p <= 2, "closest pair")
    interval = p-15, q+15
    outside = {point for point in points if not interval[0] <= point[0] <= interval[1]}
    future = {point for point in points if point[1] >= tau+16}
    for collection in (outside, future):
        require(all(not linked(a,b) for a,b in combinations(collection,2)), "tail separation")
    return dict(points=sorted(points), class_result=result,
                first_geometry_dangerous_tick=tau, closest_pair=sorted(pair),
                spatial_forcing_interval=list(interval),
                exterior_points=sorted(outside), future_points=sorted(future),
                exterior_spacing_checked=True, future_spacing_checked=True)


def main():
    c = candidates.load("G17")
    require(c.digest() == "23a14aab4d3dc4fde5562cf3e26a4536b05456f84e65850fcb3bd95a104d8ceb",
            "candidate changed: re-audit")
    triples = list(combinations(range(5),3))
    for triple in triples:
        gap = min(b-a for a,b in combinations(triple,2))
        require(gap <= 2 and gap+31 <= 33, ("forcing width",triple))
    examples = [
        certify_example(c, {(0,0),(1,0),(2,0),(-23,0),(25,0)}),
        certify_example(c, {(x,t) for x in range(3) for t in (0,15)} | {(2,38)})]
    for example in examples:
        require(example["class_result"]["level0"] == 0,
                "the examples should show tails are not original E0")
    require(examples[1]["future_points"] == [(2,38)], "late original error")
    events = 1 + (3*16)//23
    expansion = 3*16 + 2*events
    require((events,expansion,33+2*expansion) == (3,54,141), "seed arithmetic")
    receipt = dict(candidate="G17",**candidates.digests(c),
                   checker_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                   classifier_sha256=hashlib.sha256((ROOT/"gacsca/gray_errors.py").read_bytes()).hexdigest(),
                   result="finite support for the proved geometric seed reduction",
                   closest_pair_triples_checked=len(triples), fixed_forcing_width_at_most=33,
                   updates_to_lower_noise_pattern=16, endpoint_expansion_at_most=54,
                   geometric_seed_width_at_most=141, examples=examples,
                   not_proved=["seed erosion or bounded lifetime", "all simulation-field recovery",
                               "effective upper error process", "all-time reliability"])
    out=ROOT/"figs/robustness/geometry_seed_certificate.json"
    out.write_text(json.dumps(receipt,indent=2)+"\n")
    print(json.dumps(receipt,indent=2))


if __name__=="__main__":
    main()
