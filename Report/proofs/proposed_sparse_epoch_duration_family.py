"""EXPLICIT unincorporated duration-only revisions of SP28.

The full local Boolean transition is SP28's except that the common RF
force window has duration mQ. Birth still occurs only at T_wf. Q, U,
alphabet and layout are unchanged. No matching own programme is supplied
for m!=4. This module does not alter or register any active candidate.
The native counterexample allows every private field/instruction input.
"""
from types import FunctionType,SimpleNamespace
from gacsca.netlist import majority_word,w_add_const_mod,w_eq_const,w_in_range,w_add_const
import proposed_sparse_distant_epoch1024 as baseline


def epoch_helper(duration):
    def epoch(n,cells,p,majority=majority_word):
        adjusted=[w_add_const_mod(n,cells[j]['addr'],(-j)%p.Q,p.Q)
                  for j in range(1,6)]
        gf,gf_exists=majority(n,adjusted,cells[0]['addr'])
        age,age_exists=majority(n,[cells[j]['age'] for j in range(1,6)],cells[0]['age'])
        pulse_at=n.all([gf_exists,age_exists,w_eq_const(n,age,p.age_code(p.T_wf))])
        force=n.all([gf_exists,age_exists,
            w_in_range(n,age,p.age_code(p.T_wf),p.age_code(p.T_wf+duration))])
        birth=n.AND(pulse_at,w_in_range(n,gf,1,6))
        return dict(addr=gf,age=age,force=force,birth=birth,tag=w_add_const(n,gf[:4],15))
    return epoch


def full_net(p,m,net_class=None):
    """Actual full transition; its instruction inputs remain free.

    No compiler or Candidate wrapper is provided: using SP28's old ROM
    for m!=4 would not certify self-simulation of the changed transition.
    """
    if not isinstance(m,int) or not 3<=m<=189:
        raise ValueError('proved duration family is mQ, 3<=m<=189')
    duration=m*p.Q
    assert p.T_wf+duration+2*p.Q<p.U
    old_previous=baseline.previous
    starter=SimpleNamespace(**dict(old_previous.base.starter.__dict__,epoch=epoch_helper(duration)))
    base=SimpleNamespace(**dict(old_previous.base.__dict__,starter=starter))
    previous=SimpleNamespace(**dict(old_previous.__dict__,base=base))
    legacy=baseline.legacy;fn=legacy.full_net
    ns=dict(legacy.__dict__,schema=baseline.schema,width=baseline.width,previous=previous,
            dependency_table=baseline.dependency_table,service_build=baseline.service_build,
            generated_source=baseline.generated_source)
    build=FunctionType(fn.__code__,ns,fn.__name__,fn.__defaults__)
    return build(p) if net_class is None else build(p,net_class)
