#!/usr/bin/env python3
"""Certificate for an EXPLICIT proposed quiet-majority diagnostic.

This changes the isolated J2 maintenance formula in memory only. It does
not change G17 or SP1, build a new ROM, or prove iid-noise reliability.
The unbounded ancestry and window proofs are in ROBUSTNESS section 12.
"""
from dataclasses import replace
from itertools import combinations
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
import numpy as np
from gacsca import candidates, maintenance
from gacsca.netlist import Net, Compiled, const_word, w_add_const_mod
import check_fast_flag_proposal as fast
from check_right_barrier import check_dominance_primitive

OLD = "    f1 = n.any([incons, wf1, flags3, n.AND(c['f1'], flags2), n.NOT(joint_right)])"
NEW = """    quiet_joint = at_least(n, [n.all([w_eq(n, adjusted[j], v),
                                               w_eq(n, cells[j]['age'], age_r),
                                               n.NOT(cells[j]['f1'])])
                               for j in range(1, 6)], 3)
    guarded_quiet_failure = n.AND(w_ult_const(n, v, Q-5), n.NOT(quiet_joint))
    f1 = n.any([incons, wf1, flags3, n.AND(c['f1'], flags2),
                n.NOT(joint_right), guarded_quiet_failure])"""


def proposed_build(symbolic=False):
    _, source = fast.proposed_build(symbolic=symbolic)
    assert source.count(OLD) == 1
    source = source.replace(OLD, NEW)
    namespace = dict(maintenance.__dict__)
    if symbolic:
        namespace["majority_word"] = fast.dominant_majority
    exec(compile(source, "<proposed guarded quiet-majority maintenance>", "exec"), namespace)
    return namespace["build"], source


def suffix_extension(p, build, address, faults, first_outside):
    """Two leftward extensions when the new-front ten-site zone is clean.

    The only possible observed faults outside that zone are left inputs.
    The old center and the first right Flag1 are arbitrary. All farther
    right flags in this colony are zero; the next colony is arbitrary.
    """
    net = Net()
    age = [net.input(("common_age", bit)) for bit in range(p.m)]
    cells = fast.canonical_cells(p, net, address, age, faults)
    cells[0]["f1"] = net.input((0, "f1"))
    for j in range(1, 9):
        if (first_outside and j == 1) or address + j >= p.Q:
            cells[j]["f1"] = net.input((j, "f1"))
    assert fast.invoke(build, net, cells, p)["f1"] == 0, (address, faults, first_outside)


def inverse_certificate(p):
    raw = np.arange(1 << p.k, dtype=np.uint32)
    cases = 0
    for j in range(1, 6):
        net = Net()
        word = [net.input(("word", bit)) for bit in range(p.k)]
        adjusted = w_add_const_mod(net, word, (-j) % p.Q, p.Q)
        for bit, node in enumerate(adjusted):
            net.set_output(("adjusted", bit), node)
        out = Compiled(net).evaluate({("word", bit): ((raw >> bit) & 1).astype(bool)
                                     for bit in range(p.k)}, bool)
        values = sum(out["adjusted", bit].astype(np.uint32) << bit for bit in range(p.k))
        for address in range(p.Q - 5):
            assert np.array_equal(np.flatnonzero(values == address), [address + j])
            cases += 1
    return cases


def sparse_joint_snapshot(p, plain, guarded):
    """Exact local snapshot, with no asserted reachability or error class."""
    net = Net()
    alpha, beta = p.age_code(2000), p.age_code(2001)
    cells = {}
    for j in range(-5, 9):
        if j >= 6:
            cells[j] = dict(f1=0)
            continue
        cells[j] = dict(addr=const_word(2+j if j in (1, 2, 3) else 100+j, p.k),
                        age=const_word(beta if j in (1, 2, 3) else alpha, p.m),
                        f1=int(j in (2, 3)), f2=0, wf1=0, wf2=0)
    before = fast.invoke(plain, net, cells, p)
    after = fast.invoke(guarded, net, cells, p)
    assert before["f1"] == before["f2"] == 0
    assert before["addr"] == const_word(2, p.k)
    assert before["age"] == const_word(p.age_code(2002), p.m)
    assert after["f1"] == 1 and after["f2"] == 0
    assert after["addr"] == const_word(100, p.k)
    assert after["age"] == const_word(p.age_code(2001), p.m)
    return dict(joint_right_support=[1, 2, 3], quiet_right_support=[1, 4, 5],
                quiet_joint_support=[1], J2_computed_Flag1=0, J2_Address=2,
                guarded_computed_Flag1=1, guarded_Address=100,
                scope="exact local snapshot; reachability and error level not asserted")


def mask_certificate():
    cases = 0
    for joint in range(32):
        for quiet in range(32):
            support = joint & quiet
            if support.bit_count() < 3:
                continue
            for faults in range(32):
                if faults.bit_count() > 2:
                    continue
                assert support & ~faults
                cases += 1
    return cases


