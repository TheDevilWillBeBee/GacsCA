#!/usr/bin/env python3
"""Symbolic local certificate for the conditional true-colony right barrier.

All assignments of raw ages, two arbitrary structural faults, Flag2 and
Workspace.Flag2 are covered by free Boolean inputs. This does not prove
Workspace.Flag1 source exclusion for a damaged G17 simulation.
"""
from itertools import combinations
import hashlib
import inspect
import json
from pathlib import Path
import sys
from types import FunctionType

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from gacsca import candidates, maintenance, rule_g
import numpy as np
from gacsca.netlist import Net, Compiled, const_word, mixed_age_increment, majority_word, w_in_range


def dominant_majority(net, words, default):
    # Sound for every bit width: three identical words force every bit of
    # the bitwise majority and at least three word-equality checks. This
    # shortcut avoids asking Net's limited gate simplifier to prove that
    # threshold_3(a,a,a,b,c)=a with free (nonconstant) a.
    for word in words:
        if sum(other == word for other in words) >= 3:
            return word, 1
    return majority_word(net, words, default)


def certified_build():
    namespace = dict(maintenance.build.__globals__)
    namespace["majority_word"] = dominant_majority
    return FunctionType(maintenance.build.__code__, namespace,
                        "maintenance_with_proved_symbolic_dominance",
                        maintenance.build.__defaults__)


def check_dominance_primitive():
    cases = 0
    for faults in combinations(range(5), 2):
        net = Net()
        common = net.input(("common",))
        bad = [net.input(("bad", j)) for j in faults]
        default = net.input(("default",))
        words = [[bad[faults.index(j)] if j in faults else common] for j in range(5)]
        voted, exists = majority_word(net, words, [default])
        net.set_output(("voted",), voted[0])
        net.set_output(("exists",), exists)
        assignments = np.arange(16, dtype=np.uint32)
        values = {("common",): ((assignments >> 0) & 1).astype(bool),
                  ("bad", faults[0]): ((assignments >> 1) & 1).astype(bool),
                  ("bad", faults[1]): ((assignments >> 2) & 1).astype(bool),
                  ("default",): ((assignments >> 3) & 1).astype(bool)}
        result = Compiled(net).evaluate(values, bool)
        assert np.array_equal(result["voted",], values["common",])
        assert result["exists",].all()
        cases += len(assignments)
    return cases


def symbolic_case(p, build, A, faults):
    net = Net()
    common_age = [net.input(("common_age", bit)) for bit in range(p.m)]
    cells = {}
    for j in range(-5, 6):
        outside_suffix = A + j < 0
        outside_first_colony = outside_suffix or A + j >= p.Q
        arbitrary = outside_suffix or j in faults
        cells[j] = dict(
            addr=([net.input((j, "addr", bit)) for bit in range(p.k)]
                  if arbitrary else const_word((A + j) % p.Q, p.k)),
            age=([net.input((j, "age", bit)) for bit in range(p.m)]
                 if arbitrary else common_age),
            f1=net.input((j, "f1")) if outside_first_colony or j in faults else 0,
            wf1=net.input((j, "wf1")) if outside_first_colony or j in faults else 0,
            f2=net.input((j, "f2")), wf2=net.input((j, "wf2")))
    out = build(net, cells, p.k, p.m, Q=p.Q,
                nb=p.nb, radix=p.R, pos_bits=p.PB)
    assert out["f1"] == 0, (A, faults, "Flag1")
    assert out["addr"] == const_word(A, p.k), (A, faults, "Address")
    assert out["age_now"] == common_age, (A, faults, "current Age")
    expected_age = mixed_age_increment(net, common_age, p.PB, p.R, p.nb)
    assert out["age"] == expected_age, (A, faults, "incremented Age")


