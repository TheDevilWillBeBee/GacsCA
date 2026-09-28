"""Canonical output image: coherent Data/control/Wf and Flag1-masked mail.

All inputs/outputs are the fixed physical alphabet. The common mail words below
are diagnostic terms, not extra physical registers or an evolution executor.
"""
import argparse
import hashlib
import json
from pathlib import Path
import resource
import time

from gacsca.fixed_rule import compact16_holder_rule as f, compact16_holder_core as c
from gacsca.fixed_rule.word_bdd import BDD
from experiments.fixed_rule import certify_compact16_holder_raw_mail_factorization as raw_mail
from experiments.fixed_rule.audit_small_holder_position_events import sha


def mask_majority():
    b=BDD(6);bit=b.variable(0);flags=[b.variable(i+1) for i in range(5)]
    survivors=[b.inv(flag) for flag in flags]
    def majority(bits):
        counts=[1,0,0,0]
        for value in bits:
            for k in range(3,0,-1):counts[k]=b.or_(counts[k],b.and_(counts[k-1],value))
        return counts[3]
    actual=majority([b.and_(bit,alive) for alive in survivors])
    expected=b.and_(bit,majority(survivors))
    assert actual==expected
    result=dict(passed=True,independent_bits=6,assignments=64,BDD_nodes=len(b.nodes),
                relation='majority of five copies individually masked by holder Flag1 equals the common bit iff at least three holders have Flag1=0')
    b.binary.cache_clear();return result


def certify_case(phase):
    terms,raw,local=raw_mail.prepare(phase);desc=f.self_description();outputs={}
    for pos in range(-3,4):
        outputs[pos]=terms.expression(desc,tuple(w for j in f.NEIGHBORHOOD for w in raw(pos+j)))
        assert outputs[pos][f.COL['address']]==raw(pos)[f.COL['address']]
        assert outputs[pos][f.COL['age']]==terms.modular_add(raw(pos)[f.COL['age']],1,(f.U-1).bit_length())
    coherent=masked=0
    for primary in (-1,0,1):
        common=local(primary,terms.const(0))
        for name in ('data','head',*c.CONTROL):
            copies=[outputs[primary+e][f.COL[f's{2-e}_{name}']] for e in f.OFFSETS]
            assert len(set(copies))==1,('procedure coherence',phase,primary,name)
            coherent+=1
        for name in ('wf1','wf2'):
            copies=[outputs[primary+e][f.COL[f'w{2-e}_{name}']] for e in f.OFFSETS]
            assert len(set(copies))==1,('Wf coherence',phase,primary,name)
            coherent+=1
        for name in raw_mail.MAIL:
            for e in f.OFFSETS:
                holder=primary+e
                wanted=terms.select(outputs[holder][f.COL['f1']],terms.const(0),common[name])
                assert outputs[holder][f.COL[f's{2-e}_{name}']]==wanted,('mail mask',phase,primary,e,name)
                masked+=1
    return dict(phase=phase,passed=True,all_clock_ages=f.U,checked_primaries=[-1,0,1],
                coherent_five_replica_groups=coherent,masked_mail_copy_identities=masked,
                symbolic_terms=len(terms.nodes),canonical_geometry_preserved=True)

