"""GBD5 autonomous actual-native/three-gather/packing/early-CPU transducer.

Total radius<=7 rule on the explicitly counted K3387 binary alphabet.
It is NOT a self-simulating CA: beta calculates only four native outputs;
no early flag courier or late interpreter/commit is supplied. Those are
explicit omissions, never external output/native/time ports.
"""
from dataclasses import dataclass,replace
from pathlib import Path
import importlib.util

BASE=Path(__file__).resolve().parents[1]
def module(name,path):
    import sys
    spec=importlib.util.spec_from_file_location(name,path)
    m=importlib.util.module_from_spec(spec);sys.modules[name]=m;spec.loader.exec_module(m);return m

c=module('gbd5_cpu',BASE/'unregistered_gbd4/controller.py')
l=module('gbd5_layout',BASE/'unregistered_gbd4/layout.py')
# packing_kernel imports layout: bind precisely the unchanged K3387 layout.
import sys
sys.modules['layout']=l
p=module('gbd5_pack',BASE/'unregistered_gbd3/packing_kernel.py')

Q=c.Q;U=c.U;S=c.S;INV=c.INV;K=l.K;P=l.P
STARTS=(0,32*Q,64*Q)
ACTIVE=16*Q
EARLY_END=80*Q
BIRTH=p.DONE+1
LANES=tuple(range(-8,9))
FIELD_WIDTHS=dict(l.SF)

@dataclass(frozen=True)
class Cell:
    addr:int=0
    age:int=0
    f1:int=0
    f2:int=0
    wf1:int=0
    wf2:int=0
    Info:tuple=(0,)*5
    Mailbox:tuple=(0,)*5
    History:tuple=(0,)*5
    Mem:tuple=(0,)*5
    InputTag:tuple=(0,)*5
    Out:tuple=(0,)*5
    OutputTag:tuple=(0,)*5
    Scratch:tuple=(0,)*5
    Couriers:tuple=(0,)*5
    Head:tuple=(0,)*5

def vote(cells,y,name):
    mask=(1<<FIELD_WIDTHS[name])-1
    return c.majority5([getattr(cells[y+d],name)[INV[h]] for h,d in enumerate(S)])&mask

def native(cells,x,printed=False):
    """Explicit local finite arithmetic equations, never a software opcode.

    Every native input has its declared binary width. All no-quorum
    fallbacks and both printed/h1 old-Flag2 branches are defined.
    """
    r={j:dict(addr=cells[x+j].addr&(Q-1),age=cells[x+j].age&(U-1),
         f1=cells[x+j].f1&1,f2=cells[x+j].f2&1,
         wf1=cells[x+j].wf1&1,wf2=cells[x+j].wf2&1) for j in range(-5,6)}
    def quorum(values,fallback):
        for candidate in values:
            if sum(candidate==v for v in values)>=3:return candidate,True
        return fallback,False
    adjusted={j:(r[j]['addr']-j)%Q for j in range(-5,6)}
    rg,exists=quorum([adjusted[j] for j in range(1,6)],r[0]['addr'])
    lg,_=quorum([adjusted[j] for j in range(-5,0)],r[0]['addr'])
    ra,re=quorum([r[j]['age'] for j in range(1,6)],r[0]['age'])
    la,_=quorum([r[j]['age'] for j in range(-5,0)],r[0]['age'])
    inside={j:exists and 0<=rg+j<Q for j in range(-5,6)}
    rf=sum(inside[j] and r[j]['f1'] for j in range(1,6))
    f1=int(not exists or not re or
        sum(inside[j] and adjusted[j]!=rg for j in range(-5,0))>=3 or
        sum(inside[j] and r[j]['age']!=ra for j in range(-5,0))>=3 or
        sum(inside[j] and r[j]['wf1'] for j in range(-5,6))>=3 or
        rf>=3 or (r[0]['f1'] and rf>=2))
    d3=not exists and (la+1)%16==0
    d4=sum(inside[j] and r[j]['wf2'] for j in range(-5,6))>=3
    il=sum(inside[j] and r[j]['f2'] for j in range(-5,0))
    left=sum(r[j]['f2'] for j in range(-5,0))
    erase=((il==sum(inside[j] for j in range(-5,0))) if printed else il<=1) if not f1 else left==0
    f2=int((d3 or d4 or not erase) if r[0]['f2'] else
           (il>=4 or (f1 and left>=4) or d3 or d4))
    right=exists and (not f1 or f2)
    now=ra if right else la
    return dict(addr=rg if right else lg,age_now=now,age=(now+1)%U,f1=f1,f2=f2)

def capture(g,d):return STARTS[g]+(1 if d==0 else 2+abs(d)*Q)

