#!/usr/bin/env python3
"""SP17 verifier/build copy of check_sparse_schedule.py; distinct source and receipt pins."""
"""Universal abstract-program certificate for the EXPLICIT SP17 proposal.

The ROM is read from the saved own-program artifact; no sampled inputs
are used. Physical copy/routing and all-time reliability are separate
obligations. G17, its compiler files and candidates.CURRENT are unchanged.
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
import proposed_sparse_commit_reset448 as proposed
import inspect
import check_fast_mail_proposal as transport


def fixed_capture_certificate(p, table):
    source = inspect.getsource(transport.fixed_capture_certificate)
    old = 'for rank in range(10):'
    new = 'for rank in range(len(p.fam().LANE_OFFSETS)):'
    assert source.count(old) == 1
    namespace = dict(transport.__dict__)
    exec(compile(source.replace(old, new), '<SP17 all-twelve-rank capture checker>', 'exec'), namespace)
    return namespace['fixed_capture_certificate'](p, table)

from check_g17_schedule import Terms, require


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    started = time.monotonic()
    out = ROOT / "figs/robustness"
    build_file = out / "SP17_program_build.json"
    build = json.loads(build_file.read_text())
    require(build["build_complete"], "missing completed own-program build")
    require(build["proposal_source_sha256"] == digest(Path(proposed.__file__)), "proposal source changed")
    require(build["transport_checker_sha256"] == digest(ROOT / "Report/proofs/check_fast_mail_proposal.py"), "transport source changed")
    candidate = proposed.load_artifact()
    p, comp = candidate.p, candidate.comp
    require(candidate.digest() == build["proposed_candidate_sha256"], "candidate identity")
    listing_file = out / "SP17_program_listing.json"
    require(digest(listing_file) == build["listing_sha256"], "listing identity")
    listing = json.loads(listing_file.read_text())
    table = proposed.dependency_table(p)
    profile_file = out / "SP17_capture_table.json"
    require(digest(profile_file) == build["profile_sha256"], "profile identity")
    require(json.loads(profile_file.read_text()) == table, "regenerated profile")

    terms = Terms()
    node = [0, 1] + [terms.var(name) for name in comp.inputs]
    for operation, a, b in comp.gates:
        node.append(terms.op(operation, node[a], node[b]))
    require(len(node) == comp.n_nodes, "netlist size")
    sources = proposed.source_names(p)
    code = {name: i for i, name in enumerate(sources)}
    where = {(row["field"], row["bit"]): row["address"] for row in table}
    offsets = {(row["field"], row["bit"]): row["offsets"] for row in table}
    live = set(comp.outputs.values())
    for _, a, b in comp.gates:
        live.update((a, b))
    at = {}
    for name, nid in comp.index.items():
        if name[0] != "x" or nid not in live:
            continue
        _, off, field, bit = name
        src = code["info", 0] if off == 0 else code["ln", offsets[field, bit].index(off)]
        location = where[field, bit], src
        require(location not in at, ("input alias", location))
        at[location] = node[nid]

    lo, hi, H, period = p.lo, p.hi, p.H, p.PL
    previous = None
    geometry_checks = 0
    for page in range(p.NP):
        for tick in range(period):
            step = tick if page % 2 == 0 else period - 1 - tick
            centers = [lo - H + step + front * p.delta for front in range(p.fronts)]
            require(centers[0] >= 2 and centers[-1] + 2 < p.Q, "front holders cross colony edge")
            require(all(b - a >= 5 for a, b in zip(centers, centers[1:])), "front copy windows overlap")
            if previous is not None:
                delta = 0 if tick == 0 else (-1 if page % 2 == 0 else 1)
                require([x + delta for x in centers] == previous, "front carry source")
            previous = centers
            geometry_checks += p.fronts
    capture_checks = 0
    latest_captures = []
    for g, gather in enumerate(p.gathers_q):
        latest = 0
        for row in table:
            for off in row["offsets"]:
                capture = gather * p.Q + abs(off) * (p.Q // 8) + 1
                sign = 1 if off > 0 else -1
                require(sign * 8 * (capture - gather * p.Q - 1) == off * p.Q, "capture coordinate")
                deadline = p.gathers_q[g + 1] * p.Q if g < 2 else p.E0
                require(capture + 1 < deadline, "capture deadline")
                latest = max(latest, capture)
                capture_checks += 1
        latest_captures.append(latest)
    capture_truth = fixed_capture_certificate(p, table)
    _, left_load, right_load = p.courier_ticks()
    require(left_load + 1 + lo - 3 == p.T_sig, "left courier arrival")
    require(right_load + 1 + p.Q - 3 - (hi - 1) == p.T_sig, "right courier arrival")
    require(p.E0 + (p.NPe - 1) * period < min(left_load, right_load), "courier store deadline")
    require(latest_captures[-1] < min(left_load, right_load), "couriers after fast transport")

    rom = np.zeros_like(candidate.rom)
    instructions = {}
    for seq, page, tick, front, cell, op, kind, a, b, dest, _ in listing:
        require(0 <= page < p.NP and page != p.MP, ("page", seq, page))
        require(0 <= tick < period and 0 <= front < p.fronts, ("visit", seq))
        step = tick if page % 2 == 0 else period - 1 - tick
        require(cell == lo - H + step + front * p.delta and lo <= cell < hi, ("visit cell", seq))
        require((page, tick, front) not in instructions, ("duplicate visit", seq))
        column = page + (front << p.logNP)
        require(rom[cell, column] == 0, ("duplicate ROM slot", seq))
        word = op | (kind << 2) | (a << 4) | (b << (4 + p.SB)) | (dest << (4 + 2 * p.SB))
        require(word < (1 << p.IW), ("word width", seq))
        rom[cell, column] = word
        instructions[page, tick, front] = int(word)
    require(np.array_equal(rom, candidate.rom), "independently packed ROM differs from artifact")

    regs = [[None] * p.L for _ in range(p.fronts)]
    scratch, hold, flag_stores = {}, {}, {}
    counts = Counter()
    key_checks = 0
    minimum_delay = None
    flag_targets = {hi - 1: node[comp.outputs["y", "f1", 0]],
                    lo: node[comp.outputs["y", "f2", 0]]}
    require(set(where.values()).isdisjoint(flag_targets), "ordinary/flag Hold alias")
    for page in range(p.NP):
        if page == p.MP:
            for bit in range(p.k + p.PW):
                name = ("laddr", bit) if bit < p.k else ("psel", bit - p.k)
                require(regs[0][bit] == node[comp.outputs[name]], ("match key", name))
                key_checks += 1
            regs = [[None] * p.L for _ in range(p.fronts)]
            for bit in range(p.IW):
                regs[0][p.k + bit] = node[comp.index["I", bit]]
            continue
        for tick in range(period):
            clock = page * period + tick
            for front in range(p.fronts):
                word = instructions.get((page, tick, front), 0)
                if word == 0:
                    continue
                step = tick if page % 2 == 0 else period - 1 - tick
                cell = lo - H + step + front * p.delta
                operation, kind = word & 3, (word >> 2) & 3
                mask = (1 << p.SB) - 1
                a, b = (word >> 4) & mask, (word >> (4 + p.SB)) & mask
                dest = (word >> (4 + 2 * p.SB)) & ((1 << p.DB) - 1)

                def read(source):
                    nonlocal minimum_delay
                    require(source < len(sources), ("source range", page, tick, source))
                    family, index = sources[source]
                    if family == "reg":
                        require(regs[front][index] is not None, ("undefined register", page, tick, front, index))
                        return regs[front][index]
                    if family == "const":
                        return index
                    if family == "scr":
                        require((cell, index) in scratch, ("undefined scratch", page, tick, cell, index))
                        value, written = scratch[cell, index]
                        delay = clock - written
                        require(delay >= 1, ("scratch causality", page, tick, delay))
                        minimum_delay = delay if minimum_delay is None else min(minimum_delay, delay)
                        counts["scratch_reads"] += 1
                        return value
                    require((cell, source) in at, ("undefined lane", page, tick, cell, source))
                    return at[cell, source]

                value = terms.op(operation, read(a), read(b))
                counts["instructions"] += 1
                if kind == 0:
                    require(dest < p.L, "register destination")
                    regs[front][dest] = value
                    counts["register_writes"] += 1
                elif kind == 1:
                    require(cell in set(where.values()) | set(flag_targets),
                            ("unexpected Hold store", cell, page, tick))
                    hold[cell] = value
                    counts["hold_writes"] += 1
                    if cell in flag_targets:
                        require(value == flag_targets[cell], ("early flag", cell))
                        require(page < p.NPe - 1, ("early flag deadline", cell, page))
                        flag_stores[cell] = p.E0 + clock
                elif kind == 2:
                    require(dest < p.S, "scratch destination")
                    scratch[cell, dest] = value, clock
                    counts["scratch_writes"] += 1
                else:
                    counts["discarded_results"] += 1
    require(set(flag_stores) == set(flag_targets), "missing early flags")
    for bit, cell in where.items():
        require(hold.get(cell) == node[comp.outputs[("y",) + bit]], ("final Hold", bit))
    require(p.E0 + p.NP * period < p.U, "evaluation past commit")
    result = dict(
        proposal="SP17", proposed_rule_change=True, active_G17_modified=False,
        result="proved universal abstract own-ROM schedule under the listed hypotheses",
        hypotheses=["correct gathered inputs at the specified sparse locations",
                    "abstract fronts follow the certified visits with persistent registers and scratch",
                    "match pass loads the correct external instruction into front zero",
                    "no noise during this abstract execution"],
        not_proved=["physical routing and copy invariant", "whole-period self-simulation",
                    "damaged-colony restoration", "positive-noise reliability"],
        proposed_candidate_sha256=candidate.digest(), proposed_netlist_sha256=comp.digest,
        checker_sha256=digest(Path(__file__)), proposal_source_sha256=digest(Path(proposed.__file__)),
        algebra_checker_sha256=digest(ROOT / "Report/proofs/check_g17_schedule.py"),
        transport_checker_sha256=digest(ROOT / "Report/proofs/check_fast_mail_proposal.py"),
        build_receipt_sha256=digest(build_file), artifact_sha256=digest(out / "SP17_program.npz"),
        listing_sha256=digest(listing_file), reference_gates=len(comp.gates),
        input_variables=len(comp.inputs), normalized_terms=len(terms.terms),
        key_equalities=key_checks, early_flag_equalities=len(flag_stores),
        final_hold_equalities=len(where), front_geometry_checks=geometry_checks,
        gather_coordinate_checks=capture_checks, fixed_capture_assignments=capture_truth,
        latest_capture_input_ages=latest_captures, scratch_minimum_delay=minimum_delay,
        early_flag_store_ages={str(cell): age for cell, age in sorted(flag_stores.items())},
        early_flag_deadline_age=p.E0 + (p.NPe - 1) * period,
        evaluation_end_age=p.E0 + p.NP * period, commit_input_age=p.U - 1,
        counts=dict(counts), history_ranks_checked=12,
        SP14_modified=False,
        guard_source_sha256=digest(ROOT/'Report/proofs/proposed_packet_guard6.py'),
        pressure_source_sha256=digest(ROOT/'Report/proofs/proposed_packet_pressure.py'),
        buffered_service_source_sha256=digest(ROOT/'Report/proofs/proposed_buffered_framed_service.py'),
        SP15_proposal_source_sha256=digest(ROOT/'Report/proofs/proposed_sparse_guarded_pressure448.py'),
        SP16_modified=False, SP15_modified=False,
        global_reliability_established=False,
        seconds=time.monotonic() - started)
    (out / "SP17_symbolic_schedule.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result, indent=2), flush=True)


if __name__ == "__main__":
    main()
