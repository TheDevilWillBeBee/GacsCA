#!/usr/bin/env python3
"""Separate fifth-source certificates after the universal fourth reset."""
from collections import Counter
from itertools import product
from pathlib import Path
import hashlib,json,sys,time
ROOT=Path(__file__).resolve().parents[3];S=ROOT/'Report/proofs'
sys.path[:0]=[str(ROOT),str(S),str(S/'unregistered_terminal')]
from gacsca.netlist import const_word,Compiled
import proposed_native_command1024 as proposed
from probe_sp30_symbolic_left_absorption import AbsorptionNet
from check_native_command1024_first_pulse import blocked
OUT=ROOT/'figs/robustness/unregistered_sp31_fourth_reset'
NATIVE=('addr','age','f1','f2','wf1','wf2')
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def left_value(n,p,t,f,b):
    # Enclosure after the proved joint-refinement reduction. The optional
    # GF choices are enlarged to independent choices only by adding states.
    if f=='addr':
        if t<=135:return ((t%p.Q)>>b)&1
        if t<=140:return n.input(('optional_canonical',t)) if (t>>b)&1 else 0
        return n.input(('free_GF',t,b))
    if f=='age':return (p.age_code(4)>>b)&1 if t<=135 else n.input(('free_Age',t,b))
    if f=='f1':return int(t>=106) if t<=141 else n.input(('free_F1',t))
    if f=='f2':return 0 if t<=131 else n.input(('free_F2',t))
    if f=='wf1':return 0 if t<=140 else n.input(('free_WF1',t))
    if f=='wf2':return 0 if t<=141 else n.input(('free_WF2',t))
    raise AssertionError(f)

def flag_population_proof(p):
    cases=0;signature=hashlib.sha256()
    for j,v in product(range(106,140),range(p.Q)):
        known=[d for d in range(1,9) if j+d<=141 and v+d<p.Q]
        if len(known)>=3:branch='right3'
        elif j>=106 and len(known)>=2:branch='self_and_right2'
        else:
            matches=0;inside=0
            for d in range(-1,-6,-1):
                if 0<=v+d<p.Q:
                    inside+=1;t=j+d;poss={t%p.Q} if t<=135 else {0,t}
                    matches+=int((v+d)%p.Q in poss)
            assert inside-matches>=3,(j,v,known,inside,matches)
            branch='left_mismatch3'
        signature.update(f'{j},{v},{branch};'.encode());cases+=1
    assert cases==34816
    return dict(right_quorum_word_population_cases=cases,signature_sha256=signature.hexdigest(),
        no_right_quorum_forces_F1=True,range_proved=[106,139])

def native_supplements(p,build):
    selected=[]
    for j,v in product(range(106,140),(0,1020,1021,1022,1023)):
        n=AbsorptionNet();cells={}
        for d in range(-5,9):
            cells[d]={f:([left_value(n,p,j+d,f,b) for b in range(p.k if f=='addr' else p.m)]
                if f in ('addr','age') else left_value(n,p,j+d,f,0)) for f in NATIVE}
            if 1<=d<=5:cells[d]['addr']=const_word((v+d)%p.Q,p.k)
        got=build(n,cells,p.k,p.m,Q=p.Q,nb=p.nb,radix=p.R,pos_bits=p.PB,service_force=0)
        assert got['f1']==1,(j,v,'selected_RF_word')
        selected.append(dict(receiver=j,right_GF_quorum=v,F1_constant_one=True))
    exact=[]
    for j in range(92,133):
        n=AbsorptionNet();cells={d:{f:([left_value(n,p,j+d,f,b) for b in range(p.k if f=='addr' else p.m)]
            if f in ('addr','age') else left_value(n,p,j+d,f,0)) for f in NATIVE} for d in range(-5,9)}
        got=build(n,cells,p.k,p.m,Q=p.Q,nb=p.nb,radix=p.R,pos_bits=p.PB,service_force=0)
        assert got['f1']==int(j>=100) and got['f2']==0,(j,'known_left_flags')
        exact.append(dict(receiver=j,F1=int(j>=100),F2=0))
    return dict(selected_right_word_native_cofactors=selected,known_left_native_flags=exact,
        selected_checks_measured_supplements=True)

def full_foreign_and_right(p):
    foreign=[];right=[]
    for h in range(152,155):
        class Foreign(AbsorptionNet):
            def input(self,key):
                if isinstance(key,tuple) and len(key)==4 and key[0]=='x':
                    _,d,f,b=key;t=h+d
                    if f=='addr' and t>=153:return 0
                    if f in NATIVE and t>=155:return 0
                return super().input(key)
        n,_=proposed.full_net(p,Foreign)
        assert n.outputs['y','f1',0]==1,('foreign',h)
        foreign.append(dict(receiver=h,F1=1,full_cofactor_sha256=Compiled(n).digest))
    for j in range(155,196):
        class Right(AbsorptionNet):
            def input(self,key):
                if isinstance(key,tuple) and len(key)==4 and key[0]=='x':
                    _,d,f,b=key;t=j+d
                    if f in NATIVE:
                        v=(t%p.Q if f=='addr' else p.age_code(4) if f=='age' else 0) if t>=155 else 0
                        return (v>>b)&1
                return super().input(key)
        n,_=proposed.full_net(p,Right)
        assert n.outputs['y','f1',0]==int(j<=157) and n.outputs['y','f2',0]==0,(j,'right')
        right.append(dict(receiver=j,F1=int(j<=157),F2=0,full_cofactor_sha256=Compiled(n).digest))
    return dict(complete_foreign_full_cofactors=foreign,right_full_cofactors=right,
        cofactor_checks_supplement_written_refinement_and_flag_proofs=True)

