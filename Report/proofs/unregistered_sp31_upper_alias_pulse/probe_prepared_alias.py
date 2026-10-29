#!/usr/bin/env python3
"""Selected frozen full-R cofactors for a prepared upper alias pulse.

This is a proof supplement. It does not simulate a physical noise
history or supply the independent infinite-line/encoding induction.
"""
from pathlib import Path
import hashlib,json,sys,time
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT),str(ROOT/'Report/proofs'),str(ROOT/'Report/proofs/unregistered_terminal')]
import proposed_native_command1024 as proposed
from gacsca.netlist import Compiled
from probe_sp30_symbolic_left_absorption import AbsorptionNet
OUT=ROOT/'figs/robustness/unregistered_sp31_upper_alias_pulse'
NATIVE=('addr','age','f1','f2','wf1','wf2')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def at(r,x):
    return next((v for a,b,v in r['native_segments'] if a<=x<b),0)
def refined(r,x):
    votes=sum(sum(bool(at(r,x+c+u)&1) for u in range(-2,3))>=3 for c in (-30,-10,10,30))
    return int(votes>=3) if votes!=2 else at(r,x)&1
def info_holder(rows,t,x,slot):
    y=x+slot
    if y!=1021:return 0
    if t==0:return 1
    prev,now=rows[t-1],rows[t]
    vote=int(y in prev['voted_Info_ones']);v=at(now,x)
    return vote*int(not ((v&2) and ((v&1)!=refined(prev,x))))
def compute():
    start=time.monotonic();p=proposed.parameters();cand=proposed.load_artifact()
    rows=[json.loads(x) for x in (OUT/'native_trace02.jsonl').read_text().splitlines()][:-1]
    checks=[]
    times=(0,1,169,170,171,172,342,343,510,511)
    points=(-16898,-16896,-513,-512,-37,-3,0,2,3,4,169,173,509,512,1018,1019,1021,1023,1024)
    for t in times:
        for x in points:
            class ActualNative(AbsorptionNet):
                def input(self,key):
                    if isinstance(key,tuple) and len(key)==4 and key[0]=='x':
                        _,d,f,b=key;z=x+d;v=at(rows[t],z)
                        if f in NATIVE:
                            value=(z+512*(v&1))%p.Q if f=='addr' else p.age_code(p.T_wf+t) if f=='age' else (v>>1)&1 if f=='f1' else (v>>2)&1 if f=='wf1' else 0
                            return (value>>b)&1
                        if f=='info':return info_holder(rows,t,z,proposed.SLOTS[b])
                    return super().input(key)
            n,_=proposed.full_net(p,ActualNative)
            values={f:sum(n.outputs['y',f,b]<<b for b in range(dict(proposed.schema(p))[f]))
                    for f in NATIVE if all(n.outputs['y',f,b] in (0,1) for b in range(dict(proposed.schema(p))[f]))}
            v=at(rows[t+1],x)
            expected=dict(addr=(x+512*(v&1))%p.Q,age=p.age_code(p.T_wf+t+1),
                          f1=(v>>1)&1,f2=0,wf1=(v>>2)&1,wf2=0)
            assert values==expected,(t,x,values,expected)
            checks.append(dict(relative_row=t,receiver=x,outputs=values,full_cofactor_sha256=Compiled(n).digest))
    return dict(Q=p.Q,U=p.U,TF=p.T_wf,candidate_sha256=cand.digest(),netlist_sha256=cand.comp.digest,
                probe_sha256=sha(__file__),trace_sha256=sha(OUT/'native_trace02.jsonl'),
                selected_actual_native_and_Info_holder_cofactors=checks,
                actual_Info_holder_erasures_reconstructed_from_old_vote_and_refined_self_keep=True,
                all_unmentioned_private_SF_and_Instruction_inputs_symbolic=True,
                selected_checks_measured_supplements=True,
                universal_infinite_line_prepared_or_physical_lift_supplied_by_this_probe=False,
                original_J225_history_noise_failure_or_iid_threshold_claim=False,
                rule_ROM_constants_or_G17_changed=False,global_reliability_established=False,
                seconds=time.monotonic()-start)
def main():
    path=OUT/'prepared_alias_cofactors01.json';assert not path.exists()
    r=compute();path.write_text(json.dumps(r,indent=2)+'\n')
    print(json.dumps(dict(passed=True,cofactors=len(r['selected_actual_native_and_Info_holder_cofactors']),seconds=r['seconds'])),flush=True)
if __name__=='__main__':main()
