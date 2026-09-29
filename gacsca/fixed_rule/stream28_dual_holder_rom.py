"""Provisional fixed compact holder ROM with a short flag-SEND tail.

This immutable address table replaces the old 4-history instruction layout.
PC 0..9 send the early Flag2/Flag1 Hold values to adjacent colonies; PC 10
halts. Ordinary stage reset entries start at the halt PC. The dual local rule
starts a fresh PC-zero head only after its early encoded evaluator window.
The table is depth-independent initial data, not a host-side transition.
"""
from functools import lru_cache
import hashlib

from . import stream28_compact_layout as layout_module
from . import stream28_holder_core as core
from . import stream28_holder_rule as holder
from . import stream28_holder_projected as projected

Q=core.Q
INSTRUCTION_START=8176
HALT_PC=10
FIRST_SITE=0
LAST_SITE=INSTRUCTION_START+HALT_PC
FLAG1_HOLD=layout_module.build().hold[projected.COL['f1']]
FLAG2_HOLD=layout_module.build().hold[projected.COL['f2']]
assert (FLAG1_HOLD,FLAG2_HOLD)==(2496,2498)
assert LAST_SITE==Q-6


@lru_cache(maxsize=Q)
def record(address):
    if not 0<=address<Q:raise ValueError('canonical address required')
    layout=layout_module.build()
    row=dict(kind=core.MEM,index=address,a=0,b=0,d=0,
             first=0,last=0)
    if address<layout.memory_after_banks:
        row.update(layout.metadata(address))
    if address==FIRST_SITE:
        # All ordinary stage reset heads find HALT. The early post-evaluation
        # head trigger is separate and begins at PC zero.
        row.update(a=HALT_PC|(HALT_PC<<32),
                   b=HALT_PC|(HALT_PC<<32),d=HALT_PC,
                   first=1)
    if INSTRUCTION_START<=address<INSTRUCTION_START+HALT_PC:
        pc=address-INSTRUCTION_START
        if pc<5:
            row.update(kind=core.SEND,index=pc,
                       a=FLAG2_HOLD,b=pc+1,d=core.LEFT)
        else:
            row.update(kind=core.SEND,index=pc,
                       a=FLAG1_HOLD,b=Q-5+pc-5,d=core.RIGHT)
    if address==LAST_SITE:
        row.update(kind=core.HALT,index=HALT_PC,last=1)
    if address>=Q-5:row.update(a=31)
    return tuple(row[name] for name in core.STATIC)


def holder_static_fields(address):
    """Seven neighboring raw metadata rows in the exact holder schema."""
    return {f'p{offset+3}_{name}':value
            for offset in holder.STATIC_OFFSETS
            for name,value in zip(core.STATIC,record((address+offset)%Q))}


@lru_cache(maxsize=1)
def digest():
    sha=hashlib.sha256()
    for address in range(Q):
        for value in record(address):
            sha.update(int(value).to_bytes(8,'little'))
    return sha.hexdigest()
