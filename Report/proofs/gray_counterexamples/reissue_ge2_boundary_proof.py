"""Provenance-only GE2 reissue after a narrower raw-fixture clarification.

The checker, finite programme/event kernel, accepted dependencies and
results are unchanged. Preserve the completed-run proof/receipt/log;
the read-only validator then independently repeats every computation.
"""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[3]


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def reissue():
    source=Path(__file__).parent;directory=ROOT/'figs/gray_counterexamples'
    initial=directory/'GE2_second_prefix_initial_certificate.json'
    row=json.loads(initial.read_text())
    assert row['checker_sha256']==digest(source/'check_ge2_second_native_prefix.py')
    for name,value in row['source_dependencies_sha256'].items():assert digest(source/name)==value
    for name,value in row['receipt_dependencies_sha256'].items():assert digest(directory/name)==value
    oldproof=directory/'GE2_second_prefix_initial_proof.md'
    assert digest(oldproof)==row['proof_sha256']
    proof=source/'GE2_SECOND_NATIVE_PREFIX.md';text=proof.read_text()
    begin=text.index('\n\nThe local fixtures are raw representatives')
    end=text.index('\n\n## Second native window',begin)
    assert text[:begin]+text[end:]==oldproof.read_text()
    assert 'no whole-row raw-copy equality is assumed there.' in text[begin:end]
    row['proof_only_reissue_after_finite_run']=dict(initial_receipt_sha256=digest(initial),
        initial_proof_sha256=row['proof_sha256'],checker_and_all_computed_results_changed=False,
        clarification='unused SF and minority boundary raw copies are input-vote-equivalent representatives')
    row['proof_sha256']=digest(proof)
    row['source_dependencies_sha256']['reissue_ge2_boundary_proof.py']=digest(__file__)
    row['source_dependencies_sha256']['validate_ge2_second_native_prefix.py']=digest(source/'validate_ge2_second_native_prefix.py')
    row['retained_initial_assets_sha256']={name:digest(directory/name) for name in
        ('GE2_second_prefix_initial_proof.md','GE2_second_prefix_initial_certificate.json',
         'GE2_second_prefix_initial_check.log')}
    path=directory/'GE2_second_native_prefix_certificate.json'
    path.write_text(json.dumps(row,indent=2)+'\n')
    print(json.dumps(dict(proof_only_reissued_receipt_sha256=digest(path),computed_results_unchanged=True)))


if __name__=='__main__':reissue()
