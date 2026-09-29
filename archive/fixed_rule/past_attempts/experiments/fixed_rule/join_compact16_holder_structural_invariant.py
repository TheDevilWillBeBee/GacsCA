"""Join local descriptor lemmas into a canonical global structural invariant.

This checks proof dependencies and the spatial composition obligations. It is
not an evolution executor and does not infer correct simulated macrosteps.
"""
import argparse
from functools import lru_cache
import hashlib
import json
from pathlib import Path
import resource
import time

from gacsca.fixed_rule import compact16_holder_rule as f, compact16_holder_core as c
from gacsca.fixed_rule.wordcode import LIT
from experiments.fixed_rule import certify_compact16_holder_head_invariant as head


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def support(description=None):
    desc=f.self_description() if description is None else description
    @lru_cache(None)
    def used(wire):
        if wire<desc.inputs:
            name=f.SCHEMA[wire%f.FIELDS][0]
            return frozenset((wire,)) if name.startswith('s') and '_' in name and name.split('_',1)[1] in ('head',*c.CONTROL) else frozenset()
        op,a,b=desc.operations[wire-desc.inputs]
        return frozenset() if op==LIT else used(a)|used(b)
    rows={};static=0
    for index,((name,_),wire) in enumerate(zip(f.SCHEMA,desc.outputs)):
        if name.startswith('p'):
            assert wire==7*f.FIELDS+index,('static metadata changed',name);static+=1
        if name.startswith(('s','w')) and '_' in name:
            slot,suffix=name.split('_',1)
            if suffix not in ('data','head',*c.CONTROL,'wf1','wf2'):continue
            primary=int(slot[1:])-2
            sources=[]
            for source in used(wire):
                holder=source//f.FIELDS-7;old_name=f.SCHEMA[source%f.FIELDS][0]
                old_slot=int(old_name.split('_',1)[0][1:])-2
                sources.append(holder+old_slot-primary)
            relative=sorted(set(sources))
            assert all(abs(offset)<=1 for offset in relative),('head/controller logical support exceeds one',name,relative)
            rows[name]=relative
    assert static==len(f.STATIC)==49
    return dict(passed=True,static_fields_preserved=static,logical_head_controller_dependency_offsets=rows,
                maximum_head_controller_logical_radius=max(abs(x) for row in rows.values() for x in row))

