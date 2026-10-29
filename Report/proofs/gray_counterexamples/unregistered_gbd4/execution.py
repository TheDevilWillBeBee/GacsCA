"""Literal coherent-copy factor of GBD4, with real Mem/Out raw accesses.

This is an execution checker, not an ISA opcode or a host rule evaluator.
Every RUN tick calls actor; travel is the actual actor equation at the old
and adjacent Head coordinates, and WRITE uses old voted Heads at receivers.
The component's immutable coherent Mem and native ports are premises.
"""
from collections import Counter
from dataclasses import replace
import controller as c
import layout as l


class Frame(dict):
    def __init__(self,position,head,memory,outputs,age):
        super().__init__();self.position=position;self.head=head
        self.memory=memory;self.outputs=outputs;self.age=age;self.accesses=[]
    def __missing__(self,x):
        value=c.coherent_cell(x,self.age,
             lambda y:self.head if y==self.position else c.Head(),
             lambda y:self.memory.get(y,0),
             lambda y:self.outputs.get(y,((y*513719)^173913)&c.MASK))
        self[x]=value;return value
    def __getitem__(self,x):
        self.accesses.append(x);return super().__getitem__(x)


def run(program,records,initial_regs=(0,)*8,initial_ret=7139,
        initial_out=None,limit=49152,physical_every=0,trace=False):
    beta=program['beta'];assert beta is not None and len(beta)<=c.Q
    memory={l.P+h:l.bank_container(records,h) for h in range(l.CHUNKS)}
    outputs=dict(initial_out or {})
    position=l.P+2
    head=c.Head(1,3,c.RUN,0,initial_ret,5181,tuple(initial_regs))
    steps=[];opcounts=Counter();pccounts=Counter();travels=Counter()
    positions=[];role_checks=0;actual_reads=[];snapshots=[]
    for tick in range(limit):
        if not head.present:break
        oldposition,oldhead=position,head
        frame=Frame(position,head,memory,outputs,650000+tick)
        name,args,_=c.instruction(beta,head.pc)
        if head.mode==c.RUN:
            opcounts[name]+=1;pccounts[head.pc]+=1
            if name in ('READ','READQ'):
                actual_reads.append(dict(tick=tick,pc=head.pc,position=position,
                    bank=args[-1] if name=='READ' else 0,
                    lane=head.regs[args[1]],phase=head.regs[args[2]],
                    count=head.regs[args[3]],stride=5 if args[4] else 1))
            # All Head logic, including raw instruction decode and READ,
            # is evaluated by the specified physical actor equation.
            result=c.actor(frame,position,0,beta)
            newposition=position
            if name=='WRITE':
                patch=c.patches(c.write_request(head,beta,20),-2)
                changes={}
                for offset in patch:
                    y=position+offset
                    changes[y]=c.write_out(frame,y,0,beta,-2,20)
                    for q,s in enumerate(c.S):
                        assert c.write_out(frame,y-s,q,beta,-2,20)==changes[y]
                        role_checks+=1
                outputs.update(changes)
        else:
            # There is no host teleport. Actual adjacent actor equations
            # select/settle the one-site packet or keep its target row.
            candidates=[(y,c.actor(frame,y,0,beta))
                        for y in range(position-1,position+2)]
            alive=[(y,h) for y,h in candidates if h.present]
            assert len(alive)==1,(tick,'travel uniqueness',alive)
            newposition,result=alive[0]
            travels[(oldhead.pc,oldhead.target)]+=1
        if physical_every and tick%physical_every==0:
            for q,s in enumerate(c.S):
                assert c.actor(frame,newposition-s,q,beta)==result
                role_checks+=1
        position,head=newposition,result
        positions.append(position)
        if trace:steps.append((tick,oldposition,oldhead.pc,oldhead.mode,name))
        if tick<3 or name=='HALT':
            snapshots.append(dict(tick=tick+1,old_position=oldposition,
                old_pc=oldhead.pc,position=position,Head=c.pack_head(head)))
    else:raise AssertionError(('deadline',limit,position,c.pack_head(head)))
    packed=0
    for h in range(2):
        packed|=outputs.get(l.P+h,(((l.P+h)*513719)^173913)&c.MASK)<<(20*h)
    result=dict(addr=packed&8191,age=(packed>>13)&c.MASK,
                f1=(packed>>33)&1,f2=(packed>>34)&1)
    return dict(result=result,ticks=len(positions),instruction_updates=sum(opcounts.values()),
        travel_updates=sum(travels.values()),opcounts=dict(opcounts),
        pccounts={str(pc):n for pc,n in sorted(pccounts.items())},
        travels=[dict(pc=pc,target=target,updates=n) for (pc,target),n in sorted(travels.items())],
        Head_range=[min(positions),max(positions)],raw_role_checks=role_checks,
        actual_READs=actual_reads,final_outputs={str(y):z for y,z in sorted(outputs.items())},
        snapshots=snapshots,steps=steps)
