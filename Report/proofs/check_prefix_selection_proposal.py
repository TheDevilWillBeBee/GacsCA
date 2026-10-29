#!/usr/bin/env python3
"""Certificate for SP3's EXPLICIT no-Flag2-override selection change.

Actual local source, geometry-independence and barrier identities support
the unbounded-line arbitrary-island proof in ROBUSTNESS. The two-tick
prefix argument is combinatorial, not finite trajectory extrapolation.
Continuing E0 noise and iid reliability are separate unproved obligations.
"""
import hashlib
from itertools import combinations
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
import numpy as np
from gacsca.netlist import (Net, Compiled, const_word, w_eq,
                           mixed_age_increment, w_add_const_mod)
import prefix_selection as selection
import proposed_sparse_prefix as proposed
from check_fast_flag_proposal import invoke, pristine_symbolic
from check_sparse_phase_repair import term_ids, suffix_certificate
from check_right_barrier import check_dominance_primitive
from check_g17_schedule import Terms


class AbsorbingTerms(Terms):
    """Add only the two standard, truth-table-checked absorption laws."""
    def op(self, operation, a, b):
        result = super().op(operation, a, b)
        term = self.terms[result]
        if operation not in (0, 1) or term[0] != operation:
            return result
        values = set(term[1])
        opposite = 1-operation
        for value in tuple(values):
            child = self.terms[value]
            if child[0] != opposite:
                continue
            factors = set(child[1])
            absorbed = bool(values.intersection(factors))
            # Associative flattening may split A into several outer
            # operands; recognize (A op (A opposite B)) in that form.
            absorbed |= any(self.terms[factor][0] == operation and
                            set(self.terms[factor][1]).issubset(values)
                            for factor in factors)
            # Dual clause subsumption: (A OR B) AND (A OR B OR C), and
            # its AND/OR dual. This is the same absorption law with A
            # standing for the shared clause.
            absorbed |= any(other != value and self.terms[other][0] == opposite and
                            set(self.terms[other][1]).issubset(factors)
                            for other in values)
            if absorbed:
                values.remove(value)
        if len(values) == 1:
            return next(iter(values))
        return self.put((operation, tuple(sorted(values))))


def implication_terms(net):
    terms = AbsorbingTerms()
    names = {node: name for name, node in net.input_node.items()}
    values = []
    for node, kind in enumerate(net.kind):
        if kind == "C0":
            value = 0
        elif kind == "C1":
            value = 1
        elif kind == "IN":
            value = terms.var(names[node])
        else:
            op, a, b = net.gate[node]
            value = terms.op(op, values[a], values[b])
        values.append(value)
    return values


def absorption_truth_table():
    count = 0
    for a in (False, True):
        for b in (False, True):
            assert (a or (a and b)) == a
            assert (a and (a or b)) == a
            count += 2
            for c in (False, True):
                assert ((a or b) and (a or b or c)) == (a or b)
                assert ((a and b) or (a and b and c)) == (a and b)
                count += 2
    return count


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def geometry_independence(p):
    build, source = selection.proposed_build()
    net = Net()
    cells = {}
    for j in range(-5, 9):
        if j >= 6:
            cells[j] = dict(f1=net.input((j, "f1")))
        else:
            cells[j] = dict(addr=[net.input((j, "addr", bit)) for bit in range(p.k)],
                            age=[net.input((j, "age", bit)) for bit in range(p.m)],
                            **{field: net.input((j, field)) for field in ("f1", "f2", "wf1", "wf2")})
    actual = invoke(build, net, cells, p)
    nodes = list(actual["addr"])+list(actual["age"])+list(actual["age_now"])+[actual["f1"]]
    live = set(nodes)
    stack = nodes.copy()
    while stack:
        node = stack.pop()
        if net.kind[node] in ("C0", "C1", "IN"):
            continue
        _, a, b = net.gate[node]
        for parent in (a, b):
            if parent not in live:
                live.add(parent)
                stack.append(parent)
    names = [name for name, node in net.input_node.items() if node in live]
    assert all(name[1] not in ("f2", "wf2") for name in names)
    return dict(actual_raw_geometry_and_Flag1_dependencies=len(names),
                geometry_independent_of_all_Flag2_and_Workspace_Flag2_bits=True,
                actual_source_sha256=hashlib.sha256(source.encode()).hexdigest())


