#!/usr/bin/env python3
"""Universal local certificate for the paired Address/clock extension J16.

Two Address colours carry two coherent Age words. The clocks are free
Boolean words in the local certificate; the global theorem additionally
keeps both legal clock trajectories out of Workspace launch ages while
needed. No claim is made for mixed clocks within one Address colour.
"""
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from gacsca import candidates
from gacsca.netlist import Net, const_word, at_least, w_mux, mixed_age_increment, w_in_range
import proposed_sparse_quiet as proposed
import check_quiet_majority_proposal as diagnostic
import check_sparse_phase_repair as phase
from check_fast_flag_proposal import invoke
from check_right_barrier import certified_build


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def colour_case(p, build, colours, selected_address, variant):
    net = Net()
    ages = {colour: [net.input(("Age_colour", colour, bit)) for bit in range(p.m)]
            for colour in (0, 1)}
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
            cells[j] = dict(addr=const_word((words[colour]+j) % p.Q, p.k), age=ages[colour],
                            f1=flags[j] if j >= 0 else 0, f2=0, wf1=0, wf2=0)
    actual = invoke(build, net, cells, p)
    mismatch = [int(colours[-j] != right and selected_address >= j) for j in range(1, 6)]
    src = int(sum(mismatch) >= 3)
    radius = 8 if variant == "SP2" else 5
    sampled = [flags[j] if selected_address+j < p.Q else 0 for j in range(1, radius+1)]
    quiet_matches = [net.NOT(flags[j]) if colours[j] == right else 0 for j in range(1, 6)]
    guard = (net.NOT(at_least(net, quiet_matches, 3))
             if variant == "SP2" and selected_address < p.Q-5 else 0)
    expected_flag = net.any([src, at_least(net, sampled, 3),
                             net.AND(flags[0], at_least(net, sampled, 2)), guard])
    expected_address = w_mux(net, expected_flag, const_word(words[left], p.k),
                            const_word(words[right], p.k))
    # Use the circuit's right-vote orientation. The elementary certificate
    # algebra does not distribute XOR over AND to reverse a symbolic mux.
    expected_age_now = w_mux(net, net.NOT(expected_flag), ages[right], ages[left])
    expected_age = mixed_age_increment(net, expected_age_now, p.PB, p.R, p.nb)
    ids = phase.term_ids(net)
    assert ids[actual["f1"]] == ids[expected_flag], (variant, colours, selected_address)
    assert actual["f2"] == 0
    for key, expected in (("addr", expected_address), ("age_now", expected_age_now), ("age", expected_age)):
        assert all(ids[a] == ids[b] for a, b in zip(actual[key], expected)), (variant, key, colours, selected_address)


def two_colour_certificate(p, build, variant):
    radius = 8 if variant == "SP2" else 5
    regimes = tuple(range(6))+tuple(range(p.Q-radius, p.Q))
    coordinates = tuple(range(-5, 0))+tuple(range(1, 6))
    count = 0
    for bits in range(1 << 10):
        colours = {j: (bits >> i) & 1 for i, j in enumerate(coordinates)}
        for selected in regimes:
            colour_case(p, build, colours, selected, variant)
            count += 1
        if bits % 256 == 255:
            print(f"{variant}: paired clocks, {count} symbolic cases", flush=True)
    return dict(symbolic_cases=count, colour_neighbourhoods=1024,
                inside_guard_regimes=len(regimes), free_Age_bits=2*p.m,
                free_Flag1_bits=9, Address_Age_votes_select_same_colour=True,
                scope="universal local paired-clock identity; all two Age-word assignments")


