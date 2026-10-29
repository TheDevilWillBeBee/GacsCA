"""Conditional SF mail/Info identities; quiet-template premise supply open."""
from pathlib import Path
from types import FunctionType
import hashlib,json,sys,time
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'Report/proofs'))
from gacsca.netlist import Net,w_eq_const,w_in_range
from gacsca import rule_g
import proposed_sparse_signal_reservation1024 as proposed


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    started=time.monotonic();p=proposed.parameters()
    # Equality to refined self GF makes keep1 explicitly conditional.
    # Clock words below2^15 cover every legal gather/early-reset clock;
    # native geometry, all old SF values and I remain independent/free.
    def controller(n,cells,*args,**kwargs):
        clock=[n.input(('proof_clock',i)) if i<15 else 0 for i in range(p.m)]
        return dict(addr=cells[0]['addr'],age_now=clock,
                    age=[n.input(('proof_next_clock',i)) for i in range(p.m)],
                    f1=n.input(('proof_F1',0)),f2=n.input(('proof_F2',0)))
    namespace=dict(proposed.legacy.__dict__,schema=proposed.schema,width=proposed.width,
                   previous=proposed.previous,dependency_table=proposed.dependency_table,
                   service_build=proposed.service_build,generated_source=proposed.generated_source,
                   proposed_build=lambda:(controller,'conditional native interface only'))
    fn=proposed.legacy.full_net
    n,source=FunctionType(fn.__code__,namespace,fn.__name__,fn.__defaults__)(p)
    clock=[n.input(('proof_clock',i)) if i<15 else 0 for i in range(p.m)]
    load=n.any(w_eq_const(n,clock,p.age_code(g*p.Q)) for g in p.gathers_q)
    fast=n.any(w_in_range(n,clock,p.age_code(g*p.Q+1),
                         p.age_code(g*p.Q+37*(p.Q//8)+1)) for g in p.gathers_q)
    gate=n.NOT(n.input(('proof_F1',0)))
    def vote(z,f):
        return rule_g.maj5(n,[n.input(('x',z-e,f,e+2)) for e in proposed.SLOTS])
    checks=[]
    for slot in proposed.SLOTS:
        old=vote(slot,'info')
        assert n.outputs['y','info',slot+2]==old
        checks.append(('info',slot))
        for field,direction in (('ml',1),('mr',-1)):
            expected=n.AND(gate,n.MUX(load,old,
                n.MUX(fast,vote(slot+8*direction,field),vote(slot+direction,field))))
            assert n.outputs['y',field,slot+2]==expected,(field,slot)
            checks.append((field,slot))
    assert len(checks)==15
    ages=list(range(p.E0+1))
    assert max(p.age_code(t) for t in ages)<1<<15
    # Majority of the quiet physical gate equals its centre indicator.
    # Only±2 about the four boundaries are nonuniform; translation is free.
    Q=p.Q;L=0;R=6;a=-Q//2;b=R*Q
    flag=lambda x:int(a-Q//2<=x<a or b-Q//2<=x<b)
    gate_checks=[]
    for edge in (a-Q//2,a,b-Q//2,b):
        for y in range(edge-3,edge+4):
            majority=int(sum(1-flag(y-e) for e in proposed.SLOTS)>=3)
            assert majority==1-flag(y)
            gate_checks.append(y)
    capture=[]
    for g in p.gathers_q:
        start=g*Q
        for d in range(1,38):
            t=start+d*(Q//8)+1
            assert t<p.E0 and t-1-(start+1)==d*(Q//8)-1
            # From row start+1 to old capture row t are exactlyd*Q/8
            # fast updates at input clocks start+1,...,t-1.
            assert t-(start+1)==d*(Q//8)
            capture.append(dict(gather=g,distance=d,capture_input=t,
                                old_capture_row=t,fast_updates=d*(Q//8)))
    result=dict(name='Unregistered SP30 quiet mail/Info wiring identities',
        checker_sha256=sha(__file__),proposal_source_sha256=sha(proposed.__file__),
        generated_source_sha256=hashlib.sha256(source.encode()).hexdigest(),
        native_interface_is_conditional=True,keep1_required=True,
        clock_bits_free=15,other_raw_fields_Info_private_and_I_free=True,
        universal_symbolic_copy_output_identities=len(checks),identities=checks,
        quiet_gate_boundary_checks=len(gate_checks),capture_timing_records=capture,
        all_legal_pre_E0_clocks_covered=True,
        actual_global_quiet_template_or_controller_lift_or_regeneration_proved=False,
        global_reliability_established=False,elapsed_seconds=time.monotonic()-started)
    dest=ROOT/'figs/robustness/unregistered_quiet_mail';dest.mkdir(exist_ok=True)
    (dest/'receipt.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('universal_symbolic_copy_output_identities',
        'quiet_gate_boundary_checks','actual_global_quiet_template_or_controller_lift_or_regeneration_proved',
        'global_reliability_established','elapsed_seconds')}),flush=True)


if __name__=='__main__':main()
