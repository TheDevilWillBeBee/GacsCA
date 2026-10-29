#!/usr/bin/env python3
"""Certificate for a PROPOSED maintenance change, not the active G17 rule.

An in-memory function copy adds one Flag1 source: below Address Q-5, no
quiet right neighbor supports the selected Address/Age pair. No core file, candidate or ROM is
changed. This does not construct or prove a reliable self-simulating CA.
"""
import hashlib
import inspect
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from itertools import combinations
from gacsca import candidates, maintenance
from gacsca.netlist import Net, Compiled, const_word

OLD = "    f1 = n.any([incons, wf1, flags3, n.AND(c['f1'], flags2)])"
NEW = """    old_f1 = n.any([incons, wf1, flags3, n.AND(c['f1'], flags2)])
    quiet_joint = n.any(n.all([w_eq(n, adjusted[j], v),
                              w_eq(n, cells[j]['age'], age_r),
                              n.NOT(cells[j]['f1'])]) for j in range(1, 6))
    diagnostic = n.AND(w_ult_const(n, v, Q - 5), n.NOT(quiet_joint))
    f1 = n.OR(old_f1, diagnostic)"""


def proposed_build():
    source = inspect.getsource(maintenance.build)
    assert source.count(OLD) == 1
    changed = source.replace(OLD, NEW)
    namespace = dict(maintenance.__dict__)
    exec(compile(changed, "<proposed joint diagnostic; not active G17>", "exec"), namespace)
    return namespace["build"], changed


def mask_case(p, build, address_mask, age_mask, quiet_mask):
    net = Net()
    alpha, beta = p.age_code(2000), p.age_code(2001)
    cells = {}
    for j in range(-5, 6):
        addr, age, flag = j % p.Q, alpha, 0
        if j > 0:
            addr = j if (address_mask >> (j - 1)) & 1 else 100 + j
            age = beta if (age_mask >> (j - 1)) & 1 else alpha
            flag = 0 if (quiet_mask >> (j - 1)) & 1 else 1
        cells[j] = dict(addr=const_word(addr, p.k), age=const_word(age, p.m),
                        f1=flag, f2=0, wf1=0, wf2=0)
    out = build(net, cells, p.k, p.m, Q=p.Q, nb=p.nb, radix=p.R, pos_bits=p.PB)
    joint_quiet = bool(address_mask & age_mask & quiet_mask)
    assert out["f1"] == int(not joint_quiet)
    assert out["f2"] == 0
    assert out["addr"] == const_word(0, p.k)
    assert out["age_now"] == const_word(beta if joint_quiet else alpha, p.m)
    return not joint_quiet


def pristine_symbolic(p, build, A, alpha, faults):
    net = Net()
    cells = {}
    for j in range(-5, 6):
        if j in faults:
            cells[j] = dict(addr=[net.input((j, "addr", bit)) for bit in range(p.k)],
                            age=[net.input((j, "age", bit)) for bit in range(p.m)],
                            **{field: net.input((j, field)) for field in ("f1", "f2", "wf1", "wf2")})
        else:
            cells[j] = dict(addr=const_word((A + j) % p.Q, p.k),
                            age=const_word(alpha, p.m), f1=0, f2=0, wf1=0, wf2=0)
    out = build(net, cells, p.k, p.m, Q=p.Q, nb=p.nb, radix=p.R, pos_bits=p.PB)
    # Constant nodes certify every assignment of both overwritten words,
    # not a selection of numerical replacements.
    assert out["addr"] == const_word(A, p.k)
    assert out["age_now"] == const_word(alpha, p.m)
    assert out["f1"] == out["f2"] == 0


def gate_count(p, build):
    net = Net()
    cells = {j: dict(addr=[net.input((j, "addr", bit)) for bit in range(p.k)],
                     age=[net.input((j, "age", bit)) for bit in range(p.m)],
                     **{field: net.input((j, field)) for field in ("f1", "f2", "wf1", "wf2")})
             for j in range(-5, 6)}
    out = build(net, cells, p.k, p.m, Q=p.Q, nb=p.nb, radix=p.R, pos_bits=p.PB)
    for field, word in out.items():
        if isinstance(word, list):
            for bit, node in enumerate(word):
                net.set_output((field, bit), node)
        else:
            net.set_output((field,), word)
    compiled = Compiled(net)
    return dict(gates=len(compiled.gates), inputs=len(compiled.inputs), netlist_sha256=compiled.digest)


