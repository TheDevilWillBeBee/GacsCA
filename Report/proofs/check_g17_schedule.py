#!/usr/bin/env python3
"""Universal Boolean certificate for G17's *abstract* instruction schedule.

No sampled inputs and no changes to the rule. This does not verify physical
front routing, gathering, the match courier, or recovery under noise.
Run from the repository root with python3 Report/proofs/check_g17_schedule.py.
The receipt is written to figs/robustness/symbolic_schedule.json.
"""

from collections import Counter
import hashlib
import json
from pathlib import Path
import sys
import time

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

import numpy as np
from gacsca import candidates, jobsched


def require(condition, detail):
    if not condition:
        raise RuntimeError(detail)


class Terms:
    """Hash-consed terms, quotiented only by sound Boolean identities.

    AND/OR: associativity, commutativity, idempotence, constants, complements.
    XOR: associativity, commutativity, cancellation, constants.
    ANDN(a,b) is AND(a,XOR(b,1)). Equality is sufficient, never necessary,
    for Boolean equivalence. Integers 0 and 1 denote the Boolean constants.
    """

    def __init__(self):
        self.terms = [("constant", 0), ("constant", 1)]
        self.intern = {term: i for i, term in enumerate(self.terms)}

    def put(self, term):
        if term not in self.intern:
            self.intern[term] = len(self.terms)
            self.terms.append(term)
        return self.intern[term]

    def var(self, name):
        return self.put(("variable", tuple(name)))

    def op(self, operation, a, b):
        if operation == 3:
            return self.op(0, a, self.op(2, b, 1))
        require(operation in (0, 1, 2), ("operation", operation))
        args = []
        for x in (a, b):
            term = self.terms[x]
            args.extend(term[1] if term[0] == operation else (x,))
        if operation == 2:
            counts = Counter(args)
            vals = tuple(sorted(x for x, count in counts.items() if x != 0 and count % 2))
            if not vals:
                return 0
            if len(vals) == 1:
                return vals[0]
            return self.put((2, vals))
        absorbing, neutral = (0, 1) if operation == 0 else (1, 0)
        vals = set(args)
        if absorbing in vals:
            return absorbing
        vals.discard(neutral)
        # A complemented term is its XOR-normal form with constant 1 toggled.
        for x in tuple(vals):
            term = self.terms[x]
            neg_args = set(term[1]) if term[0] == 2 else {x}
            neg_args.symmetric_difference_update({1})
            neg_tuple = tuple(sorted(neg_args))
            neg = (next(iter(neg_args)) if len(neg_args) == 1
                   else self.intern.get((2, neg_tuple)))
            if neg in vals:
                return absorbing
        vals = tuple(sorted(vals))
        if not vals:
            return neutral
        if len(vals) == 1:
            return vals[0]
        return self.put((operation, vals))


