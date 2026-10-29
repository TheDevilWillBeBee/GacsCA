#!/usr/bin/env python3
"""Certificate for GMW0's raw-GF birth hole; frozen kernel is not modified."""
from dataclasses import asdict, replace
from pathlib import Path
import hashlib
import json
import sys

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "Report/proofs/gray_counterexamples"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(SOURCE))
from gacsca import gray_errors
import gray_moving_word_kernel as k
import literal_maintenance


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    outdir = ROOT / "figs/robustness"
    beta, _, _ = k.native_word_programme()
    simulated = {j: dict(addr=j % k.Q, age=0, f1=0, f2=0, wf1=0, wf2=0)
                 for j in range(-5, 6)}
    tape = k.tape_from_native(simulated)
    expected_native = literal_maintenance.scalar(simulated)
    assert expected_native == dict(addr=0, age_now=0, age=1, f1=0, f2=0)

    def cell(x, age=112 * k.Q):
        return k.Cell(addr=x % k.Q, age=age,
                      mem=tuple(tape.get((x + s) % k.Q, 0) for s in k.SLOTS))

    witnesses = []
    affected = [k.ENTRY - s for s in k.SLOTS]
    for x in range(k.ENTRY - 7, k.ENTRY + 8):
        pristine = {j: cell(x + j) for j in range(-5, 6)}
        faulty = dict(pristine)
        if -5 <= k.ENTRY - x <= 5:
            d = k.ENTRY - x
            faulty[d] = replace(faulty[d], addr=k.ENTRY + 1)
        clean_out = k.local_transition(pristine, beta)
        faulty_out = k.local_transition(faulty, beta)
        assert (faulty_out.addr, faulty_out.age, faulty_out.f1, faulty_out.f2,
                faulty_out.wf1, faulty_out.wf2) == (x % k.Q, 112 * k.Q + 1, 0, 0, 0, 0)
        assert faulty_out.heads == (0,) * 5
        assert clean_out.heads == tuple(k.pack(k.initial_packet()) if x + s == k.ENTRY else 0
                                       for s in k.SLOTS)
        assert replace(clean_out, heads=(0,) * 5) == faulty_out
        witnesses.append(dict(x=x, clean_input={j: asdict(c) for j, c in pristine.items()},
                              faulty_input={j: asdict(c) for j, c in faulty.items()},
                              clean_output=asdict(clean_out), faulty_output=asdict(faulty_out)))
    assert set(affected) == {k.ENTRY - 2, k.ENTRY - 1, k.ENTRY, k.ENTRY + 1, k.ENTRY + 2}
    # All later clock classes used in the headless induction and boundary read.
    closure_checks = 0
    column = k.NATIVE_COLUMNS['age'][0]
    for age in (112 * k.Q + 1, 112 * k.Q + 2, 120 * k.Q - 1,
                120 * k.Q, k.U - 2, k.U - 1):
        for s in k.SLOTS:
            x = column - s
            actual = k.local_transition({j: cell(x + j, age) for j in range(-5, 6)}, beta)
            assert actual == replace(cell(x, age), age=(age + 1) % k.U)
            closure_checks += 1
    errors = [(k.ENTRY, 1)]
    classification = gray_errors.classify(errors, Q=k.Q, U=k.U, sep=k.ERROR_SEPARATION)
    assert gray_errors.level0_points(errors) == set(errors)
    assert classification['level0'] == 1 and not classification['level1']
    witnesspath = outdir / "GMW0_birth_E0_witness.json"
    witnesspath.write_text(json.dumps(dict(simulated_native_inputs=simulated,
                                         expected_native_output=expected_native,
                                         local_replays=witnesses), indent=2) + "\n")
    dependencies = (SOURCE / 'gray_moving_word_kernel.py', SOURCE / 'literal_maintenance.py',
                    SOURCE / 'GMW0_PHYSICAL_NATIVE_PROGRAMME.md',
                    ROOT / 'figs/gray_counterexamples/GMW0_native_programme_certificate.json')
    result = dict(scope='ROBUSTNESS J163: prepared GMW0 native-prefix birth, not an intact whole hierarchy',
                  Q=k.Q, U=k.U, error_lambda=k.LAMBDA, error_separation_c=k.ERROR_SEPARATION,
                  error_set=errors, error_classification=classification,
                  overwritten_field='Address', original_value=k.ENTRY, replacement_value=k.ENTRY + 1,
                  error_row_common_age=112 * k.Q, repaired_birth_row_common_age=112 * k.Q + 1,
                  missing_head_holders=affected, headless_native_age_bit_column=column,
                  clean_committed_age_bit=1, faulty_committed_age_bit=0,
                  complete_birth_cell_replays=len(witnesses), headless_clock_class_replays=closure_checks,
                  exact_E0_birth_transparency_counterexample_proved=True,
                  native_repair_and_headless_commit_proof_in_written_document=True,
                  five_site_voted_birth_fix_proved_under_canonical_clock_geometry=True,
                  proposed_birth_equation_change_applied=False,
                  native_quiet_prefix_theorem_refuted=False, whole_recursive_initialization_proved=False,
                  full_E0_execution_fix_proved=False, smallest_reliability_change_proved=False,
                  faithful_Gray_counterexample_proved=False, G17_counterexample_proved=False,
                  iid_memory_failure_proved=False, global_reliability_established=False,
                  active_rule_modified=False, finite_replays_measured_only=True,
                  checker_sha256=digest(__file__),
                  written_proof_sha256=digest(ROOT / 'Report/proofs/GMW0_BIRTH_E0_OBSTRUCTION.md'),
                  witness_sha256=digest(witnesspath),
                  dependency_sha256={str(p.relative_to(ROOT)): digest(p) for p in dependencies})
    (outdir / 'GMW0_birth_E0_certificate.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({key: result[key] for key in ('complete_birth_cell_replays',
          'headless_clock_class_replays', 'exact_E0_birth_transparency_counterexample_proved',
          'global_reliability_established')}))


if __name__ == '__main__':
    main()
