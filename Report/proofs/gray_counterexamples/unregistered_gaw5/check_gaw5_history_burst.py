"""Actual intact GAW2R real1 History burst near96Q; no claimed Gray failure.

Retained banks are modified by an actual legal lower-state error. Native
geometry and sources are derived, not chosen. Both selected histories
recover by2U; malformed native padding is audited separately.
"""
from pathlib import Path
from dataclasses import replace
import hashlib,json,sys,time
ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT/'Report/proofs/gray_counterexamples/unregistered_gaw4'))
import check_gaw4_real1_mail as base
k=base.k;own=base.own;I=base.I;H=base.H;D=ROOT/'figs/gray_counterexamples/unregistered_gaw5'
P=k.PRIMARY_START;FAULT_SLOTS=(0,2,3)


def raw_H(g):return k.cell_words(H(g))
def raw_nextH(g):return k.cell_words(base.nextH(g))

def tape_of(raw,g=0):
    return {P+i:sum(raw(g+j)[i]<<((j+8)*k.WORD) for j in range(-8,9)) for i in range(k.FRAME_WORDS)}


def run(tape,early=False):
    packet=k.Packet(p=1,pc=own.ROM.early_pc if early else 0);address=P;out={};scratch={};h=hashlib.sha256();lo=hi=address
    for n in range(147455):
        address+=1 if packet.move==1 else -1 if packet.move==2 else 0
        assert P<=address<P+k.FRAME_WORDS
        lo=min(lo,address);hi=max(hi,address)
        packet,ow,sw=k.step_packet(packet,address,tape.get(address,0),out.get(address,0),scratch.get(address,0),k.beta_bit(own.ROM,address),own.ROM)
        if ow is not None:out[address]=ow
        if sw is not None:scratch[address]=sw
        h.update(json.dumps([address,hex(k.pack(packet)),None if ow is None else hex(ow),None if sw is None else hex(sw)],separators=(',',':')).encode()+b'\n')
        if packet.mode in (k.HALT,k.ERROR):break
    assert packet.mode==k.HALT
    frame=[out[P+i] for i in range(6 if early else k.FRAME_WORDS)]
    return dict(updates=n+1,head_min=lo,head_max=hi,final_address=address,
        packet_hex=hex(k.pack(packet)),out_words=[hex(v) for v in frame],
        scratch=[[a,hex(v)] for a,v in sorted(scratch.items())],trace_digest=h.hexdigest()),out,scratch,packet,address


def bank(y):return sum(I(y+j*k.Q)<<((j+8)*k.WORD) for j in range(-8,9))


def pre96(x,early):
    _,out,scratch,packet,address=early
    return k.Cell(addr=x%k.Q,age=96*k.Q-1,
        heads=tuple(k.pack(packet) if x+s==address else 0 for s in k.SLOTS),
        mem=tuple(bank(x+s) for s in k.SLOTS),
        out=tuple(out.get(x+s,0) for s in k.SLOTS),scratch=tuple(scratch.get(x+s,0) for s in k.SLOTS),
        info=tuple(I(x+s) for s in k.SLOTS),program=tuple(k.beta_bit(own.ROM,(x+s)%k.Q) for s in k.SLOTS),
        mail_l=tuple(I(x+s+16*k.Q-2) for s in k.SLOTS),mail_r=tuple(I(x+s-16*k.Q+2) for s in k.SLOTS),
        history1=tuple(bank(x+s) for s in k.SLOTS),history2=tuple(bank(x+s) for s in k.SLOTS),history3=tuple(bank(x+s) for s in k.SLOTS))