def raw_view(cells,x,n):
    class View(dict):
        def __missing__(self,z):
            raw=cells[z]
            result=c.Cell(n['addr'] if z==x else raw.addr,
                    n['age_now'] if z==x else raw.age,raw.Head,raw.Mem,raw.Out)
            self[z]=result;return result
    return View()

def local(cells,x,beta,printed=False):
    """One actual raw synchronous update; no computed native input ports.

    Only centre x consumes its computed native fields. Neighbour native
    values in CPU views are unused. All SF dependencies use OLD raw slots.
    Workspace reads the final computed self Info; native uses OLD Workspace.
    """
    assert len(beta)<=Q
    n=native(cells,x,printed);t=n['age_now'];keep=n['addr']==(cells[x].addr&(Q-1))
    sf={name:[] for name in FIELD_WIDTHS}
    view=raw_view(cells,x,n)
    for q,s in enumerate(S):
        y=x+s;a=(n['addr']+s)%Q
        info=vote(cells,y,'Info')
        mail=vote(cells,y,'Mailbox');hist=vote(cells,y,'History')
        if t in STARTS:mail=0
        elif t in tuple(start+1 for start in STARTS):mail=info|(info<<1)
        elif any(start<t<start+ACTIVE for start in STARTS):
            mail=(vote(cells,y-1,'Mailbox')&1)|(((vote(cells,y+1,'Mailbox')>>1)&1)<<1)
        else:mail&=3
        if n['f1']:mail=0
        for g in range(3):
            if t in STARTS[:g+1]:hist&=~(((1<<17)-1)<<(17*g))
            else:
                for lane,d in enumerate(LANES):
                    if t==capture(g,d):
                        bit=info if d==0 else ((vote(cells,y,'Mailbox')>>(0 if d<0 else 1))&1)
                        index=17*g+lane;hist=(hist&~(1<<index))|(bit<<index)
        def packet(at):
            tag=vote(cells,at,'InputTag')
            return p.Packet(vote(cells,at,'Mem'),tag&8191,(tag>>13)&1)
        temporal=p.majority3(*[(vote(cells,y,'History')>>(17*g))&p.HISTORY_MASK for g in range(3)])
        packed=p.stage_action(a,t,packet(y),packet(y-1),packet(y+1),temporal)
        if t==BIRTH:
            head=c.pack_head(c.Head(1,0,c.RUN,0,0,0,(0,)*8) if a==P+2 else c.Head())
            out=c.vote(view,y,'out',c.MASK)
        elif BIRTH<t<EARLY_END:
            head=c.pack_head(c.actor(view,x,q,beta));out=c.write_out(view,x,q,beta,-2,20)
        else:head=0;out=c.vote(view,y,'out',c.MASK)
        values=dict(Info=info,Mailbox=mail,History=hist,Mem=packed.data,
            InputTag=packed.tag|(packed.valid<<13),Out=out,Head=head,
            OutputTag=0,Scratch=0,Couriers=0)
        for name,v in values.items():sf[name].append(v&((1<<FIELD_WIDTHS[name])-1) if keep else 0)
    # An actual, total source equation is supplied, but there is NO authentic
    # early flag-delivery write to these special Info locations. The prefix
    # theorem stops before this guard opens; this is not Gray completion.
    pulse=96*Q<=t<98*Q
    computed_info=sf['Info'][0]
    wf1=int(pulse and n['addr']==Q-3 and computed_info)
    wf2=int(pulse and n['addr']==3 and not n['f1'] and computed_info)
    return Cell(n['addr'],n['age'],n['f1'],n['f2'],wf1,wf2,
                **{name:tuple(values) for name,values in sf.items()})

def encode(record,unused,x):
    g,a=divmod(x,Q)
    info=lambda y:((record(y//Q)>>(y%Q-P))&1) if P<=y%Q<P+K else unused(y)
    return Cell(addr=a,age=0,Info=tuple(info(x+s)&1 for s in S))

def native_net(printed=False):
    """Emit actual finite native hardware, independent from ISA software."""
    from gacsca.netlist import Net,Compiled
    from gacsca import maintenance
    import sys
    if str(BASE) not in sys.path:sys.path.insert(0,str(BASE))
    import literal_maintenance
    graph=Net();inputs={}
    widths=(('addr',13),('age',20),('f1',1),('f2',1),('wf1',1),('wf2',1))
    for j in range(-5,6):
        inputs[j]={}
        for name,w in widths:
            bits=[graph.input((j,name,b)) for b in range(w)]
            inputs[j][name]=bits if w>1 else bits[0]
    outputs=(literal_maintenance.build if printed else maintenance.build)(graph,inputs,13,20)
    for name,bits in outputs.items():
        for b,node in enumerate(bits if isinstance(bits,list) else [bits]):graph.set_output((name,b),node)
    return Compiled(graph)
