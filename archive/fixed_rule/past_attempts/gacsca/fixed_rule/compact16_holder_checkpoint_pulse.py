"""Explicit coherent Info pulses on an existing complete Age-zero image.

The damaged state is represented by the original complete bank/Signals plus
these sparse physical bit flips. This function returns its actual Info, not a
simulated successor or repaired encoding. Other bank words remain unchanged.
"""
import numpy as np
from . import compact16_holder_rule as f,compact16_holder_program as p


def apply(bank,physical_faults):
    g=p.layout()
    if not isinstance(bank,np.ndarray) or bank.dtype!=np.uint64 or bank.ndim!=2 or bank.shape[1]!=g.memory_count+5 or not len(bank):raise ValueError('complete canonical bank required')
    if not isinstance(physical_faults,np.ndarray) or physical_faults.dtype!=np.uint64 or physical_faults.ndim!=2 or physical_faults.shape[1]!=3:raise ValueError('explicit position/field/bit triples required')
    offsets={f.COL[f's{d+2}_data']:d for d in f.OFFSETS};addresses={a:k for k,a in enumerate(g.info)};groups={};seen=set();size=len(bank)*f.Q
    for pos,field,xor in physical_faults:
        pos,field,xor=int(pos),int(field),int(xor)
        if not 0<=pos<size or field not in offsets or xor<=0 or xor&(xor-1) or (pos,field) in seen:raise ValueError('distinct in-range single Data-bit faults required')
        seen.add((pos,field));offset=offsets[field];col,address=divmod((pos+offset)%size,f.Q)
        if address not in addresses:raise ValueError('Info-only pulse required')
        groups.setdefault((col,address),{})[offset]=xor
    for group in groups.values():
        if set(group)!=set(f.OFFSETS) or len(set(group.values()))!=1:raise ValueError('pulse leaves the coherent endpoint domain')
    info=np.ascontiguousarray(bank[:,g.info]);updates=[]
    for (col,address),group in sorted(groups.items()):
        xor=next(iter(group.values()));info[col,addresses[address]]^=np.uint64(xor);updates.append((col,address,xor))
    return info,np.array(updates,dtype=np.uint64).reshape(-1,3)
