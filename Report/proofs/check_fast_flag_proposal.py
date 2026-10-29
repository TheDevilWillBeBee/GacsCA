#!/usr/bin/env python3
"""Local certificate for an EXPLICITLY PROPOSED radius-eight maintenance rule.

No active rule, candidate, ROM or compiler is modified. The proposal adds
right-vote pair validation and observes three farther Flag1 bits. It is
not a self-simulating candidate or a positive-noise reliability theorem.
"""
from fractions import Fraction
from itertools import combinations
import hashlib
import inspect
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
import numpy as np
from gacsca import candidates, maintenance
from gacsca.netlist import Net, Compiled, const_word, mixed_age_increment
from check_right_barrier import dominant_majority, check_dominance_primitive

REPLACEMENTS = [
    ("    for j in range(-5, 6):", "    for j in range(-5, 9):"),
    ("    flag_bits = [n.AND(inside[j], cells[j]['f1']) for j in range(1, 6)]",
     "    flag_bits = [n.AND(inside[j], cells[j]['f1']) for j in range(1, 9)]"),
    ("    f1 = n.any([incons, wf1, flags3, n.AND(c['f1'], flags2)])",
     """    joint_right = at_least(n, [n.AND(w_eq(n, adjusted[j], v),
                                            w_eq(n, cells[j]['age'], age_r))
                               for j in range(1, 6)], 3)
    f1 = n.any([incons, wf1, flags3, n.AND(c['f1'], flags2), n.NOT(joint_right)])"""),
]


def proposed_build(symbolic=False, pair_validation=True):
    source = inspect.getsource(maintenance.build)
    for old, new in REPLACEMENTS:
        assert source.count(old) == 1
        source = source.replace(old, new)
    if not pair_validation:
        source = source.replace(", n.NOT(joint_right)])", "])")
    namespace = dict(maintenance.__dict__)
    if symbolic:
        namespace["majority_word"] = dominant_majority
    exec(compile(source, "<proposed radius-eight maintenance; not active G17>", "exec"), namespace)
    return namespace["build"], source


def invoke(build, net, cells, p):
    return build(net, cells, p.k, p.m, Q=p.Q, nb=p.nb, radix=p.R, pos_bits=p.PB)


def canonical_cells(p, net, A, age, faults=()):
    cells = {}
    for j in range(-5, 9):
        if j >= 6:
            cells[j] = dict(f1=net.input((j, "f1")) if j in faults else 0)
            continue
        if j in faults:
            cells[j] = dict(addr=[net.input((j, "addr", bit)) for bit in range(p.k)],
                            age=[net.input((j, "age", bit)) for bit in range(p.m)],
                            **{field: net.input((j, field)) for field in ("f1", "f2", "wf1", "wf2")})
        else:
            cells[j] = dict(addr=const_word((A + j) % p.Q, p.k), age=age,
                            f1=0, f2=0, wf1=0, wf2=0)
    return cells


def pristine_symbolic(p, build, A, faults):
    net = Net()
    common_age = [net.input(("common_age", bit)) for bit in range(p.m)]
    out = invoke(build, net, canonical_cells(p, net, A, common_age, faults), p)
    assert out["addr"] == const_word(A, p.k), (A, faults)
    assert out["age_now"] == common_age, (A, faults)
    assert out["age"] == mixed_age_increment(net, common_age, p.PB, p.R, p.nb)
    assert out["f1"] == out["f2"] == 0, (A, faults)


def validation_off_on_joint_support(p, validated, plain, A, good):
    net = Net()
    common_age = [net.input(("common_age", bit)) for bit in range(p.m)]
    cells = {}
    for j in range(-5, 9):
        if j >= 6:
            cells[j] = dict(f1=net.input((j, "f1")))
            continue
        cells[j] = dict(
            addr=const_word((A + j) % p.Q, p.k) if j in good else
                 [net.input((j, "addr", bit)) for bit in range(p.k)],
            age=common_age if j in good else
                [net.input((j, "age", bit)) for bit in range(p.m)],
            **{field: net.input((j, field)) for field in ("f1", "f2", "wf1", "wf2")})
    assert invoke(validated, net, cells, p) == invoke(plain, net, cells, p), (A, good)


