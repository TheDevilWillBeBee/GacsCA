#!/usr/bin/env python3
"""Exact literal-Gray singleton Flag2 persistence certificate.

The proof is an induction on a specified native-field invariant. It does
not presume a compiled simulation structure or prove memory failure.
"""
from pathlib import Path
import hashlib
import inspect
import json
import sys

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'Report/proofs'))
import numpy as np
from gacsca import maintenance, gray_errors
from gacsca.netlist import Net, Compiled, const_word, w_add_const
from check_g17_schedule import Terms
import literal_maintenance as literal


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def symbolic_case(reader, corrected=False):
    n = Net()
    age = [n.input(('common_age', bit)) for bit in range(literal.M)]
    cells = {j: dict(addr=const_word((4096 + reader + j) % literal.Q, literal.K),
                    age=age, f1=0, f2=int(reader + j == 0), wf1=0, wf2=0)
             for j in range(-5, 6)}
    output = (maintenance.build if corrected else literal.build)(n, cells, literal.K, literal.M)
    assert output['addr'] == const_word((4096 + reader) % literal.Q, literal.K)
    assert output['age_now'] == age
    assert output['age'] == w_add_const(n, age, 1)
    assert output['f1'] == 0
    expected_flag = int(reader == 0 and not corrected)
    assert output['f2'] == expected_flag, (reader, corrected, output['f2'])
    return dict(reader=reader, corrected=corrected, symbolic_clock_bits=literal.M,
                output_flag2=expected_flag, cofactor_gates=n.gate_count())


def native_net():
    n = Net()
    widths = dict(addr=literal.K, age=literal.M, f1=1, f2=1, wf1=1, wf2=1)
    cells = {j: {field: [n.input(('x', j, field, bit)) for bit in range(width)]
                 for field, width in widths.items()} for j in range(-5, 6)}
    cells = {j: {field: value[0] if widths[field] == 1 else value
                 for field, value in cell.items()} for j, cell in cells.items()}
    out = literal.build(n, cells)
    for field, value in out.items():
        for bit, node in enumerate(value if isinstance(value, list) else [value]):
            n.set_output(('y', field, bit), node)
    return Compiled(n)


def adjacent_pair_cases():
    """Literal clause, h0 single-token repair, and candidate-B h1 repair."""
    variants = [('literal', literal.build), ('h1', maintenance.build)]
    source = inspect.getsource(maintenance.build)
    old = 'n.NOT(at_least(n, left_inside, 2))'
    assert source.count(old) == 1
    namespace = dict(maintenance.__dict__)
    exec(compile(source.replace(old,'n.NOT(at_least(n, left_inside, 1))'),
                 '<healthy Flag2 h0 variant>', 'exec'), namespace)
    variants.append(('h0', namespace['build']))
    checked = []
    for label, build in variants:
        for reader in range(-5,7):
            net = Net()
            age = [net.input(('clock', bit)) for bit in range(literal.M)]
            cells = {j:dict(addr=const_word((4096+reader+j)%literal.Q,literal.K),
                    age=age,f1=0,f2=int(reader+j in (0,1)),wf1=0,wf2=0)
                     for j in range(-5,6)}
            got = build(net,cells,literal.K,literal.M)
            wanted = int(reader in (0,1)) if label == 'literal' else int(label == 'h0' and reader == 1)
            assert got['f2'] == wanted, (label,reader,got['f2'])
            assert got['f1'] == 0
            assert got['addr'] == const_word((4096+reader)%literal.Q,literal.K)
            assert got['age_now'] == age
            checked.append(dict(variant=label,reader=reader,output_flag2=wanted,
                                symbolic_clock_bits=literal.M))
    return checked


