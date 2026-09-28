"""Bind the experimental compiler evidence without replacing baseline identity."""
from collections import Counter
import json
from pathlib import Path
from experiments.fixed_rule.audit_retimed_holder_prefix_embedding import sha
from gacsca.fixed_rule import sparse_holder_program as p, retimed_holder_rule as f
from gacsca.fixed_rule.wordcode import LIT


def main():
    fig = Path('figs/fixed_rule')
    out = fig / 'sparse_holder_compiler_evidence_v1.json'
    if out.exists():
        raise FileExistsError(out)
    prior_path = fig / 'lowmask_holder_compiler_evidence_v1.json'
    prior = json.loads(prior_path.read_text())
    files = dict(prior['files'])
    assert len(files) == 516
    for path, digest in files.items():
        assert sha(path) == digest, path
    for path, digest in prior['external_bank_sha256'].items():
        assert sha(path) == digest, path

    def bind(path, digest=None):
        path = Path(path)
        if path.is_absolute():
            path = path.relative_to(Path.cwd())
        actual = sha(path)
        assert digest is None or actual == digest, str(path)
        assert str(path) not in files or files[str(path)] == actual, str(path)
        files[str(path)] = actual

    documents = []
    for name in ('sparse_holder_rom_v1', 'sparse_holder_paths_v1'):
        path = fig / (name + '.json')
        doc = json.loads(path.read_text())
        assert doc['passed'] and doc['physical_descriptor_sha256'] == prior['descriptor_sha256']
        for source, digest in doc['source_sha256'].items():
            bind(source, digest)
        bind(path)
        documents.append(doc)
    rom, paths = documents
    assert rom['ROM_sha256'] == paths['ROM_sha256']
    assert rom['reference_ROM_sha256'] == prior['ROM_sha256']
    assert paths['packet_schedule']['passed']
    assert sha('figs/fixed_rule/retimed_holder_clock_transfer_v1.json') == paths['clock_transfer_sha256']
    for name in ('sparse_holder_rom_v1', 'sparse_holder_paths_v1', 'sparse_holder_tests_v1'):
        watch_path = fig / (name + '_watch.json')
        watch = json.loads(watch_path.read_text())
        assert watch['returncode'] == 0 and watch['termination_reason'] is None
        bind(watch_path)
        bind(fig / (name + '.log'))
    assert 'Ran 6 tests' in (fig / 'sparse_holder_tests_v1.log').read_text()
    for path in (prior_path, Path(__file__),
                 Path('Report/fixed_rule/SPARSE_RETRIEVAL.md'),
                 Path('Report/fixed_rule/STATUS_BEFORE_SPARSE_RETRIEVAL_20260927.md'),
                 Path('gacsca/fixed_rule/sparse_holder_initial.py'),
                 Path('tests/fixed_rule/test_sparse_holder.py')):
        bind(path)
    description = p.compiled_description()
    used = {wire for op, a, b in description.operations if op != LIT
            for wire in (a, b) if wire < description.inputs}
    used.update(wire for wire in description.outputs if wire < description.inputs)
    assert len(used) == 738
    counts = Counter(wire // f.FIELDS-7 for wire in used)
    result = dict(evidence_integrity_verified=True, prior_evidence_files_verified=516,
                  files=dict(sorted(files.items())), external_bank_sha256=prior['external_bank_sha256'],
                  descriptor_sha256=prior['descriptor_sha256'], ROM_sha256=prior['ROM_sha256'],
                  candidate_ROM_sha256=rom['ROM_sha256'], candidate_promoted_to_baseline=False,
                  controller_ticks_saved=rom['controller_ticks_saved'],
                  controller_ticks_after=rom['controller_path_ticks'],
                  complete_conditional_candidate_self_reference=True,
                  new_candidate_physical_period_executed=False, focused_tests_passed=6,
                  gathered_inputs=rom['gathered_inputs'], core_cells=rom['core_cells'],
                  Q=rom['Q'], U=rom['U'], parameters_actually_changed=False,
                  input_support_inventory=dict(dense_inputs=description.inputs, used_inputs=len(used),
                      used_words_by_offset=dict(sorted(counts.items())),
                      used_words=sorted(used), descriptor_sha256=description.digest(),
                      implemented_sparse_retrieval=True),
                  general_noise_theorem=False, full_project_goal_complete=False)
    with out.open('x') as stream:
        stream.write(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(json.dumps(dict(output=str(out), verified_files=len(files),
                          prior_files_unchanged=516, input_support_words=len(used))))


if __name__ == '__main__':
    main()
