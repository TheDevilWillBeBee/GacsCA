#!/usr/bin/env python3
"""F31 abstract suffix probe; no recovered-frame seed reachability theorem."""
from pathlib import Path
from types import FunctionType
import hashlib,json,sys,time
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT/'Report/proofs'))
import proposed_native_command1024 as actual
import probe_short_force1024_late_suffix as old
def main():
    ns=dict(old.__dict__,proposed=actual)
    fn=FunctionType(old.run.__code__,ns,old.run.__name__,old.run.__defaults__)
    p=actual.parameters();c=actual.load_artifact()
    listing_path=ROOT/'figs/robustness/SP31_program_listing.json'
    listing=json.loads(listing_path.read_text())
    started=time.monotonic();cases=[]
    for mode in ('all_readonly_zero','native_inputs_zero','shifted_initial_private_zero'):
        result=fn(p,c,listing,mode,284547);cases.append(result)
        fields={f:[v['proved_constant'] for k,v in result['selected_Hold_outputs'].items() if k.startswith(f+':')]
            for f in ('addr','age','f1','f2','wf1','wf2')}
        print(json.dumps(dict(mode=mode,selected_native_outputs=fields,terms=result['terms'])),flush=True)
    receipt=dict(scope='Abstract F31 suffix only; readonly hypotheses/free seed reachability not yet proved for recovered frames',
        candidate_sha256=c.digest(),listing_sha256=hashlib.sha256(listing_path.read_bytes()).hexdigest(),
        borrowed_probe_sha256=hashlib.sha256(Path(old.__file__).read_bytes()).hexdigest(),cases=cases,
        actual_recovered_frame_Age_bank_proved=False,additional_rule_change=False,
        global_reliability_established=False,seconds=time.monotonic()-started)
    (ROOT/'figs/robustness/SP31_abstract_native_late_suffix_exploration.json').write_text(json.dumps(receipt,indent=2)+'\n')
if __name__=='__main__':main()