def routes_and_work(p):
    strip=((155*p.Q-512,155*p.Q),);phases={(r['field'],r['bit']):r['address'] for r in proposed.dependency_table(p)}
    counts=Counter()
    for row in proposed.dependency_table(p):
        if row['field'] not in NATIVE:continue
        phase=row['address']
        for j in range(155,192):
            for d in row['offsets']:
                for gather in p.gathers_q:
                    assert blocked(strip,j,d,phase,p.Q)==(j+d<=154),(j,d,phase)
                    counts['right_true_native_routes']+=1
        for h in range(152,155):
            for d in row['offsets']:
                for gather in p.gathers_q:
                    hit=blocked(strip,h-1,d,phase+512,p.Q)
                    assert hit==(h+d>=155),(h,d,phase,hit)
                    counts['foreign_right_barrier_native_routes']+=1
        for j in range(92,142):
            for d in row['offsets']:
                if j+d<=141:
                    # All such routes stay left of the possible Flag1 hull.
                    assert max(j*p.Q+phase,(j+d)*p.Q+phase)<142*p.Q-2
                    counts['left_known_native_clear_routes']+=3
    margins=[]
    for h in range(152,155):
        origin=(h-1)*p.Q+512
        assert 152*p.Q-512<=origin+58-39 and origin+965+39<155*p.Q-512
        assert origin+3-2>=152*p.Q-512 and origin+1021+2<155*p.Q-512
        margins.append(dict(foreign_frame=h,origin=origin,work_with_native_margin=[origin+58-39,origin+965+39],
            courier_holder_interval=[origin+1,origin+1023]))
    return dict(route_counts=dict(counts),complete_foreign_work_and_courier_margins=margins)

def aliases(p):
    one={'509':list(range(152,155)),'1021':[*range(100,140),*range(155,158)],'3':[],'515':[]}
    free={'509':list(range(142,152)),'1021':list(range(140,151)),'3':list(range(133,152)),'515':list(range(142,155))}
    assert sum(map(len,free.values()))==53 and sum(map(len,one.values()))==46
    roles=[]
    for phase,j,slot in product((3,509,515,1021),range(92,196),proposed.SLOTS):
        y=j*p.Q+phase;x=y-slot
        labels=(0,) if x<142*p.Q+1 or x>=155*p.Q else (1,) if x>=152*p.Q-512 else (0,1)
        virtual=[(phase+512*b)%p.Q for b in labels]
        special=any(v in (3,1021) for v in virtual)
        if j in one[str(phase)] or j in free[str(phase)]:assert special,(phase,j,slot,virtual)
        if phase==509 and not 142<=j<=154:assert not special
        if phase==515 and not 142<=j<=154:assert not special
        if phase==3 and 152<=j<=154:assert not special
        if phase==1021 and 151<=j<=154:assert not special
        roles.append(dict(physical_phase=phase,colony=j,slot=slot,possible_virtual_primaries=virtual))
    return dict(one_colonies=one,free_colonies=free,other_votes_zero=True,free_votes=53,enclosure_members=1<<53,
        one_votes=46,holder_alias_roles=roles,independence_or_reachability_proved=False)

def compute():
    start=time.monotonic();p=proposed.parameters();c=proposed.load_artifact();build,source=proposed.proposed_build()
    return dict(Q=p.Q,U=p.U,TF=p.T_wf,fifth_source_time=4*p.U+p.T_wf,radius=37,
        candidate_sha256=c.digest(),netlist_sha256=c.comp.digest,probe_sha256=sha(__file__),
        maintenance_source_sha256=hashlib.sha256(source.encode()).hexdigest(),
        left_flag_population=flag_population_proof(p),native_checks=native_supplements(p,build),
        full_checks=full_foreign_and_right(p),physical_routes=routes_and_work(p),command_enclosure=aliases(p),
        actual_fifth_source_lift_supplied_by_written_proof=False,
        actual_fifth_pulse_or_full_upper_successor_or_eventual_general_higher_iid_or_minimum_proved=False,
        additional_rule_change=False,active_G17_modified=False,Gray_or_G17_refutation=False,
        global_reliability_established=False,seconds=time.monotonic()-start)
def main():
    OUT.mkdir(parents=True,exist_ok=True);path=OUT/'fifth_source_cofactor_receipt.json';assert not path.exists()
    r=compute();path.write_text(json.dumps(r,indent=2)+'\n')
    print(json.dumps(dict(passed=True,free_votes=53,one_votes=46,source_time=r['fifth_source_time'],
        population_cases=34816,selected_native=len(r['native_checks']['selected_right_word_native_cofactors']),
        foreign_full=len(r['full_checks']['complete_foreign_full_cofactors']),right_full=len(r['full_checks']['right_full_cofactors']),seconds=r['seconds'])),flush=True)
if __name__=='__main__':main()
