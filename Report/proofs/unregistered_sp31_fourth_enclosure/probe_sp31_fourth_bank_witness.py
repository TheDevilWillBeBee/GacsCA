#!/usr/bin/env python3
"""Shared captured-table witnesses only: physical reachability unproved."""
from pathlib import Path
import hashlib,json,sys,time
ROOT=Path(__file__).resolve().parents[3];S=ROOT/'Report/proofs'
sys.path[:0]=[str(ROOT),str(S),str(S/'unregistered_terminal'),str(Path(__file__).resolve().parent)]
from gacsca.netlist import Compiled
from probe_sp30_symbolic_left_absorption import AbsorptionNet
from check_native_command1024_first_pulse import blocked
from probe_sp31_fourth_enclosure import NATIVE,fourth_left_value,fourth_foreign_value
import proposed_native_command1024 as proposed
OUT=ROOT/'figs/robustness/unregistered_sp31_fourth_bank_witness'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def word(n,f,width):
    bits=[n.outputs['y',f,b] for b in range(width)]
    assert all(b in (0,1) for b in bits),(f,bits)
    return sum(v<<b for b,v in enumerate(bits))

def main():
    start=time.monotonic();p=proposed.parameters();c=proposed.load_artifact()
    certpath=ROOT/'figs/robustness/SP31_fourth_source_enclosure_certificate.json';cert=json.loads(certpath.read_text())
    assert cert['candidate_sha256']==c.digest() and cert['actual_full_fourth_source_enclosure_proved']
    phases={(r['field'],r['bit']):r['address'] for r in proposed.dependency_table(p)}
    strips=((148*p.Q,149*p.Q-512),(152*p.Q-512,152*p.Q));records=[]
    for mode in (0,1):
        for kind,receivers in (('true',range(132,148)),('foreign',range(149,152))):
            for j in receivers:
                class Prepared(AbsorptionNet):
                    def input(self,key):
                        if isinstance(key,tuple) and len(key)==4 and key[0] in ('fourth_true','fourth_partial','fourth_recovered','fourth_foreign'):
                            _,s,f,b=key
                            value=p.age_code(15) if mode and f=='age' else mode if f in ('f1','f2') else 0
                            return (value>>b)&1
                        if key==('fourth_foreign149_F2',):return mode
                        if isinstance(key,tuple) and len(key)==4 and key[0]=='x':
                            _,d,f,b=key
                            if f in NATIVE:
                                shifted=kind=='foreign'
                                if blocked(strips,j-int(shifted),d,phases[f,b]+512*int(shifted),p.Q):return 0
                                return fourth_foreign_value(self,p,j+d,f,b,q149=0) if shifted else fourth_left_value(self,p,j+d,f,b,a=0,q134=0,q141=0)
                        return super().input(key)
                n,_=proposed.full_net(p,Prepared)
                got={f:word(n,f,dict(c.schema)[f]) for f in ('addr','age','f1','f2','wf1','wf2')}
                assert got['f1']==1 and got['f2']==mode,(mode,kind,j,got)
                records.append(dict(mode=mode,kind=kind,j=j,outputs=got,netlist_sha256=Compiled(n).digest))
    OUT.mkdir(exist_ok=True)
    result=dict(scope='One shared assignment of proved J242 captured-bank enclosure gives all19 complete optional Flag2 commands1, another gives all0; partial commands merely allowed. No physical bank or initial-upperInfo reachability claim',
        Q=p.Q,U=p.U,candidate_sha256=c.digest(),netlist_sha256=c.comp.digest,
        probe_sha256=sha(__file__),source_enclosure_certificate_sha256=sha(certpath),
        input_table_source_sha256=sha(Path(__file__).with_name('probe_sp31_fourth_enclosure.py')),
        all_GF_exceptions=0,GF133_conditional_a=0,ones_free_Age=p.age_code(15),
        ones_all_free_old_Flag2=1,all_free_Workspace=0,cofactor_records=records,
        complete_optional_commands=19,selected_full_cofactors=len(records),
        remaining_two_partial_votes_assigned_only_as_enclosure=True,
        shared_captured_table_extreme_witnesses_checked=True,
        actual_physical_bank_or_initial_upper_Info_reachability_proved=False,
        actual_fourth_pulse_or_noise_failure_proved=False,
        active_G17_modified=False,additional_rule_change=False,global_reliability_established=False,
        seconds=time.monotonic()-start)
    (OUT/'witness_receipt.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(passed=True,selected_full_cofactors=len(records),complete_optional_commands=19,actual_physical_reachability_proved=False,seconds=result['seconds'])),flush=True)
if __name__=='__main__':main()
