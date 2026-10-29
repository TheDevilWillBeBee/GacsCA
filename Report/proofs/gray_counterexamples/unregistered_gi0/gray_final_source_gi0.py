"""GI0 total native/SimBit/Workspace projection of the stipulated interfaces.

This finite projection has no programme, future-store, head or oracle port.
It is not a whole self-simulating rule. It reads57 of GE1's2462 old raw bits.
Old native equations are printed or explicitly h1-corrected; the literal
Workspace reads the FINAL computed primary SimBit, with reader wipe priority.
"""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[4]
REGISTERED=Path(__file__).resolve().parent.parent
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(REGISTERED))
from gacsca import maintenance
from gacsca.netlist import Net,at_least,w_eq_const,w_in_range,w_add_const
import literal_maintenance as literal
import gray_raw_gather as gather

Q=8192;U=1048576;SLOTS=gather.SLOTS
NATIVE=(('addr',13),('age',20),('f1',1),('f2',1),('wf1',1),('wf2',1))
DATA=('simbit','nextbit','courierL','courierR')
INTERVAL=tuple(range(-7,9))
RAW_PROJECTION_BITS=sum(w for f,w in NATIVE)+5*len(DATA)


def majority(values):return int(sum(values)>=3)


def native_at(cells,source,h1=False):
    fn=maintenance.maintenance_scalar if h1 else literal.scalar
    return fn({j:{field:cells[source+j][field] for field,width in NATIVE}
        for j in range(-5,6)},Q,U)


def vote(cells,logical,field):
    return majority([cells[logical-s][field][i]&1 for i,s in enumerate(SLOTS)])


def computed_simbit_copy(cells,reader,slot,native=None,h1=False):
    n=native_at(cells,reader,h1) if native is None else native
    address,age=n['addr'],n['age'];logical=reader+slot
    if age==0:result=vote(cells,logical,'nextbit')
    elif age==gather.FLAG_DELIVERY and (address+slot)%Q==3:
        result=vote(cells,logical,'courierL')
    elif age==gather.FLAG_DELIVERY and (address+slot)%Q==Q-3:
        result=vote(cells,logical,'courierR')
    else:result=vote(cells,logical,'simbit')
    wipe=n['f1'] and address!=cells[reader]['addr']
    return 0 if wipe else result


def project(cells,h1=False):
    n=native_at(cells,0,h1);address,age=n['addr'],n['age']
    wipe=bool(n['f1'] and address!=cells[0]['addr'])
    late=96*Q<=age<98*Q
    wf1=int(late and Q-5<=address<Q and not wipe and
        computed_simbit_copy(cells,Q-3-address,0,h1=h1))
    wf2=int(late and 0<=address<5 and not n['f1'] and
        computed_simbit_copy(cells,3-address,0,h1=h1))
    return dict(addr=address,age=age,f1=n['f1'],f2=n['f2'],wf1=wf1,wf2=wf2,
        simbit=tuple(computed_simbit_copy(cells,0,s,n,h1) for s in SLOTS))


def netlist(h1=False):
    n=Net();cells={}
    for x in INTERVAL:
        row={}
        for field,width in NATIVE:
            bits=[n.input(('x',x,field,b)) for b in range(width)]
            row[field]=bits if width>1 else bits[0]
        for field in DATA:row[field]=[n.input(('x',x,field,b)) for b in range(5)]
        cells[x]=row
    native_cache={};vote_cache={};source_cache={}
    def nat(source):
        if source not in native_cache:
            builder=maintenance.build if h1 else literal.build
            native_cache[source]=builder(n,{j:{f:cells[source+j][f] for f,w in NATIVE}
                for j in range(-5,6)},13,20)
        return native_cache[source]
    def raw_vote(logical,field):
        key=logical,field
        if key not in vote_cache:
            vote_cache[key]=at_least(n,[cells[logical-s][field][i]
                for i,s in enumerate(SLOTS)],3)
        return vote_cache[key]
    def simbit(reader,slot):
        key=reader,slot
        if key in source_cache:return source_cache[key]
        v=nat(reader);p=w_add_const(n,v['addr'],slot%Q)
        value=n.MUX(w_eq_const(n,v['age'],0),raw_vote(reader+slot,'nextbit'),
            n.MUX(n.AND(w_eq_const(n,v['age'],gather.FLAG_DELIVERY),w_eq_const(n,p,3)),
                raw_vote(reader+slot,'courierL'),
                n.MUX(n.AND(w_eq_const(n,v['age'],gather.FLAG_DELIVERY),w_eq_const(n,p,Q-3)),
                    raw_vote(reader+slot,'courierR'),raw_vote(reader+slot,'simbit'))))
        equal=n.all(n.NOT(n.XOR(a,b)) for a,b in zip(v['addr'],cells[reader]['addr']))
        wipe=n.AND(v['f1'],n.NOT(equal))
        source_cache[key]=n.AND(value,n.NOT(wipe))
        return source_cache[key]
    v=nat(0)
    equal=n.all(n.NOT(n.XOR(a,b)) for a,b in zip(v['addr'],cells[0]['addr']))
    wipe=n.AND(v['f1'],n.NOT(equal))
    late=w_in_range(n,v['age'],96*Q,98*Q)
    wf1=n.AND(n.AND(late,n.NOT(wipe)),n.any(
        n.AND(w_eq_const(n,v['addr'],Q-3-j),simbit(j,0)) for j in range(-2,3)))
    wf2=n.AND(n.AND(late,n.NOT(v['f1'])),n.any(
        n.AND(w_eq_const(n,v['addr'],3-j),simbit(j,0)) for j in range(-1,4)))
    for field,width in NATIVE:
        value=wf1 if field=='wf1' else wf2 if field=='wf2' else v[field]
        if width>1:
            for bit,node in enumerate(value):n.set_output(('y',field,bit),node)
        else:n.set_output(('y',field,0),value)
    for i,s in enumerate(SLOTS):n.set_output(('y','simbit',i),simbit(0,s))
    return n


def values(cells):
    result={}
    for x in INTERVAL:
        for field,width in NATIVE:
            for b in range(width):result['x',x,field,b]=(cells[x][field]>>b)&1
        for field in DATA:
            for b in range(5):result['x',x,field,b]=cells[x][field][b]
    return result


def decoded(outputs):
    result={}
    for field,width in NATIVE:
        result[field]=sum(outputs['y',field,b]<<b for b in range(width))
    result['simbit']=tuple(outputs['y','simbit',b] for b in range(5))
    return result