def prefix_certificate(p, build):
    count = 0
    for offset, values in ((0, range(3, p.Q)), (1, range(5, p.Q)),
                           (2, range(5, p.Q)), (3, range(5, p.Q))):
        for value in values:
            net = Net()
            ages = {colour: [net.input(("Age_colour", colour, bit)) for bit in range(p.m)]
                    for colour in (0, 1)}
            cells = {}
            for j in range(-5, 9):
                flag = net.input(("Flag1", j))
                if j >= 6:
                    cells[j] = dict(f1=flag)
                else:
                    bad = (-j < offset) if j < 0 else (1 <= j <= 3)
                    A = value if bad else 0
                    cells[j] = dict(addr=const_word((A+j) % p.Q, p.k), age=ages[int(bad)],
                                    f1=flag, f2=0, wf1=0, wf2=0)
            actual = invoke(build, net, cells, p)
            expected_age = mixed_age_increment(net, ages[0], p.PB, p.R, p.nb)
            ids = phase.term_ids(net)
            assert actual["f1"] == 1 and actual["f2"] == 0
            assert actual["addr"] == const_word(0, p.k)
            assert all(ids[a] == ids[b] for a, b in zip(actual["age_now"], ages[0]))
            assert all(ids[a] == ids[b] for a, b in zip(actual["age"], expected_age))
            count += 1
    return dict(symbolic_cases=count, both_Age_words_free=True,
                correct_Address_and_Age_from_protected_left_prefix=True)


def quiet_clock_certificate(p, geometry_bound, flag_bound):
    cases = 0
    # Actual integer circuit predicates for every legal tick before the
    # launch interval, including the last one. Packing is monotone there.
    for tick in range(p.T_wf):
        net = Net()
        active = w_in_range(net, const_word(p.age_code(tick), p.m),
                            p.age_code(p.T_wf), p.age_code(p.T_wf+2*p.Q-1)+1)
        assert active == 0, tick
        cases += 1
    assert p.T_wf < p.U
    return dict(actual_quiet_launch_predicate_cases=cases,
                maximum_initial_good_clock_tick=p.T_wf-flag_bound,
                maximum_initial_bad_clock_tick=p.T_wf-geometry_bound,
                good_clock_required_quiet_through_input=flag_bound-1,
                bad_clock_required_quiet_through_input=geometry_bound-1,
                legal_clock_encoding="Params.age_code(tick)",
                no_wrap_during_repair=True)


def main():
    out = ROOT / "figs/robustness"
    base = json.loads((out / "SP2_coherent_phase_certificate.json").read_text())
    sp2 = proposed.load_artifact()
    g17 = candidates.load("G17")
    assert sp2.digest() == base["proposed_candidate_sha256"]
    assert candidates.digests(g17) == {key: base["G17"][key] for key in candidates.digests(g17)}
    build2, source = diagnostic.proposed_build(symbolic=True)
    result = dict(proposed_rule_change=False, active_G17_modified=False,
                  proposal_rule_scope="unchanged G17 and separately specified SP2",
                  checker_sha256=digest(Path(__file__)),
                  phase_checker_sha256=digest(ROOT / "Report/proofs/check_sparse_phase_repair.py"),
                  base_proof_receipt_sha256=digest(out / "SP2_coherent_phase_certificate.json"),
                  quiet_majority_checker_sha256=digest(ROOT / "Report/proofs/check_quiet_majority_proposal.py"),
                  majority_shortcut_sha256=digest(ROOT / "Report/proofs/check_right_barrier.py"),
                  algebra_checker_sha256=digest(ROOT / "Report/proofs/check_g17_schedule.py"),
                  helpers_sha256=digest(ROOT / "gacsca/netlist.py"),
                  SP2_proposal_source_sha256=digest(Path(proposed.__file__)),
                  SP2_candidate_sha256=sp2.digest(), SP2_netlist_sha256=sp2.comp.digest,
                  global_reliability_established=False, results={})
    for name, candidate, build, geom, flags in (("G17", g17, certified_build(), 588, 800),
                                               ("SP2", sp2, build2, 631, 847)):
        result["results"][name] = dict(two_colour=two_colour_certificate(candidate.p, build, name),
                                      prefix=prefix_certificate(candidate.p, build),
                                      quiet_clocks=quiet_clock_certificate(candidate.p, geom, flags))
    result["G17_digests"] = candidates.digests(g17)
    (out / "paired_phase_certificate.json").write_text(json.dumps(result, indent=2)+"\n")
    print(json.dumps({name: item["quiet_clocks"] for name, item in result["results"].items()}, indent=2))


if __name__ == "__main__":
    main()
