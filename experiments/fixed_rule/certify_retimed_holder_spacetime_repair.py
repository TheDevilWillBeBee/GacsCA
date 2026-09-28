"""Compose and replay the complete-descriptor conditional one-step invariant.

No new physical transition, field, ROM, or recovery shortcut is installed.
The healthy premises must hold at every transition to which this lemma is applied.
"""
import argparse
import json
import resource
import time
from pathlib import Path
from gacsca.fixed_rule import retimed_holder_rule as f
from experiments.fixed_rule.compose_retimed_holder_sparse_repair import compose
from experiments.fixed_rule.certify_retimed_holder_two_tick_repair import structural
from experiments.fixed_rule.certify_retimed_holder_replica_repair import gates, cut
from experiments.fixed_rule.run_retimed_holder_streamed_repair import sha


def certify():
    sparse = compose()  # validates all 55 geometry cases and their source hashes
    structure = structural()  # replay complete outputs, not just a receipt boolean
    majority = gates()
    full_cut = cut()
    procedure = {f's{k}_{name}' for k in range(5) for name, _ in f.PROCEDURE}
    other = set(structure['all_mutable_nonprocedure_fields_equal'])
    static = {name for name, _ in f.STATIC}
    assert len(procedure) == 90 and len(other) == 15 and len(static) == 49
    assert procedure | other | static == {name for name, _ in f.SCHEMA}
    assert not (procedure & other or procedure & static or other & static)
    gp = Path('figs/fixed_rule/retimed_holder_two_site_geometry_v1.json')
    geometry = json.loads(gp.read_text())
    for case in geometry['cases']:
        assert all(name not in procedure for _, name in case['support'])
        assert all(name in other for _, name in case['support'])
    assert set(structure['healthy_output_coherent_procedure_fields']) == {n for n, _ in f.PROCEDURE}
    assert structure['unrestricted_logical_procedure_words'] and structure['no_head_count_assumption']
    return dict(
        passed=True, descriptor_sha256=f.self_description().digest(),
        geometry_ignores_all_previous_procedure_residuals=True,
        complete_structural_certificate_replayed=True,
        majority_gate_checks=majority,
        complete_procedure_cut_groups=full_cut['identified_majority_groups'],
        structural_cut_groups=structure['cut_groups'],
        current_geometry_window=11, previous_union_current_vote_window=5,
        maximum_defects_per_window=2,
        procedure_fields=sorted(procedure), nonprocedure_fields=sorted(other),
        static_fields=sorted(static), all_legal_clocks=f.U, all_addresses=f.Q,
        proof_inputs=sparse['proof_inputs'],
        hypotheses=[
            'Infinite line, or periodic ring of size divisible by Q.',
            'Healthy input x has canonical Address, uniform legal Age, zero Flag1/Flag2 and all Wf copies, coherent fivefold procedure words and coherent fivefold Signals.',
            'Before this step, z differs from x only in procedure fields at sites P; values at these sites may be arbitrary typed words.',
            'Input y is obtained from z by arbitrary complete G-state replacements at sites D.',
            'Each eleven-site interval contains at most two sites of D.',
            'Each five-site interval contains at most two sites of P union D.'
        ],
        conclusion='G(y) differs from G(x) only in procedure fields at sites D. All nonprocedure and reconstructed metadata fields agree everywhere. Healthy output procedure copies remain coherent.',
        induction='For consecutive transitions set P to the preceding D (or any verified residual-support subset), check both spatial bounds, and require the healthy-context premises at each input time. No fault-free global time gap is needed. A step with D empty then yields complete equality.',
        limitations='Conditional deterministic continuing-noise lemma. Healthy Signal/flag/Wf premises are not claimed invariant across forcing or capture. No noise threshold, cluster recovery, probability estimate, hierarchical amplification or execution shortcut.',
        trusted_basis='Exact BDD geometry receipts, replayed Boolean majority and complete DAG/algebra cuts, and the stated finite dependency composition; not a proof-assistant derivation.'
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    out = Path(args.output)
    if out.exists():
        raise FileExistsError(out)
    started = time.perf_counter()
    result = certify()
    sources = (Path(__file__), Path('experiments/fixed_rule/compose_retimed_holder_sparse_repair.py'), Path('experiments/fixed_rule/certify_retimed_holder_two_tick_repair.py'), Path('experiments/fixed_rule/certify_retimed_holder_replica_repair.py'), Path('gacsca/fixed_rule/retimed_holder_spacetime_domain.py'), Path(f.__file__))
    result.update(seconds=time.perf_counter()-started, host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss, source_sha256={str(p): sha(p) for p in sources})
    out.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, indent=2), flush=True)


if __name__ == '__main__':
    main()
