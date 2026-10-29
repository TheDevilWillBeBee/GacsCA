#!/usr/bin/env python3
"""Provenance-check and read-only replay the isolated GFD0 component.

--issue writes only the new standalone manifest, after its issuer passes.
Default replay writes only temporary files, checks every pinned dependency,
recomputes all new mathematical checks, and compares exact graphs/C and arrays.
It does not rewrite main Gray documents/checkpoint or inherited GT0 assets.
"""
from pathlib import Path
import argparse, hashlib, json, subprocess, sys, tempfile, time
import numpy as np
ROOT=Path(__file__).resolve().parents[4]
SOURCE=Path(__file__).resolve().parent
FIG=ROOT/'figs/gray_counterexamples/unregistered_gfd0'
MANIFEST=FIG/'GFD0_standalone_assets.json'
RECEIPT=FIG/'GFD0_binary_stage3_certificate.json'


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def dependency_paths():
    paths=list(SOURCE.glob('*.py'))+list(SOURCE.glob('*.md'))
    paths += [ROOT/p for p in (
        'Report/proofs/gray_counterexamples/gray_raw_gather.py',
        'Report/proofs/gray_counterexamples/literal_maintenance.py',
        'Report/proofs/gray_counterexamples/GT0_RAW_GATHER.md',
        'Report/proofs/gray_counterexamples/GT0_RADIUS_INTEGRATION.md',
        'Report/proofs/gray_counterexamples/GRAY_COMPUTED_SIMBIT_ORDER.md',
        'Report/proofs/gray_counterexamples/unregistered_gi0/GI0_TOTAL_SOURCE_INTERFACE.md',
        'figs/gray_counterexamples/GT0_raw_gather_certificate.json',
        'figs/gray_counterexamples/GT0_transitions.json',
        'figs/gray_counterexamples/GT0_transitions.c',
        'figs/gray_counterexamples/GT0_transitions.so',
        'figs/gray_counterexamples/GT0_C_comparison_inputs_outputs.npz',
        'figs/gray_counterexamples/GT0_preliminary_frame_layout.json',
        'papers_txt/gray_readers_guide.txt',
        "papers/A Reader's Guide to Gacs's ``Positive Rates'' Paper.pdf",
        'Report/GRAY_COUNTEREXAMPLES.md',
        'Report/proofs/gray_counterexamples/validate_gray_counterexamples.py',
        'figs/gray_counterexamples/checkpoint_validation.json')]
    paths += list((ROOT/'gacsca').glob('*.py'))
    paths += [p for p in FIG.iterdir() if p.is_file() and p != MANIFEST
              and not p.name.startswith('GFD0_read_only_replay')]
    return sorted(set(paths))


def receipt_checks(receipt):
    assert receipt['passed'] is True
    assert (receipt['Q'],receipt['U'],receipt['lambda_'],receipt['c'])==(8192,1048576,24,104)
    assert receipt['component_frame_bits']==2322 and receipt['radius']==5
    assert receipt['input_bank_all_407_bits_free'] and receipt['native_oldF2zero_printed_h1_symbolic_identity']
    assert receipt['native_controls_actual_prefix_internal']
    assert receipt['late_WF_and_fifth_write_ports_open']
    assert receipt['symbolic_route_identities']==335480
    assert receipt['actual_three_gather_last_capture']==565250
    assert receipt['evaluation']==565288 and receipt['info_delivery']==655359
    for key in ('early_flag_oracle_or_immutable_instruction_ROM','own_beta_fit',
                'full_ProgramBit_hardwirer_refinement','full_period','continuing_E0',
                'Gray_counterexample','iid_theorem','shorter_U','final_frame_proved'):
        assert receipt[key] is False,key
    for path,digest in receipt['source_hashes'].items():assert sha(ROOT/path)==digest,path
    for name,digest in receipt['product_hashes'].items():assert sha(FIG/name)==digest,name
    old=json.loads((ROOT/'figs/gray_counterexamples/GT0_raw_gather_certificate.json').read_text())
    assert old['raw_full_state_gather_G_proved_for_component_conditionally']
    assert old['record_retention_R_proved_for_component_conditionally']
    assert old['actual_Gray_full_rule_G_R_refinement_proved'] is False
    for key,path in (
        ('primitive_sha256','Report/proofs/gray_counterexamples/gray_raw_gather.py'),
        ('written_proof_sha256','Report/proofs/gray_counterexamples/GT0_RAW_GATHER.md'),
        ('emitted_transition_graph_sha256','figs/gray_counterexamples/GT0_transitions.json'),
        ('emitted_C_source_sha256','figs/gray_counterexamples/GT0_transitions.c'),
        ('emitted_C_library_sha256','figs/gray_counterexamples/GT0_transitions.so'),
        ('C_comparison_asset_sha256','figs/gray_counterexamples/GT0_C_comparison_inputs_outputs.npz'),
        ('preliminary_layout_sha256','figs/gray_counterexamples/GT0_preliminary_frame_layout.json')):
        assert sha(ROOT/path)==old[key],path


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--issue',action='store_true')
    args=parser.parse_args();start=time.monotonic()
    receipt=json.loads(RECEIPT.read_text());receipt_checks(receipt)
    if args.issue:
        manifest=dict(name='GFD0 frozen binary stage-3 component',
            assets={str(path.relative_to(ROOT)):sha(path) for path in dependency_paths()},
            new_math_recomputed_by_default=True,inherited_GT0_exact_provenance_checked=True,
            main_gray_documents_unchanged=True,active_rule_unchanged=True,
            full_Gray_rule_or_iid_claim=False)
        MANIFEST.write_text(json.dumps(manifest,indent=2,sort_keys=True)+'\n')
        print(json.dumps(dict(issued=True,assets=len(manifest['assets']),manifest_sha256=sha(MANIFEST))),flush=True)
        return
    manifest=json.loads(MANIFEST.read_text())
    for path,digest in manifest['assets'].items():assert sha(ROOT/path)==digest,path
    with tempfile.TemporaryDirectory(prefix='gfd0_replay_') as directory:
        fresh=Path(directory)
        subprocess.run([sys.executable,str(SOURCE/'check_gfd0_binary_flag_delivery.py'),
                        '--outdir',str(fresh)],check=True,cwd=ROOT)
        replay=json.loads((fresh/RECEIPT.name).read_text())
        assert replay==receipt,'new mathematical certificate differs'
        for name in receipt['product_hashes']:
            if name.endswith('.npz'):
                with np.load(FIG/name) as old,np.load(fresh/name) as new:
                    assert set(old.files)==set(new.files)
                    for key in old.files:assert np.array_equal(old[key],new[key]),(name,key)
            else:assert sha(FIG/name)==sha(fresh/name),name
    for path,digest in manifest['assets'].items():assert sha(ROOT/path)==digest,path
    print(json.dumps(dict(passed=True,readonly=True,elapsed=time.monotonic()-start,
        assets=len(manifest['assets']),certificate_sha256=sha(RECEIPT),manifest_sha256=sha(MANIFEST),
        actual_binary_radius5_component=True,complete_Gray_rule=False,iid_theorem=False)),flush=True)


if __name__=='__main__':main()
