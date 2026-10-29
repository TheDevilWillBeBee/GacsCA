#!/usr/bin/env python3
"""Exploratory universal commit/reset ports; no fifth command theorem."""
from pathlib import Path
from types import FunctionType
import hashlib,json,sys,time
ROOT=Path(__file__).resolve().parents[3];S=ROOT/'Report/proofs'
sys.path[:0]=[str(ROOT),str(S),str(S/'unregistered_terminal')]
from gacsca.netlist import Net,Compiled,const_word,w_eq,w_add_const_mod
import proposed_native_command1024 as proposed
import check_native_command1024_encoded as encoded
from probe_sp30_symbolic_left_absorption import AbsorptionNet

OUT=ROOT/'figs/robustness/unregistered_sp31_fourth_reset'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def conditional_commit(p):
    seen={}
    def controller(n,cells,*args,**kwargs):
        gf=[n.input(('proof','free_computed_GF',b)) for b in range(p.k)]
        f1=n.input(('proof','free_computed_F1'))
        seen.update(gf=gf,selfgf=cells[0]['addr'],f1=f1)
        return dict(addr=gf,age_now=const_word(p.age_code(p.U-1),p.m),age=const_word(0,p.m),
            f1=f1,f2=n.input(('proof','free_computed_F2')))
    namespace=dict(proposed.legacy.__dict__,schema=proposed.schema,width=proposed.width,
        previous=proposed.previous,dependency_table=proposed.dependency_table,
        service_build=proposed.service_build,pulse=proposed.pulse,
        generated_source=proposed.generated_source,proposed_build=lambda:(controller,'conditional interface only'))
    fn=proposed.legacy.full_net
    n,_=FunctionType(fn.__code__,namespace,fn.__name__,fn.__defaults__)(p,AbsorptionNet)
    fields={f for f,_ in proposed.schema(p)}-{'addr','age','f1','info'}
    zeros=0
    for f,width in proposed.schema(p):
        if f in fields:
            for b in range(width):assert n.outputs['y',f,b]==0,(f,b);zeros+=1
    assert zeros==807
    keep=n.NOT(n.AND(seen['f1'],n.NOT(w_eq(n,seen['gf'],seen['selfgf']))))
    expr=[]
    for slot in proposed.SLOTS:
        address=w_add_const_mod(n,seen['gf'],slot%p.Q,p.Q)
        expected=n.AND(keep,n.AND(encoded.old_encoding.allowed(n,address,p),encoded.reset.forwarded_hold(n,p,0,slot)))
        values=encoded.reset.normalized(n)
        assert values[n.outputs['y','info',slot+2]]==values[expected],slot
        expr.append(dict(slot=slot,normalized_Info_forwarding_identity=True))
    return dict(private_and_native_reset_bits=zeros,masked_keep_Hold_Info_identities=expr,
        refined_self_and_computed_GF_independent=True,conditional_netlist_sha256=Compiled(n).digest)

def actual_common_clock_commit(p):
    class Bound(AbsorptionNet):
        def input(self,key):
            if isinstance(key,tuple) and len(key)==4 and key[0]=='x' and key[2]=='age':
                return (p.age_code(p.U-1)>>key[3])&1
            return super().input(key)
    n,_=proposed.full_net(p,Bound)
    for b in range(p.m):assert n.outputs['y','age',b]==0,('Age',b)
    fields={f for f,_ in proposed.schema(p)}-{'addr','age','f1','info'}
    count=0
    for f,width in proposed.schema(p):
        if f in fields:
            for b in range(width):assert n.outputs['y',f,b]==0,(f,b);count+=1
    assert count==807
    return dict(common_raw_legal_Age=p.U-1,raw_GF_flags_SF_and_instruction_all_free=True,
        native_successor_Age_zero_bits=p.m,all807_reset_bits_zero=True,actual_cofactor_netlist_sha256=Compiled(n).digest)

def aliases(p):
    normal=(set(range(58,901))-{509,515})|{901,902,965}
    cases=[]
    for phase in (3,509,515,1021):
        for slot in proposed.SLOTS:
            for label in (0,1):
                holder=(phase-slot)%p.Q;virtual=(holder+512*label+slot)%p.Q
                assert virtual in (3,509,515,1021) and virtual not in normal
                cases.append(dict(physical_phase=phase,slot=slot,computed_GF_label=label,virtual_primary=virtual,Info_zero=True))
    assert len(cases)==40
    return cases

def compute():
    start=time.monotonic();p=proposed.parameters();c=proposed.load_artifact()
    assert c.digest()=='dc456bac4904647b66ee1f922788cdeb4428df91e21858fd8de0b3ccb4a69421'
    return dict(Q=p.Q,U=p.U,radius=37,candidate_sha256=c.digest(),netlist_sha256=c.comp.digest,
        probe_sha256=sha(__file__),conditional_commit=conditional_commit(p),actual_common_clock_commit=actual_common_clock_commit(p),
        alias_cases=aliases(p),
        actual_fourth_boundary_and_quiet_fifth_prefix_lift_supplied_by_written_proof=False,
        fifth_commands_or_full_upper_successor_or_eventual_general_higher_iid_or_minimum_proved=False,
        additional_rule_change=False,active_G17_modified=False,Gray_or_G17_refutation=False,
        global_reliability_established=False,seconds=time.monotonic()-start)

def main():
    OUT.mkdir(parents=True,exist_ok=True);path=OUT/'reset_cofactor_receipt.json';assert not path.exists()
    r=compute();path.write_text(json.dumps(r,indent=2)+'\n')
    print(json.dumps(dict(passed=True,reset_bits=r['conditional_commit']['private_and_native_reset_bits'],
        actual_all_free_GF_common_clock_reset=r['actual_common_clock_commit']['all807_reset_bits_zero'],
        alias_cases=len(r['alias_cases']),seconds=r['seconds'])),flush=True)
if __name__=='__main__':main()
