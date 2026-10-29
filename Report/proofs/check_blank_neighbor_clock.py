#!/usr/bin/env python3
"""Exact full-rule blank-neighbor identity for G17 and isolated SP4.

Neighbors are externally clamped to the all-zero raw word. This is a local
input identity, not an autonomous CA trajectory or an iid counterexample.
An explicitly proposed left-clock fallback is checked in memory only; it
is not installed, recompiled into a ROM, or claimed sufficient for reliability.
"""
import hashlib
import inspect
import json
from pathlib import Path
import sys
from types import FunctionType, SimpleNamespace

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
import numpy as np
from gacsca import candidates, maintenance, rule_g
from gacsca.netlist import Net, Compiled, const_word
import proposed_sparse_prefix448 as proposed
import prefix_selection as selection
import check_fast_mail_proposal as transport
from check_fast_flag_proposal import invoke


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def coupled_left_clock(source):
    old_age = "    age_l, _ = majority_word(n, [cells[j]['age'] for j in range(-1, -6, -1)], c['age'])"
    old_addr = "    addr_l, _ = majority_word(n, [adjusted[j] for j in range(-1, -6, -1)], c['addr'])"
    assert source.count(old_age) == source.count(old_addr) == 1
    source = source.replace(old_addr + '\n', '')
    source = source.replace(old_age, """    addr_l, left_exists = majority_word(n, [adjusted[j] for j in range(-1, -6, -1)], c['addr'])
    age_l, _ = majority_word(n, [cells[j]['age'] for j in range(-1, -6, -1)], c['age'])
    age_l = w_mux(n, left_exists, age_l, c['age'])""")
    namespace = dict(maintenance.__dict__)
    exec(compile(source, '<EXPLICIT proposed left-clock fallback>', 'exec'), namespace)
    return namespace['build'], source


