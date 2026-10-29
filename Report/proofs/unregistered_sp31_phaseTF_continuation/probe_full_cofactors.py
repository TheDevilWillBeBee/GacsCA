#!/usr/bin/env python3
"""New full-R native/alias and current-reset supplements for J261's fault."""
from pathlib import Path
import hashlib,json,sys,time
ROOT=Path(__file__).resolve().parents[3];HERE=Path(__file__).resolve().parent
sys.path[:0]=[str(ROOT),str(ROOT/'Report/proofs'),str(ROOT/'Report/proofs/unregistered_terminal'),
    str(ROOT/'Report/proofs/unregistered_sp31_upper_alias_pulse')]
import proposed_native_command1024 as proposed
import check_native_command1024_first_pulse as first
import probe_prepared_alias as factor
from probe_sp30_symbolic_left_absorption import AbsorptionNet
from gacsca.netlist import Compiled
OUT=ROOT/'figs/robustness/unregistered_sp31_phaseTF_continuation'
NATIVE=('addr','age','f1','f2','wf1','wf2');ALIASES=(3,509,515,1021)
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def compute():
    start=time.monotonic();p=proposed.parameters();candidate=proposed.load_artifact()
    trace=OUT/'native_trace01.jsonl';rows=[json.loads(s) for s in trace.read_text().splitlines()][:-1]
    checks=[]
    times=(0,170,171,172,510,511,512,513,854,855,2048,6143)
    points=(-15361,-15360,-14849,-14848,-513,-512,-3,0,2,173,512,1019,1021,1024)
    for t in times:
        for x in points:
            class ActualNative(AbsorptionNet):
                def input(self,key):
                    if isinstance(key,tuple) and len(key)==4 and key[0]=='x':
                        _,d,f,b=key;z=x+d;v=factor.at(rows[t],z)
                        if f in NATIVE:
                            value=(z+512*(v&1))%p.Q if f=='addr' else p.age_code(p.T_wf+t) if f=='age' else (v>>1)&1 if f=='f1' else (v>>2)&1 if f=='wf1' else 0
                            return (value>>b)&1
                        if f=='info' and (z+proposed.SLOTS[b])%p.Q in ALIASES:
                            return factor.info_holder(rows,t,z,proposed.SLOTS[b])
                    return super().input(key)
            n,_=proposed.full_net(p,ActualNative)
            values={f:sum(n.outputs['y',f,b]<<b for b in range(dict(proposed.schema(p))[f]))
                for f in NATIVE if all(n.outputs['y',f,b] in (0,1) for b in range(dict(proposed.schema(p))[f]))}
            v=factor.at(rows[t+1],x)
            expect=dict(addr=(x+512*(v&1))%p.Q,age=p.age_code(p.T_wf+t+1),f1=(v>>1)&1,f2=0,wf1=(v>>2)&1,wf2=0)
            assert values==expect,(t,x,values,expect)
            checks.append(dict(relative_row=t,receiver=x,native_outputs=values,full_cofactor_sha256=Compiled(n).digest))
    # The original exact common-clock quiet fragment, at the new endpoints.
    quiet=first.quiet_cofactors(p,L=-14,R=1)
    reset=[]
    commit_points=sorted({*(y-s for col in (0,1) for a in ALIASES for y in (col*p.Q+a,) for s in proposed.SLOTS),
        -15361,-15360,-14849,-14848,-14847,511,512,1023,1024})
    for x in commit_points:
        class CurrentCommit(AbsorptionNet):
            def input(self,key):
                if isinstance(key,tuple) and len(key)==4 and key[0]=='x':
                    _,d,f,b=key;z=x+d;label,flag=first.template(z,p.Q,L=-14,R=1)
                    if f in NATIVE:
                        value=(z+512*label)%p.Q if f=='addr' else p.age_code(p.U-1) if f=='age' else flag if f=='f1' else 0
                        return (value>>b)&1
                    if f=='info' and (z+proposed.SLOTS[b])%p.Q in ALIASES:return 0
                return super().input(key)
        n,_=proposed.full_net(p,CurrentCommit)
        private=[v for key,v in n.outputs.items() if len(key)==3 and key[0]=='y' and key[1] not in ('addr','age','f1','info')]
        assert len(private)==807 and all(v==0 for v in private),(x,'reset')
        label,flag=first.template(x,p.Q,L=-14,R=1)
        expect=dict(addr=(x+512*label)%p.Q,age=0,f1=flag,f2=0,wf1=0,wf2=0)
        values={f:sum(n.outputs['y',f,b]<<b for b in range(dict(proposed.schema(p))[f])) for f in NATIVE}
        assert values==expect,(x,values,expect)
        alias_bits=[b for b,s in enumerate(proposed.SLOTS) if (x+s)%p.Q in ALIASES]
        assert all(n.outputs['y','info',b]==0 for b in alias_bits)
        reset.append(dict(receiver=x,native_outputs=values,reset_output_bits=807,
            zero_alias_Info_components=alias_bits,full_cofactor_sha256=Compiled(n).digest))
    return dict(Q=p.Q,U=p.U,TF=p.T_wf,candidate_sha256=candidate.digest(),netlist_sha256=candidate.comp.digest,
        probe_sha256=sha(__file__),trace_sha256=sha(trace),selected_actual_native_alias_cofactors=checks,
        exact_new_endpoint_free_common_clock_quiet_fragment=quiet,selected_full_current_commit_cofactors=reset,
        all_other_private_SF_instruction_and_ordinary_Info_inputs_symbolic=True,
        selected_full_R_checks_measured_supplements=True,
        universal_allrow_actual_lift_quiet_tail_reset_and_encoded_bit_interval_proved_by_this_probe=False,
        full_remaining_Info_at_U_later_repair_original_J225_or_iid_claim=False,
        rule_ROM_constants_or_G17_changed=False,global_reliability_established=False,seconds=time.monotonic()-start)
def main():
    path=OUT/'full_cofactors01.json';assert not path.exists();r=compute()
    path.write_text(json.dumps(r,indent=2)+'\n')
    print(json.dumps(dict(passed=True,native_alias_cofactors=len(r['selected_actual_native_alias_cofactors']),
        free_clock_quiet_fragment=r['exact_new_endpoint_free_common_clock_quiet_fragment'],
        current_full_commit_cofactors=len(r['selected_full_current_commit_cofactors']),seconds=r['seconds'])),flush=True)
if __name__=='__main__':main()
