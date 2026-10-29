"""Small exact native transcription supplement to primary Gray review."""
from hashlib import sha256
from pathlib import Path
import argparse,json,sys
ROOT=Path(__file__).resolve().parents[4];sys.path.insert(0,str(ROOT))
from gacsca.maintenance import maintenance_scalar
def digest(p):return sha256(p.read_bytes()).hexdigest()
def run(output):
    paper=next((ROOT/'papers').glob('A Reader*'))
    text=ROOT/'papers_txt/gray_readers_guide.txt';lines=text.read_text().splitlines()
    flattened=' '.join(text.read_text().split())
    assert 'whose Age value differs from a. Otherwise, there is consistency' in flattened
    assert 'the computed value of Flag1 at x is 0 or' in flattened
    cases=[]
    for Q in (4096,8192):
        for x in range(-8,9):
            old={j:dict(addr=(x+j)%Q,age=2 if x+j in (-1,0,1) else 1,
                        f1=0,f2=0,wf1=0,wf2=0) for j in range(-5,6)}
            got=maintenance_scalar(old,Q,128*Q)
            want=dict(addr=x%Q,age_now=1,age=2,f1=int(x in (-4,-3,-2)),f2=0)
            assert got==want,(Q,x,got,want)
            cases.append({'Q':Q,'target':x,'old_neighborhood':old,'actual_output':got})
    source=Path(__file__);proof=source.with_name('GRAY_AGE_TRIPLE_PRIMARY_COMPARISON.md')
    scalar=ROOT/'gacsca/maintenance.py'
    out={'passed':True,'scope':'primary literal-native comparison and34 finite first-update cofactors',
         'Q_baseline':8192,'U_baseline':1048576,'lambda':24,'c':104,
         'cases':cases,'primary_text_locations':{
             'Age_inconsistency':[896,898],'clock_selector':[982,986],'Proposition2':[1174,1181]},
         'sources':{str(p.relative_to(ROOT)):digest(p) for p in (source,proof,paper,text,scalar)},
         'native_clock_glider':False,'missing_printed_Age_clause':False,
         'Gray_Proposition2_counterexample':False,'full_physical_replay':False,
         'lower_to_upper_fault_realizability_proved':False,'iid_claim':False}
    output.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps({k:v for k,v in out.items() if k!='cases'},indent=2))
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True)
    run(p.parse_args().output)
