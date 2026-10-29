"""J116: EXPLICIT unincorporated right-mode epoch starter, separate from SP17.

At RF clock T_wf force native maintenance right, and replace the command/
guard birth with an unconditional five-position RF-GF birth. Packet tag
uses the RF GF, not the maintenance-selected GF. No raw state is added.
This is a full local transition proposal at SP17's parameters, with I
free. No own programme or self-simulating candidate is supplied here.
"""
from functools import lru_cache
from types import FunctionType, SimpleNamespace

from gacsca import rule_g
from gacsca.netlist import (Net, majority_word, w_add_const_mod, w_eq_const,
                           w_in_range, w_add_const)
import check_fast_mail_proposal as transport
import proposed_sparse_commit_reset448 as base

parameters=base.parameters
schema=base.schema
width=base.width
COMMIT_RESET_FIELDS=base.COMMIT_RESET_FIELDS


def epoch(n,cells,p,majority=majority_word):
    adjusted=[w_add_const_mod(n,cells[j]['addr'],(-j)%p.Q,p.Q)
              for j in range(1,6)]
    gf,gf_exists=majority(n,adjusted,cells[0]['addr'])
    age,age_exists=majority(n,[cells[j]['age'] for j in range(1,6)],cells[0]['age'])
    force=n.all([gf_exists,age_exists,w_eq_const(n,age,p.age_code(p.T_wf))])
    birth=n.AND(force,w_in_range(n,gf,1,6))
    return dict(addr=gf,age=age,force=force,birth=birth,
                tag=w_add_const(n,gf[:4],15))


@lru_cache(None)
def generated_source(p):
    source=base.generated_source(p)
    marker='    mt = maintenance.build('
    assert source.count(marker) == 1
    source=source.replace(marker,'    right_epoch = epoch_build(n, cell, p)\n'+marker)
    marker="        service_force=service_now['service_force'],\n"
    assert source.count(marker) == 1
    source=source.replace(marker,
        "        service_force=n.OR(service_now['service_force'], right_epoch['force']),\n")
    start=source.index('    repair_age = ')
    end=source.index('    packet_count = ',start)
    source=source[:start]+(
        "    packet_now = dict(tag=service_now['packet_tag'], valid=service_now['packet_valid'], wf2=service_now['wf2'], count=service_now['packet_count'], cohort_exists=service_now['packet_any_cohort'])\n"
        "    packet_birth = right_epoch['birth']\n"
        "    packet_tag = w_mux(n, packet_birth, right_epoch['tag'], packet_now['tag'])\n")+source[end:]
    assert 'packet_command =' not in source and 'packet_guard =' not in source
    return source


def full_net(p,net_class=Net,majority=None,maintenance=None,observe=False,symbolic=False):
    source=generated_source(p)
    if observe:
        marker="    packet_birth = right_epoch['birth']\n"
        assert source.count(marker) == 1
        source=source.replace(marker,marker+
            "    n.set_output(('proof', 'epoch_force'), right_epoch['force'])\n"
            "    n.set_output(('proof', 'birth'), packet_birth)\n")
    mode=majority_word
    if symbolic:
        from check_right_barrier import dominant_majority
        from check_shifted_halfline import dominant_bit
        mode=dominant_majority
        majority=majority or dominant_bit
    namespace=dict(rule_g.__dict__,Net=net_class,LANE_OFFSETS=base.LANE_OFFSETS,
        logical_width=base.logical_width,source_names=base.source_names,schema=base.schema,
        maintenance=SimpleNamespace(build=maintenance or base.proposed_build(symbolic=symbolic)[0]),
        service_build=base.service.build,epoch_build=lambda n,cells,p:epoch(n,cells,p,mode),
        OFFSETS=tuple(range(-12,13)),sparse_controls=transport.sparse_controls,
        sparse_table=base.dependency_table(p))
    for name,fn in rule_g.__dict__.items():
        if isinstance(fn,FunctionType) and fn.__module__ == rule_g.__name__:
            namespace[name]=FunctionType(fn.__code__,namespace,fn.__name__,fn.__defaults__,fn.__closure__)
    namespace.update(logical_width=base.logical_width,source_names=base.source_names,schema=base.schema)
    if majority is not None:
        namespace['maj5']=majority
    exec(compile(source,'<EXPLICIT unincorporated right-mode epoch starter; not SP17>', 'exec'),namespace)
    return namespace['build'](p),source
