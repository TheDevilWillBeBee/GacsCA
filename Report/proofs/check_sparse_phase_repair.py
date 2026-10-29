#!/usr/bin/env python3
"""Local certificate for the G17/SP2 coherent-phase repair theorems.

The unbounded-line proof is in ROBUSTNESS section 12. The certificate
checks its exact two-colour reduction and prefix/barrier lemmas with
free Flag1 bits and a free common Age, plus the displayed bounds. It
does not establish arbitrary whole-state-error or iid-noise reliability.
"""
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from gacsca import candidates
from gacsca.netlist import Net, const_word, at_least, w_mux, w_add_const_mod, mixed_age_increment
import proposed_sparse_quiet as proposed
import check_quiet_majority_proposal as diagnostic
from check_fast_flag_proposal import invoke
from check_right_barrier import check_dominance_primitive, certified_build
from check_g17_schedule import Terms


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def term_ids(net):
    terms = Terms()
    values = []
    for i, kind in enumerate(net.kind):
        if kind == "C0":
            value = 0
        elif kind == "C1":
            value = 1
        elif kind == "IN":
            value = terms.var(next(name for name, node in net.input_node.items() if node == i))
        else:
            op, a, b = net.gate[i]
            value = terms.op(op, values[a], values[b])
        values.append(value)
    return values


def arithmetic_identity(p):
    cases = 0
    for A in range(p.Q):
        for offset in range(-8, 9):
            net = Net()
            actual = w_add_const_mod(net, const_word(A, p.k), offset % p.Q, p.Q)
            assert actual == const_word((A+offset) % p.Q, p.k)
            cases += 1
    return cases


def colour_case(p, build, colours, selected_address, variant):
    net = Net()
    common = [net.input(("common_Age", bit)) for bit in range(p.m)]
    flags = {j: net.input(("Flag1", j)) for j in range(9)}
    right = int(sum(colours[j] for j in range(1, 6)) >= 3)
    left = int(sum(colours[j] for j in range(-5, 0)) >= 3)
    words = {right: selected_address, 1-right: (selected_address+101) % p.Q}
    cells = {}
    for j in range(-5, 9):
        if j >= 6:
            cells[j] = dict(f1=flags[j])
        else:
            colour = colours.get(j, 0)
            cells[j] = dict(addr=const_word((words[colour]+j) % p.Q, p.k), age=common,
                            f1=flags[j] if j >= 0 else 0, f2=0, wf1=0, wf2=0)
    actual = invoke(build, net, cells, p)
    # Independent two-colour specification: words disappear, leaving
    # colour counts and the inside mask of the selected right word.
    mismatch = [int(colours[-j] != right and selected_address >= j) for j in range(1, 6)]
    src = int(sum(mismatch) >= 3)
    flag_radius = 8 if variant == "SP2" else 5
    sampled = [flags[j] if selected_address+j < p.Q else 0 for j in range(1, flag_radius+1)]
    quiet_matches = [net.NOT(flags[j]) if colours[j] == right else 0 for j in range(1, 6)]
    guard = (net.NOT(at_least(net, quiet_matches, 3))
             if variant == "SP2" and selected_address < p.Q-5 else 0)
    expected_flag = net.any([src, at_least(net, sampled, 3),
                             net.AND(flags[0], at_least(net, sampled, 2)), guard])
    expected_address = w_mux(net, expected_flag, const_word(words[left], p.k),
                            const_word(words[right], p.k))
    expected_age = mixed_age_increment(net, common, p.PB, p.R, p.nb)
    ids = term_ids(net)
    assert ids[actual["f1"]] == ids[expected_flag], (colours, selected_address)
    assert actual["f2"] == 0
    assert all(ids[a] == ids[b] for a, b in zip(actual["addr"], expected_address))
    assert actual["age_now"] == common and actual["age"] == expected_age