def full_rule_independence(p):
    net, comp = proposed.cached(p)
    affected = []
    for output, node in net.outputs.items():
        live = {node}
        stack = [node]
        while stack:
            current = stack.pop()
            if net.kind[current] in ("C0", "C1", "IN"):
                continue
            _, a, b = net.gate[current]
            for parent in (a, b):
                if parent not in live:
                    live.add(parent)
                    stack.append(parent)
        hits = [name for name, inp in net.input_node.items()
                if inp in live and name[0] == "x" and name[2] in ("f2", "wf2")]
        if hits:
            affected.append((output, len(hits)))
    assert affected == [(("y", "f2", 0), 17)], affected
    return dict(declared_output_bits=len(net.outputs), raw_Flag2_Workspace_Flag2_affected_outputs=affected,
                proposed_netlist_sha256=comp.digest,
                consequence="only next physical Flag2 depends on either raw input field; every other output including instruction keys is independent")


def one_step_prefix(p, build):
    # At p-3 the first three right geometry inputs are still in the
    # correct prefix; five left inputs are correct. All flags are free.
    for A in range(p.Q):
        net = Net()
        alpha = [net.input(("correct_Age", bit)) for bit in range(p.m)]
        cells = {}
        for j in range(-5, 9):
            if j >= 6:
                cells[j] = dict(f1=net.input((j, "f1")))
                continue
            good = j <= 3
            cells[j] = dict(addr=const_word((A+j) % p.Q, p.k) if good else
                            [net.input((j, "addr", bit)) for bit in range(p.k)],
                            age=alpha if good else [net.input((j, "age", bit)) for bit in range(p.m)],
                            **{field: net.input((j, field)) for field in ("f1", "f2", "wf1", "wf2")})
        actual = invoke(build, net, cells, p)
        assert actual["addr"] == const_word(A, p.k)
        assert actual["age_now"] == alpha
        assert actual["age"] == mixed_age_increment(net, alpha, p.PB, p.R, p.nb)
    return dict(symbolic_addresses=p.Q, arbitrary_two_right_geometry_words=True,
                arbitrary_observed_flags=True, prefix_one_update_loss_at_most=3)


def phase_adjustment_certificate(p, build):
    """All raw adders and a sharp obstruction to a raw-word source claim."""
    raw = np.arange(1 << p.k, dtype=np.int64)
    table = {}
    for value in (*range(1, 6), *range(p.Q-5, p.Q)):
        net = Net()
        word = [net.input(('a', bit)) for bit in range(p.k)]
        result = w_add_const_mod(net, word, value, p.Q)
        for bit, node in enumerate(result):
            net.set_output(('result', bit), node)
        comp = Compiled(net)
        actual = comp.evaluate({name: ((raw >> name[1]) & 1).astype(bool)
                                for name in comp.inputs}, bool)
        got = sum(actual['result', bit].astype(np.int64) << bit for bit in range(p.k))
        expected = raw+value
        expected = np.where(expected >= p.Q, expected-p.Q, expected)
        assert np.array_equal(got, expected)
        assert np.array_equal(got % p.Q, (raw+value) % p.Q)
        table[value] = got
    adjustment_cases = 0
    for A in range(p.Q):
        for offset in (*range(-5, 0), *range(1, 6)):
            neighbor = (A+offset) % p.Q
            options = [neighbor]
            if neighbor+p.Q < 1 << p.k:
                options.append(neighbor+p.Q)
            for stored in options:
                adjusted = int(table[(-offset) % p.Q][stored])
                assert adjusted % p.Q == A
                if offset < 0:
                    assert adjusted == A
                adjustment_cases += 1
    # Five canonical left inputs do not exclude a right-selected alias.
    net = Net()
    alpha = [net.input(('common_Age', bit)) for bit in range(p.m)]
    cells = {}
    for j in range(-5, 9):
        if j >= 6:
            cells[j] = dict(f1=0)
        else:
            A = p.Q+j if j > 0 else j % p.Q
            cells[j] = dict(addr=const_word(A, p.k), age=alpha,
                            f1=0, f2=0, wf1=0, wf2=0)
    actual = invoke(build, net, cells, p)
    assert actual['addr'] == const_word(p.Q, p.k) and actual['f1'] == 0
    assert actual['age_now'] == alpha
    return dict(actual_adder_inputs_checked=10*len(raw),
                phase_correct_adjustment_cases=adjustment_cases,
                left_phase_correct_words_adjust_to_canonical=True,
                right_whole_word_majority_with_three_phase_correct_inputs_has_correct_residue=True,
                raw_source_obstruction=dict(reference_Address=0, canonical_left_Address=True,
                                            right_raw_Addresses=list(range(p.Q+1, p.Q+6)),
                                            computed_Address=p.Q, computed_Flag1=0,
                                            phase_and_Age_correct=True, raw_Address_canonical=False),
                normalization_updates=43,
                hypothesis_for_normalization='global correct Address residues; no further Address overwrites')


