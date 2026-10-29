"""Intact GAW2R real1 final-rest fault: actual commit/Mail spread/recovery.

Frozen GAW2R and emitted beta are used unchanged. No Gray attribution.
The global physical-prefix lift uses the accepted noiseless period proof.
"""
from pathlib import Path
from dataclasses import replace,asdict
from functools import lru_cache
import hashlib,json,sys,time
ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT/'Report/proofs/gray_counterexamples/unregistered_gaw2'))
sys.path.insert(0,str(ROOT))
import gray_three_gather_gaw2r as k
import gaw2r_compositional_cost as own
from gacsca import gray_errors
D=ROOT/'figs/gray_counterexamples/unregistered_gaw4'
TARGET=k.PRIMARY_START+k.FIELD['info']
NAMES=('heads','mem','out','info','scratch','program','courier_l','courier_r','mail_l','mail_r','history1','history2','history3')


def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()


@lru_cache(None)
def I(y):
    """Unique terminating primary Info of an intact reset initializer H."""
    g,a=divmod(y,k.Q);i=a-k.PRIMARY_START
    if not 0<=i<k.FRAME_WORDS:return 0
    if i<6:return g%k.Q if i==0 else 0
    name=k.FIELD_NAMES[(i-6)//5];slot=(i-6)%5
    if name=='info':
        nxt=g+k.SLOTS[slot]
        assert abs(nxt)<abs(y),(y,nxt)
        return I(nxt)
    if name=='program':return k.beta_bit(own.ROM,(g+k.SLOTS[slot])%k.Q)
    return 0


@lru_cache(None)
def H(x):
    return k.Cell(addr=x%k.Q,info=tuple(I(x+s) for s in k.SLOTS),
                  program=tuple(k.beta_bit(own.ROM,(x+s)%k.Q) for s in k.SLOTS))


@lru_cache(None)
def nextH(x):
    return k.local_transition({j:H(x+j) for j in range(-8,9)},own.ROM)


@lru_cache(None)
def changed(x):
    c=nextH(x)
    return replace(c,info=(1,)+c.info[1:]) if x==0 else c


@lru_cache(None)
def next2H(x):
    return k.local_transition({j:nextH(x+j) for j in range(-8,9)},own.ROM)


def D1(y,damaged=False):
    g,a=divmod(y,k.Q);i=a-k.PRIMARY_START
    if not 0<=i<k.FRAME_WORDS:return 0
    return k.cell_words(changed(g) if damaged else nextH(g))[i]


def encoded(x,upper):
    def data(y):
        g,a=divmod(y,k.Q);i=a-k.PRIMARY_START
        return k.cell_words(upper(g))[i] if 0<=i<k.FRAME_WORDS else 0
    return k.Cell(addr=x%k.Q,info=tuple(data(x+s) for s in k.SLOTS),
                  program=tuple(k.beta_bit(own.ROM,(x+s)%k.Q) for s in k.SLOTS))


def initializer_checks():
    assert k.FIELD['info']==206 and TARGET==4054
    cases=0;copycases=0
    # These checks supplement the field-case recursion proof, not sampling
    # evidence for an unbounded quantifier. Include both quotient signs.
    for g in (-k.Q-2,-k.Q,-100,-2,-1,0,1,2,100,k.Q,k.Q+2,10**40,-10**40):
        words=k.cell_words(H(g))
        for i,w in enumerate(words):
            y=g*k.Q+k.PRIMARY_START+i
            assert I(y)==w,(g,i,I(y),w);cases+=1
            for h,s in enumerate(k.SLOTS):
                assert H(y-s).info[h]==w;copycases+=1
    assert all(I(s)==0 for s in k.SLOTS)
    assert all(I(y)==0 for y in (0,3,k.Q-3,-1,1,2))
    return dict(field_case_checks=cases,actual_holder_checks=copycases,
                all496_fields_proved_by_definition=True,recursion_strict_abs_descent=True,
                unused_and_special_Info_zero=True,all_five_cell0_Info_slots_zero=True,
                Programme_uses_actual_beta=True,intact_every_level=True)


def execute_actual_bank(upper):
    cells={j:upper(j) for j in range(-8,9)};tape=k.input_tape(cells)
    packet=k.Packet(p=1,pc=0);address=k.HEAD_ADDRESS;out={};scratch={};digest=hashlib.sha256()
    low=high=address
    for tick in range(141558):
        address+=1 if packet.move==1 else -1 if packet.move==2 else 0
        assert k.PRIMARY_START<=address<k.PRIMARY_START+k.FRAME_WORDS
        low=min(low,address);high=max(high,address)
        packet,ow,sw=k.step_packet(packet,address,tape.get(address,0),out.get(address,0),scratch.get(address,0),k.beta_bit(own.ROM,address),own.ROM)
        if ow is not None:out[address]=ow
        if sw is not None:scratch[address]=sw
        digest.update(json.dumps([address,hex(k.pack(packet)),None if ow is None else hex(ow),None if sw is None else hex(sw)],separators=(',',':')).encode()+b'\n')
        if packet.mode in (k.HALT,k.ERROR):break
    assert packet.mode==k.HALT and tick+1<=141557
    expected=k.local_transition(cells,own.ROM)
    assert [out[k.PRIMARY_START+i] for i in range(k.FRAME_WORDS)]==k.cell_words(expected)
    assert out[TARGET]==0
    return out,scratch,packet,address,dict(updates=tick+1,min_head_address=low,max_head_address=high,
            actual_gather_input_words=[[j,[hex(v) for v in k.cell_words(cells[j])]] for j in range(-8,9)],
            execution_digest_sha256=digest.hexdigest(),final_packet_hex=hex(k.pack(packet)),
            final_head_address=address,output_words=[hex(out[k.PRIMARY_START+i]) for i in range(k.FRAME_WORDS)],
            scratch_words=[[a,hex(v)] for a,v in sorted(scratch.items())],
            input_bank_derived_from_actual_global_start=True,independently_preloaded_bank=False)


def precommit(x,execution):
    out,scratch,packet,address,_=execution
    def bank(y):return sum(I(y+j*k.Q)<<((j+8)*k.WORD) for j in range(-8,9))
    return k.Cell(addr=x%k.Q,age=k.U-1,
        heads=tuple(k.pack(packet) if x+s==address else 0 for s in k.SLOTS),
        mem=tuple(bank(x+s) for s in k.SLOTS),
        out=tuple(out.get(x+s,0) for s in k.SLOTS),info=tuple(I(x+s) for s in k.SLOTS),
        scratch=tuple(scratch.get(x+s,0) for s in k.SLOTS),
        program=tuple(k.beta_bit(own.ROM,(x+s)%k.Q) for s in k.SLOTS),
        history1=tuple(bank(x+s) for s in k.SLOTS),history2=tuple(bank(x+s) for s in k.SLOTS),history3=tuple(bank(x+s) for s in k.SLOTS))


def gather_row(x,age,damaged):
    assert 1<=age<2*k.Q
    data=lambda y:D1(y,damaged)
    def history(y):
        result=data(y)<<(8*k.WORD)
        for d in (-1,1):
            if age>=k.Q+2:result|=data(y+d*k.Q)<<((8+d)*k.WORD)
        return result
    return k.Cell(addr=x%k.Q,age=age,info=tuple(data(x+s) for s in k.SLOTS),
        program=tuple(k.beta_bit(own.ROM,(x+s)%k.Q) for s in k.SLOTS),
        mail_l=tuple(data(x+s+age-1) for s in k.SLOTS),mail_r=tuple(data(x+s-age+1) for s in k.SLOTS),
        history1=tuple(history(x+s) for s in k.SLOTS))


def update(state):
    return {x:k.local_transition({j:state[x+j] for j in range(-8,9)},own.ROM)
            for x in range(min(state)+8,max(state)-7)}


def words(state):return [[x,[hex(v) for v in k.cell_words(c)]] for x,c in sorted(state.items())]


def actual_witness(execution):
    sites=[TARGET-s for s in k.SLOTS];support={(x,k.U-1) for x in sites}
    cl=gray_errors.classify(support,support,Q=k.Q,U=k.U,sep=104)
    assert cl['level0']==0 and cl['candidate_level1'] and cl['level1'] and cl['extent']==(5,1)
    clean={x:precommit(x,execution) for x in range(TARGET-24,TARGET+25)}
    noisy=dict(clean);payloads=[]
    for h,s in enumerate(k.SLOTS):
        x=TARGET-s;old=noisy[x];newout=list(old.out);assert newout[h]==0;newout[h]=1
        noisy[x]=replace(old,out=tuple(newout))
        assert k.cell_words(noisy[x])!=k.cell_words(old)
        payloads.append(dict(x=x,t=k.U-1,only_raw_tuple_changed='Out[%d]'%h,new_value=1,
            old_words=[hex(v) for v in k.cell_words(old)],replacement_words=[hex(v) for v in k.cell_words(noisy[x])]))
    clean_boundary=update(clean);noisy_boundary=update(noisy)
    for x in clean_boundary:
        assert clean_boundary[x]==encoded(x,nextH)
        assert noisy_boundary[x]==encoded(x,changed)
    boundary_gap=[x for x in clean_boundary if clean_boundary[x]!=noisy_boundary[x]]
    assert boundary_gap==sorted(sites)
    # Actual following reset LOAD uses only the just-committed state.
    clean_load=update(clean_boundary);noisy_load=update(noisy_boundary)
    for x in clean_load:
        assert clean_load[x]==gather_row(x,1,False)
        assert noisy_load[x]==gather_row(x,1,True)
    # Analytic one-step transport identity covers all Q intervening updates.
    # Execute the actual local_R at all three decisive cones after Q shifts.
    show_age=k.Q+1;observations=[];colony_set=set()
    for centre,field in ((TARGET-k.Q,'mail_l'),(TARGET,'info'),(TARGET+k.Q,'mail_r')):
        previous={x:gather_row(x,k.Q,False) for x in range(centre-16,centre+17)}
        prev_noisy={x:gather_row(x,k.Q,True) for x in previous}
        shadow=update(previous);result=update(prev_noisy)
        for x in result:
            assert result[x]==gather_row(x,show_age,True)
            assert shadow[x]==gather_row(x,show_age,False)
        holder_state={j:result[centre+j] for j in range(-8,9)}
        shadow_state={j:shadow[centre+j] for j in range(-8,9)}
        assert k.logical(holder_state,field,0)==1 and k.logical(shadow_state,field,0)==0
        for h,s in enumerate(k.SLOTS):
            x=centre-s
            assert getattr(result[x],field)[h]==1 and getattr(shadow[x],field)[h]==0
            colony_set.add(x//k.Q)
        observations.append(dict(logical_position=centre,field=field,
            physical_holders=[centre-s for s in k.SLOTS],shadow_words=words(shadow),actual_words=words(result),
            old_shadow_words=words(previous),old_actual_words=words(prev_noisy)))
    assert colony_set=={-1,0,1}
    # Complete upper single-step recovery, not a primary-only vote claim.
    recovery=[]
    for x in range(-8,9):
        actual=k.local_transition({j:changed(x+j) for j in range(-8,9)},own.ROM)
        reference=next2H(x)
        assert actual==reference
        recovery.append([x,[hex(v) for v in k.cell_words(reference)]])
    assert changed(0).info[0]==1 and nextH(0).info[0]==0
    return dict(Q=k.Q,U=k.U,error_lambda=24,error_separation=104,
        intact_start='H=E(H,0), with terminating primary Info recursion and actual fixed-beta Programme',
        target_logical_primary=TARGET,error_support=sorted(support),error_classification=cl,payloads=payloads,
        clean_precommit_words=words(clean),actual_precommit_words=words(noisy),
        clean_boundary_words=words(clean_boundary),actual_boundary_words=words(noisy_boundary),
        boundary_difference_sites=boundary_gap,actual_first_boundary_encoding='E(Cprime,0), Cprime=F(H) with upper cell0 Info[0]=1',
        clean_load_words=words(clean_load),actual_load_words=words(noisy_load),
        simultaneous_show_tick=k.U+k.Q+1,simultaneous_difference_colonies=sorted(colony_set),observations=observations,
        upper_actual_single_step_recovery_words=recovery,upper_error_is_one_holder=True,
        second_boundary_exact_shadow_proved_by_noiseless_period=True,
        Gray_or_iid_refutation=False,literal_Prop4_pointwise_box_transplant_refuted=True,
        prior_frozen_rule_confinement_theorem_refuted=False,
        failure_caused_by102Q_start_proved=False)


def main(write=True):
    start=time.monotonic();initial=initializer_checks();first=execute_actual_bank(H);second=execute_actual_bank(changed)
    assert first[4]['output_words'][k.FIELD['info']]=='0x0'
    assert second[4]['output_words']==[hex(v) for v in k.cell_words(next2H(0))]
    witness=actual_witness(first)
    receipt=dict(name='GAW4 intact GAW2R original-real1 temporary-Mail envelope and decoded recovery',
        initializer=initial,first_actual_execution=first[4],second_actual_execution=second[4],witness=witness,
        old_GAW2R_modified=False,registered_main_modified=False,elapsed_seconds=time.monotonic()-start)
    path=D/'GAW4_real1_mail_witness.json'
    if write:path.write_text(json.dumps(receipt,indent=2)+'\n')
    else:
        retained=json.loads(path.read_text());a=dict(receipt);a.pop('elapsed_seconds');retained.pop('elapsed_seconds')
        assert json.loads(json.dumps(a))==retained
    print(json.dumps(dict(passed=True,intact_initializer=initial,error_class=witness['error_classification'],
         first_updates=first[4]['updates'],second_updates=second[4]['updates'],
         show_tick=witness['simultaneous_show_tick'],three_colonies=witness['simultaneous_difference_colonies'],
         second_boundary_recovers=True,Gray_iid_or102Q_attribution=False,elapsed_seconds=receipt['elapsed_seconds'])))
    return receipt

if __name__=='__main__':main()
