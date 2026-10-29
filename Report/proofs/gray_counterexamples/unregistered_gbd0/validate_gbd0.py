"""Read-only replay of every NEW GBD0 claim, exact inherited provenance."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time

ROOT=Path(__file__).resolve().parents[4]
HERE=Path(__file__).resolve().parent
MANIFEST=ROOT/'figs/gray_counterexamples/unregistered_gbd0/GBD0_manifest.json'


def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()


def check_assets(assets):
    for name,h in assets.items():
        assert sha(ROOT/name)==h,(name,'source/receipt hash mismatch')


def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True)
    a=p.parse_args();start=time.monotonic()
    m=json.loads(MANIFEST.read_text());check_assets(m['assets'])
    old=ROOT/m['inherited_manifest'];oldm=json.loads(old.read_text())
    check_assets(oldm['assets'])
    for name in ('inherited_child_replay','inherited_parent_replay'):
        r=json.loads((ROOT/m[name]).read_text())
        assert r['passed'] and r['hashes_unchanged']
        assert r['manifest_sha256']==sha(old)
        assert not r['whole_own_beta'] and not r['universal_full_runtime']
    with tempfile.TemporaryDirectory(prefix='gbd0_replay_') as temp:
        out=Path(temp)/'new.json'
        env=dict(os.environ,PYTHONDONTWRITEBYTECODE='1')
        run=subprocess.run([sys.executable,str(HERE/'check_design.py'),
                            '--output',str(out)],cwd=ROOT,env=env,
                            stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
        assert run.returncode==0,run.stderr
        new=json.loads(out.read_text())
        accepted=json.loads((ROOT/m['receipt']).read_text())
        assert new==accepted,'new mathematical receipt disagrees'
    check_assets(m['assets'])
    for flag in ('complete_rule','complete_own_emitter','Q_bit_own_beta',
                 'whole_period','faithful_Gray','noise_theorem',
                 'Gray_refutation','iid_failure','shorter_U'):
        assert new[flag] is False
    r=dict(passed=True,assets=len(m['assets']),hashes_unchanged=True,
           manifest_sha256=sha(MANIFEST),
           receipt_sha256=sha(ROOT/m['receipt']),
           inherited_exact_provenance_only=True,all_new_claims_recomputed=True,
           source_coordinate_cases=new['packed_window']['coordinate_control_cases'],
           full_value_comparisons=new['packed_window']['selected_full_value_comparisons'],
           component_gate_upper_bound=new['packed_window']['gate_upper_bound']['total'],
           physical_stencil=new['packed_window']['physical_stencil'],
           exact_listing_bits=42716,non_cpu_remainder_bits=13523,
           hybrid_K_arithmetic_only=3262,full_rule=False,own_beta=False,
           universal_runtime=False,physical_period=False,
           faithful_Gray=False,gray_refutation=False,iid_failure=False,
           shorter_U=False,elapsed_seconds=time.monotonic()-start)
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(r,indent=2)+'\n')
    print(json.dumps(r,indent=2))


if __name__=='__main__':main()