def same_on_joint_majority(p, build, A, good, right_flags):
    net = Net()
    alpha = p.age_code(2000)
    cells = {}
    for j in range(-5, 6):
        if j in good:
            addr, age = const_word((A + j) % p.Q, p.k), const_word(alpha, p.m)
        else:
            addr = [net.input((j, "addr", bit)) for bit in range(p.k)]
            age = [net.input((j, "age", bit)) for bit in range(p.m)]
        cells[j] = dict(addr=addr, age=age,
                        f1=(right_flags >> (j - 1)) & 1 if j > 0 else net.input((j, "f1")),
                        **{field: net.input((j, field)) for field in ("f2", "wf1", "wf2")})
    original = maintenance.build(net, cells, p.k, p.m, Q=p.Q,
                                 nb=p.nb, radix=p.R, pos_bits=p.PB)
    proposed = build(net, cells, p.k, p.m, Q=p.Q,
                     nb=p.nb, radix=p.R, pos_bits=p.PB)
    assert original == proposed, (A, good, right_flags)


def ungated_quieting_obstruction(p):
    # Guard is essential: an ungated NOT K holds homogeneous Flag1=1
    # forever, including the colony's right boundary where old Flag1 clears.
    build, source = proposed_build()
    source = source.replace("n.AND(w_ult_const(n, v, Q - 5), n.NOT(quiet_joint))",
                            "n.NOT(quiet_joint)")
    namespace = dict(maintenance.__dict__)
    exec(compile(source, "<rejected ungated diagnostic>", "exec"), namespace)
    ungated = namespace["build"]
    net = Net()
    for A in range(p.Q):
        cells = {j: dict(addr=const_word((A + j) % p.Q, p.k),
                         age=const_word(p.age_code(2000), p.m),
                         f1=1, f2=0, wf1=0, wf2=0) for j in range(-5, 6)}
        out = ungated(net, cells, p.k, p.m, Q=p.Q,
                      nb=p.nb, radix=p.R, pos_bits=p.PB)
        assert out["f1"] == 1
        assert out["addr"] == const_word(A, p.k)
        assert out["age_now"] == const_word(p.age_code(2000), p.m)
    return dict(checked_addresses=p.Q, homogeneous_raised_Flag1_remains_raised=True,
                scope="exact local proof for rejected ungated variant; no active-rule change")


def main():
    c = candidates.load("G17")
    p = c.p
    assert c.digest() == "23a14aab4d3dc4fde5562cf3e26a4536b05456f84e65850fcb3bd95a104d8ceb"
    build, source = proposed_build()
    masks = [mask for mask in range(32) if mask.bit_count() >= 3]
    cases = added = 0
    for A in masks:
        for B in masks:
            for Z in masks:
                added += mask_case(p, build, A, B, Z)
                cases += 1
    symbolic_cases = 0
    for address in (0, 1, 2, 4, 5, 378, 379, 380, 381, 382, 383):
        for age in (p.age_code(2000), 65535):
            for faults in combinations(range(-5, 6), 2):
                pristine_symbolic(p, build, address, age, faults)
                symbolic_cases += 1
    old_count, new_count = gate_count(p, maintenance.build), gate_count(p, build)
    equivalence_cases = 0
    for A in (0, 1, 378, 379, 382, 383):
        for good in combinations(range(1, 6), 3):
            for flags in range(32):
                same_on_joint_majority(p, build, A, good, flags)
                equivalence_cases += 1
    ungated = ungated_quieting_obstruction(p)
    receipt = dict(base_candidate="G17", **candidates.digests(c),
                   checker_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                   helpers_sha256=hashlib.sha256((ROOT / "gacsca/netlist.py").read_bytes()).hexdigest(),
                   maintenance_sha256=hashlib.sha256((ROOT / "gacsca/maintenance.py").read_bytes()).hexdigest(),
                   result="local certificate for explicitly proposed Flag1 diagnostic; not an implemented candidate",
                   proposed_change="below Address Q-5, Flag1 source when no quiet right neighbor agrees with both selected right votes",
                   source_replacement=dict(original=OLD, proposed=NEW),
                   proposed_local_source_sha256=hashlib.sha256(source.encode()).hexdigest(),
                   support_mask_cases=cases, mask_cases_with_added_Flag1=added,
                   symbolic_two_arbitrary_fault_cases=symbolic_cases,
                   symbolic_agreement_on_three_joint_supporters_cases=equivalence_cases,
                   rejected_ungated_variant=ungated,
                   current_maintenance=old_count, proposed_maintenance=new_count,
                   extra_maintenance_gates=new_count["gates"] - old_count["gates"],
                   state_fields_added=0, radius=5,
                   active_rule_changed=False, proposed_transition_change=True,
                   proof_scope=["joint quiet right ancestry below Address Q-5", "pointwise minimal strengthened Flag1 output for this restricted inference",
                                "unchanged maintenance on three joint right supporters, with arbitrary flags and left data",
                                "pristine structural two-fault correction", "noise-free short-seed quiet window"],
                   not_proved=["a self-interpreting ROM for the changed rule", "mixed E0 island recovery",
                               "upper error footprints", "higher-level coordination", "positive noise reliability"])
    output = ROOT / "figs/robustness/joint_diagnostic_certificate.json"
    output.write_text(json.dumps(receipt, indent=2) + "\n")
    print(json.dumps(receipt, indent=2))


if __name__ == "__main__":
    main()