def two_colour_certificate(p, build, variant):
    # These are all distinct inside/guard regimes. The other phase word
    # matters only through equality/inequality, not its numerical value.
    flag_radius = 8 if variant == "SP2" else 5
    regimes = tuple(range(6)) + tuple(range(p.Q-flag_radius, p.Q))
    seen = set()
    for A in range(p.Q):
        signature = (tuple(A >= j for j in range(1, 6)),
                     tuple(A+j < p.Q for j in range(1, flag_radius+1)),
                     variant == "SP2" and A < p.Q-5)
        seen.add(signature)
    representatives = {(tuple(A >= j for j in range(1, 6)),
                        tuple(A+j < p.Q for j in range(1, flag_radius+1)),
                        variant == "SP2" and A < p.Q-5)
                       for A in regimes}
    assert seen == representatives and len(regimes) == len(seen)
    coordinates = tuple(range(-5, 0)) + tuple(range(1, 6))
    count = 0
    for bits in range(1 << 10):
        colours = {j: (bits >> i) & 1 for i, j in enumerate(coordinates)}
        for selected in regimes:
            colour_case(p, build, colours, selected, variant)
            count += 1
        if bits % 256 == 255:
            print(f"{variant}: certified colour patterns 0..{bits}: {count} symbolic cases", flush=True)
    return dict(colour_neighbourhoods=1024, inside_guard_regimes=len(regimes),
                symbolic_cases=count, free_Flag1_bits_per_case=9,
                free_common_Age_bits_per_case=p.m,
                scope="exact two-colour maintenance reduction, all Flag1 assignments; not a sampled trajectory")


def prefix_case(p, build, value, new_offset):
    net = Net()
    age = [net.input(("common_Age", bit)) for bit in range(p.m)]
    cells = {}
    for j in range(-5, 9):
        flag = net.input(("Flag1", j))
        if j >= 6:
            cells[j] = dict(f1=flag)
        else:
            if j < 0:
                bad = -j < new_offset
            else:
                bad = 1 <= j <= 3
            A = value if bad else 0
            cells[j] = dict(addr=const_word((A+j) % p.Q, p.k), age=age,
                            f1=flag, f2=0, wf1=0, wf2=0)
    out = invoke(build, net, cells, p)
    assert out["f1"] == 1 and out["f2"] == 0
    assert out["addr"] == const_word(0, p.k)
    assert out["age_now"] == age


def prefix_certificate(p, build):
    preserved = advanced = 0
    for value in range(3, p.Q):
        prefix_case(p, build, value, 0)
        preserved += 1
    for value in range(5, p.Q):
        for offset in (1, 2, 3):
            prefix_case(p, build, value, offset)
            advanced += 1
    return dict(five_good_left_cases=preserved, far_left_three_good_cases=advanced,
                all_observed_Flag1_bits_free=True,
                proof_factorization="valid-phase addition and distinct phases make all opposite-colour comparisons false; only selected bad Address controls the mask")


def suffix_certificate(p, build):
    count = 0
    for A in range(p.Q):
        net = Net()
        common = [net.input(("common_Age", bit)) for bit in range(p.m)]
        cells = {}
        for j in range(-5, 9):
            same_colony = 0 <= A+j < p.Q
            flag = 0 if same_colony else net.input((j, "f1"))
            if j >= 6:
                cells[j] = dict(f1=flag)
                continue
            if j < 0 and not same_colony:
                addr = [net.input((j, "addr", bit)) for bit in range(p.k)]
                age = [net.input((j, "age", bit)) for bit in range(p.m)]
            else:
                addr, age = const_word((A+j) % p.Q, p.k), common
            cells[j] = dict(addr=addr, age=age, f1=flag,
                            f2=net.input((j, "f2")), wf2=net.input((j, "wf2")),
                            wf1=0 if same_colony else net.input((j, "wf1")))
        out = invoke(build, net, cells, p)
        assert out["f1"] == 0 and out["addr"] == const_word(A, p.k)
        assert out["age_now"] == common
        count += 1
    return dict(symbolic_addresses=count, arbitrary_outside_colony_left_words=True,
                arbitrary_outside_colony_flags=True,
                hypothesis="first protected true colony has Flag1 and Workspace.Flag1 zero; suffix geometry canonical/common")


