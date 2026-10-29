"""Finite raw-holder transcriptions for GAWN11; no repair trajectory.

The universal SF confinement and conditional boundary arguments are written
separately. These selected arbitrary-word cofactors do not prove Address
termination, upper triple correction or iid reliability.
"""
from pathlib import Path
from dataclasses import replace
import argparse,hashlib,json,random,sys,time
import numpy as np
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(HERE.parent/'unregistered_gawn2'))
import small_rule_gawn2 as k
import small_compositional_cost as own
T0=100*k.Q+2
SF=('heads','mem','out','info','scratch','program','courier_l','courier_r',
    'mail_l','mail_r','history1','history2','history3')
WIDTHS=dict(heads=k.HEAD_BITS,mem=17*k.WORD,history1=17*k.WORD,
            history2=17*k.WORD,history3=17*k.WORD)
SCENARIOS=((4,8),(9,1),(9,k.Q-1),(k.Q-104,104),(0,3),(0,8),(3,1),(0,k.Q-1))
AGES=(T0,T0+103,127*k.Q-1,127*k.Q,k.U-1)
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def add(d,value):d.update((json.dumps(value,separators=(',',':'))+'\n').encode())
def ell_at(b,delta):
    r=(b-3+delta)%k.Q
    return b-3-r if r<=5 else b-3
def pair_at(ell):return (0,2*k.Q) if ell>=1 else (-k.Q,2*k.Q)
def random_word(rng,name):return rng.getrandbits(WIDTHS.get(name,k.WORD))
def geometry():
    delta=np.arange(1,k.Q,dtype=np.int32);dig=hashlib.sha256();pair=triple=0
    for b in range(k.Q):
        r=(b-3+delta)%k.Q;ell=np.where(r<=5,b-3-r,b-3).astype(np.int16)
        assert np.all(ell>=b-8)
        pair+=int(np.count_nonzero(ell>=1));triple+=int(np.count_nonzero(ell<=0));dig.update(ell.tobytes())
    assert (pair,triple)==(16756730,16390)
    holder_rows=[]
    for ell in range(-8,k.Q-3):
        lo,hi=pair_at(ell)
        for y in (lo-3,lo-2,lo-1,hi,hi+1,hi+2,lo,hi-1):
            holders=[y-s for s in k.SLOTS]
            good=[x for x in holders if not ell<=x<k.Q]
            assert len(good)>=3,(ell,y,holders)
            holder_rows.append([ell,lo,hi,y,len(good)])
    assert all(ell_at(b,delta)>=1 for b,delta in SCENARIOS[:4])
    assert all(ell_at(b,delta)<=0 for b,delta in SCENARIOS[4:])
    return dict(all_b_delta_pairs=pair+triple,adjacent_pair_cases=pair,triple_cases=triple,
        ell_array_sha256=dig.hexdigest(),all_conservative_ell_values=k.Q+5,
        endpoint_and_exterior_holder_counts=len(holder_rows),minimum_canonical_holders=3,
        holder_geometry_sha256=hashlib.sha256(json.dumps(holder_rows,separators=(',',':')).encode()).hexdigest())
def native(rng,x,b,delta,ell,age):
    foreign=ell<=x<k.Q and rng.randrange(2)
    return dict(addr=(x+delta*foreign)%k.Q,age=age,
        f1=rng.randrange(2) if -k.Q<=x<k.Q else 0,
        f2=rng.randrange(2) if b-3<=x<k.Q else 0,
        wf1=rng.randrange(2) if b<=x<min(b+104,k.Q) and age<T0+104 else 0,
        wf2=rng.randrange(2) if b<=x<min(b+104,k.Q) and age<T0+104 else 0)
def force_minority(state,b,delta,ell,age):
    # Exact admissible native-envelope cofactor: three raw WF2 bits in A
    # force foreign computed GF at x=1, while x<=0 stays canonical.
    if (b,delta)==(4,8) and age in AGES[:2]:
        for x in state:
            if ell<=x<=ell+12:state[x]=replace(state[x],addr=(x+delta)%k.Q)
            if 4<=x<=6:state[x]=replace(state[x],wf2=1)
