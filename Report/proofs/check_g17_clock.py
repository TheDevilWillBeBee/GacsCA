#!/usr/bin/env python3
"""Exhaustive certificate for G17's 16-bit packed clock on unused words.

This proves eventual legality and absence of newly created clock phases,
not repair of a wrong phase or noisy reliability.
The ancestry and probability arguments are in ROBUSTNESS §7.
"""
from collections import deque
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
import numpy as np
from gacsca import candidates
from gacsca.netlist import Net, Compiled, mixed_age_increment


def main():
    c = candidates.load("G17")
    p = c.p
    if c.digest() != "23a14aab4d3dc4fde5562cf3e26a4536b05456f84e65850fcb3bd95a104d8ceb":
        raise RuntimeError("candidate changed: re-audit")
    words = np.arange(1 << p.m, dtype=np.uint32)
    position_mask = (1 << p.PB) - 1
    block_mask = (1 << (p.m - p.PB)) - 1
    pos, block = words & position_mask, words >> p.PB
    next_pos = np.where(pos == p.R - 1, 0, (pos + 1) & position_mask)
    next_block = np.where(pos == p.R - 1,
                          np.where(block == p.nb - 1, 0, (block + 1) & block_mask), block)
    reference = (next_block << p.PB) | next_pos
    legal = (pos < p.R) & (block < p.nb)

    net = Net()
    inputs = [net.input(("age", bit)) for bit in range(p.m)]
    outputs = mixed_age_increment(net, inputs, p.PB, p.R, p.nb)
    for bit, output in enumerate(outputs):
        net.set_output(("new", bit), output)
    compiled = Compiled(net)
    actual = compiled.evaluate({("age", bit): ((words >> bit) & 1).astype(bool)
                                for bit in range(p.m)}, bool)
    generated = np.zeros_like(words)
    for bit in range(p.m):
        generated |= actual["new", bit].astype(np.uint32) << bit
    if not np.array_equal(generated, reference):
        raise RuntimeError("actual clock gates differ from independent integer formula")
    if not np.all(legal[reference[legal]]):
        raise RuntimeError("legal clock words leave the legal set")

    reverse = [[] for _ in words]
    for word, successor in enumerate(reference):
        reverse[int(successor)].append(word)
    distances = np.full(len(words), -1, dtype=np.int32)
    distances[legal] = 0
    phases = np.full(len(words), -1, dtype=np.int32)
    phases[legal] = (block[legal] * p.R + pos[legal]).astype(np.int32)
    queue = deque(int(word) for word in words[legal])
    while queue:
        successor = queue.popleft()
        for word in reverse[successor]:
            if distances[word] == -1:
                distances[word] = distances[successor] + 1
                phases[word] = (phases[successor] - 1) % p.U
                queue.append(word)
    if np.any(distances < 0):
        raise RuntimeError("some unused clock words never become legal")
    maximum = int(distances.max())
    worst = words[distances == maximum].tolist()
    if maximum != 16352 or worst != [37152]:
        raise RuntimeError((maximum, worst))
    if np.any(phases < 0) or not np.array_equal(phases[reference], (phases + 1) % p.U):
        raise RuntimeError("the all-word clock phase map fails its successor identity")
    phase_sizes = np.bincount(phases, minlength=p.U)
    cone_size = maximum + 5 * maximum * (maximum - 1)
    receipt = dict(candidate="G17", **candidates.digests(c),
                   checker_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                   netlist_helpers_sha256=hashlib.sha256((ROOT / "gacsca/netlist.py").read_bytes()).hexdigest(),
                   result="exhaustive packed-clock legality and phase-map certificate; no phase-repair claim",
                   checked_words=len(words), legal_words=int(legal.sum()),
                   invalid_words=int((~legal).sum()), maximum_normalization_updates=maximum,
                   worst_initial_words=worst, worst_initial_position=288, worst_initial_block=72,
                   past_fault_cone_sites=cone_size,
                   phase_successor_identity_checked_words=len(words),
                   legal_cycle_length=p.U,
                   maximum_words_per_clock_phase=int(phase_sizes.max()),
                   example_clock_phases={str(word): int(phases[word])
                                         for word in (37152, 17868, 65535)},
                   hypotheses=["Age selects one entire neighboring/default word before increment",
                               "no fault on a selected ancestral path during its normalization"],
                   not_proved=["correct clock phase", "Address normalization or erosion",
                               "hierarchy maintenance or memory under random noise"])
    path = ROOT / "figs/robustness/clock_legality_certificate.json"
    path.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()
