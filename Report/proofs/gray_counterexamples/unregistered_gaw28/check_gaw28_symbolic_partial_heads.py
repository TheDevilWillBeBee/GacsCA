"""Universal arbitrary-SF partial-head absorption in the actual RF family.

Calls the frozen interpreter. A tainted Word100 supports only bitwise
data operations; using it in branch, opcode, address or arithmetic control
raises. Native banks remain exact integers. Thus one trace represents all
SF payloads, rather than a zero-tape execution.
"""
from dataclasses import replace
from pathlib import Path
import hashlib,json,sys,time
import discover_gaw28_native_renewal as r
k=r.k;own=r.own;Q=r.Q;U=r.U;P=r.P;S=r.S;ROOT=r.ROOT
D=ROOT/'figs/gray_counterexamples/unregistered_gaw28'
class Tainted:
    def __bool__(self):raise AssertionError('SF payload used as branch control')
    def __eq__(self,other):raise AssertionError('SF payload used as comparison control')
    def __lt__(self,other):raise AssertionError('SF payload used as arithmetic/control')
    def __ge__(self,other):raise AssertionError('SF payload used as address/control')
    def __and__(self,other):return 0 if isinstance(other,int) and other==0 else self
    __rand__=__and__
    def __or__(self,other):return self
    __ror__=__or__
    def __xor__(self,other):return self
    __rxor__=__xor__
    def __repr__(self):return 'arbitrary_Word100'