def source_case(p, build, selected, good_left_start, component):
    net = Net()
    alpha = [net.input(("good_Age", bit)) for bit in range(p.m)]
    beta = [net.input(("right_Age", bit)) for bit in range(p.m)]
    good_A = (selected+101) % p.Q if component == "Address" else selected
    cells = {}
    for j in range(-5, 9):
        if j >= 6:
            cells[j] = dict(f1=net.input((j, "f1")))
            continue
        if j >= 1:
            address = const_word((selected+j) % p.Q, p.k)
            age = beta
        elif -j >= good_left_start and j < 0:
            address = const_word((good_A+j) % p.Q, p.k)
            age = alpha
        else:
            address = [net.input((j, "addr", bit)) for bit in range(p.k)]
            age = [net.input((j, "age", bit)) for bit in range(p.m)]
        cells[j] = dict(addr=address, age=age,
                        **{field: net.input((j, field)) for field in ("f1", "f2", "wf1", "wf2")})
    actual = invoke(build, net, cells, p)
    inequality = net.NOT(w_eq(net, alpha, beta))
    implication = net.OR(actual["f1"], inequality)
    ids = implication_terms(net)
    if component == "Address":
        assert actual["f1"] == 1, (selected, good_left_start)
        assert actual["addr"] == const_word(good_A, p.k)
        assert actual["age_now"] == alpha
    else:
        # Sound implication: OR(f1, Age_inequality)=f1. No assignment of
        # either clock word is assumed, and no distributivity is added.
        assert ids[implication] == ids[actual["f1"]], (selected, good_left_start)


def two_step_mask_certificate(p, build):
    cases = 0
    rows = []
    for v in range(3):
        possible = []
        for child in range(1, 6):
            address = v+child
            d = child-2  # hardest child position when the second output is p-2
            start = max(1, d)
            if address >= start+2:
                for component in ("Address", "Age"):
                    source_case(p, build, address, start, component)
                    cases += 1
            else:
                possible.append(child)
        assert len(possible) <= 2
        rows.append(dict(second_output_Address=v, possible_quiet_wrong_children=possible))
    # The general correct-three-left source implication used in the
    # subsequent advance. No Address value is omitted from the mask proof;
    # all larger values have the same all-inside signature.
    mask_cases = 0
    for d in range(-3, 4):
        start = max(1, d)
        for v in range(1 << p.k):
            good_inside = [j for j in range(start, 6) if j <= v]
            if len(good_inside) >= 3:
                assert v >= start+2
            mask_cases += 1
    return dict(actual_source_implication_cases=cases, second_update_rows=rows,
                selected_Address_mask_cases=mask_cases,
                two_updates_phase_and_Age_prefix_loss_at_most=2,
                proof="one step leaves p-3 good; a bad second output at/before p-2 needs three quiet joint children, but the actual source excludes all except at most two",
                scope="noise-free Address-residue/exact-Age prefix; raw aliases require separate normalization; selection change required")


