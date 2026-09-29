"""Apply explicit initial physical bit flips to a coherent Info representation.

This is initialization only. It rejects patterns that leave the represented
physical state incoherent; it never repairs, rounds or silently drops a fault.
"""
import numpy as np
from . import retimed_holder_rule as f,retimed_holder_program as p


def apply(info,faults):
    if not isinstance(info,np.ndarray) or info.dtype!=np.uint64 or info.ndim!=2 or info.shape[1]!=f.FIELDS or not len(info):raise ValueError('complete raw Info array required')
    if not isinstance(faults,np.ndarray) or faults.dtype!=np.uint64 or faults.ndim!=2 or faults.shape[1]!=3:raise ValueError('physical position/raw field/XOR triples required')
    lookup={address:k for k,address in enumerate(p.layout().info)}
    offsets={f.COL[f's{d+2}_data']:d for d in f.OFFSETS};groups={};seen=set();size=len(info)*f.Q
    for pos,field,xor in faults:
        pos,field,xor=int(pos),int(field),int(xor)
        if not 0<=pos<size or field not in offsets or not xor or xor&(xor-1) or (pos,field) in seen:raise ValueError('distinct in-range single Data-bit faults required')
        seen.add((pos,field));offset=offsets[field];col,address=divmod((pos+offset)%size,f.Q)
        if address not in lookup:raise ValueError('fault outside encoded Info')
        group=groups.setdefault((col,lookup[address]),{})
        if offset in group:raise ValueError('duplicate physical replica')
        group[offset]=xor
    # Validate the entire list before modifying any initial Data.
    for group in groups.values():
        if set(group)!=set(f.OFFSETS) or len(set(group.values()))!=1:raise ValueError('fault leaves the coherent endpoint entry domain')
    for (col,k),group in groups.items():info[col,k]^=np.uint64(next(iter(group.values())))
    return dict(physical_bit_faults=len(faults),encoded_word_changes=len(groups),all_five_physical_copies_explicitly_flipped=True,initialization_only=True)
