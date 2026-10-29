"""Read-only primary comparison replay; exact pins before and after."""
from hashlib import sha256
from pathlib import Path
import argparse,json,subprocess,sys,tempfile
ROOT=Path(__file__).resolve().parents[4];S=Path(__file__).resolve().parent
D=ROOT/'figs/gray_counterexamples/unregistered_gray_age_triple_review'
def digest(p):return sha256(p.read_bytes()).hexdigest()
def run(output):
    mp=D/'Gray_age_triple_review_manifest.json';m=json.loads(mp.read_text())
    before={r:digest(ROOT/r) for r in m['assets']};assert before==m['assets']
    old=json.loads((D/'Gray_age_triple_primary_comparison.json').read_text())
    for rel,h in old['sources'].items():assert digest(ROOT/rel)==h,rel
    with tempfile.TemporaryDirectory(prefix='gray-triple-primary-') as td:
        tmp=Path(td)/'comparison.json'
        r=subprocess.run([sys.executable,str(S/'check_gray_age_triple_primary.py'),'--output',str(tmp)],cwd=ROOT,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,text=True)
        assert r.returncode==0,r.stdout
        assert json.loads(tmp.read_text())==old
    assert old['passed'] and len(old['cases'])==34
    for k in ('native_clock_glider','missing_printed_Age_clause','Gray_Proposition2_counterexample','full_physical_replay','lower_to_upper_fault_realizability_proved','iid_claim'):
        assert old[k] is False,k
    assert {r:digest(ROOT/r) for r in m['assets']}==before
    out={'passed':True,'hashes_unchanged':True,'assets':len(before),'cofactors':34,
         'manifest_sha256':digest(mp),'receipt_sha256':digest(D/'Gray_age_triple_primary_comparison.json'),
         'primary_comparison_only':True,'Gray_refutation':False,'iid_claim':False}
    output.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);run(p.parse_args().output)
