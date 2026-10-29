"""GR1: isolated stage-timed physical prototype, NOT Gray verbatim.

Explicit departures: h1 healthy Flag2 repair, five-front microcode, and
Workspace flags read corrected current SimBit rather than the literal
computed-SimBit composition. All refinement/probabilistic claims are open
unless separately certified. Active G17 and compiler are unchanged.
"""
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
import sys
import numpy as np
from gacsca import rule_g,maintenance,compiler,machine
from gacsca.netlist import Net,Compiled,at_least,w_add_const,w_mux,w_in_range,w_eq,w_eq_const
import gray_staged_transport as transport

OFFSETS=tuple(range(-5,6))
LANE_OFFSETS=rule_g.LANE_OFFSETS
EARLY_START=70*transport.Q
FINAL_START=112*transport.Q+2
FRONT=('reg','pend','pkind','pval')


@dataclass(frozen=True)
class ParamsStaged(rule_g.ParamsG):
    @property
    def T_sig(self): return transport.FLAG_AGE
    @property
    def T_wf(self): return 96*self.Q
    def fam(self): return sys.modules[__name__]
    def courier_ticks(self):
        return min(transport.LEFT_COURIER,transport.RIGHT_COURIER),transport.LEFT_COURIER,transport.RIGHT_COURIER
    def capture_age(self,off,g=0):
        return transport.capture_age(g,transport.LANES.index(off))
    def check(self):
        assert self.Q==8192 and self.U==128*self.Q==1<<self.m
        assert self.PL==512 and self.R==512 and self.PB==9
        assert self.L>=self.k+max(self.PW,self.IW)
        assert self.lo==transport.LO and self.hi==transport.HI
        assert self.NPe<self.MP<self.NP and self.MP%2==1
        assert self.NP<(1<<self.logNP)
        assert EARLY_START+self.NPe*self.PL<min(self.courier_ticks())
        assert FINAL_START+self.NP*self.PL<=120*self.Q
        assert self.lo-self.H>=2 and self.hi+self.H+1<self.Q
        assert 2*self.margin-2*self.H-3>=200
        return self


def parameters():
    return ParamsStaged(k=13,m=20,L=64,S=4,NP=124,NPe=32,MP=65,E0q=112,
        gathers_q=(0,32,64),q=8192,nb=2048,margin=transport.LO,burst=200,
        computed_front=True,five_front=True,compact_front=True,mux_front=True,
        confined=True,fronts=5,delta=5,skew=(-5,-4,-3,-2,-1,1,2,3,4,5)).check()


def fivefold_fields(p):
    return tuple(f for f,_ in transport.FIELDS)+('pend','pkind','pval')


def logical_width(f,p):
    return dict(transport.FIELDS,reg=p.L,pend=1,pkind=p.PK,pval=1)[f]


def schema(p):
    return [('addr',p.k),('age',p.m),('f1',1),('f2',1),('wf1',1),('wf2',1)]+[
        (f,5*logical_width(f,p)) for f in fivefold_fields(p)]+[('reg',p.L)]


def width(p): return sum(w for _,w in schema(p))
def work_range(p): return p.lo,p.hi
def reserved_cells(p): return 3,p.Q-3,p.lo,p.hi-1
def flag_store_cells(p): return p.hi-1,p.lo
def info_copies(p): return [(s,2-s) for s in range(5)]
def source_names(p): return rule_g.source_names(p)