def main():
    out = ROOT / 'figs/robustness'
    cases = {}
    for name, candidate in (('G17', candidates.load('G17')), ('SP4', proposed.load_artifact())):
        p = candidate.p
        if name == 'G17':
            source = inspect.getsource(rule_g.build)
            namespace = dict(rule_g.__dict__)
            original, maintenance_source = maintenance.build, inspect.getsource(maintenance.build)
        else:
            factory = FunctionType(transport.concrete_sparse_net.__code__,
                                   dict(transport.__dict__, proposed_maintenance=selection.proposed_build))
            actual, source = factory(p, proposed.dependency_table(p))
            assert Compiled(actual).digest == candidate.comp.digest
            original, maintenance_source = selection.proposed_build()
            namespace = dict(rule_g.__dict__, maintenance=SimpleNamespace(build=original),
                             OFFSETS=tuple(range(-12, 13)), sparse_controls=transport.sparse_controls,
                             sparse_table=proposed.dependency_table(p))

        class BoundNet(Net):
            def input(self, key):
                if key[0] == 'x':
                    _, offset, field, bit = key
                    if offset != 0:
                        return 0
                    return super().input(('centre', field, bit))
                return super().input(key)

        namespace['Net'] = BoundNet
        exec(compile(source, '<actual full rule with blank neighbors>', 'exec'), namespace)
        bound = namespace['build'](p)
        expected = {}
        for field, width in candidate.schema:
            for bit in range(width):
                value = (bound.input_node['centre', 'addr', bit] if field == 'addr'
                         else int((field == 'age' and bit == 0) or field == 'f1'))
                assert bound.outputs['y', field, bit] == value, (name, field, bit)
                expected[field, bit] = value
        # Exact node equality is a universal Boolean identity: all centre
        # fields and all instruction bits remain free in this check.
        assert len(expected) == candidate.W
        live = set(bound.live_nodes())
        live_inputs = [key for key, node in bound.input_node.items() if node in live]
        assert all(key[0] == 'centre' and key[1] == 'addr' for key in live_inputs
                   if key[0] != 'I')
        # Nonphysical lookup-key outputs may use I-independent centre Address;
        # only the physical y outputs are asserted above.

        patched, patch_source = coupled_left_clock(maintenance_source)
        n = Net()
        central = dict(addr=[n.input(('own_addr', bit)) for bit in range(p.k)],
                       age=[n.input(('own_age', bit)) for bit in range(p.m)],
                       **{field:n.input(('own', field)) for field in ('f1', 'f2', 'wf1', 'wf2')})
        cells = {j:(central if j == 0 else dict(addr=const_word(0, p.k), age=const_word(0, p.m),
                                              f1=0, f2=0, wf1=0, wf2=0))
                 for j in range(-5, 9)}
        modified = invoke(patched, n, cells, p)
        assert modified['addr'] == central['addr'] and modified['age_now'] == central['age']
        assert modified['f1'] == 1
        for bit, node in enumerate(modified['age']):
            n.set_output(('age', bit), node)
        n.set_output(('f2',), modified['f2'])
        compiled = Compiled(n)
        ticks = np.arange(p.U, dtype=np.int64)
        ages = np.asarray([p.age_code(int(tick)) for tick in ticks], dtype=np.int64)
        # The symbolic identity already proves arbitrary own address and f1/
        # Workspace. Check both values of own f2 and every legal clock code.
        for old_flag in (0, 1):
            values = {key:((ages >> key[1]) & 1).astype(bool) if key[0] == 'own_age'
                      else np.full(p.U, bool(old_flag if key == ('own', 'f2') else 0))
                      for key in compiled.inputs}
            got = compiled.evaluate(values, bool)
            next_age = sum(got['age', bit].astype(np.int64) << bit for bit in range(p.m))
            assert np.array_equal(next_age, np.asarray([p.age_code((int(tick)+1) % p.U) for tick in ticks]))
            assert np.array_equal(got['f2',], ((ticks+1) % 16 == 0))

        cases[name] = dict(candidate_sha256=candidate.digest(), netlist_sha256=candidate.comp.digest,
                           Q=p.Q, U=p.U, physical_output_bits=candidate.W,
                           full_generated_source_sha256=hashlib.sha256(source.encode()).hexdigest(),
                           maintenance_generated_source_sha256=hashlib.sha256(maintenance_source.encode()).hexdigest(),
                           arbitrary_central_raw_word=True, arbitrary_instruction_bits=True,
                           unchanged_raw_Address=True, computed_age_code=1,
                           computed_Flag1=1, computed_Flag2=0, other_physical_outputs_zero=True,
                           literal_output_node_identities=candidate.W,
                           proposed_fallback_source_sha256=hashlib.sha256(patch_source.encode()).hexdigest(),
                           proposed_fallback_legal_clock_and_old_Flag2_cases=2*p.U,
                           proposed_fallback_clock_advances=True,
                           proposed_fallback_Flag2_output_iff_next_tick_divisible_by_16=True)
    dependencies = ('SP4_program_build.json', 'SP4_autonomy_certificate.json',
                    'SP4_maintenance_certificate.json', 'clock_legality_certificate.json')
    result = dict(checker_sha256=digest(Path(__file__)),
                  full_rule_sha256=digest(ROOT / 'gacsca/rule_g.py'),
                  maintenance_sha256=digest(ROOT / 'gacsca/maintenance.py'),
                  netlist_helpers_sha256=digest(ROOT / 'gacsca/netlist.py'),
                  transport_checker_sha256=digest(Path(transport.__file__)),
                  selection_source_sha256=digest(Path(selection.__file__)),
                  SP4_proposal_source_sha256=digest(Path(proposed.__file__)),
                  proof_receipt_sha256={name:digest(out / name) for name in dependencies},
                  rules=cases, status='proved local Boolean identities; finite legal-clock exhaustion for proposed fallback',
                  all_neighbors_externally_clamped_to_blank=True,
                  proposed_rule_change_checked_in_memory=True, active_G17_modified=False,
                  isolated_SP4_modified=False, proposed_fallback_self_interpreter_built=False,
                  autonomous_CA_fixed_point_established=False,
                  physical_mail_blocking_implies_blank_inputs_established=False,
                  iid_unreliability_established=False, global_reliability_established=False,
                  scope='local blank-input reset and clock self-loop; proposed fallback only resolves this local liveness obstruction')
    (out / 'blank_neighbor_clock_certificate.json').write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(dict(rules=list(cases), physical_output_node_identities=sum(row['literal_output_node_identities'] for row in cases.values()),
                          proposed_fallback_legal_clock_cases=sum(row['proposed_fallback_legal_clock_and_old_Flag2_cases'] for row in cases.values()),
                          global_reliability_established=False)), flush=True)


if __name__ == '__main__':
    main()