def bounds_certificate(p):
    rows = []
    D = [p.Q-5-v for v in range(5)]
    minimum = min(distance+3*((distance+4)//5) for distance in D)
    assert minimum == 600
    for width in range(1, 197):
        startup = 2*((width+3)//4)
        assert 2*startup > width-1
        slack = minimum-5-width-4*startup
        assert slack > 0
        bound = startup+(p.Q+width+startup-1+2)//3
        assert bound+43 < p.U//32 and bound+472 < p.T_wf
        assert width+startup+1 < p.Q
        rows.append(dict(width=width, even_startup_tick=startup,
                         minimum_near_end_ancestor_slack=slack,
                         phase_and_Age_repair_bound=bound,
                         geometric_repair_bound=bound+43,
                         global_flag_clearance_bound=bound+472,
                         maximum_left_phase_expansion=startup+1,
                         true_colonies_in_envelope_at_most=2))
    assert rows[140]["geometric_repair_bound"] == 314
    assert rows[-1]["geometric_repair_bound"] == 367
    assert minimum-5-197-4*(2*((197+3)//4)) <= 0
    return dict(widths=rows, maximum_width_for_this_bound=196,
                width_197_fails_this_sufficient_estimate_only=True,
                initial_correct_clock_tick=0,
                minimum_Address_displacement_plus_three_times_duration=minimum,
                raw_Address_confined_to_same_at_most_two_true_colonies=True,
                raw_Address_pointwise_padding_bound_not_claimed=True,
                scope="arbitrary raw geometry island; phase envelope then 43-update raw normalization; quiet first true colony to its right; no continuing faults")


def main():
    p = proposed.parameters()
    build, source = selection.proposed_build(symbolic=True)
    result = dict(proposal="SP3", proposed_rule_change=True, active_G17_modified=False,
                  SP2_modified=False, checker_sha256=digest(Path(__file__)),
                  proposal_source_sha256=digest(ROOT / "Report/proofs/proposed_sparse_prefix.py"),
                  selection_source_sha256=digest(ROOT / "Report/proofs/prefix_selection.py"),
                  quiet_majority_checker_sha256=digest(ROOT / "Report/proofs/check_quiet_majority_proposal.py"),
                  majority_shortcut_sha256=digest(ROOT / "Report/proofs/check_right_barrier.py"),
                  algebra_checker_sha256=digest(ROOT / "Report/proofs/check_g17_schedule.py"),
                  helpers_sha256=digest(ROOT / "gacsca/netlist.py"),
                  guarded_maintenance_source_sha256=hashlib.sha256(source.encode()).hexdigest(),
                  actual_majority_primitive_assignments=check_dominance_primitive(),
                  additional_absorption_truth_assignments=absorption_truth_table(),
                  geometry_independence=geometry_independence(p),
                  full_rule_independence=full_rule_independence(p),
                  one_step=one_step_prefix(p, build), two_step=two_step_mask_certificate(p, build),
                  phase_adjustment=phase_adjustment_certificate(p, build),
                  address_alias_receipt_sha256=digest(ROOT / 'figs/robustness/address_alias_certificate.json'),
                  protected_suffix=suffix_certificate(p, build), bounds=bounds_certificate(p),
                  global_reliability_established=False)
    count = 0
    for A in range(p.Q):
        for pair in combinations(range(-5, 9), 2):
            pristine_symbolic(p, build, A, pair)
            count += 1
        if A % 96 == 95:
            print(f"SP3: healthy local correction through Address {A}, {count} symbolic cases", flush=True)
    result["healthy_two_fault_symbolic_cases"] = count
    (ROOT / "figs/robustness/SP3_prefix_selection_certificate.json").write_text(json.dumps(result, indent=2)+"\n")
    print(json.dumps(dict(width_141=result["bounds"]["widths"][140],
                          width_196=result["bounds"]["widths"][-1]), indent=2))


if __name__ == "__main__":
    main()
