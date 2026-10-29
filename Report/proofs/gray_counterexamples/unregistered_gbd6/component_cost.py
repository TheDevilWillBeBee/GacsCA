"""Exact zero-data cost factor for the ISSUED controller component.

All upper SF data are irrelevant to pc/position control. The only varying
control inputs are theta, nativeF1 and nativeGF==oldselfGF. This checker
uses actual generic instruction/ALU semantics and real word coordinates.
It is not a new opcode or an emitted full-rule program.
"""
from dataclasses import replace
from collections import Counter
import controller_emitter as e
c=e.c;l=e.l

def signature(t):
    stage,phase=divmod(t,32*c.Q)
    mail=('hold' if stage>=3 or phase>=16*c.Q else
          'zero' if phase==0 else 'Info' if phase==1 else 'shift')
    # Distinguish the stage>=3 early exit: instruction costs differ.
    if stage>=3:mail='late_hold'
    hs=[]
    for g in range(3):
        if phase==0 and stage<=g:hs.append(('zero',));continue
        offset=(t-32*c.Q*g)&c.MASK
        if offset==1:hs.append(('Info',));continue
        z=(offset-2)&c.MASK;k=z>>13
        if (z&(c.Q-1))==0 and 1<=k<=8:hs.append(('pair',k))
        else:
            # The software has three different exits; retain the exact
            # predicate path, not only the final functional 'hold'.
            hs.append(('hold',int(phase==0),int((z&(c.Q-1))!=0),int(k<1),int(k>8)))
    return (mail,tuple(hs),t==c.U-1)

def partition():
    table={}
    for theta in range(c.U):
        key=signature(theta)
        if key not in table:table[key]=[theta,0]
        table[key][1]+=1
    assert sum(n for _,n in table.values())==c.U
    return table

def run(programme,theta,f1,keep):
    beta=programme['beta'];h=c.Head(1,0,c.RUN,0,0,0,
        (0,0,0,200 if keep else 201,(theta+1)&c.MASK,0,0,0))
    position=l.P+2;outputs={e.n.RAM_BASE+e.n.RAM['F1']:f1}
    ticks=stationary=travel=0;writes=Counter();pcpath=[]
    # All upper SF bits0; only the raw self GF used by initial RAW is200.
    def bit(record,index):return ((200>>index)&1) if record==0 and index<13 else 0
    while h.present:
        assert ticks<100000
        if h.mode==c.TRAVEL:
            if position==h.target:h=replace(h,mode=c.RUN,move=0)
            else:
                position+=1 if h.target>position else -1
                h=replace(h,mode=c.RUN if position==h.target else c.TRAVEL,
                    move=0 if position==h.target else 2 if h.target>position else 1)
            travel+=1;ticks+=1;continue
        name,args,_=c.instruction(beta,h.pc);value=0;pcpath.append(h.pc)
        if name in ('READ','READQ'):
            dst,lane,phase,count,st,*banks=args
            lane=h.regs[lane];phase=h.regs[phase];count=h.regs[count];stride=5 if st else 1
            bank=banks[0] if banks else 0
            assert 0<=count<=20 and 0<=phase<20
            for i in range(count):
                if name=='READQ':
                    values=[]
                    for k in range(5):
                        chunk,b=divmod(phase+stride*i+c.INV[k],20)
                        raw_index=20*(position-2+chunk-l.P)+b
                        values.append(bit(lane+c.S[k]-8,raw_index))
                    value|=int(sum(values)>=3)<<i
                else:
                    chunk,b=divmod(phase+stride*i,20);at=position-2+chunk
                    source=outputs.get(at,0) if bank else 0
                    v=((source>>b)&1) if bank else bit(lane-8,20*(at-l.P)+b)
                    value|=v<<i
        if name=='WRITE':
            for d,(mask,data) in c.patches(c.write_request(h,beta,20),-2).items():
                outputs[position+d]=(outputs.get(position+d,0)&~mask)|data
        if name=='HALT' or name=='INVALID':assert name=='HALT'
        # This is exactly the generic finite instruction equation. Its
        # READ argument was evaluated above from the actual declared bank
        # coordinates; there is no native or full-rule evaluation operation.
        h=c.execute(h,position%c.Q,650000,value,beta)
        stationary+=1;ticks+=1
    return dict(updates=ticks,stationary=stationary,travel=travel,
        pc_path_sha256=__import__('hashlib').sha256(','.join(map(str,pcpath)).encode()).hexdigest())

def contract():
    p=e.standalone();classes=partition();cases=[]
    for key,(theta,population) in classes.items():
        for f1 in (0,1):
            for keep in (0,1):
                cost=run(p,theta,f1,keep)
                cases.append(dict(theta_representative=theta,population=population,
                    signature=key,nativeF1=f1,GFkeep=keep,**cost))
    maximum=max(v['updates'] for v in cases)
    return dict(all_theta_words=c.U,phase_classes=len(classes),control_cases=len(cases),
        all_theta_F1_keep_controls=True,zero_SF_data_control_factor=True,
        universal_issued_component_updates=maximum,cases=cases,
        complete_concatenated_beta_executable=False,full_rule_runtime_proved=False)
