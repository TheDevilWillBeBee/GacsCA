"""All-clock canonical procedure factorization with arbitrary raw context.

Z erases only physical flags, Signals and Wf. Compare F(x) with F(Z(x)):
Data/controllers agree, and mail differs only by computed holder Flag1 masking.
Z is a proof map, never an operation inserted into physical evolution.
"""
import argparse
import hashlib
import json
from pathlib import Path
import resource
import time

from gacsca.fixed_rule import compact16_holder_rule as f, compact16_holder_core as c
from experiments.fixed_rule import certify_compact16_holder_signal_flag_boundaries as boundary

CONTEXT=('f1','f2','signal',*(f'w{d+2}_{name}' for d in f.OFFSETS for name in ('wf1','wf2')))
MAIL=tuple(name for name,_ in f.PROCEDURE if name.startswith(('lp_','rp_')))


def prepare():
    t,raw,_,expected=boundary.prepare()
    def erased(site):
        row=list(raw(site))
        for name in CONTEXT:row[f.COL[name]]=t.const(0)
        return tuple(row)
    return t,raw,erased,expected


def certify(description=None):
    t,raw,erased,expected=prepare();desc=f.self_description() if description is None else description
    full=t.expression(desc,tuple(word for j in f.NEIGHBORHOOD for word in raw(j)))
    clean=t.expression(desc,tuple(word for j in f.NEIGHBORHOOD for word in erased(j)))
    zero=t.const(0);own=raw(0)
    assert clean[f.COL['f1']]==clean[f.COL['f2']]==zero
    for row in (full,clean):
        assert row[f.COL['address']]==own[f.COL['address']]
        assert row[f.COL['age']]==t.modular_add(own[f.COL['age']],1,(f.U-1).bit_length())
    nonmail=mail=static=0;wanted=list(clean)
    for delta in f.OFFSETS:
        for name,_ in f.PROCEDURE:
            col=f.COL[f's{delta+2}_{name}']
            if name in MAIL:
                wanted[col]=t.select(full[f.COL['f1']],zero,clean[col]);mail+=1
            else:
                assert full[col]==clean[col],('context changes Data/controller',delta,name)
                nonmail+=1
    for name,_ in f.STATIC:
        col=f.COL[name];assert full[col]==clean[col]==own[col];static+=1
    # Independent all-clock maintenance/Signal/Wf formulas fill the context.
    for name,value in expected(0).items():wanted[f.COL[name]]=value
    assert full==tuple(wanted),'complete raw factorization failed'
    return dict(passed=True,all_clock_ages=f.U,all_addresses=f.Q,complete_raw_words=f.FIELDS,
                nonmail_procedure_identities=nonmail,masked_mail_identities=mail,static_identity_fields=static,
                erased_fields=list(CONTEXT),symbolic_terms=len(t.nodes),
                domain='Canonical Address and uniform Age only. Arbitrary raw metadata, Data, head, controller, mail, flags, Signals and Wf; no coherence or head-count premise.',
                relation='F(x) is F(Z(x)) with every mail copy masked by computed holder Flag1 and geometry/flags/Signal/Wf supplied by the independent canonical boundary formulas.')

