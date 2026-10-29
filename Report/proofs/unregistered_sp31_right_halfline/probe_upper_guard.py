#!/usr/bin/env python3
"""Exact unchanged full-F31 native output at the first upper WF tick."""
from pathlib import Path
import hashlib,json,sys,time
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT),str(ROOT/'Report/proofs'),str(ROOT/'Report/proofs/unregistered_terminal')]
import proposed_native_command1024 as proposed
from gacsca.netlist import Compiled
from probe_sp30_symbolic_left_absorption import AbsorptionNet
NATIVE=('addr','age','f1','f2','wf1','wf2')
OUT=ROOT/'figs/robustness/unregistered_sp31_right_halfline'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def compute():
    t=time.monotonic();p=proposed.parameters();c=proposed.load_artifact();rows=[]
    for bit,age in ((0,p.T_wf),(1,p.T_wf-1),(1,p.T_wf)):
        class Guard(AbsorptionNet):
            def input(self,key):
                if isinstance(key,tuple) and len(key)==4 and key[0]=='x':
                    _,d,f,b=key
                    if f in NATIVE:
                        value=d%p.Q if f=='addr' else p.age_code(age) if f=='age' else 0
                        return (value>>b)&1
                    if f=='info' and d+proposed.SLOTS[b]==3:return bit
                return super().input(key)
        n,_=proposed.full_net(p,Guard)
        values={f:sum(n.outputs['y',f,b]<<b for b in range(dict(proposed.schema(p))[f]))
                for f in NATIVE if all(n.outputs['y',f,b] in (0,1) for b in range(dict(proposed.schema(p))[f]))}
        expected=dict(addr=0,age=p.age_code(age+1),f1=0,f2=0,wf1=0,wf2=int(bit==1 and age==p.T_wf))
        assert values==expected,(bit,age,values,expected)
        rows.append(dict(upper_Age=age,logical_special_Info3=bit,native_outputs=values,full_net_cofactor_sha256=Compiled(n).digest))
    return dict(Q=p.Q,U=p.U,TF=p.T_wf,candidate_sha256=c.digest(),netlist_sha256=c.comp.digest,
        probe_sha256=sha(__file__),selected_full_unchanged_native_cofactors=rows,
        all_unmentioned_SF_Instruction_and_Info_inputs_symbolic=True,
        output_WF2_one_is_a_legitimate_shadow_command_not_a_noise_failure=True,
        physical_prepared_A_guard_sharpness_supplied_by_separate_written_proof=False,
        actual_J225_late_failure_or_Gray_G17_iid_failure_or_minimum_proved=False,
        rule_ROM_constants_or_G17_changed=False,global_reliability_established=False,
        seconds=time.monotonic()-t)
def main():
    path=OUT/'upper_guard_probe01_receipt.json';assert not path.exists()
    r=compute();path.write_text(json.dumps(r,indent=2)+'\n')
    print(json.dumps(dict(passed=True,full_cofactors=3,seconds=r['seconds'])),flush=True)
if __name__=='__main__':main()
