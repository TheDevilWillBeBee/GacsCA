"""GT0: explicit radius-five raw-state gathering/storage transducer.

New isolated implementation choice, not a fully specified Gray CA. Native
computed controls, two early flag results and final interpreter stores are
integration ports. No GR1 code, ROM, compiler or front is used. These
future write ports have no effect during the first two gathering stages.
"""
from gacsca.netlist import Net,Compiled,at_least,w_eq_const,w_in_range,w_add_const

Q=8192
U=128*Q
K=13
M=20
SLOTS=(0,-2,-1,1,2)  # Primary first, then four secondary holders.
LANES=tuple(range(-5,6))
STAGES=((0,16*Q,32*Q),(32*Q,48*Q,64*Q),(64*Q,80*Q,96*Q),
        (96*Q,104*Q,112*Q),(112*Q,120*Q,U))
FLAG_DELIVERY=80*Q-1  # Chosen interface time, within the printed interval.
FIELDS=(('simbit',1),('mailR',1),('mailL',1),
        ('history1',11),('history2',11),('history3',11),
        ('voted',11),('nextbit',1))
DATA_BITS=5*sum(w for _,w in FIELDS)
FRAME_SCHEMA=(('addr',K),('age',M),('f1',1),('f2',1),('wf1',1),('wf2',1))+tuple(
    (f,5*w) for f,w in FIELDS)
FRAME_BITS=sum(w for _,w in FRAME_SCHEMA)


def capture_age(stage,lane):
    off=LANES[lane]; start=STAGES[stage][0]
    return start+1 if off==0 else start+2+abs(off)*Q


def clock_boundaries():
    points={0,U}
    for start,active_end,end in STAGES:points.update((start,active_end,end))
    events={s[0] for s in STAGES}|{s[0]+1 for s in STAGES[:3]}
    events|={capture_age(g,lane) for g in range(3) for lane in range(11)}
    events|={FLAG_DELIVERY,STAGES[4][0]+1}
    for age in events:points.update((age,age+1))
    return sorted(points)


def address_boundaries():
    points={0,Q}
    for slot in SLOTS:
        for target in (3,Q-3):
            phase=(target-slot)%Q
            points.update((phase,phase+1))
    return sorted(points)


def scalar_plan(age,address,slot,field,bit=0):
    """Independent scalar route equation, before Flag1/native-wipe masks."""
    starts={s[0] for s in STAGES}; current=(field,slot,bit)
    if field=='simbit':
        if age==0:return ('nextbit',slot,0)
        if age==FLAG_DELIVERY:
            if (address+slot)%Q==3:return ('flag2_port',)
            if (address+slot)%Q==Q-3:return ('flag1_port',)
        return current
    if field=='nextbit':
        if age in starts:return ('zero',)
        if STAGES[4][0]<=age<STAGES[4][1]:
            return ('write_port',slot,current)
        return current
    if field in ('mailL','mailR'):
        if age in starts:return ('zero',)
        if age in {s[0]+1 for s in STAGES[:3]}:return ('simbit',slot,0)
        if any(start<=age<active_end for start,active_end,_ in STAGES[:3]):
            return (field,slot+(1 if field=='mailL' else -1),0)
        return current
    if field in ('history1','history2','history3'):
        g=int(field[-1])-1
        if age in {s[0] for s in STAGES[:g+1]}:return ('zero',)
        if age==capture_age(g,bit):
            off=LANES[bit]
            return ('simbit' if off==0 else 'mailR' if off<0 else 'mailL',slot,0)
        return current
    if field=='voted':
        if age in starts:return ('zero',)
        if age==STAGES[4][0]+1:
            return ('majority3',*(('history'+str(g),slot,bit) for g in (1,2,3)))
        return current
    raise ValueError(field)


