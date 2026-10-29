"""Freeze the new GBC0 component only, after sources and receipts settle."""
import hashlib
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[4]
SOURCE = Path(__file__).resolve().parent
DATA = ROOT / 'figs/gray_counterexamples/unregistered_gbc0'


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


registered = {
    'Report/GRAY_COUNTEREXAMPLES.md': '27efe30dca8bb4a94077158cc8b56f2c49143ddae927ecbc23c3af02170c775c',
    'Report/proofs/gray_counterexamples/validate_gray_counterexamples.py': '8e921ae50894401b0c133e5c280c9e02411dcf6760b5d985c1e88b536e39506d',
    'figs/gray_counterexamples/checkpoint_validation.json': 'df969dd88774a8714a3dd019eed1f9f74b7cd0d92dd73ed1596712564267bb7d',
}
for name, digest in registered.items():
    assert sha(ROOT / name) == digest, (name, 'registered child checkpoint changed')
paths = []
for directory in (SOURCE, DATA):
    for path in directory.iterdir():
        if path.is_file() and path.suffix in ('.py', '.md', '.json', '.log'):
            if path.name.startswith(('GBC0_manifest', 'GBC0_validation', 'GBC0_readonly')):
                continue
            paths.append(path)
dependencies = [
    'gacsca/maintenance.py', 'gacsca/netlist.py', 'gacsca/__init__.py',
    'gacsca/candidates.py', 'gacsca/rule.py', 'gacsca/compiler.py',
    'papers_txt/gray_readers_guide.txt',
    'Report/proofs/gray_counterexamples/unregistered_gbp2/profile_frozen_gbp1r.py',
    'figs/gray_counterexamples/unregistered_gbp2/GBP1R_actual_cost_profile.json',
    'Report/proofs/gray_counterexamples/unregistered_gbp0/GBP1R_OWN_EMISSION_AND_CLEAN_DEADLINE.md',
    *registered,
]
paths.extend(ROOT / name for name in dependencies)
assets = {str(p.relative_to(ROOT)): sha(p) for p in sorted(set(paths))}
scope = {
    'frozen': True, 'Q': 8192, 'U': 1048576, 'lambda': 24, 'c': 104,
    'name': 'GBC0 total binary radius8 machine with partial immutable Q-bit programme',
    'radius': 8, 'K': 3087, 'Head_bits': 553, 'immutable_code_capacity': 8192,
    'actual_programme_bits': 1058, 'dictionary_bits': 0,
    'prepared_delta_all_raw': True, 'universal_prepared_delta_updates': 4135,
    'restricted_global_raw_period_equality': True,
    'upper_native_premise': 'canonical GF/common Age theta in [1,Q]/old native flags and Workspace zero',
    'upper_SF_premise': 'every bit pattern, including incoherent five copies',
    'first_excluded_capture_clean_own_identity_failure': True,
    'upper_failure_phase': 8193, 'failure_wrong_raw_bits': [97, 98, 99, 100, 101],
    'full_own_beta': False, 'all_raw_own_equivalence': False,
    'universal_whole_rule_deadline': False, 'recursive_intact_start': False,
    'physical_error_history': [], 'gray_counterexample': False,
    'noise_theorem': False, 'iid_failure': False, 'shorter_U': False,
    'active_rule_modified': False, 'registered_checkpoint_modified': False,
}
result = {
    'scope': scope, 'assets': assets,
    'provenance': 'The initial unpinned diagnostic is explicitly historical. The final check02 receipt is reproduced exactly from the pinned current sources; only wall times are excluded. The restricted period theorem is a written universal proof, supported by literal execution-holder and native checks.',
    'validator_command': 'python3 Report/proofs/gray_counterexamples/unregistered_gbc0/validate_gbc0_component.py --output /tmp/GBC0_parent_readonly_validation.json',
}
(DATA / 'GBC0_manifest.json').write_text(json.dumps(result, indent=2) + '\n')
print(json.dumps({'passed': True, 'assets': len(assets),
                  'manifest_sha256': sha(DATA / 'GBC0_manifest.json')}))
