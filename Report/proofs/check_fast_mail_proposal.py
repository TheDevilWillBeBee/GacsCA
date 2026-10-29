#!/usr/bin/env python3
"""Boolean/arithmetic certificate for an EXPLICITLY PROPOSED mail module.

This is not the active rule, a complete new candidate, or a reliability
experiment. It checks voted speed-eight gathers, speed-one couriers,
the five-copy dependency coordinates, E0 spacing and capture arithmetic.
No compiler, schema, candidate or ROM is modified.
"""
from itertools import combinations
import hashlib
import inspect
import json
from pathlib import Path
import sys
from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
import numpy as np
from gacsca import candidates, gray_errors, rule_g
from gacsca.netlist import Net, Compiled, w_eq_const, w_in_range
from check_right_barrier import dominant_majority, check_dominance_primitive
from check_fast_flag_proposal import proposed_build as proposed_maintenance

SLOTS = tuple(range(-2, 3))
SPEED = 8


def proposed_module(net, vote, control):
    """Proposed five-copy outputs, relative to physical holder zero.

    vote(field,z) reads the corrected value at logical primary z.
    Controls are reference controls shared by the five holders of z.
    Computed Flag1 is zero; output wipes and new overwrites are accounted
    for separately by the Z_t invariant, not suppressed in the active rule.
    One history lane per direction is enough: the formula is lane-wise.
    """
    out = {}
    for slot in SLOTS:
        load = control("load", slot)
        fast = control("fast", slot)
        commit = control("commit", slot)
        info, hold = vote("info", slot), vote("hold", slot)
        for direction, field, courier in ((-1, "mr", "cr"), (1, "ml", "cl")):
            shifted = net.MUX(fast, vote(field, slot + direction * SPEED),
                              vote(field, slot + direction))
            mail = net.MUX(load, info,
                           net.MUX(control(courier, slot), hold, shifted))
            out[field, slot] = net.AND(mail, net.NOT(commit))
            h1, h2 = vote("h1_" + field, slot), vote("h2_" + field, slot)
            passing = vote(field, slot)  # old mail, before this tick's shift
            h1n = net.MUX(control("capture0_" + field, slot), passing, h1)
            h1n = net.MUX(control("capture2_" + field, slot),
                           rule_g.maj3(net, h1, h2, passing), h1n)
            h2n = net.MUX(control("capture1_" + field, slot), passing, h2)
            out["h1_" + field, slot] = net.AND(h1n, net.NOT(commit))
            out["h2_" + field, slot] = net.AND(h2n, net.NOT(commit))
    return out


def maj5_truth():
    net = Net()
    inputs = [net.input(("bit", j)) for j in range(5)]
    net.set_output(("vote",), rule_g.maj5(net, inputs))
    assignments = np.arange(32, dtype=np.uint32)
    values = {("bit", j): ((assignments >> j) & 1).astype(bool) for j in range(5)}
    got = Compiled(net).evaluate(values, bool)["vote",]
    expected = np.array([int(x).bit_count() >= 3 for x in assignments])
    assert np.array_equal(got, expected)
    return len(assignments)


def symbolic_copy_case(faults):
    net = Net()
    correct = lambda field, primary: net.input(("reference", field, primary))
    control = lambda kind, primary: net.input(("control", kind, primary))
    support = set()

    def voted(field, primary):
        copies = []
        for slot in SLOTS:
            holder = primary - slot
            support.add(holder)
            bit = (net.input(("fault", field, holder, slot)) if holder in faults
                   else correct(field, primary))
            copies.append([bit])
        result, exists = dominant_majority(net, copies, [0])
        assert exists == 1
        return result[0]

    actual = proposed_module(net, voted, control)
    reference = proposed_module(net, correct, control)
    assert actual == reference, faults
    assert min(support) == -12 and max(support) == 12
    return len(actual)


def dependency_certificate():
    net = Net()
    supports = {}

    def vote(field, primary):
        holders = tuple(primary - slot for slot in SLOTS)
        supports[field, primary] = holders
        return rule_g.maj5(net, [net.input(("raw", field, holder, slot))
                                for holder, slot in zip(holders, SLOTS)])

    controls = lambda kind, primary: net.input(("control", kind, primary))
    for key, node in proposed_module(net, vote, controls).items():
        net.set_output(key, node)
    used = [key for key in net.used_inputs() if key[0] == "raw"]
    holders = [key[2] for key in used]
    assert min(holders) == -12 and max(holders) == 12
    assert all(max(xs) - min(xs) == 4 for xs in supports.values())
    mr = sorted({key[2] for key in used if key[1] == "mr" and key[2] <= -4})
    ml = sorted({key[2] for key in used if key[1] == "ml" and key[2] >= 4})
    assert mr == list(range(-12, -3)) and ml == list(range(4, 13))
    return dict(radius=12, slot_count=5, voter_span=4,
                fast_MR_holder_range=[-12, -4], fast_ML_holder_range=[4, 12],
                gates=net.gate_count(), inputs=len(net.input_names),
                scope="mail/history module only; controls already correct")