def main():
    start = time.monotonic()
    c = candidates.load("G17")
    p, comp = c.p, c.comp
    require(c.digest() == "23a14aab4d3dc4fde5562cf3e26a4536b05456f84e65850fcb3bd95a104d8ceb",
            "G17 identity changed: re-audit before changing this verifier")
    eng = jobsched.Engine(p, comp, c.layout, MP=p.MP,
                          **candidates.RECIPES["G17"]["compile"]["jobs"])
    eng.run()
    print("Schedule regenerated; checking symbolic identities.", flush=True)

    terms = Terms()
    node = [0, 1] + [terms.var(name) for name in comp.inputs]
    for operation, a, b in comp.gates:
        node.append(terms.op(operation, node[a], node[b]))
    require(len(node) == comp.n_nodes, "netlist size")

    # Reconstruct operand locations from the schema, not the scheduler's DAG.
    sources = p.fam().source_names(p)
    source_code = {name: i for i, name in enumerate(sources)}
    bits = [(f, i) for f, width in c.schema for i in range(width)]
    where = {bit: int(c.layout[i]) for i, bit in enumerate(bits)}
    at = {}
    for name, nid in comp.index.items():
        if name[0] != "x":
            continue
        _, offset, field, bit = name
        cell = where[field, bit]
        if offset == 0:
            code = source_code["info", 0]
        else:
            lane = p.fam().LANE_OFFSETS.index(offset)
            cell += p.skew[lane]
            code = source_code["ln", lane]
        require((cell, code) not in at, ("aliased input location", cell, code))
        at[cell, code] = node[nid]

    lo, hi = p.lo, p.hi
    overhang = (p.fronts - 1) * p.delta
    period = hi - lo + overhang
    require(period == p.PL, "pass period")
    geometry_checks = 0
    previous_centers = None
    for page in range(p.NP):
        for tick in range(period):
            step = tick if page % 2 == 0 else period - 1 - tick
            centers = [lo - overhang + step + front * p.delta
                       for front in range(p.fronts)]
            require(centers[0] >= 2 and centers[-1] + 2 < p.Q,
                    ("front holders cross a colony boundary", page, tick))
            require(all(b - a >= 5 for a, b in zip(centers, centers[1:])),
                    ("front holder windows overlap", page, tick))
            if previous_centers is not None:
                source_delta = 0 if tick == 0 else (-1 if page % 2 == 0 else 1)
                require([center + source_delta for center in centers] == previous_centers,
                        ("front carry source", page, tick))
            previous_centers = centers
            geometry_checks += p.fronts
    capture_checks = 0
    for gather in range(3):
        for offset, skew in zip(p.fam().LANE_OFFSETS, p.skew):
            capture = p.capture_age(offset, gather)
            distance = capture - p.gathers_q[gather] * p.Q - 1
            displacement = -distance if offset < 0 else distance
            require(skew + displacement == offset * p.Q, "gather address")
            deadline = (p.gathers_q[gather + 1] * p.Q
                        if gather < 2 else p.E0)
            require(capture + 1 < deadline, "capture finishes before reuse/evaluation")
            capture_checks += 1
    _, left_load, right_load = p.courier_ticks()
    require(left_load + 1 + lo - 3 == p.T_sig, "left courier arrival")
    require(right_load + 1 + p.Q - 3 - (hi - 1) == p.T_sig, "right courier arrival")
    require(p.E0 + (p.NPe - 1) * period < min(left_load, right_load),
            "flag store deadline precedes couriers")
    rom = np.zeros_like(c.rom)
    instructions = {}
    for seq, page, tick, front, cell, op, kind, a, b, dest, _note in eng.prog.listing:
        require(0 <= page < p.NP and page != p.MP, ("page", seq, page))
        require(0 <= tick < period and 0 <= front < p.fronts, ("visit", seq))
        step = tick if page % 2 == 0 else period - 1 - tick
        expected_cell = lo - overhang + step + front * p.delta
        require(lo <= cell < hi and cell == expected_cell, ("geometry", seq, cell))
        col = page + (front << p.logNP)
        require((page, tick, front) not in instructions, ("duplicate visit", seq))
        require(rom[cell, col] == 0, ("duplicate slot", seq))
        # Independent packing, then execution from the packed word below.
        word = op | (kind << 2) | (a << 4) | (b << (4 + p.SB)) | (dest << (4 + 2 * p.SB))
        require(word < (1 << p.IW), ("word width", seq))
        rom[cell, col] = word
        instructions[page, tick, front] = int(word)
    require(np.array_equal(rom, c.rom), "regenerated listing differs from pinned ROM")

    regs = [[None] * p.L for _ in range(p.fronts)]
    scratch, hold, flag_stores = {}, {}, {}
    counts = Counter()
    key_checks = 0
    scratch_min_delay = None
    flag_targets = {hi - 1: node[comp.outputs["y", "f1", 0]],
                    lo: node[comp.outputs["y", "f2", 0]]}
    require(set(where.values()).isdisjoint(flag_targets), "flag and ordinary Hold alias")

    for page in range(p.NP):
        if page == p.MP:
            for bit in range(p.k + p.PW):
                name = ("laddr", bit) if bit < p.k else ("psel", bit - p.k)
                require(regs[0][bit] == node[comp.outputs[name]], ("match key", name))
                key_checks += 1
            # Assume correct external instruction fetching; discard every other
            # register to certify the schedule never relies on its old contents.
            regs = [[None] * p.L for _ in range(p.fronts)]
            for bit in range(p.IW):
                regs[0][p.k + bit] = node[comp.index["I", bit]]
            continue
        for tick in range(period):
            clock = page * period + tick
            # Distinct fronts visit distinct cells at any fixed tick. Reads
            # below must use scratch written on a strictly earlier tick.
            for front in range(p.fronts):
                word = instructions.get((page, tick, front), 0)
                if word == 0:
                    # AND R0,R0 -> R0 is the identity for arbitrary R0.
                    continue
                step = tick if page % 2 == 0 else period - 1 - tick
                cell = lo - overhang + step + front * p.delta
                op, kind = word & 3, (word >> 2) & 3
                mask = (1 << p.SB) - 1
                a, b = (word >> 4) & mask, (word >> (4 + p.SB)) & mask
                dest = (word >> (4 + 2 * p.SB)) & ((1 << p.DB) - 1)

                def read(code):
                    nonlocal scratch_min_delay
                    require(code < len(sources), ("source range", page, tick, front, code))
                    family, index = sources[code]
                    if family == "reg":
                        value = regs[front][index]
                        require(value is not None, ("undefined register", page, tick, front, index))
                        return value
                    if family == "const":
                        return index
                    if family == "scr":
                        require((cell, index) in scratch, ("undefined scratch", page, tick, cell, index))
                        value, written = scratch[cell, index]
                        delay = clock - written
                        require(delay >= 1, ("scratch causality", page, tick, cell, index, delay))
                        scratch_min_delay = delay if scratch_min_delay is None else min(scratch_min_delay, delay)
                        counts["scratch_reads"] += 1
                        return value
                    require((cell, code) in at, ("undefined lane", page, tick, cell, code))
                    return at[cell, code]

                value = terms.op(op, read(a), read(b))
                counts["instructions"] += 1
                if kind == 0:
                    require(dest < p.L, ("register destination", dest))
                    regs[front][dest] = value
                    counts["register_writes"] += 1
                elif kind == 1:
                    hold[cell] = value
                    counts["hold_writes"] += 1
                    if cell in flag_targets:
                        require(value == flag_targets[cell], ("early flag value", cell, page, tick))
                        require(page < p.NPe - 1, ("early flag deadline", cell, page))
                        flag_stores[cell] = p.E0 + clock
                elif kind == 2:
                    require(dest < p.S, ("scratch destination", dest))
                    scratch[cell, dest] = value, clock
                    counts["scratch_writes"] += 1
                else:
                    counts["discarded_results"] += 1

    require(set(flag_stores) == set(flag_targets), "missing early flag store")
    for bit, cell in where.items():
        require(hold.get(cell) == node[comp.outputs[("y",) + bit]], ("final Hold", bit, cell))
    require(p.E0 + p.NP * period < p.U, "evaluation extends past commit")
    receipt = dict(
        result="proved for the abstract schedule under the listed hypotheses",
        hypotheses=["correct gathered inputs at the reconstructed lane locations",
                    "abstract fronts execute their visits with persistent registers and scratch",
                    "match pass loads the correct external I into front 0",
                    "no noise during this abstract execution"],
        not_proved=["physical routing/copy invariant", "physical gathering and match courier",
                    "continuing-period invariant", "reliability against noise"],
        candidate="G17", **candidates.digests(c),
        checker_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        input_variables=len(comp.inputs), reference_gates=len(comp.gates),
        normalized_terms=len(terms.terms), key_equalities=key_checks,
        front_geometry_checks=geometry_checks, gather_address_checks=capture_checks,
        early_flag_equalities=len(flag_stores), final_hold_equalities=len(where),
        scratch_minimum_delay=scratch_min_delay,
        early_flag_store_ages={str(cell): age for cell, age in sorted(flag_stores.items())},
        early_flag_deadline_age=p.E0 + (p.NPe - 1) * period,
        evaluation_end_age=p.E0 + p.NP * period,
        counts=dict(counts), seconds=time.monotonic() - start)
    destination = ROOT / "figs/robustness/symbolic_schedule.json"
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps(receipt, indent=2), flush=True)


if __name__ == "__main__":
    main()
