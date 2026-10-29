#!/usr/bin/env python3
"""Proof-only semantic refinement cofactor; unchanged physical F31 is pinned.

Two valid equal outward blocks plus a raw equal default imply that the
literal joint3/4 replacement equals that default, irrespective of the
other two blocks. The written proof supplies universal word scope.
This adapter substitutes only that identity while building cofactors;
it is never installed in a physical rule, ROM, or candidate.
"""
from contextlib import contextmanager
from itertools import product
from pathlib import Path
import hashlib,json,sys,time
ROOT=Path(__file__).resolve().parents[3]
sys.path[:0]=[str(ROOT),str(ROOT/'Report/proofs'),str(ROOT/'Report/proofs/unregistered_terminal')]
import proposed_native_command1024 as proposed
from gacsca.netlist import Compiled,Net,majority_word,w_add_const_mod
from probe_sp30_symbolic_left_absorption import AbsorptionNet
NATIVE=('addr','age','f1','f2','wf1','wf2')
OUT=ROOT/'figs/robustness/unregistered_sp31_right_halfline'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def quorum_lemma():
    # Equalities, not selected bit values: each input pair is default A or
    # one of at most two other classes B/C. B and C may coincide.
    count=0;trace=hashlib.sha256()
    for a,b,c,vb,vc in product(range(4),range(4),range(4),(False,True),(False,True)):
        blocks=[(b,vb),(c,vc),(a,True),(a,True)]
        triples=[x for x in range(4) if sum(valid and word==x for word,valid in blocks)>=3]
        assert not triples or triples==[a]
        n=Net();bits=lambda x:[(x>>i)&1 for i in range(2)]
        value,exists=proposed.local.block_quorum(n,[(bits(x),int(v)) for x,v in blocks],bits(a))
        assert value==bits(a) and exists==int(bool(triples))
        trace.update(f'{a},{b},{c},{int(vb)},{int(vc)},{value},{exists};'.encode());count+=1
    assert count==256
    # Source semantics of both quorum primitives are pinned by the manifest;
    # this finite table supplements the arbitrary-word equality proof.
    return dict(selected_two_bit_exact_joint_quorum_cases=count,trace_sha256=trace.hexdigest(),
                universal_word_scope_supplied_by_written_equality_argument=True)
@contextmanager
def refinement_identity(receiver):
    old=proposed.local.refine
    def specialized(n,cells,p):
        out={}
        for d in proposed.local.REFINED:
            if receiver+d>=0:
                raw=[*cells[d]['addr'],*cells[d]['age']]
                assert all(v in (0,1) for v in raw)
                for center in (10,30):
                    words=[]
                    for u in range(-2,3):
                        displacement=center+u;c=cells[d+displacement]
                        adjusted=w_add_const_mod(n,c['addr'],(-displacement)%p.Q,p.Q)
                        words.append([*adjusted,*c['age']])
                    value,valid=majority_word(n,words,raw)
                    assert value==raw and valid==1,(receiver,d,center)
                out[d]=dict(addr=cells[d]['addr'],age=cells[d]['age'])
            else:out[d]=proposed.local.refine_one(n,cells,p,d)[0]
        return out
    proposed.local.refine=specialized
    try:yield
    finally:proposed.local.refine=old
def outputs(n,p):
    return {f:sum(n.outputs['y',f,b]<<b for b in range(dict(proposed.schema(p))[f]))
        for f in NATIVE if all(n.outputs['y',f,b] in (0,1) for b in range(dict(proposed.schema(p))[f]))}
def upper(p):
    rows=[]
    for age,j in product((295,p.T_wf-1),(*range(38),1019,1020,1021,1022,1023)):
        class Half(AbsorptionNet):
            def input(self,key):
                if isinstance(key,tuple) and len(key)==4 and key[0]=='x':
                    _,d,f,b=key;t=j+d
                    if t>=0 and f in NATIVE:
                        value=t%p.Q if f=='addr' else p.age_code(age) if f=='age' else 0
                        return (value>>b)&1
                return super().input(key)
        with refinement_identity(j):n,_=proposed.full_net(p,Half)
        v=outputs(n,p);expected=dict(addr=j%p.Q,age=p.age_code(age+1),f1=0,f2=0,wf1=0,wf2=0)
        assert v==expected,(age,j,v,expected)
        rows.append(dict(Age=age,receiver=j,outputs=v,semantic_cofactor_sha256=Compiled(n).digest))
    return rows
def lower(p):
    rows=[];phases=(0,1,2,3,4,5,6,37,38,511,512,513,1018,1019,1020,1021,1022,1023)
    for age,j in product((0,p.T_wf,p.T_wf+2*p.Q,p.U-1),phases):
        class Half(AbsorptionNet):
            def input(self,key):
                if isinstance(key,tuple) and len(key)==4 and key[0]=='x':
                    _,d,f,b=key;t=j+d
                    if t>=0 and f in NATIVE:
                        value=t%p.Q if f=='addr' else p.age_code(age) if f=='age' else 0
                        return (value>>b)&1
                    if f=='info':
                        primary=t+proposed.SLOTS[b]
                        if primary>=0 and primary%p.Q in (3,509,515,1021):return 0
                return super().input(key)
        with refinement_identity(j):n,_=proposed.full_net(p,Half)
        v=outputs(n,p);expected=dict(addr=j%p.Q,age=p.age_code((age+1)%p.U),f1=0,f2=0,wf1=0,wf2=0)
        assert v==expected,(age,j,v,expected)
        rows.append(dict(Age=age,receiver=j,outputs=v,semantic_cofactor_sha256=Compiled(n).digest))
    return rows
def compute():
    start=time.monotonic();p=proposed.parameters();c=proposed.load_artifact();old=proposed.local.refine
    r=dict(Q=p.Q,U=p.U,TF=p.T_wf,radius=37,candidate_sha256=c.digest(),netlist_sha256=c.comp.digest,
        probe_sha256=sha(__file__),quorum=quorum_lemma(),upper_cofactors=upper(p),lower_cofactors=lower(p),
        proof_only_semantic_refiner_identity_not_physical_rule_change=True,
        arbitrary_left_native_words_and_unmentioned_SF_Instruction_Info_inputs_symbolic=True,
        selected_phase_Age_cofactors_measured_supplements=True,
        universal_native_halfline_scope_and_physical_period_supplied_by_separate_written_proof=False,
        future_physical_or_all_time_general_higher_iid_or_minimum_proved=False,
        rule_ROM_constants_or_G17_changed=False,global_reliability_established=False)
    assert proposed.local.refine is old
    r['seconds']=time.monotonic()-start;return r
def main():
    OUT.mkdir(parents=True,exist_ok=True);path=OUT/'halfline_contract_probe01_receipt.json';assert not path.exists()
    r=compute();path.write_text(json.dumps(r,indent=2)+'\n')
    print(json.dumps(dict(passed=True,upper_cofactors=len(r['upper_cofactors']),lower_cofactors=len(r['lower_cofactors']),seconds=r['seconds'])),flush=True)
if __name__=='__main__':main()