def packet(rng,index,bit):
    if index==0:p=k.unpack(rng.getrandbits(k.HEAD_BITS))
    elif index==1:p=k.Packet(p=1,mode=k.SEEK,target=rng.choice((0,k.Q-1)),regs=tuple(rng.getrandbits(k.WORD) for _ in range(16)))
    elif index==2:p=k.Packet(p=1,mode=k.RUN,pc=rng.randrange(own.ROM.token_count),regs=tuple(rng.getrandbits(k.WORD) for _ in range(16)))
    elif index==3:p=k.Packet(p=1,mode=k.HALT,move=2 if bit==0 else 1)
    elif index==4:p=k.Packet(p=1,mode=k.ERROR,move=3)
    else:p=k.Packet(p=0,move=3)
    return k.pack(replace(p,move=p.move&~(1<<bit)))
def endpoints():
    rng=random.Random(0x4741574e313101);dig=hashlib.sha256();cases=kernels=foreign_controls=0
    branches=dict(active=0,hold=0,reset=0);canonical_outputs=0
    for b,delta in SCENARIOS:
        ell=ell_at(b,delta);lo,hi=pair_at(ell)
        for endpoint in (lo,hi-1):
            bit=1 if endpoint==lo else 0
            for age in AGES:
                for style in range(6):
                    state={x:k.Cell(**native(rng,x,b,delta,ell,age),
                        **{name:tuple(random_word(rng,name) for _ in k.SLOTS) for name in SF})
                        for x in range(endpoint-10,endpoint+11)}
                    force_minority(state,b,delta,ell,age)
                    good=[]
                    for h,s in enumerate(k.SLOTS):
                        x=endpoint-s;canonical=not ell<=x<k.Q
                        words=list(state[x].heads)
                        words[h]=packet(rng,style,bit) if canonical else (1<<k.HEAD_BITS)-1
                        state[x]=replace(state[x],heads=tuple(words))
                        if canonical:good.append(h)
                    assert len(good)>=3
                    old_vote=k.unpack(k.vote([state[endpoint-s].heads[h] for h,s in enumerate(k.SLOTS)]))
                    assert not(old_vote.move&(1<<bit))
                    outputs=[];next_heads=[]
                    for h,s in enumerate(k.SLOTS):
                        x=endpoint-s;out=k.local_transition({j:state[x+j] for j in range(-8,9)},own.ROM)
                        assert out.age==(age+1)%k.U and not out.wf1 and not out.wf2
                        if h in good:
                            assert out.addr==x%k.Q
                            assert not(k.unpack(out.heads[h]).move&(1<<bit));canonical_outputs+=1
                        else:foreign_controls+=out.addr!=x%k.Q
                        branch='reset' if out.age==0 else 'active' if out.age<=127*k.Q else 'hold'
                        branches[branch]+=1;outputs.append([hex(v) for v in k.cell_words(out)])
                        next_heads.append(out.heads[h]);kernels+=1
                    assert not(k.unpack(k.vote(next_heads)).move&(1<<bit))
                    add(dig,[b,delta,ell,endpoint,age,style,good,
                        [[hex(v) for v in k.cell_words(state[x])] for x in range(endpoint-10,endpoint+11)],outputs])
                    cases+=1
    assert (cases,kernels)==(480,2400) and foreign_controls>0 and all(branches.values())
    return dict(selected_endpoint_configs=cases,actual_full_kernel_calls=kernels,
        actually_foreign_computed_minority_controls=foreign_controls,
        canonical_holder_zero_forbidden_bit_outputs=canonical_outputs,
        actual_Head_branch_counts=branches,arbitrary_all13_SF_selected=True,
        malformed_Head_and_two_noncanonical_minority_controls_admitted=True,
        inputs_outputs_sha256=dig.hexdigest())