def bound_certificate(p, variant, maximum_width, quiet_threshold, flag_clearance):
    rows = []
    for width in range(1, maximum_width+1):
        maximum_startup_extent = width+5
        quiet_updates = (maximum_startup_extent+quiet_threshold-1)//quiet_threshold
        # Through both prefix-advance updates every possible wrong
        # Address lies below Q-5; a near-end quiet birth is impossible.
        assert maximum_startup_extent-1+3*(quiet_updates+2) < p.Q-5
        if quiet_threshold == 3:
            assert 2*maximum_startup_extent+7 < p.Q-5
        else:
            assert 4*maximum_startup_extent+5 < p.Q-5
        travel = p.Q+width+4
        geometry_bound = travel+2*(quiet_updates+2)
        flags_bound = geometry_bound+flag_clearance
        assert flags_bound < p.T_wf
        assert geometry_bound < p.U//32
        rows.append(dict(width=width, maximum_startup_extent=maximum_startup_extent,
                         maximum_startups=2, quiet_updates=quiet_updates,
                         geometric_repair_bound=geometry_bound,
                         Flag1_clearance_bound=flags_bound))
    expected = {"G17": (588, 800), "SP2": (631, 847)}[variant]
    assert (rows[-1]["geometric_repair_bound"], rows[-1]["Flag1_clearance_bound"]) == expected
    return dict(widths=rows, initial_physical_Age=0,
                clock_source_free_until_input=p.T_wf, compared_with_U_over_32=p.U//32,
                scope="deterministic noiseless single-coherent-phase seed; not arbitrary clocks/flags or continuing E0")


def main():
    candidate = proposed.load_artifact()
    p = candidate.p
    assert candidate.digest() == "0fc552fbe43de355bb5ae45146de04bddc1fe00e9e26c2a647193a787d100cba"
    build, source = diagnostic.proposed_build(symbolic=True)
    g17 = candidates.load("G17")
    assert g17.digest() == "23a14aab4d3dc4fde5562cf3e26a4536b05456f84e65850fcb3bd95a104d8ceb"
    g17_build = certified_build()
    result = dict(proposal="SP2", proposed_rule_change=True, active_G17_modified=False,
                  proposed_candidate_sha256=candidate.digest(), proposed_netlist_sha256=candidate.comp.digest,
                  checker_sha256=digest(Path(__file__)), proposal_source_sha256=digest(Path(proposed.__file__)),
                  helpers_sha256=digest(ROOT / "gacsca/netlist.py"),
                  majority_shortcut_sha256=digest(ROOT / "Report/proofs/check_right_barrier.py"),
                  algebra_checker_sha256=digest(ROOT / "Report/proofs/check_g17_schedule.py"),
                  quiet_majority_checker_sha256=digest(ROOT / "Report/proofs/check_quiet_majority_proposal.py"),
                  guarded_maintenance_source_sha256=hashlib.sha256(source.encode()).hexdigest(),
                  actual_majority_primitive_assignments=check_dominance_primitive(),
                  valid_Address_addition_cases=arithmetic_identity(p),
                  two_colour=two_colour_certificate(p, build, "SP2"),
                  prefix=prefix_certificate(p, build), protected_suffix=suffix_certificate(p, build),
                  bounds=bound_certificate(p, "SP2", 141, 3, 216),
                  G17=dict(**candidates.digests(g17),
                           two_colour=two_colour_certificate(g17.p, g17_build, "G17"),
                           prefix=prefix_certificate(g17.p, g17_build),
                           protected_suffix=suffix_certificate(g17.p, g17_build),
                           bounds=bound_certificate(g17.p, "G17", 62, 1, 212)),
                  global_reliability_established=False,
                  scope="universal local/arithmetic certificate supporting the stated coherent-phase theorem; not iid-noise reliability")
    output = ROOT / "figs/robustness/SP2_coherent_phase_certificate.json"
    output.write_text(json.dumps(result, indent=2)+"\n")
    print(json.dumps({key: result[key] for key in ("two_colour", "prefix", "protected_suffix")}, indent=2))
    print(json.dumps(result["bounds"]["widths"][-1], indent=2))


if __name__ == "__main__":
    main()
