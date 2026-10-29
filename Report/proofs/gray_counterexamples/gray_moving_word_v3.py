"""GMW3 changed radius5 fast travel with one-site restoration rows.

All GMW2 sources remain unchanged. Q8192/U128Q/lambda24/c104 retained.
Instruction/ROM/tape semantics are inherited; transport alone changes.
REST_PERIOD=2 is the initial candidate. Period0 explicitly means unpaused;
other periods are experimental variants, not implicit proved repairs.
"""
from dataclasses import replace
import gray_moving_word_v2 as base
from gray_moving_word_v2 import *

REST_PERIOD=2


def travel_stride(p,address,fast):
    """Explicit all-raw movement choice; caller already tests old direction.

    RUN/HALT/ERROR/invalid modes move at most one. IO-mode travel may move
    up to3 toward start+index. Nonpositive distance also defaults to1.
    Invalid descriptors are handled by the inherited finite head step.
    """
    if not fast or p.mode not in (SEEK,LOAD,WRITE):return 1
    target=p.start+p.index
    distance=target-address if p.move==1 else address-target
    return min(3,distance) if distance>0 else 1


def selected_head(cells,y,address,fast):
    def voted(z):
        # Keep the threshold3 over five nominal copies; unavailable
        # copies are zero. This is NOT majority of the3 visible copies.
        return unpack(base.old.vote([cells[z-t].heads[i] if -5<=z-t<=5 else 0
            for i,t in enumerate(SLOTS)]))
    candidates=[]
    for delta in (0,-1,-2,-3,1,2,3):
        p=voted(y+delta)
        if not p.p:continue
        if delta==0:
            ok=p.move in (0,3)
        else:
            direction=1 if delta<0 else 2
            source_address=(address+delta)%Q
            ok=p.move==direction and travel_stride(p,source_address,fast)==abs(delta)
        if ok:candidates.append(p)
    if not candidates:return ZERO
    return fail(candidates[0]) if len(candidates)>1 else candidates[0]


def local_transition(cells,beta,rest_period=REST_PERIOD):
    """Complete same-alphabet component; clipped fast votes stay radius5."""
    assert len(beta)==CODE_CAPACITY and set(cells)==set(range(-5,6)) and rest_period>=0
    native={j:{n:getattr(c,n)&(8191 if n=='addr' else MASK if n=='age' else 1)
        for n in ('addr','age','f1','f2','wf1','wf2')} for j,c in cells.items()}
    a=base.scalar_native(native);age=a['age'];reset=age in (0,112*Q);birth=age==112*Q+1
    active=112*Q+1<age<=120*Q;wipe=a['f1'] and a['addr']!=native[0]['addr']
    fast=not rest_period or age%rest_period!=0
    values={n:[] for n in ('heads','mem','out','info','scratch','program')}
    def logical(n,y):return base.old.vote([getattr(cells[y-t],n)[i] for i,t in enumerate(SLOTS)])
    for y in SLOTS:
        address=(a['addr']+y)%Q
        mem=logical('mem',y)&2047;out=logical('out',y)&1;scratch=logical('scratch',y)&1
        info=out if age==0 else logical('info',y)&1;pb=beta[address]&1
        if reset:head=ZERO;out=scratch=0
        elif birth:head=initial_packet() if address==HEAD_ADDRESS else ZERO
        elif active:
            head=selected_head(cells,y,address,fast)
            head,ow,sw=base.step_packet(head,address,mem,out,scratch,logical('program',y)&1,beta)
            if ow is not None:out=ow
            if sw is not None:scratch=sw
        else:head=unpack(logical('heads',y))
        if wipe:head=ZERO;mem=out=info=scratch=pb=0
        for n,v in (('heads',pack(head)),('mem',mem),('out',out),('info',info),('scratch',scratch),('program',pb)):
            values[n].append(v)
    return Cell(**a,**{n:tuple(v) for n,v in values.items()})


def execute(beta,tape,limit=65535,record=False,rest_period=REST_PERIOD):
    """Uninterrupted scheduled-travel runner; gate scope remains explicit."""
    address=HEAD_ADDRESS;p=initial_packet();out={};scratch={};history=[];age=112*Q+1
    for tick in range(limit):
        newage=(age+1)%U;fast=not rest_period or newage%rest_period!=0
        distance=travel_stride(p,address%Q,fast) if p.move in (1,2) else 0
        address+=distance if p.move==1 else -distance if p.move==2 else 0
        assert 0<=address<Q
        oldp=p;p,ow,sw=base.step_packet(p,address,tape.get(address,0),out.get(address,0),
            scratch.get(address,0),beta[address],beta)
        if ow is not None:out[address]=ow
        if sw is not None:scratch[address]=sw
        if record:history.append((address,oldp,p,ow,sw,age,newage,distance))
        age=newage
        if p.mode in (HALT,ERROR):return out,tick+1,p,history
    return out,limit,p,history