def workrow(x,age,fake,first=None):
    def held(y):return fake if y==P else bank(y)
    return k.Cell(addr=x%k.Q,age=age,
        mem=tuple(held(x+s) for s in k.SLOTS) if age>=102*k.Q+1 else (0,)*5,
        heads=tuple(k.pack(k.Packet(p=1)) if x+s==P else 0 for s in k.SLOTS) if age==102*k.Q+1 else (0,)*5,
        info=tuple(I(x+s) for s in k.SLOTS),program=tuple(k.beta_bit(own.ROM,(x+s)%k.Q) for s in k.SLOTS),
        history1=tuple(held(x+s) for s in k.SLOTS),history2=tuple(held(x+s) for s in k.SLOTS),history3=tuple(held(x+s) for s in k.SLOTS))


def precommit(x,fake,execution):
    _,out,scratch,packet,address=execution
    def held(y):return fake if y==P else bank(y)
    return k.Cell(addr=x%k.Q,age=k.U-1,
        heads=tuple(k.pack(packet) if x+s==address else 0 for s in k.SLOTS),
        mem=tuple(held(x+s) for s in k.SLOTS),out=tuple(out.get(x+s,0) for s in k.SLOTS),
        scratch=tuple(scratch.get(x+s,0) for s in k.SLOTS),info=tuple(I(x+s) for s in k.SLOTS),
        program=tuple(k.beta_bit(own.ROM,(x+s)%k.Q) for s in k.SLOTS),
        history1=tuple(held(x+s) for s in k.SLOTS),history2=tuple(held(x+s) for s in k.SLOTS),history3=tuple(held(x+s) for s in k.SLOTS))


def raw_encoding(x,raw):
    def data(y):
        g,a=divmod(y,k.Q);i=a-P
        return raw(g)[i] if 0<=i<k.FRAME_WORDS else 0
    return k.Cell(addr=x%k.Q,info=tuple(data(x+s) for s in k.SLOTS),
                  program=tuple(k.beta_bit(own.ROM,(x+s)%k.Q) for s in k.SLOTS))


def update(state):return base.update(state)
def words(state):return base.words(state)


def one_case(tag,GFwords,early):
    fake=sum(v<<((j+8)*k.WORD) for j,v in GFwords.items())
    before={x:pre96(x,early) for x in range(P-40,P+41)}
    correct=update(before)
    for x,c in correct.items():assert c==workrow(x,96*k.Q,bank(P))
    noisy=dict(correct);payload=[];support=set()
    for h in FAULT_SLOTS:
        x=P-k.SLOTS[h];c=noisy[x];changes={}
        for name in ('history1','history2','history3'):
            v=list(getattr(c,name));v[h]=fake;changes[name]=tuple(v)
        new=replace(c,**changes);noisy[x]=new;support.add((x,96*k.Q))
        payload.append(dict(x=x,t=96*k.Q,only_changed_fields=['History1[%d]'%h,'History2[%d]'%h,'History3[%d]'%h],
            old_words=[hex(v) for v in k.cell_words(c)],replacement_words=[hex(v) for v in k.cell_words(new)]))
    classification=base.gray_errors.classify(support,support,Q=k.Q,U=k.U,sep=104)
    assert classification['level0']==0 and classification['level1'] and classification['extent']==(3,1)
    after=update(noisy)
    for x,c in after.items():assert c==workrow(x,96*k.Q+1,fake)
    held={x:workrow(x,102*k.Q-1,fake) for x in range(P-32,P+33)}
    reset=update(held);born=update(reset)
    for x,c in reset.items():assert c==workrow(x,102*k.Q,fake)
    for x,c in born.items():assert c==workrow(x,102*k.Q+1,fake)
    tape=tape_of(raw_H);tape[P]=fake
    # The actual affected17-lane bank may have malformed native padding;
    # it is legal lower WORD100 state, not asserted to be a legal upper cell.
    first=run(tape)
    output=[int(v,16) for v in first[0]['out_words']]
    assert output[1]==1 and output[3:6]==[0,0,0]
    if tag=='shift1':
        assert output[0]==1 and output[2]==0
        V=lambda j:replace(H(j),addr=(j+1)%k.Q)
        assert output==k.cell_words(k.local_transition({j:V(j) for j in range(-8,9)},own.ROM))
    else:
        assert output[0]==1<<99 and output[2]==1
    def newraw(g):return output if g==0 else raw_nextH(g)
    pre={x:precommit(x,fake,first) for x in range(P-24,P+25)}
    boundary=update(pre)
    for x,c in boundary.items():assert c==raw_encoding(x,newraw)
    # Next period's actual snapshots are this derived raw boundary. It need
    # not be narrow E(C) when unused native padding is nonzero. Check all
    # affected early sources and complete late outputs, not host-masked Cells.
    second=[]
    for g in range(-8,9):
        actual_tape=tape_of(newraw,g)
        e=run(actual_tape,early=True)
        assert [int(v,16) for v in e[0]['out_words']][2:4]==[0,0]
        s=run(actual_tape)
        expected=k.cell_words(base.next2H(g))
        assert [int(v,16) for v in s[0]['out_words']]==expected,(tag,g)
        second.append(dict(receiver=g,early_execution=e[0],late_execution=s[0],
                           derived_actual_input_words=[[j,[hex(v) for v in newraw(g+j)]] for j in range(-8,9)]))
    return dict(case=tag,actual_lower_error_support=sorted(support),classification=classification,payloads=payload,
        native_geometry_Flags_WF_unchanged=True,WF_and_SimBit_sources_derived_from_H_and_same_fault=True,
        corrupt_GF_bank_words=[[j,hex(v)] for j,v in sorted(GFwords.items())],
        pre96_words=words(before),actual96_words_before_error=words(correct),actual96_words_after_error=words(noisy),
        actual96plus1_words=words(after),actual102reset_words=words(reset),actual102birth_words=words(born),
        first_actual_execution=first[0],actual_U_precommit_words=words(pre),actual_U_boundary_words=words(boundary),
        first_native_output=[hex(v) for v in output[:6]],
        first_boundary_normal_native_padding_legal=(output[0]<k.Q),
        second_actual_receiver_executions=second,second_boundary_complete_shadow_recovery=True,
        induced_raw_record_difference_only_upper_cell0=True,
        ordinary_sacrificed_upper_fault_permitted=True,operational_reliability_failure=False,
        Gray_or_iid_or102Q_causal_refutation=False)


