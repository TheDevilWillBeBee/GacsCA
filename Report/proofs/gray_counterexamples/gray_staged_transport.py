"""Isolated Gray-timed fivefold transport/reset primitive, NOT a full CA.

The computed Address/Age and native wipe controls are explicit inputs.
No interpreter writes Hold/scratch here; a separate own programme and
native/computed-SimBit refinement are still required. This supplies three
separate snapshots, stage-gated mail, selective resets and a stage5 vote.
"""
from gacsca.netlist import at_least,w_add_const,w_eq_const,w_in_range
from gray_protocol_spec import Q,U,STAGES

SLOTS=tuple(range(-2,3))
LANES=tuple(range(-5,6))
SKEW=tuple(range(-5,6))
FIELDS=(('info',1),('hold',1),('mr',1),('ml',1),
        ('h1',11),('h2',11),('h3',11),('voted',11),('scr',4))
LO=3850
HI=Q-LO
FLAG_AGE=80*Q-1
LEFT_COURIER=FLAG_AGE-(LO-3)-1
RIGHT_COURIER=FLAG_AGE-(Q-3-(HI-1))-1


def capture_age(stage,lane):
    off=LANES[lane]; skew=SKEW[lane]
    if off==0:
        return STAGES[stage].start+1
    distance=abs(off)*Q+(skew if off<0 else -skew)
    return STAGES[stage].start+2+distance


def clock_boundaries():
    points={0,U}
    for s in STAGES:
        points.update((s.start,s.active_end,s.end))
    events={s.start for s in STAGES}|{s.start+1 for s in STAGES[:3]}
    events|={capture_age(g,lane) for g in range(3) for lane in range(11)}
    events|={FLAG_AGE,LEFT_COURIER,RIGHT_COURIER,STAGES[4].start+1}
    for event in events:
        points.update((event,event+1))
    return sorted(points)


def address_boundaries():
    points={0,Q}
    for slot in SLOTS:
        for target in (3,Q-3,LO,HI-1):
            phase=(target-slot)%Q
            points.update((phase,phase+1))
    return sorted(points)


def plan(age,address,slot,field,index=0):
    """Independent scalar routing specification before native wipe masks."""
    logical=(address+slot)%Q
    current=(field,slot,index)
    starts={s.start for s in STAGES}
    loads=[age==s.start+1 for s in STAGES[:3]]
    moving=any(s.start<=age<s.active_end for s in STAGES[:3])
    if field=='info':
        if age==0:
            return ('hold',slot,0)
        if age==FLAG_AGE and logical in (3,Q-3):
            return ('ml' if logical==3 else 'mr',slot,0)
        return current
    if field in ('hold','scr'):
        return ('zero',) if age in starts else current
    if field in ('mr','ml'):
        if age in starts:
            return ('zero',)
        if any(loads):
            return ('info',slot,0)
        courier=(age==LEFT_COURIER and logical==LO if field=='ml' else
                 age==RIGHT_COURIER and logical==HI-1)
        if courier:
            return ('hold',slot,0)
        return (field,slot+(1 if field=='ml' else -1),0) if moving else current
    if field in ('h1','h2','h3'):
        g=int(field[1])-1
        if age in {s.start for s in STAGES[:g+1]}:
            return ('zero',)
        if age==capture_age(g,index):
            off=LANES[index]
            return ('info' if off==0 else 'mr' if off<0 else 'ml',slot,0)
        return current
    if field=='voted':
        if age in starts:
            return ('zero',)
        if age==STAGES[4].start+1:
            return ('majority3',('h1',slot,index),('h2',slot,index),('h3',slot,index))
        return current
    raise ValueError(field)


def build(n,cells,computed_address,computed_age,computed_flag1,wipe):
    """Return fivefold physical output bits, indexed(field,slot,index).

    cells[j][field] stores slot0..4 copies of logical cells j−2..j+2.
    Input radius is5. Every helper source has an explicit five-copy vote.
    """
    widths=dict(FIELDS); cache={}
    def corrected(logical,field,index=0):
        key=logical,field,index
        if key not in cache:
            cache[key]=at_least(n,[cells[logical-s][field][(s+2)*widths[field]+index]
                                  for s in SLOTS],3)
        return cache[key]
    eq=lambda a:w_eq_const(n,computed_age,a)
    resets=[eq(s.start) for s in STAGES]
    reset=n.any(resets)
    load=n.any(eq(s.start+1) for s in STAGES[:3])
    moving=n.any(w_in_range(n,computed_age,s.start,s.active_end) for s in STAGES[:3])
    captures=[[eq(capture_age(g,lane)) for lane in range(11)] for g in range(3)]
    result={}
    for slot in SLOTS:
        logical=w_add_const(n,computed_address,slot%Q)
        left_special=n.AND(eq(FLAG_AGE),w_eq_const(n,logical,3))
        right_special=n.AND(eq(FLAG_AGE),w_eq_const(n,logical,Q-3))
        left_courier=n.AND(eq(LEFT_COURIER),w_eq_const(n,logical,LO))
        right_courier=n.AND(eq(RIGHT_COURIER),w_eq_const(n,logical,HI-1))
        for field,width in FIELDS:
            for index in range(width):
                current=corrected(slot,field,index)
                if field=='info':
                    value=n.MUX(eq(0),corrected(slot,'hold'),
                        n.MUX(left_special,corrected(slot,'ml'),
                              n.MUX(right_special,corrected(slot,'mr'),current)))
                elif field in ('hold','scr'):
                    value=n.AND(current,n.NOT(reset))
                elif field in ('mr','ml'):
                    source=corrected(slot+(1 if field=='ml' else -1),field)
                    courier=left_courier if field=='ml' else right_courier
                    value=n.MUX(reset,0,n.MUX(load,corrected(slot,'info'),
                        n.MUX(courier,corrected(slot,'hold'),n.MUX(moving,source,current))))
                elif field in ('h1','h2','h3'):
                    g=int(field[1])-1
                    off=LANES[index]
                    source=corrected(slot,'info' if off==0 else 'mr' if off<0 else 'ml')
                    value=n.MUX(n.any(resets[:g+1]),0,n.MUX(captures[g][index],source,current))
                elif field=='voted':
                    a,b,c=[corrected(slot,h,index) for h in ('h1','h2','h3')]
                    voted=n.OR(n.AND(a,b),n.AND(c,n.OR(a,b)))
                    value=n.MUX(reset,0,n.MUX(eq(STAGES[4].start+1),voted,current))
                else:
                    raise AssertionError(field)
                if field in ('mr','ml'):
                    value=n.AND(value,n.NOT(computed_flag1))
                result[field,slot,index]=n.AND(value,n.NOT(wipe))
    return result
