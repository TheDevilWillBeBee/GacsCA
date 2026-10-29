"""GH1: GT0-style full raw gathers after the concrete GH0 hardwirer.

Explicitly changed stage1 snapshot20367/captures; stage endpoints remain
Gray's U128Q. All previous GT0 sources/receipts are immutable. A compact
own programme, native/pulse composition and the final frame remain open.
"""
from gacsca.netlist import Net,Compiled,at_least,w_eq_const,w_in_range,w_add_const
import gray_raw_gather as gt
import gray_layout_hardwirer as gh

Q=gh.Q;U=gh.U;SLOTS=gh.SLOTS;FIELDS=gt.FIELDS
GATHER_LOAD=(gh.completion_age(Q-1)+1,32*Q+1,64*Q+1)
FRAME_BITS=gh.FRAME_BITS


def capture_age(stage,lane):
    off=gt.LANES[lane]
    return GATHER_LOAD[stage] if not off else GATHER_LOAD[stage]+1+abs(off)*Q


def data_build(n,cells,address,age,flag1,wipe,flag1_result,flag2_result,writes):
    """GT0 equations with exactly the named new load/capture times."""
    widths=dict(FIELDS);cache={}
    def value(logical,field,bit=0):
        key=logical,field,bit
        if key not in cache:
            cache[key]=at_least(n,[cells[logical-s][field][SLOTS.index(s)*widths[field]+bit] for s in SLOTS],3)
        return cache[key]
    eq=lambda x:w_eq_const(n,age,x)
    resets=[eq(s[0]) for s in gt.STAGES];reset=n.any(resets)
    load=n.any(eq(v) for v in GATHER_LOAD)
    moving=n.any(w_in_range(n,age,s[0],s[1]) for s in gt.STAGES[:3])
    updating=w_in_range(n,age,gt.STAGES[4][0],gt.STAGES[4][1])
    result={}
    for slot in SLOTS:
        logical_address=w_add_const(n,address,slot%Q)
        left_special=n.AND(eq(gt.FLAG_DELIVERY),w_eq_const(n,logical_address,3))
        right_special=n.AND(eq(gt.FLAG_DELIVERY),w_eq_const(n,logical_address,Q-3))
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
                    g=int(field[-1])-1;off=gt.LANES[bit]
                    source=value(slot,'simbit' if off==0 else 'mailR' if off<0 else 'mailL')
                    v=n.MUX(n.any(resets[:g+1]),0,n.MUX(eq(capture_age(g,bit)),source,current))
                elif field=='voted':
                    a,b,c=[value(slot,h,bit) for h in ('history1','history2','history3')]
                    v=n.MUX(reset,0,n.MUX(eq(gt.STAGES[4][0]+1),n.OR(n.AND(a,b),n.AND(c,n.OR(a,b))),current))
                if field in ('mailL','mailR'):v=n.AND(v,n.NOT(flag1))
                result[field,slot,bit]=n.AND(v,n.NOT(wipe))
    return result


def netlist():
    n=Net()
    cells={j:{f:[n.input(('x',j,f,b)) for b in range(5*w)] for f,w in FIELDS} for j in range(-5,6)}
    for j in range(-5,6):
        cells[j]['head']=[n.input(('x',j,'hardwire_head',b)) for b in range(5*gh.HEAD_BITS)]
        cells[j]['programme']=[n.input(('x',j,'programme',b)) for b in range(5)]
    address=[n.input(('computed_address',b)) for b in range(13)]
    age=[n.input(('computed_age',b)) for b in range(20)]
    ports={f:n.input((f,)) for f in ('computed_flag1','native_wipe','flag1_result','flag2_result')}
    writes={s:(n.input(('write_enable',s)),n.input(('write_value',s))) for s in SLOTS}
    data=data_build(n,cells,address,age,ports['computed_flag1'],ports['native_wipe'],
        ports['flag1_result'],ports['flag2_result'],writes)
    base=[data['simbit',s,0] for s in SLOTS]
    auxiliary=gh.build(n,cells,address,age,ports['native_wipe'],base)
    for name,node in data.items():
        if name[0]=='simbit':node=auxiliary[name]
        n.set_output(('y',)+name,node)
    for (field,slot,bit),node in auxiliary.items():
        if field=='head':n.set_output(('y','hardwire_head',slot,bit),node)
    return n


def compiled():return Compiled(netlist())


def clock_boundaries():
    points=set(gt.clock_boundaries())
    events={gh.BIRTH,gh.ACTIVE_END}|set(GATHER_LOAD)|{capture_age(g,b) for g in range(3) for b in range(11)}
    for age in events:points.update((age,age+1))
    return sorted(points)