TAINT=Tainted()
ZERO_HISTORY_FIELDS=tuple(range(241,246))+tuple(range(251,256))
def offset(p):
    for foreign in (False,True):
        g,a=divmod(p+(Q//2 if foreign else 0),Q)
        if P<=a<P+k.FRAME_WORDS:return g,foreign,a-P
    return None
class TapeWord:
    def __init__(self,values):self.values=values
    def __rshift__(self,shift):
        assert isinstance(shift,int) and shift%100==0 and 0<=shift<=1600
        return self.values[shift//100]
def control(p):return [p.p,p.move,p.mode,p.pc,p.target,p.args]
def coupled(T,V,n,A,origins):
    nextA=A+3
    def addr(p):return (p+(Q//2 if (nextA+.5)*Q<=p<(nextA+4)*Q else 0))%Q
    def mem(p):
        z=offset(p)
        if not r.retained(p,A):return TapeWord([0]*17)
        if z and z[2]<6:
            return TapeWord(r.bank(T,V,z[0],z[1],A,True)[z[2]])
        if z and z[2] in ZERO_HISTORY_FIELDS:return TapeWord([0]*17)
        return TapeWord([TAINT]*17)
    heads={o+P:k.Packet(p=1,pc=0) for o in origins};out={};scratch={}
    digest=hashlib.sha256();collisions=[];stores=[];fetched=set();tainted_reads=0
    # Complete-neighbour's data_updates read must not be consumed before
    # absorption. Native prefix/workspace/main controls remain concrete.
    for tick in range(1,147456):
        targets={y+(1 if p.move==1 else -1 if p.move==2 else 0) for y,p in heads.items()}
        newheads={};pending=[]
        for y in sorted(targets):
            old=[heads.get(y+j,k.ZERO) for j in (-1,0,1)]
            candidates=[p for i,p in enumerate(old) if p.p and ((i==1 and p.move not in (1,2)) or(i==0 and p.move==1) or(i==2 and p.move==2))]
            if len(candidates)>1:collisions.append(dict(tick=tick,physical_position=y,old_controls=[control(p) for p in old]))
            packet=k.incoming(old)
            assert all(isinstance(v,int) for v in control(packet))
            if packet.mode==k.RUN:fetched.add(packet.pc)
            if packet.mode==k.SEEK and addr(y)==packet.target and (packet.args&3)==0:
                source=(packet.args>>11)&3;lane=(packet.args>>6)&31
                if source==0 and isinstance(mem(y).values[lane],Tainted):tainted_reads+=1
                if source==1:assert packet.pc!=1094,(n,origins,tick,'data_updates consumed before absorption')
            packet,ow,sw=k.step_packet(packet,addr(y),mem(y),out.get(y,0),scratch.get(y,0),k.beta_bit(own.ROM,addr(y)),own.ROM)
            assert all(isinstance(v,int) for v in control(packet))
            if packet.p:newheads[y]=packet
            if ow is not None:pending.append(('out',y,ow));stores.append((tick,y,ow if isinstance(ow,int) else 'arbitrary_Word100'))
            if sw is not None:pending.append(('scratch',y,sw))
            digest.update(json.dumps([tick,y,control(packet),ow if isinstance(ow,int) else str(ow),sw if isinstance(sw,int) else str(sw)],separators=(',',':')).encode())
        for name,y,value in pending:(out if name=='out' else scratch)[y]=value
        heads=newheads
        if heads and all(p.mode==k.ERROR and p.move==0 for p in heads.values()):break
    assert len(collisions)==1 and heads and all(p.mode==k.ERROR and p.move==0 for p in heads.values())
    assert tainted_reads>0
    native_values={};native_stores=0;maximum=[]
    for o in origins:
        native_values[str(o)]=[out.get(o+P+i,0) for i in range(6)]
        z=offset(o+P);assert z
        assert native_values[str(o)]==r.native(r.bank(T,V,z[0],z[1],A,True))
        indices=[p-o-P for t,p,v in stores if o+P<=p<o+P+k.FRAME_WORDS]
        maximum.append(max(indices))
        for t,p,v in stores:
            if o+P<=p<o+P+6:
                assert t<=213 and isinstance(v,int);native_stores+=1
        for i in ZERO_HISTORY_FIELDS:assert out.get(o+P+i,0)==0
    assert max(maximum)==491 and min(maximum)==241
    return dict(old_boundary=n,A=A,origins=origins,ticks=tick,collision=collisions[0],
        exact_native_six_outputs=native_values,native_stores=native_stores,
        maximum_stored_field_indices=maximum,arbitrary_SF_lane_reads=tainted_reads,
        SF_payload_never_used_for_branch_address_opcode_or_native_value=True,
        both_ERROR_before_complete_data_updates_read=True,
        all_ten_special_source_History1_fields_remain_zero=True,
        control_trace_sha256=digest.hexdigest())
def main():
    start=time.monotonic();issue='--issue' in sys.argv
    T={g:r.old.native_output_table(g) for g in range(r.LO,r.HI)}
    V={g:r.old.native_output_table(g,True) for g in range(r.LO,r.HI)};cases=[]
    for n in range(4,15):
        A=3*n+13
        cases.extend(coupled(T,V,n,A,origins) for origins in ([(A+3)*Q,(A+4)*Q-Q//2],[(A+7)*Q-Q//2,(A+7)*Q]))
        T,V=r.next_records(T,V,n,A)
    result=dict(passed=True,Q=Q,U=U,error_lambda=24,error_separation=104,
        actual_partial_late_head_pairs_on_RF_renewal_before_first_Flag2=cases,
        universal_arbitrary_other_SF_words_by_taint_noninterference=True,
        ten_old_History1_source_words_zero_is_explicit_induction_premise=True,
        literal_frozen_step_packet_used_not_substitute_interpreter=True,
        full_raw_SF_boundary_and_after_Flag2_pulse_not_claimed=True)
    path=D/'GAW28_symbolic_partial_heads_certificate.json';result=json.loads(json.dumps(result))
    if issue:assert not path.exists();path.write_text(json.dumps(result,indent=2)+'\n')
    else:assert result==json.loads(path.read_text())
    print(json.dumps(dict(passed=True,seconds=time.monotonic()-start,pairs=len(cases),receipt_sha256=hashlib.sha256(path.read_bytes()).hexdigest())),flush=True)
if __name__=='__main__':main()
