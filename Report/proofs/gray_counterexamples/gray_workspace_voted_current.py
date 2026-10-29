"""GV0: explicitly changed p41 Workspace interface, radius five.

The source is the majority of CURRENT five-holder SimBit copies, before
any source-site write or mandatory wipe. This differs from final computed
SimBit and from a scheduled pre-wipe output. It is an isolated component,
not a full Gray CA or a certified self-programme.
"""
from gacsca.netlist import Net,Compiled,at_least,w_eq_const,w_in_range,w_eq,const_word
import literal_maintenance

Q=8192;U=128*Q;K=13;M=20
SLOTS=(0,-2,-1,1,2)


def vote(n,cells,logical):
    return at_least(n,[cells[logical-s]['simbit'][SLOTS.index(s)] for s in SLOTS],3)


def interface(n,cells,address,age,flag1,wipe):
    """Per-cell WF1/2 ports; primary/raw-work redundancy not completed."""
    source1=n.any(n.AND(w_eq_const(n,address,a),vote(n,cells,Q-3-a))
                  for a in range(Q-5,Q))
    source2=n.any(n.AND(w_eq_const(n,address,a),vote(n,cells,3-a))
                  for a in range(5))
    pulse=w_in_range(n,age,96*Q,98*Q)
    return dict(wf1=n.AND(pulse,n.AND(source1,n.NOT(wipe))),
                wf2=n.AND(pulse,n.AND(source2,n.NOT(flag1))))


def netlist():
    n=Net()
    cells={j:dict(addr=[n.input(('x',j,'addr',b)) for b in range(K)],
                  age=[n.input(('x',j,'age',b)) for b in range(M)],
                  simbit=[n.input(('x',j,'simbit',b)) for b in range(5)],
                  **{f:n.input(('x',j,f)) for f in ('f1','f2','wf1','wf2')})
           for j in range(-5,6)}
    native=literal_maintenance.build(n,cells,K,M)
    wipe=n.AND(native['f1'],n.NOT(w_eq(n,native['addr'],cells[0]['addr'])))
    for field,node in interface(n,cells,native['addr'],native['age'],native['f1'],wipe).items():
        n.set_output(('y',field),node)
    return n


def compiled():return Compiled(netlist())