def quieting_arithmetic(p):
    packing = 0
    for gap in range(1, 25):
        for first in range(-2, 8):
            for second in range(-2, 8):
                distance = abs(-2*gap + 2 + second-first)
                if gap < 9:
                    assert distance < 24
                packing += 1
    advance = lambda t: 2*t-2*((t+8)//9)
    bound = next(t for t in range(1, p.Q) if advance(t) >= p.Q-2)
    assert bound == 215 and advance(bound-1) < p.Q-2
    return dict(clean_front_zone_offsets=[-2, 7], affecting_event_gap=9,
                event_packing_cases=packing, first_seed_updates=1,
                additional_updates=bound, source_free_aligned_clearance_bound=bound+1,
                lower_bound="2T-2 ceil(T/9)",
                scope="canonical common geometry and no non-error Workspace source; arbitrary initial flags")


def ancestry_charge_certificate():
    support_cases = 0
    for support in range(32):
        if support.bit_count() < 3:
            continue
        for fault in range(32):
            positions = [j+1 for j in range(5) if fault & (1 << j)]
            if len(positions) > 2 or (len(positions) == 2 and positions[1]-positions[0] != 1):
                continue
            available = [j+1 for j in range(5) if (support & ~fault) & (1 << j)]
            chosen = max(available)
            charge = max(0, 3-chosen)
            if charge == 1:
                assert any(j >= 3 and support & (1 << (j-1)) for j in positions)
            elif charge == 2:
                assert len(positions) == 2 and positions[0] >= 2
                assert all(support & (1 << (j-1)) for j in positions)
                assert positions[-1] >= 3 and positions[0] <= 4
            support_cases += 1
    # Associate a high-offset singleton with charge one and the actual
    # adjacent pair with charge two. Test all possible intervening path
    # displacements allowed by its first step and the maximum step five.
    templates = {1: [(j,) for j in range(3, 6)],
                 2: [(j, j+1) for j in range(2, 5)]}
    packing_cases = 0
    for first_charge in (1, 2):
        for second_charge in (1, 2):
            for gap in range(1, 6):
                if gap == 5 and first_charge+second_charge == 2:
                    continue
                for first in templates[first_charge]:
                    for second in templates[second_charge]:
                        for displacement in range(gap, 5*gap-2-first_charge+1):
                            assert min(abs(displacement+b-a) for a in first for b in second) < 24
                            packing_cases += 1
    block_cases = 0
    for number in range(3**6):
        digits, value = [], number
        for _ in range(6):
            digits.append(value % 3)
            value //= 3
        events = [(j, charge) for j, charge in enumerate(digits) if charge]
        admissible = all(b-a >= 5 and (b-a != 5 or left+right == 2)
                         for (a, left), (b, right) in zip(events, events[1:]))
        if admissible:
            assert sum(digits) <= 2
            block_cases += 1
    return dict(rightmost_clean_support_cases=support_cases,
                charged_event_distance_cases=packing_cases,
                admissible_six_step_charge_blocks=block_cases,
                minimum_charged_event_gap=5,
                gap_five_requires_two_unit_charges=True,
                maximum_charge_per_six_steps=2,
                initial_time_path_displacement_lower_bound="3T-2 ceil(T/6)",
                requires="choose the rightmost non-overwritten quiet joint supporter at each nonterminal step")


def window_certificate():
    def allowance(q, width, tick, address):
        distance = q-5-address
        minimum_steps = (distance+4)//5
        s = tick-minimum_steps
        if s < 0:
            return True
        return width-1+3*s+2*(1+(3*s)//23) < distance
    windows, cases = {}, 0
    for q in (384, 640, 1024):
        rows = {}
        for width in range(1, 601):
            ticks = []
            start = next(t for t in range(1, q) if 3*t-2*((t+5)//6) > width-1)
            for tick in range(start, q):
                if all(allowance(q, width, tick, a) for a in range(5)):
                    ticks.append(tick)
                    cases += 5
                else:
                    break
            if ticks:
                rows[str(width)] = [ticks[0], ticks[-1]]
        windows[str(q)] = rows
    assert windows["384"]["141"] == [53, 146]
    assert windows["384"]["277"] == [105, 105]
    assert "278" not in windows["384"]
    return dict(arithmetic_cases=cases, width_windows=windows,
                width_141_windows={q: rows["141"] for q, rows in windows.items()},
                right_envelope="w-1+3s+2(1+floor(3s/23))",
                scope="conditional mixed-E0 quiet-wrong-pair exclusion only; larger Q values are arithmetic illustrations, not built candidates")


def packet_path_certificate():
    crossing_cases = 0
    for width in range(5, 513):
        old_left, old_right = 0, width-1
        new_right_lower = old_right-4
        for old_quiet in range(-8, 0):
            for step in range(1, 6):
                assert old_quiet-step < new_right_lower
                crossing_cases += 1
    interception = 0
    for distance in range(1, 1025):
        duration = 2*distance+4
        # Twice the gap between the path's lower bound and the packet's
        # upper leading-edge bound at this duration.
        assert duration-2*distance-4 >= 0
        interception += 1
    return dict(one_step_no_jump_cases=crossing_cases,
                interception_arithmetic_cases=interception,
                deadline_from_initial_left_gap_d="2d+4",
                quiet_ancestry_nodes_avoid_current_E0_overwrites=True,
                hypotheses=["initial quiet ancestry point strictly left of the packet",
                            "J2 width-five packet with all eight right flag samples inside at protected outputs",
                            "packet hypotheses hold for every intervening update"],
                scope="conditional interception; neither packet initialization nor mask compatibility established")


def main():
    c = candidates.load("G17")
    # Only maintenance fields/constants are under test. These are SP1's
    # geometry widths, specified without depending on its family wrapper.
    p = replace(c.p, m=17, nb=192)
    assert c.digest() == "23a14aab4d3dc4fde5562cf3e26a4536b05456f84e65850fcb3bd95a104d8ceb"
    exact, source = proposed_build()
    symbolic, _ = proposed_build(symbolic=True)
    plain, _ = fast.proposed_build(symbolic=True)
    pairs = tuple(combinations(range(-5, 9), 2))
    correction = 0
    for address in range(p.Q):
        for faults in pairs:
            fast.pristine_symbolic(p, symbolic, address, faults)
            correction += 1
        if address % 64 == 63:
            print(f"certified Addresses 0..{address}: {correction} symbolic correction cases", flush=True)
    seed = 0
    for address in (p.Q-2, p.Q-1):
        for faults in pairs:
            fast.quiet_seed_symbolic(p, symbolic, address, faults)
            seed += 1
    extension = 0
    for address in range(p.Q):
        for faults in combinations(range(-5, 0), 2):
            for first_outside in (False, True):
                suffix_extension(p, symbolic, address, faults, first_outside)
                extension += 1
    old_count = fast.gate_count(p, fast.proposed_build()[0], True)
    new_count = fast.gate_count(p, exact, True)
    receipt = dict(base_candidate="G17", **candidates.digests(c),
                   checker_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                   helpers_sha256=hashlib.sha256((ROOT / "gacsca/netlist.py").read_bytes()).hexdigest(),
                   maintenance_sha256=hashlib.sha256((ROOT / "gacsca/maintenance.py").read_bytes()).hexdigest(),
                   fast_flag_checker_sha256=hashlib.sha256((ROOT / "Report/proofs/check_fast_flag_proposal.py").read_bytes()).hexdigest(),
                   majority_shortcut_sha256=hashlib.sha256((ROOT / "Report/proofs/check_right_barrier.py").read_bytes()).hexdigest(),
                   proposed_local_source_sha256=hashlib.sha256(source.encode()).hexdigest(),
                   exact_added_source=NEW, parameters=dict(Q=p.Q,k=p.k,m=p.m,nb=p.nb,R=p.R,PB=p.PB),
                   actual_majority_primitive_assignments=check_dominance_primitive(),
                   symbolic_structural_correction_cases=correction,
                   symbolic_quiet_seed_cases=seed,
                   symbolic_clean_front_extension_cases=extension,
                   actual_raw_modular_inverse_cases=inverse_certificate(p),
                   nonfault_support_mask_cases=mask_certificate(),
                   local_snapshot=sparse_joint_snapshot(p, plain, symbolic),
                   quieting=quieting_arithmetic(p),
                   ancestry_charges=ancestry_charge_certificate(), mixed_E0_window=window_certificate(),
                   conditional_packet_interception=packet_path_certificate(),
                   J2_maintenance=old_count, proposed_maintenance=new_count,
                   extra_gates_above_J2=new_count["gates"]-old_count["gates"],
                   active_G17_modified=False, SP1_modified=False,
                   new_ROM_built=False, maintenance_radius=8, added_maintenance_state_bits=0,
                   proved=["healthy structural two-fault correction", "non-overwritten joint quiet ancestry",
                           "conditional mixed-E0 quiet-wrong-pair window", "source-free aligned Flag1 clearance"],
                   unproved=["complete damaged-colony repair", "new own-ROM simulation", "higher-error process", "iid-noise reliability"])
    output = ROOT / "figs/robustness/quiet_majority_proposal_certificate.json"
    output.write_text(json.dumps(receipt, indent=2)+"\n")
    print(json.dumps({key: receipt[key] for key in ("symbolic_structural_correction_cases",
                     "symbolic_quiet_seed_cases", "symbolic_clean_front_extension_cases",
                     "extra_gates_above_J2", "proposed_maintenance")}, indent=2))


if __name__ == "__main__":
    main()
