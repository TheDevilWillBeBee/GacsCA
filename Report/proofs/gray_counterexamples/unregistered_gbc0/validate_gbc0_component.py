"""Read-only provenance and exact mathematical replay of frozen GBC0.

Only --output is written outside a temporary directory. No registered or
retained receipt is overwritten. The replay uses the actual total rule,
issued beta and all five execution holders, not a host-rule opcode.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[4]
SOURCE = Path(__file__).resolve().parent
DATA = ROOT / 'figs/gray_counterexamples/unregistered_gbc0'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def normalized(value):
    if isinstance(value, dict):
        return {k: normalized(v) for k, v in value.items()
                if k != 'elapsed_seconds'}
    if isinstance(value, list):
        return [normalized(v) for v in value]
    return value


def run():
    start = time.monotonic()
    manifest_path = DATA / 'GBC0_manifest.json'
    manifest = json.loads(manifest_path.read_text())
    assets = manifest['assets']
    for name, digest in assets.items():
        assert sha(ROOT / name) == digest, (name, 'frozen dependency changed')
    scope = manifest['scope']
    assert scope['frozen'] and scope['prepared_delta_all_raw']
    assert scope['restricted_global_raw_period_equality']
    assert not any(scope[k] for k in ('full_own_beta', 'gray_counterexample',
                                    'iid_failure', 'shorter_U'))
    expected = json.loads((DATA / 'GBC0_certificate.json').read_text())
    expected_beta = json.loads((DATA / 'GBC0_passive_beta.json').read_text())
    assert expected['passed'] and expected['passive_upper_Age_interval'] == [1, 8192]
    assert expected['programme_bits'] == 1058 and expected['instructions'] == 80
    assert expected['K'] == 3087 and expected['2K'] == 6174
    assert expected['native_phases'] == 24576
    assert expected['five_bit_vote_cases'] == 3520
    assert len(expected_beta) == 8192 and set(expected_beta) == {0, 1}
    assert hashlib.sha256(bytes(expected_beta)).hexdigest() == expected['beta_sha256']
    assert sum(c['physical_local_checks'] for c in expected['cases']) == 20675
    assert all(c['halt_updates'] == 4135 and not c['wrong_raw_bits']
               for c in expected['cases'])
    missing = expected['first_missing_capture']
    assert missing['wrong_raw_bits'] == [97, 98, 99, 100, 101]
    assert missing['upper_output']['history1'] == [512] * 5
    assert missing['actual_upper_output']['history1'] == [0] * 5
    assert all(not expected[k] for k in ('full_own_beta', 'all_raw_own_equivalence',
                                        'universal_whole_rule_deadline', 'gray_refutation',
                                        'noise_theorem', 'iid_failure', 'shorter_U'))
    begin = time.monotonic()
    with tempfile.TemporaryDirectory(prefix='gbc0_replay_') as temporary:
        directory = Path(temporary)
        command = [sys.executable, '-u', str(SOURCE / 'check_compact_stream.py'),
                   '--output-dir', str(directory), '--full-physical']
        env = dict(os.environ)
        env['PYTHONDONTWRITEBYTECODE'] = '1'
        process = subprocess.run(command, cwd=ROOT, env=env, stdout=subprocess.PIPE,
                                 stderr=subprocess.STDOUT, text=True)
        assert process.returncode == 0, (process.returncode, process.stdout)
        actual = json.loads((directory / 'GBC0_certificate.json').read_text())
        actual_beta = json.loads((directory / 'GBC0_passive_beta.json').read_text())
        assert normalized(actual) == normalized(expected), 'full-value receipt mismatch'
        assert actual_beta == expected_beta, 'actual emitted beta mismatch'
    for name, digest in assets.items():
        assert sha(ROOT / name) == digest, (name, 'changed during read-only replay')
    replay = {'exit_code': process.returncode, 'all_full_values_equal': True,
              'actual_beta_equal': True, 'elapsed_seconds': time.monotonic() - begin}
    print(json.dumps({'stage': 'all_new_gbc0_checks', 'passed': True, **replay}), flush=True)
    return {'passed': True, 'manifest_sha256': sha(manifest_path),
            'asset_count': len(assets), 'asset_hashes': assets, 'scope': scope,
            'replay': replay, 'physical_execution_holder_checks': 20675,
            'native_phase_checks': 24576, 'universal_prepared_delta_bound': 4135,
            'counted_programme_bits': 1058, 'full_own_beta': False,
            'first_excluded_capture_wrong_bits': [97, 98, 99, 100, 101],
            'actual_error_history': [], 'recursive_intact_start': False,
            'noise_theorem': False, 'gray_refutation': False,
            'iid_failure': False, 'shorter_U': False,
            'elapsed_seconds': time.monotonic() - start}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True, type=Path)
    options = parser.parse_args()
    result = run()
    options.output.write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({k: v for k, v in result.items()
                      if k not in ('asset_hashes', 'scope', 'replay')}, sort_keys=True), flush=True)