def main():
    output_dir = ROOT / 'figs/gray_counterexamples'
    cases = [symbolic_case(reader, corrected) for corrected in (False, True) for reader in range(-5, 6)]
    pair_cases = adjacent_pair_cases()
    comp = native_net()
    rng = np.random.default_rng(20261009)
    independent_scalar_checks = 1000
    saved_inputs = []
    saved_outputs = []
    for _ in range(independent_scalar_checks):
        cells = {j: dict(addr=int(rng.integers(literal.Q)), age=int(rng.integers(literal.U)),
                         f1=int(rng.integers(2)), f2=int(rng.integers(2)),
                         wf1=int(rng.integers(2)), wf2=int(rng.integers(2))) for j in range(-5, 6)}
        wanted = literal.scalar(cells)
        values = {name: (cells[name[1]][name[2]] >> name[3]) & 1 for name in comp.inputs}
        raw = comp.evaluate_scalar(values)
        got = {field: sum(raw['y', field, bit] << bit for bit in range(width))
               for field, width in dict(addr=literal.K, age_now=literal.M, age=literal.M, f1=1, f2=1).items()}
        assert got == wanted, (got, wanted)
        saved_inputs.append([[cells[j][field] for field in ('addr','age','f1','f2','wf1','wf2')]
                             for j in range(-5,6)])
        saved_outputs.append([wanted[field] for field in ('addr','age_now','age','f1','f2')])
    scalar_asset = output_dir/'printed_flag2_scalar_inputs.npz'
    np.savez_compressed(scalar_asset,inputs=np.asarray(saved_inputs,dtype=np.int64),
                        outputs=np.asarray(saved_outputs,dtype=np.int64))
    singleton = [(4096, 1)]
    e0 = gray_errors.level0_points(singleton)
    assert e0 == set(singleton)
    candidate = gray_errors.classify(singleton, Q=literal.Q, U=literal.U, sep=literal.ERROR_SEPARATION)
    assert candidate['level0'] == 1 and not candidate['level1']
    report = dict(Q=literal.Q, U=literal.U, radius=5, error_lambda=literal.LAMBDA,
        error_condition_iii_separation=literal.ERROR_SEPARATION,
        active_rule_modified=False, current_candidate_modified=False,
        checker_sha256=digest(__file__), literal_module_sha256=digest(literal.__file__),
        base_maintenance_sha256=digest(maintenance.__file__),
        literal_generated_maintenance_sha256=literal.source_sha256(),
        gray_text_sha256=digest(ROOT/'papers_txt/gray_readers_guide.txt'),
        literal_native_netlist_sha256=comp.digest, literal_native_gates=len(comp.gates),
        symbolic_cases=cases, adjacent_pair_symbolic_cases=pair_cases,
        all_common_clock_words_covered=2**literal.M,
        independent_scalar_random_checks=independent_scalar_checks,
        scalar_inputs_asset_sha256=digest(scalar_asset), scalar_random_seed=20261009,
        gray_pdf_sha256=digest(next((ROOT/'papers').glob('A Reader*'))),
        visually_confirmed_pdf_page=21,
        page21_image_sha256=digest(output_dir/'Gray_page21.png'),
        error_set=singleton, error_location_classification=candidate,
        initial_native_context=dict(address='x modulo Q', age=0, f1=0, f2=0, wf1=0, wf2=0),
        overwrite=dict(site=4096, time=1, field='f2', value=1),
        subsequent_errors=[], prescribed_workspace_flags_zero_at_all_times=True,
        invariant_proved='One Flag2 at site4096 persists; every Address/Age remains canonical; Flag1 remains zero.',
        exact_native_counterexample_proved=True,
        published_initialization_two_tick_flag_counterexample_proved=True,
        two_tick_context_workspace_zero_reason='Initial Workspace flags are0; computed Age1 is outside the published pulse[3U/4,3U/4+2Q).',
        full_all_time_simulation_context_certified=False,
        intended_corrected_gray_refuted=False, gacs_2001_refuted=False,
        iid_unreliability_proved=False,
        scope='Literal native all-time invariant with Workspace-zero premise; two-tick published Flags contradiction needs only stated initialization. Full programme dynamics and iid memory are separate obligations.')
    path = output_dir/'printed_flag2_certificate.json'
    path.write_text(json.dumps(report, indent=2)+'\n')
    print(json.dumps({key:report[key] for key in ('Q','U','literal_native_gates','all_common_clock_words_covered','exact_native_counterexample_proved','full_all_time_simulation_context_certified','iid_unreliability_proved')}))


if __name__ == '__main__':
    main()