def spacing_certificate():
    # A five-holder voter at adjacent state times cannot meet two E0
    # groups: every two such points are (24,24)-linked.
    local = [(x, t) for x in range(5) for t in (-1, 0)]
    linked_pairs = 0
    for a, b in combinations(local, 2):
        assert gray_errors.linked({a}, {b}, 24, 24)
        linked_pairs += 1

    # Even the complete radius-12 input interval meets at most two raw
    # damaged holders across Z_t, despite possibly meeting two groups.
    # Three distinct holders in an interval of diameter 24 would require
    # two separated groups, one a pair; the nearest cross distance is <24.
    triples = 0
    for xs in combinations(range(-12, 13), 3):
        for times in range(8):
            points = {(x, -((times >> j) & 1)) for j, x in enumerate(xs)}
            assert gray_errors.level0_points(points) != points
            triples += 1
    two_groups = {(-12, 0), (12, -1)}
    assert gray_errors.level0_points(two_groups) == two_groups
    # At the prospective reduced upper spacing (22,23), the whole input
    # interval can contain four bad holders. Each constituent voter still
    # meets one group. Do not transfer the global two-holder bound there.
    reduced = (-12, -11, 11, 12)
    assert reduced[2] - reduced[1] == 22
    for primary in range(-10, 11):
        assert len(set(reduced) & set(range(primary - 2, primary + 3))) <= 2
    return dict(voter_linked_pairs=linked_pairs,
                forbidden_three_holder_patterns=triples,
                two_group_endpoint_example=sorted(map(list, two_groups)),
                largest_raw_error_holder_count_in_25_sites=2,
                reduced_spacing=[22, 23], reduced_four_holder_example=list(reduced),
                reduced_global_two_holder_bound=False,
                scope="separated groups in current/previous rows; not mixed higher damage")