def source_counterexample(p):
    net = Net()
    alpha, beta = p.age_code(2000), p.age_code(2001)
    cells = {}
    for j in range(-5, 6):
        cells[j] = dict(addr=const_word((j + (32 if j < 0 else 0)) % p.Q, p.k),
                        age=const_word(beta if j < 0 else alpha, p.m),
                        f1=0, f2=0, wf1=int(j in (0, 1, 2)), wf2=0)
    out = maintenance.build(net, cells, p.k, p.m, Q=p.Q,
                            nb=p.nb, radix=p.R, pos_bits=p.PB)
    assert out["f1"] == 1 and out["f2"] == 0
    assert out["addr"] == const_word(32, p.k)
    assert out["age_now"] == const_word(beta, p.m)
    assert out["age"] == const_word(p.age_code(2002), p.m)
    return dict(true_boundary_Address=0, right_geometry_correct=True,
                raised_Workspace_Flag1_offsets=[0, 1, 2],
                computed_Flag1=1, computed_Flag2=0,
                wrong_computed_Address=32, wrong_computed_Age=p.age_code(2002),
                expected_Address=0, expected_Age=p.age_code(2001),
                scope="exact local source-hypothesis counterexample; not pristine-hierarchy unreliability")


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


def finite_barrier_envelopes(p):
    start, front = p.Q - 10, 64
    groups = [()] + [(x,) for x in range(front - 15, front + 16)]
    groups += [(x, x + 1) for x in range(front - 15, front + 15)]
    flag_cases = 0
    for noise in groups:
        raw = interval(front, p.Q - 1) | sum(1 << x for x in noise)
        right = [raw >> j for j in range(1, 6)]
        output = threshold(right, 3) | (raw & threshold(right, 2)) | interval(start, p.Q - 1)
        charge = sum(front - 5 <= x <= front - 1 for x in noise)
        new_front = front - 3 - charge
        assert not (output & interval(0, new_front - 1)), noise
        flag_cases += 1
    source_cases = 0
    for noise in [()] + [(x,) for x in range(p.Q - 25, p.Q + 6)] + [
            (x, x + 1) for x in range(p.Q - 25, p.Q + 5)]:
        workspace = interval(p.Q - 5, p.Q - 1)
        workspace |= sum(1 << x for x in noise)
        workspace &= interval(0, p.Q - 1)
        inputs = [workspace << -j if j < 0 else workspace >> j for j in range(-5, 6)]
        computed_source = threshold(inputs, 3)
        assert not (computed_source & interval(0, start - 1)), noise
        source_cases += 1
    packing_cases = 0
    for gap in range(24, 65):
        for previous_offset in range(1, 6):
            for next_offset in range(1, 6):
                for charge in (1, 2):
                    assert 3 * gap + charge + next_offset - previous_offset - (charge - 1) >= 24
                    packing_cases += 1
    displacement = lambda ticks: 3 * ticks + 2 * (1 + (3 * ticks + 1) // 23)
    safe_updates = max(t for t in range(p.Q) if start - displacement(t) >= 5)
    assert safe_updates == 113
    assert start - displacement(113) == 5
    assert start - displacement(114) < 5
    arithmetic_cases = 0
    for duration in range(1, 1025):
        # The telescoping separation inequality is 23(k-1)<=3T+1.
        max_events = 1 + (3 * duration + 1) // 23
        assert 23 * (max_events - 1) <= 3 * duration + 1 < 23 * max_events
        assert 3 * duration + 2 * max_events == displacement(duration)
        arithmetic_cases += 1
    return dict(local_Flag1_front_cases=flag_cases, Workspace_source_cut_cases=source_cases,
                packing_cases=packing_cases, all_duration_arithmetic_cases=arithmetic_cases,
                initial_Flag1_envelope_start=start, source_cut=start,
                front_displacement_bound="3T+2[1+floor((3T+1)/23)]",
                safe_full_rule_updates=safe_updates,
                comparison_at_113=dict(displacement=displacement(113), remaining_prefix=5),
                scope="proved conditional finite barrier, not an optimal lifetime or repair theorem")


def actual_flag_predicate(p):
    net = Net()
    flags = [net.input(("flag", j)) for j in range(6)]
    source = net.input(("source",))
    cells = {j: dict(addr=const_word(50 + j, p.k), age=const_word(p.age_code(2000), p.m),
                     f1=flags[j] if j >= 0 else 0, f2=0,
                     wf1=source if j in (0, 1, 2) else 0, wf2=0)
             for j in range(-5, 6)}
    out = maintenance.build(net, cells, p.k, p.m, Q=p.Q,
                            nb=p.nb, radix=p.R, pos_bits=p.PB)
    net.set_output(("flag",), out["f1"])
    assignments = np.arange(128, dtype=np.uint32)
    values = {("flag", j): ((assignments >> j) & 1).astype(bool) for j in range(6)}
    values["source",] = ((assignments >> 6) & 1).astype(bool)
    got = Compiled(net).evaluate(values, bool)["flag",]
    expected = np.array([bool((int(x) >> 6) & 1) or
                         sum((int(x) >> j) & 1 for j in range(1, 6)) >= 3 or
                         (bool(int(x) & 1) and sum((int(x) >> j) & 1 for j in range(1, 6)) >= 2)
                         for x in assignments])
    assert np.array_equal(got, expected)
    return len(assignments)


def workspace_output_gate(p):
    source = inspect.getsource(rule_g.build)
    for exact_line in ("    right_end = w_in_range(n, addr_now, Q - 5, Q)",
                       "    wf1 = n.all([right_end, in_wf, sim_r])"):
        assert source.count(exact_line) == 1
    assert "wf1=[wf1]" in source
    counts = {}
    for name, width, low, high in (("Address", p.k, p.Q - 5, p.Q),
                                   ("Age", p.m, p.age_code(p.T_wf),
                                    p.age_code(p.T_wf + 2 * p.Q - 1) + 1)):
        net = Net()
        word = [net.input((name, bit)) for bit in range(width)]
        mask = w_in_range(net, word, low, high)
        net.set_output(("mask",), mask)
        assignments = np.arange(1 << width, dtype=np.uint32)
        got = Compiled(net).evaluate({(name, bit): ((assignments >> bit) & 1).astype(bool)
                                      for bit in range(width)}, bool)["mask",]
        assert np.array_equal(got, (assignments >= low) & (assignments < high))
        if name == "Age":
            legal_words = np.array([p.age_code(t) for t in range(p.U)])
            assert np.array_equal(got[legal_words],
                                  (np.arange(p.U) >= p.T_wf) & (np.arange(p.U) < p.T_wf + 2 * p.Q))
        counts[name] = len(assignments)
    return dict(checked_source_shape=True, actual_range_gate_cases=counts,
                full_rule_sha256=hashlib.sha256((ROOT / "gacsca/rule_g.py").read_bytes()).hexdigest())


def main():
    c = candidates.load("G17")
    p = c.p
    assert c.digest() == "23a14aab4d3dc4fde5562cf3e26a4536b05456f84e65850fcb3bd95a104d8ceb"
    dominance_cases = check_dominance_primitive()
    build = certified_build()
    pairs = tuple(combinations(range(-5, 6), 2))
    cases = 0
    for A in range(p.Q):
        for faults in pairs:
            symbolic_case(p, build, A, faults)
            cases += 1
        if A % 64 == 63:
            print(f"certified Addresses 0..{A}: {cases} symbolic cases", flush=True)
    counterexample = source_counterexample(p)
    envelopes = finite_barrier_envelopes(p)
    flag_assignments = actual_flag_predicate(p)
    workspace_gate = workspace_output_gate(p)
    receipt = dict(base_candidate="G17", **candidates.digests(c),
                   checker_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                   helpers_sha256=hashlib.sha256((ROOT / "gacsca/netlist.py").read_bytes()).hexdigest(),
                   maintenance_sha256=hashlib.sha256((ROOT / "gacsca/maintenance.py").read_bytes()).hexdigest(),
                   actual_majority_primitive_assignments=dominance_cases,
                   symbolic_simplification="proved identical-word dominance shortcut; copied build code object and otherwise unchanged globals",
                   symbolic_cases=cases, canonical_Addresses_checked=p.Q,
                   raw_common_Age_bits_free=p.m, arbitrary_faults_per_case=2,
                   free_fields_everywhere=["Flag2", "Workspace.Flag2"],
                   free_fields_outside_first_colony=["Flag1", "Workspace.Flag1"],
                   free_fields_left_of_true_boundary=["Address", "Age", "Flag1", "Workspace.Flag1"],
                   literal_outputs=["canonical Address", "common Age before increment", "Flag1=0"],
                   source_hypothesis_counterexample=counterexample,
                   finite_barrier_certificate=envelopes,
                   actual_Flag1_envelope_assignments=flag_assignments,
                   Workspace_Flag1_output_gate=workspace_gate,
                   result="local universal certificate for the conditional right suffix barrier",
                   active_rule_changed=False,
                   not_proved=["source exclusion in a damaged simulation", "full structural recovery",
                               "bounded upper-error footprints", "positive-noise reliability"])
    output = ROOT / "figs/robustness/right_barrier_certificate.json"
    output.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()