def clean_word(name,z):
    if name in ('mail_l','mail_r','courier_l','courier_r'):return 0
    if name=='program':return k.beta_bit(own.ROM,z%k.Q)
    if name=='heads':return k.pack(k.Packet(p=1,mode=k.HALT))
    width=WIDTHS.get(name,k.WORD)
    return int.from_bytes(hashlib.shake_256(f'GAWN11:{name}:{z}'.encode()).digest((width+7)//8),'little')&((1<<width)-1)
def exterior():
    rng=random.Random(0x4741574e313102);dig=hashlib.sha256();cases=kernels=foreign_controls=f1_external=0
    for b,delta in SCENARIOS:
        ell=ell_at(b,delta);lo,hi=pair_at(ell)
        for y in (lo-1,lo-2,hi,hi+1):
            for age in AGES:
                state={};reference={}
                for x in range(y-10,y+11):
                    actual_fields={};reference_fields={}
                    for name in SF:
                        vals=[];ref=[]
                        for s in k.SLOTS:
                            z=x+s;ref.append(clean_word(name,z))
                            value=random_word(rng,name) if lo<=z<hi else ref[-1]
                            if name=='heads' and z in (lo,hi-1):
                                bit=1 if z==lo else 0
                                p=k.unpack(value);value=k.pack(replace(p,move=p.move&~(1<<bit)))
                            vals.append(value)
                        actual_fields[name]=tuple(vals);reference_fields[name]=tuple(ref)
                    state[x]=k.Cell(**native(rng,x,b,delta,ell,age),**actual_fields)
                    reference[x]=k.Cell(addr=x%k.Q,age=age,**reference_fields)
                force_minority(state,b,delta,ell,age)
                actual=[];expected=[];outputs=[]
                for h,s in enumerate(k.SLOTS):
                    x=y-s
                    got=k.local_transition({j:state[x+j] for j in range(-8,9)},own.ROM)
                    want=k.local_transition({j:reference[x+j] for j in range(-8,9)},own.ROM)
                    assert got.age==want.age==(age+1)%k.U
                    foreign_controls+=got.addr!=x%k.Q;f1_external+=got.f1
                    actual.append({name:getattr(got,name)[h] for name in SF})
                    expected.append({name:getattr(want,name)[h] for name in SF})
                    outputs.append([[hex(v) for v in k.cell_words(got)],[hex(v) for v in k.cell_words(want)]])
                    kernels+=2
                for name in SF:
                    assert k.vote([v[name] for v in actual])==k.vote([v[name] for v in expected]),(b,delta,y,age,name)
                add(dig,[b,delta,ell,y,age,
                    [[hex(v) for v in k.cell_words(state[x])] for x in range(y-10,y+11)],outputs])
                cases+=1
    assert (cases,kernels)==(160,1600) and foreign_controls>0 and f1_external>0,(cases,kernels,foreign_controls,f1_external)
    return dict(selected_exterior_configs=cases,actual_and_reference_full_kernel_calls=kernels,
        all13_voted_outputs_equal_reference=True,
        actually_foreign_computed_minority_controls=foreign_controls,
        external_computed_Flag1_positive_outputs=f1_external,
        clean_late_Mail_zero_erasure_compared=True,inputs_outputs_sha256=dig.hexdigest())
def compute():
    g=geometry();e=endpoints();x=exterior()
    sources=(Path(__file__),HERE/'GAWN11_ADDRESS_BURST_SF_CONFINEMENT.md',
        HERE.parent/'unregistered_gawn2/small_rule_gawn2.py',HERE.parent/'unregistered_gawn2/small_compositional_cost.py')
    return dict(name='GAWN11 exact late two-offset Address-burst logical SF confinement',passed=True,
        Q=k.Q,U=k.U,lambda_original=24,error_separation=104,first_fault_row=T0,
        GAWN10_exact_fault_hypotheses_required=True,
        universal_logical_SF_confinement_without_nativequiet_proved=True,raw_holder_halo=2,
        adjacent_pair_if_ell_at_least=1,otherwise_triple=True,
        conditional_nativequiet_after_last_fault_beforeU_required=True,
        actual_U_represented_D_encoding_proved_conditionally=True,
        adjacent_pair_complete2U_alllater_proved_conditionally=True,
        triple_exact2U_encoding_reduction_proved_conditionally=True,
        universal_Address_termination_upper_triple_repair_general_higher_iid_proved=False,
        faithful_Gray_G17_refutation_shorterU_or_global_minimum_proved=False,
        new_evolving_fullSF_Address_burst_or_complete2U_physical_simulation=False,
        rule_ROM_constants_G17_changed=False,geometry=g,endpoint_full_kernel=e,exterior_full_kernel=x,
        source_sha256={str(p.relative_to(ROOT)):sha(p) for p in sources})
def main():
    parser=argparse.ArgumentParser();parser.add_argument('--write',action='store_true');args=parser.parse_args()
    start=time.perf_counter();result=compute()
    if args.write:
        out=ROOT/'figs/gray_counterexamples/unregistered_gawn11/GAWN11_SF_confinement_certificate.json'
        out.parent.mkdir(parents=True,exist_ok=True);out.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(passed=True,pair_geometries=result['geometry']['adjacent_pair_cases'],
        triple_geometries=result['geometry']['triple_cases'],endpoint_configs=480,exterior_configs=160,
        full_kernel_calls=4000,unconditional_SF_confinement=True,
        nativequiet_still_required_for_boundary=True,full_reliability=False,elapsed=time.perf_counter()-start)))
if __name__=='__main__':main()