def build(p):
    p.check(); n=Net()
    cells={j:{f:[n.input(('x',j,f,b)) for b in range(w)] for f,w in schema(p)} for j in OFFSETS}
    I=[n.input(('I',b)) for b in range(p.IW)]
    native=maintenance.build(n,{j:dict(addr=cells[j]['addr'],age=cells[j]['age'],
        **{f:cells[j][f][0] for f in ('f1','f2','wf1','wf2')}) for j in OFFSETS},p.k,p.m)
    addr,age,f1=native['addr'],native['age'],native['f1']
    wipe=n.AND(f1,n.NOT(w_eq(n,addr,cells[0]['addr'])))
    cache={}
    def lv(x,f,b=0):
        key=x,f,b
        if key not in cache:
            if f=='reg':
                value=at_least(n,[cells[x+e]['reg'][b] for e in transport.SLOTS],3)
            else:
                w=logical_width(f,p)
                value=at_least(n,[cells[x-e][f][(e+2)*w+b] for e in transport.SLOTS],3)
                if f in ('hold','scr'):
                    target=0 if f=='hold' else b+1
                    hit=n.AND(lv(x,'pend'),w_eq_const(n,[lv(x,'pkind',j) for j in range(p.PK)],target))
                    value=n.MUX(hit,lv(x,'pval'),value)
            cache[key]=value
        return cache[key]
    early=w_in_range(n,age,EARLY_START,EARLY_START+p.NPe*p.PL)
    final=w_in_range(n,age,FINAL_START,FINAL_START+p.NP*p.PL)
    # Virtual front clock restarts page0 independently in both physical
    # windows. No early registers/scratch are relied on by the final replay.
    virtual=w_mux(n,early,w_add_const(n,age,p.E0-EARLY_START),
                  w_mux(n,final,w_add_const(n,age,p.E0-FINAL_START),[0]*p.m))
    def eval_lv(x,f,b=0):
        if f in ('info','h1'):
            lane=5 if f=='info' else b if b<5 else b+1
            h=[lv(x,bank,lane) for bank in ('h1','h2','h3')]
            early_vote=n.OR(n.AND(h[0],h[1]),n.AND(h[2],n.OR(h[0],h[1])))
            return n.MUX(early,early_vote,lv(x,'voted',lane))
        return lv(x,f,b)
    front=rule_g._five_front(n,p,I,eval_lv,virtual,addr,
                            raw=dict(cell=cells,copy=None,pend_hits=None))
    # The transport primitive shares this corrected-value accessor so Hold
    # reads forward a physically pending evaluator write.
    # Transport helper accepts raw copies. Forward Hold/scratch values by
    # replacing every copy input with its shared corrected/forwarded value.
    # Other fields keep the native five-copy voting operator unchanged.
    transport_cells={j:dict(cell) for j,cell in cells.items()}
    for j in OFFSETS:
        for f in ('hold','scr'):
            w=logical_width(f,p)
            transport_cells[j][f]=[
                lv(j+s,f,b) if -2<=j+s<=2 else cells[j][f][(s+2)*w+b]
                for s in transport.SLOTS for b in range(w)]
    logical_out=transport.build(n,transport_cells,addr,age,f1,wipe)
    outputs=dict(addr=addr,age=age,f1=[f1],f2=[native['f2']])
    for f,w in transport.FIELDS:
        outputs[f]=[logical_out[f,s,b] for s in transport.SLOTS for b in range(w)]
    for f in FRONT:
        outputs[f]=[n.AND(n.NOT(wipe),b) for b in front[f]]
    # Explicit changed equation: computed native clock, but corrected current
    # SimBit, not p41's recursively computed primary SimBit at another site.
    pulse=w_in_range(n,age,96*p.Q,98*p.Q)
    sim_l=n.any(n.AND(w_eq_const(n,addr,a),lv(3-a,'info')) for a in range(5))
    sim_r=n.any(n.AND(w_eq_const(n,addr,a),lv(p.Q-3-a,'info')) for a in range(p.Q-5,p.Q))
    outputs['wf1']=[n.AND(n.NOT(wipe),n.all([pulse,w_in_range(n,addr,p.Q-5,p.Q),sim_r]))]
    outputs['wf2']=[n.AND(n.NOT(wipe),n.all([pulse,w_in_range(n,addr,0,5),sim_l,n.NOT(f1)]))]
    for f,w in schema(p):
        assert len(outputs[f])==w,(f,w,len(outputs[f]))
        for b,node in enumerate(outputs[f]):
            n.set_output(('y',f,b),node)
    return n


@lru_cache(maxsize=2)
def cached(p):
    net=build(p); return net,Compiled(net)


def layout(p): return compiler.end_aware_layout(p,cached(p)[1])


def load_artifact():
    data=np.load(Path(__file__).resolve().parents[3]/'figs/gray_counterexamples/GR1_program.npz')
    return machine.Candidate(parameters(),data['rom'],data['layout'])


def metadata():
    p=parameters(); _,comp=cached(p)
    return dict(Q=p.Q,U=p.U,width=width(p),radius=5,gates=len(comp.gates),netlist_sha256=comp.digest,
        error_lambda=24,error_separation_c=104,explicit_healthy_flag2_repair_h=1,
        explicit_current_corrected_SimBit_Workspace_change=True,
        virtual_early_start=EARLY_START,virtual_final_start=FINAL_START,
        final_window_end=FINAL_START+p.NP*p.PL,
        separate_history_banks=True,stage5_vote_computed_age=112*p.Q+1,
        computed_native_clock=True,gray_verbatim_simulation=False,
        physical_self_simulation_proved=False,full_physical_E0_lift_proved=False,
        own_programme_verified=False,global_reliability_established=False)