def quiet_seed_symbolic(p, build, A, faults):
    net = Net()
    age = [net.input(("common_age", bit)) for bit in range(p.m)]
    cells = canonical_cells(p, net, A, age, faults)
    for j in range(-5, 9):
        cells[j]["f1"] = net.input((j, "f1"))
        if j <= 5:
            cells[j]["f2"] = net.input((j, "f2"))
            cells[j]["wf2"] = net.input((j, "wf2"))
    assert invoke(build, net, cells, p)["f1"] == 0, (A, faults)


def actual_flag_truth(p, build):
    net = Net()
    flags = {j: net.input(("flag", j)) for j in range(9)}
    source = net.input(("source",))
    cells = {j: dict(addr=const_word(200 + j, p.k), age=const_word(p.age_code(2000), p.m),
                     f1=flags[j] if j >= 0 else 0, f2=0,
                     wf1=source if j in (0, 1, 2) else 0, wf2=0)
             for j in range(-5, 9)}
    out = invoke(build, net, cells, p)
    net.set_output(("flag",), out["f1"])
    assignments = np.arange(1024, dtype=np.uint32)
    values = {("flag", j): ((assignments >> j) & 1).astype(bool) for j in range(9)}
    values["source",] = ((assignments >> 9) & 1).astype(bool)
    got = Compiled(net).evaluate(values, bool)["flag",]
    expected = np.array([bool((int(x) >> 9) & 1) or
                         sum((int(x) >> j) & 1 for j in range(1, 9)) >= 3 or
                         (bool(int(x) & 1) and sum((int(x) >> j) & 1 for j in range(1, 9)) >= 2)
                         for x in assignments])
    assert np.array_equal(got, expected)
    return len(assignments)


def pair_validation_obstruction(p, build):
    net = Net()
    alpha, beta = p.age_code(2000), p.age_code(2001)
    cells = {}
    for j in range(-5, 9):
        if j >= 6:
            cells[j] = dict(f1=0)
        else:
            cells[j] = dict(addr=const_word(j % p.Q if j <= 3 else 375 + j, p.k),
                            age=const_word(beta if j in (3, 4, 5) else alpha, p.m),
                            f1=int(j in (2, 3)), f2=0, wf1=0, wf2=0)
    out = invoke(build, net, cells, p)
    assert out["f1"] == 1 and out["f2"] == 0
    assert out["addr"] == const_word(0, p.k)
    assert out["age"] == const_word(p.age_code(2001), p.m)
    return dict(pair_support_count=1, computed_Flag1=1,
                computed_Address=0, computed_Age=p.age_code(2001),
                scope="local rejection of the current-rule independent-vote obstruction")


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


def pulse(word):
    right = [word >> j for j in range(1, 9)]
    return threshold(right, 3) | (word & threshold(right, 2))


def interval_case(width, holes):
    a, b = 12, 11 + width
    word = interval(a, b)
    for hole in holes:
        word &= ~(1 << (a + hole))
    leading = any(0 <= hole <= 2 for hole in holes)
    trailing = any(width - 3 <= hole <= width - 1 for hole in holes)
    lo, hi = a - 6 + 2 * leading, b - 2 - 2 * trailing
    wanted = interval(lo, hi)
    assert pulse(word) & wanted == wanted, (width, holes, lo, hi)
    assert hi - lo + 1 >= width