def main(write=True):
    start=time.monotonic();early=run(tape_of(raw_H),early=True)
    assert early[0]['updates']<=213 and [int(v,16) for v in early[0]['out_words']][2:4]==[0,0]
    cases=[one_case('shift1',{j:(j+1)%k.Q for j in range(-8,9)},early),
           one_case('padding99',{j:1<<99 if j==0 else 0 for j in range(-8,9)},early)]
    result=dict(name='GAW5 actual intact real1 History bursts: permitted error map and padding audit',
        Q=k.Q,U=k.U,error_lambda=24,error_separation=104,initial_H_definition='frozenGAW4 H=E(H,0), actual Programme',
        first_actual_early_execution=early[0],cases=cases,frozen_GAW2R_modified=False,
        all_arbitrary_native_bursts_recovery_proved=False,Gray_or_iid_failure_proved=False,
        physical_prefix_lift='derived actual reset/capture/held-bank/packet equations; no independent prepared bank',
        elapsed_seconds=time.monotonic()-start)
    p=D/'GAW5_history_burst_receipt.json'
    if write:p.write_text(json.dumps(result,indent=2)+'\n')
    else:
        old=json.loads(p.read_text());current=dict(result);current.pop('elapsed_seconds');old.pop('elapsed_seconds')
        assert json.loads(json.dumps(current))==old
    print(json.dumps(dict(passed=True,first_updates=[c['first_actual_execution']['updates'] for c in cases],
        second_receiver_executions=sum(len(c['second_actual_receiver_executions']) for c in cases),
        first_native_outputs=[c['first_native_output'] for c in cases],
        both_recover_by2U=True,padding99_not_narrow_E_at_U=True,operational_Gray_iid_failure=False,
        elapsed_seconds=result['elapsed_seconds'])))
    return result

if __name__=='__main__':main()