def capture_age(Q, off, skew, gather):
    assert Q % SPEED == skew % SPEED == 0 and off != 0
    sign = 1 if off > 0 else -1
    return gather + abs(off) * (Q // SPEED) + 1 - sign * (skew // SPEED)


def capture_certificate():
    cases = 0
    for Q in (384, 512, 576, 768):
        for off in range(-12, 13):
            if off == 0:
                continue
            sign = 1 if off > 0 else -1
            for skew in range(-96, 97, 8):
                for gather in (0, 10 * Q, 20 * Q):
                    age = capture_age(Q, off, skew, gather)
                    tau = age - gather - 1
                    assert tau >= 0
                    # p=mQ+L+skew; source p+sign*8*tau=(m+off)Q+L.
                    assert skew + sign * SPEED * tau == off * Q
                    cases += 1
    Q = 384
    deadlines = []
    for gather in (0, 10 * Q, 20 * Q):
        times = [capture_age(Q, off, skew, gather)
                 for off in range(-12, 13) if off != 0 for skew in (-8, 0, 8)]
        deadlines.append(max(times))
    assert deadlines == [578, 4418, 8258]
    assert deadlines[0] < 3840 and deadlines[1] < 7680 and deadlines[2] < 9792
    assert 9792 - deadlines[2] == 1534
    cand = candidates.load("G17")
    a_l, a_r = cand.p.courier_ticks()[1:]
    assert deadlines[-1] < min(a_l, a_r)
    return dict(identity_cases=cases, illustrative_Q=Q,
                illustrative_gathers=[0, 3840, 7680],
                illustrative_offsets=[-12, 12], illustrative_skews=[-8, 0, 8],
                latest_capture_input_ages=deadlines, evaluation_input_age=9792,
                latest_capture_to_evaluation=1534,
                G17_courier_input_ages=[a_l, a_r],
                G17_skews_reused=False,
                scope="capture arithmetic only; illustrative values do not define a candidate")


def storage_certificate():
    p = candidates.load("G17").p
    old_width = rule_g.width(p)
    extra_lanes = 24 - len(rule_g.LANE_OFFSETS)
    extra_history_bits = 2 * 5 * extra_lanes
    assert old_width == 258 and extra_history_bits == 140
    proposed_partial_width = old_width + extra_history_bits
    assert proposed_partial_width == 398
    # This alone excludes a dense-lane implementation with current Q384.
    assert proposed_partial_width > p.Q - 2 * p.margin
    return dict(G17_raw_width=old_width, old_lanes=10, dense_radius12_lanes=24,
                added_raw_history_bits=extra_history_bits,
                width_before_other_repacking=proposed_partial_width,
                G17_work_cells=p.Q - 2 * p.margin,
                current_Q384_layout_impossible_with_this_dense_schema=True,
                scope="fixed G17 packing plus dense history extension; not an obstruction to sparse gathers")


def sparse_controls(net, p, age, address, rank, table):
    """Fixed finite capture lookup for a zero-skew sparse layout.

    table rows specify the represented bit at each layout address and
    its ordered nonzero neighbor offsets. All controls depend only on
    corrected geometry, with no new external input or stored field.
    """
    selected = {}
    for row in table:
        if rank < len(row["offsets"]):
            off = row["offsets"][rank]
            selected.setdefault(off, []).append(row["address"])

    def member(addresses):
        # Exact interval coalescing is only a Boolean size optimization.
        addresses = sorted(addresses)
        runs = []
        for value in addresses:
            if runs and value == runs[-1][1]:
                runs[-1][1] += 1
            else:
                runs.append([value, value + 1])
        return net.any(w_eq_const(net, address, lo) if hi == lo + 1 else
                       w_in_range(net, address, lo, hi) for lo, hi in runs)

    matches = {off: member(addresses) for off, addresses in selected.items()}
    captures = [net.any(net.AND(match, w_eq_const(net, age, p.age_code(
                    gather * p.Q + abs(off) * (p.Q // SPEED) + 1)))
                for off, match in matches.items()) for gather in p.gathers_q]
    negative = net.any(match for off, match in matches.items() if off < 0)
    return captures, negative


def concrete_sparse_net(p, table):
    """Explicit proposed circuit with fixed sparse captures; NO own ROM yet."""
    source = inspect.getsource(rule_g.build)
    start = "    load_mail = n.any(gather_start)"
    fast = """    load_mail = n.any(gather_start)
    fast_mail = n.any(w_in_range(n, age_now, p.age_code(g * Q + 1),
                                 p.age_code(g * Q + 12 * (Q // 8) + 1))
                      for g in p.gathers_q)"""
    capture_block_start = source.index("    capture = []   # capture[g][lane idx]")
    capture_block_end = source.index("    wipe = n.AND", capture_block_start)
    source = source[:capture_block_start] + source[capture_block_end:]
    replacements = [
        (start, fast),
        ("lv(x - 1, 'mr')))",
         "n.MUX(fast_mail, lv(x - 8, 'mr'), lv(x - 1, 'mr'))))"),
        ("lv(x + 1, 'ml')))",
         "n.MUX(fast_mail, lv(x + 8, 'ml'), lv(x + 1, 'ml'))))"),
        ("            passing = lv(x, 'mr') if off < 0 else lv(x, 'ml')",
         """            caps, negative = sparse_controls(n, p, age_now, xaddr, idx, sparse_table)
            passing = n.MUX(negative, lv(x, 'mr'), lv(x, 'ml'))"""),
        ("n.MUX(capture[0][idx], passing, h1)", "n.MUX(caps[0], passing, h1)"),
        ("n.MUX(capture[2][idx], maj3(n, h1, h2, passing), h1n)",
         "n.MUX(caps[2], maj3(n, h1, h2, passing), h1n)"),
        ("n.MUX(capture[1][idx], passing, h2)", "n.MUX(caps[1], passing, h2)"),
    ]
    for old, new in replacements:
        assert source.count(old) == 1, old
        source = source.replace(old, new)
    namespace = dict(rule_g.__dict__)
    maintenance_build, _ = proposed_maintenance()
    namespace.update(maintenance=SimpleNamespace(build=maintenance_build),
                     OFFSETS=tuple(range(-12, 13)), sparse_controls=sparse_controls,
                     sparse_table=table)
    exec(compile(source, "<proposed fixed sparse circuit, not compiled candidate>", "exec"), namespace)
    net = namespace["build"](p)
    assert all(name[0] in ("x", "I") for name in net.input_names)
    return net, source


def fixed_capture_certificate(p, table):
    cases = 0
    # Exhaust all Address words, all ten ranks and all ages at which this
    # table can capture (plus the immediately neighboring ages). Outside
    # these ages every equality factor is identically false.
    ages = {g * p.Q + abs(off) * (p.Q // SPEED) + 1 + shift
            for g in p.gathers_q for off in range(1, 13) for shift in (-1, 0, 1)}
    assignments = [(address, age) for address in range(1 << p.k) for age in sorted(ages)]
    address_values = np.array([a for a, _ in assignments], dtype=np.uint32)
    age_values = np.array([p.age_code(t) for _, t in assignments], dtype=np.uint32)
    by_address = {row["address"]: row["offsets"] for row in table}
    for rank in range(10):
        net = Net()
        address = [net.input(("address", i)) for i in range(p.k)]
        age = [net.input(("age", i)) for i in range(p.m)]
        captures, negative = sparse_controls(net, p, age, address, rank, table)
        for g, bit in enumerate(captures):
            net.set_output(("capture", g), bit)
        net.set_output(("negative",), negative)
        values = {("address", i): ((address_values >> i) & 1).astype(bool) for i in range(p.k)}
        values.update({("age", i): ((age_values >> i) & 1).astype(bool) for i in range(p.m)})
        got = Compiled(net).evaluate(values, bool)
        off = np.array([by_address[a][rank] if a in by_address and rank < len(by_address[a]) else 0
                        for a in address_values], dtype=np.int32)
        assert np.array_equal(got["negative",], off < 0)
        for g in range(3):
            expected = (off != 0) & (np.array([t for _, t in assignments]) ==
                        p.gathers_q[g] * p.Q + np.abs(off) * (p.Q // SPEED) + 1)
            assert np.array_equal(got["capture", g], expected)
        cases += len(assignments)
    return cases


def sparse_profile_certificate():
    """Dependency envelope, NOT a runnable candidate or a compiled program.

    Free timing/direction controls cover all per-primary capture tables.
    They must eventually be replaced by fixed functions of corrected
    Address/Age. That adds only the already present [-5,5] geometry inputs.
    """
    p = candidates.load("G17").p
    source = inspect.getsource(rule_g.build)
    replacements = [
        ("    load_mail = n.any(gather_start)",
         "    load_mail = n.any(gather_start)\n    fast_mail = n.input(('proof_control', 'fast'))"),
        ("lv(x - 1, 'mr')))",
         "n.MUX(fast_mail, lv(x - 8, 'mr'), lv(x - 1, 'mr'))))"),
        ("lv(x + 1, 'ml')))",
         "n.MUX(fast_mail, lv(x + 8, 'ml'), lv(x + 1, 'ml'))))"),
        ("            passing = lv(x, 'mr') if off < 0 else lv(x, 'ml')",
         """            passing = n.MUX(n.input(('proof_direction', x, idx)), lv(x, 'mr'), lv(x, 'ml'))
            caps = [n.input(('proof_capture', g, x, idx)) for g in range(3)]"""),
        ("n.MUX(capture[0][idx], passing, h1)", "n.MUX(caps[0], passing, h1)"),
        ("n.MUX(capture[2][idx], maj3(n, h1, h2, passing), h1n)",
         "n.MUX(caps[2], maj3(n, h1, h2, passing), h1n)"),
        ("n.MUX(capture[1][idx], passing, h2)", "n.MUX(caps[1], passing, h2)"),
    ]
    for old, new in replacements:
        assert source.count(old) == 1, old
        source = source.replace(old, new)
    namespace = dict(rule_g.__dict__)
    maintenance_build, _ = proposed_maintenance()
    namespace["maintenance"] = SimpleNamespace(build=maintenance_build)
    namespace["OFFSETS"] = tuple(range(-12, 13))
    exec(compile(source, "<dependency envelope, not a CA candidate>", "exec"), namespace)
    net = namespace["build"](p)
    live = set(net.live_nodes())
    used = [name for name, node in net.input_node.items() if node in live]
    profile = {(f, i): set() for f, width in rule_g.schema(p) for i in range(width)}
    for name in used:
        if name[0] == "x":
            _, offset, field, bit = name
            if offset:
                profile[field, bit].add(offset)
    largest = max(map(len, profile.values()))
    assert largest == 10
    assert profile["f1", 0] == set(range(1, 9))
    # Other than Mail, all dependencies still lie in the old neighborhood.
    for (field, bit), offsets in profile.items():
        if field not in ("mr", "ml"):
            assert all(-5 <= x <= 5 for x in offsets) or field == "f1"
    # Zero skew gives an injective (primary,history-rank) location for
    # each used input, with the own-cell bit remaining on Info.
    addresses = [a for a in range(p.lo, p.hi)
                 if a not in rule_g.reserved_cells(p)][:len(profile)]
    assert len(addresses) == len(profile) == 258
    locations = {}
    serialized = []
    for ((field, bit), offsets), address in zip(profile.items(), addresses):
        ranks = {offset: rank for rank, offset in enumerate(sorted(offsets))}
        for offset, rank in ranks.items():
            location = (address, rank)
            assert location not in locations
            locations[location] = (offset, field, bit)
        serialized.append(dict(field=field, bit=bit, address=address,
                               offsets=sorted(offsets)))
    counts = {field: max(len(xs) for (f, _), xs in profile.items() if f == field)
              for field, _ in rule_g.schema(p)}
    concrete, concrete_source = concrete_sparse_net(p, serialized)
    live_concrete = set(concrete.live_nodes())
    covered_inputs = 0
    for name, node in concrete.input_node.items():
        if name[0] == "x" and node in live_concrete:
            _, off, field, bit = name
            assert off == 0 or off in profile[field, bit], name
            covered_inputs += 1
    return dict(
        envelope_source_sha256=hashlib.sha256(source.encode()).hexdigest(),
        fast_flag_checker_sha256=hashlib.sha256((ROOT / "Report/proofs/check_fast_flag_proposal.py").read_bytes()).hexdigest(),
        maximum_nonzero_offsets_per_raw_bit=largest,
        per_field_maximum_nonzero_offsets=counts,
        raw_state_width=258, history_slots_per_primary=10,
        assigned_nonzero_inputs=len(locations), zero_skew_layout_cells=addresses,
        profile_sha256=hashlib.sha256(json.dumps(serialized, sort_keys=True).encode()).hexdigest(),
        profile=serialized,
        concrete_circuit_source_sha256=hashlib.sha256(concrete_source.encode()).hexdigest(),
        concrete_circuit_digest=concrete.digest(),
        concrete_circuit_gates=concrete.gate_count(),
        concrete_circuit_used_raw_inputs=covered_inputs,
        concrete_circuit_capture_controls_external=False,
        fixed_capture_assignments=fixed_capture_certificate(p, serialized),
        self_interpreter_compiled=False, complete_candidate=False,
        scope="fixed sparse capture circuit and complete input coverage; own interpreter/ROM and full simulation not proved")


def main():
    points = tuple(range(-12, 13))
    faults = [()] + [(x,) for x in points] + list(combinations(points, 2))
    outputs = sum(symbolic_copy_case(f) for f in faults)

    def separated_components(xs):
        groups = [[xs[0]]]
        for x in xs[1:]:
            if x == groups[-1][-1] + 1:
                groups[-1].append(x)
            else:
                groups.append([x])
        return (all(len(g) <= 2 for g in groups) and
                all(b[0] - a[-1] >= 22 for a, b in zip(groups, groups[1:])))

    reduced_patterns = [xs for k in (3, 4) for xs in combinations(points, k)
                        if separated_components(xs)]
    reduced_outputs = sum(symbolic_copy_case(f) for f in reduced_patterns)
    assert (-12, -11, 11, 12) in reduced_patterns
    result = dict(
        proposed_rule_change=True, active_rule_modified=False,
        complete_candidate=False, positive_noise_reliability_established=False,
        checker_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        module_source_sha256=hashlib.sha256(inspect.getsource(proposed_module).encode()).hexdigest(),
        majority_shortcut_sha256=hashlib.sha256((ROOT / "Report/proofs/check_right_barrier.py").read_bytes()).hexdigest(),
        netlist_helpers_sha256=hashlib.sha256((ROOT / "gacsca/netlist.py").read_bytes()).hexdigest(),
        full_rule_sha256=hashlib.sha256((ROOT / "gacsca/rule_g.py").read_bytes()).hexdigest(),
        classifier_sha256=hashlib.sha256((ROOT / "gacsca/gray_errors.py").read_bytes()).hexdigest(),
        majority_truth_assignments=maj5_truth(),
        whole_word_dominance_truth_assignments=check_dominance_primitive(),
        symbolic_copy_cases=len(faults), symbolic_output_equalities=outputs,
        reduced_spacing_extra_patterns=len(reduced_patterns),
        reduced_spacing_extra_output_equalities=reduced_outputs,
        symbolic_controls="load, speed, couriers, captures and commit free; already correctly computed",
        dependency=dependency_certificate(), spacing=spacing_certificate(),
        capture=capture_certificate(), storage=storage_certificate(),
        sparse_profile=sparse_profile_certificate(),
        scope="conditional local transport and timing certificate; no simulation or iid threshold")
    destination = ROOT / "figs/robustness/fast_mail_proposal_certificate.json"
    destination.write_text(json.dumps(result, indent=2) + "\n")
    summary = dict(result)
    summary["sparse_profile"] = {k: v for k, v in result["sparse_profile"].items()
                                 if k not in ("profile", "zero_skew_layout_cells")}
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