def pulse_certificate():
    cases = 0
    for width in range(5, 65):
        points = tuple(range(-5, width + 5))
        for holes in [()] + [(x,) for x in points] + list(combinations(points, 2)):
            interval_case(width, holes)
            cases += 1
    multi_group_cases = 0
    for width in (26, 32, 64, 128, 256, 512):
        for left in range(-3, 5):
            for right in range(width - 6, width + 3):
                if right - (left + 1) < 24:
                    continue
                interval_case(width, (left, left + 1, right, right + 1))
                multi_group_cases += 1
    packing_cases = 0
    for gap in range(1, 25):
        for first_offset in range(3):
            for next_offset in range(3):
                leading_distance = abs(-6 * gap + 2 + next_offset - first_offset)
                trailing_distance = abs(-2 * gap - 2 + next_offset - first_offset)
                if gap < 4:
                    assert leading_distance < 24
                if gap < 10:
                    assert trailing_distance < 24
                packing_cases += 1
    arithmetic_cases = 0
    for duration in range(1, 10001):
        left_loss = 2 * ((duration + 3) // 4)
        right_loss = 2 * ((duration + 9) // 10)
        assert -6 * duration + left_loss <= -Fraction(11, 2) * duration + 2
        assert -2 * duration - right_loss >= -Fraction(11, 5) * duration - 2
        assert 4 * duration - left_loss - right_loss >= Fraction(33, 10) * duration - 4
        arithmetic_cases += 1
    comparison_cases = 0
    for initial_gap in range(1, 1025):
        duration = 2 * initial_gap + 4
        leading_bound = -Fraction(11, 2) * duration + 2
        path_lower_bound = -initial_gap - 5 * duration
        assert path_lower_bound >= leading_bound
        comparison_cases += 1
    return dict(interval_cases=cases, two_separated_group_cases=multi_group_cases,
                event_packing_cases=packing_cases, duration_arithmetic_cases=arithmetic_cases,
                quiet_path_comparison_cases=comparison_cases,
                minimum_nominal_width=5, leading_event_gap=4, trailing_event_gap=10,
                leading_speed_lower_bound="11/2", trailing_speed_upper_bound="11/5",
                width_growth_lower_bound="33T/10-4",
                required_inside_hypothesis="all eight right Flag1 samples inside at the protected outputs",
                comparison_requires="a quiet path with steps left by 1..5 and no direct overwrite on its nodes")


def quieting_certificate(p):
    front = 64
    groups = [()] + [(x,) for x in range(front - 15, front + 16)]
    groups += [(x, x + 1) for x in range(front - 15, front + 15)]
    local_cases = 0
    for noise in groups:
        raw = interval(0, front - 1) | sum(1 << x for x in noise)
        affected = any(front - 1 <= x <= front + 7 for x in noise)
        new_front = front - 2 + 2 * affected
        assert not (pulse(raw) & interval(new_front, p.Q - 1)), noise
        local_cases += 1
    packing_cases = 0
    for gap in range(1, 25):
        for first_offset in range(-1, 8):
            for next_offset in range(-1, 8):
                distance = abs(-2 * gap + 2 + next_offset - first_offset)
                if gap < 9:
                    assert distance < 24
                packing_cases += 1
    shifts = lambda steps: 2 * steps - 2 * ((steps + 8) // 9)
    more_updates = next(t for t in range(1, p.Q) if shifts(t) >= p.Q - 2)
    assert more_updates == 215
    assert shifts(214) < p.Q - 2
    return dict(local_zero_suffix_cases=local_cases, event_packing_cases=packing_cases,
                source_free_end_seed_updates=1, additional_updates_bound=more_updates,
                total_source_free_updates_bound=1+more_updates, affecting_event_gap=9,
                zero_front_advance_lower_bound="2T-2 ceil(T/9)",
                scope="aligned canonical geometry, common Age and no computed Flag1 source, with E0; not damaged-island quieting")


def gate_count(p, build, extended):
    net = Net()
    cells = {}
    for j in range(-5, 9 if extended else 6):
        cells[j] = dict(f1=net.input((j, "f1")))
        if j <= 5:
            cells[j].update(addr=[net.input((j, "addr", bit)) for bit in range(p.k)],
                            age=[net.input((j, "age", bit)) for bit in range(p.m)],
                            **{field: net.input((j, field)) for field in ("f2", "wf1", "wf2")})
    out = invoke(build, net, cells, p)
    for field, word in out.items():
        if isinstance(word, list):
            for bit, node in enumerate(word):
                net.set_output((field, bit), node)
        else:
            net.set_output((field,), word)
    compiled = Compiled(net)
    return dict(inputs=len(compiled.inputs), gates=len(compiled.gates), netlist_sha256=compiled.digest)


def main():
    c = candidates.load("G17")
    p = c.p
    assert c.digest() == "23a14aab4d3dc4fde5562cf3e26a4536b05456f84e65850fcb3bd95a104d8ceb"
    exact, source = proposed_build()
    symbolic, _ = proposed_build(symbolic=True)
    plain, _ = proposed_build(symbolic=True, pair_validation=False)
    dominance_cases = check_dominance_primitive()
    pairs = tuple(combinations(range(-5, 9), 2))
    correction_cases = 0
    for A in range(p.Q):
        for faults in pairs:
            pristine_symbolic(p, symbolic, A, faults)
            correction_cases += 1
        if A % 64 == 63:
            print(f"certified Addresses 0..{A}: {correction_cases} two-fault cases", flush=True)
    agreement_cases = 0
    for A in (0, 1, 375, 378, 379, 383):
        for good in combinations(range(1, 6), 3):
            validation_off_on_joint_support(p, symbolic, plain, A, good)
            agreement_cases += 1
    seed_cases = 0
    for A in (p.Q-2, p.Q-1):
        for faults in pairs:
            quiet_seed_symbolic(p, symbolic, A, faults)
            seed_cases += 1
    old_count, new_count = gate_count(p, maintenance.build, False), gate_count(p, exact, True)
    receipt = dict(base_candidate="G17", **candidates.digests(c),
                   checker_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                   helpers_sha256=hashlib.sha256((ROOT / "gacsca/netlist.py").read_bytes()).hexdigest(),
                   maintenance_sha256=hashlib.sha256((ROOT / "gacsca/maintenance.py").read_bytes()).hexdigest(),
                   majority_shortcut_sha256=hashlib.sha256((ROOT / "Report/proofs/check_right_barrier.py").read_bytes()).hexdigest(),
                   proposed_local_source_sha256=hashlib.sha256(source.encode()).hexdigest(),
                   exact_source_replacements=REPLACEMENTS,
                   actual_majority_primitive_assignments=dominance_cases,
                   symbolic_two_fault_cases=correction_cases,
                   symbolic_pair_validation_off_on_joint_support_cases=agreement_cases,
                   symbolic_quiet_end_seed_cases=seed_cases,
                   actual_Flag1_truth_assignments=actual_flag_truth(p, exact),
                   independent_vote_obstruction=pair_validation_obstruction(p, exact),
                   pulse_certificate=pulse_certificate(),
                   quieting_certificate=quieting_certificate(p),
                   old_maintenance=old_count, proposed_maintenance=new_count,
                   extra_maintenance_gates=new_count["gates"]-old_count["gates"],
                   extra_observed_fields=["Flag1 at +6", "Flag1 at +7", "Flag1 at +8"],
                   maintenance_state_bits_added=0, proposed_rule_radius=8,
                   active_rule_changed=False, implemented_self_simulating_candidate=False,
                   proof_scope=["healthy local structural two-fault correction", "joint quiet right ancestry",
                                "conditional E0 pulse speed exceeding five", "unpunctured quiet-path interception",
                                "conditional source-free aligned flag quieting"],
                   not_proved=["pulse initialization at every island", "inside-mask compatibility",
                               "mixed E0 path restarts", "new gather/schema/ROM self-interpreter",
                               "noisy island restoration", "upper error footprints", "positive-noise reliability"])
    output = ROOT / "figs/robustness/fast_flag_proposal_certificate.json"
    output.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()