def build(n,cells,address,age,flag1,wipe,flag1_result,flag2_result,writes):
    """Actual Boolean output equations for the component.

    cells[x][f][SLOTS.index(slot)*width+b] holds the logical bit at x+slot.
    writes[slot]=(enable,value) is an unspecified interpreter result port,
    clock-gated to the fifth active stage. It is not an upper-level oracle
    supplied by a completed CA. A full rule must implement these ports.
    """
    widths=dict(FIELDS); cache={}
    def value(logical,field,bit=0):
        key=logical,field,bit
        if key not in cache:
            cache[key]=at_least(n,[cells[logical-s][field][SLOTS.index(s)*widths[field]+bit]
                                  for s in SLOTS],3)
        return cache[key]
    eq=lambda x:w_eq_const(n,age,x)
    resets=[eq(s[0]) for s in STAGES]; reset=n.any(resets)
    load=n.any(eq(s[0]+1) for s in STAGES[:3])
    moving=n.any(w_in_range(n,age,s[0],s[1]) for s in STAGES[:3])
    updating=w_in_range(n,age,STAGES[4][0],STAGES[4][1])
    result={}
    for slot in SLOTS:
        logical_address=w_add_const(n,address,slot%Q)
        left_special=n.AND(eq(FLAG_DELIVERY),w_eq_const(n,logical_address,3))
        right_special=n.AND(eq(FLAG_DELIVERY),w_eq_const(n,logical_address,Q-3))
        for field,width in FIELDS:
            for bit in range(width):
                current=value(slot,field,bit)
                if field=='simbit':
                    v=n.MUX(eq(0),value(slot,'nextbit'),
                        n.MUX(left_special,flag2_result,n.MUX(right_special,flag1_result,current)))
                elif field=='nextbit':
                    enable,output=writes[slot]
                    v=n.MUX(reset,0,n.MUX(n.AND(updating,enable),output,current))
                elif field in ('mailL','mailR'):
                    source=value(slot+(1 if field=='mailL' else -1),field)
                    v=n.MUX(reset,0,n.MUX(load,value(slot,'simbit'),n.MUX(moving,source,current)))
                elif field in ('history1','history2','history3'):
                    g=int(field[-1])-1; off=LANES[bit]
                    source=value(slot,'simbit' if off==0 else 'mailR' if off<0 else 'mailL')
                    v=n.MUX(n.any(resets[:g+1]),0,
                            n.MUX(eq(capture_age(g,bit)),source,current))
                elif field=='voted':
                    a,b,c=[value(slot,h,bit) for h in ('history1','history2','history3')]
                    v=n.MUX(reset,0,n.MUX(eq(STAGES[4][0]+1),
                        n.OR(n.AND(a,b),n.AND(c,n.OR(a,b))),current))
                if field in ('mailL','mailR'):v=n.AND(v,n.NOT(flag1))
                result[field,slot,bit]=n.AND(v,n.NOT(wipe))
    return result


def netlist():
    n=Net()
    cells={j:{f:[n.input(('x',j,f,b)) for b in range(5*w)] for f,w in FIELDS}
           for j in range(-5,6)}
    address=[n.input(('computed_address',b)) for b in range(K)]
    age=[n.input(('computed_age',b)) for b in range(M)]
    ports={f:n.input((f,)) for f in ('computed_flag1','native_wipe','flag1_result','flag2_result')}
    writes={s:(n.input(('write_enable',s)),n.input(('write_value',s))) for s in SLOTS}
    outputs=build(n,cells,address,age,ports['computed_flag1'],ports['native_wipe'],
                  ports['flag1_result'],ports['flag2_result'],writes)
    for name,node in outputs.items():n.set_output(('y',)+name,node)
    return n


def preliminary_layout():
    """Data-frame layout only; adding an interpreter requires a new layout."""
    tags=[(f,b) for f,w in FRAME_SCHEMA for b in range(w)]
    start=Q//2-len(tags)//2
    return {tag:start+i for i,tag in enumerate(tags)}


def compiled():return Compiled(netlist())
