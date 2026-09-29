"""Diagnostic Age-zero block relation for the single fixed projected rule.

Initialization/validation/decoding only. No function evolves a simulated cell.
Parent access may be lazy; neither state width nor rule selection depends on it.
"""
from functools import lru_cache

from . import retimed_holder_rule as f, retimed_holder_core as c
from . import retimed_holder_projected as r, retimed_holder_program as p


@lru_cache(maxsize=1)
def info_fields():return {address:index for index,address in enumerate(p.layout().info)}


def encode_at(parent,parent_count,position,*,scratch=None,signal=None):
    """Return one full raw physical cell in a member of the boundary relation.

    parent(colony) returns a projected cell. Optional functions supply arbitrary
    initial MEM scratch and physical Signal words. This is host initialization.
    """
    if type(parent_count) is not int or parent_count<1:raise ValueError('positive parent count required')
    if type(position) is not int:raise ValueError('integral physical position required')
    size=parent_count*f.Q;position%=size;info=info_fields();parents={}
    values=dict(address=position%f.Q,signal=0 if signal is None else signal(position))
    for delta in f.OFFSETS:
        primary=(position+delta)%size;colony,address=divmod(primary,f.Q)
        if address in info:
            if colony not in parents:parents[colony]=f.encode_cell(r.lift(parent(colony)))
            data=parents[colony][info[address]]
        elif r.record(address)['kind']==c.MEM:
            data=0 if scratch is None else scratch(primary)
        else:data=0
        values[f's{delta+2}_data']=data
    return r.lift(r.Cell(**values))


def decode_colony(read,parent_count,colony):
    if type(parent_count) is not int or parent_count<1:raise ValueError('positive parent count required')
    colony%=parent_count
    words=tuple(read(colony*f.Q+address).s2_data for address in p.layout().info)
    raw=f.decode_cell(words);projected=r.project(raw)
    if r.lift(projected)!=raw:raise ValueError('Info metadata is not normalized from the represented Address')
    return projected


def validate_at(read,parent_count,position,*,parent=None):
    """Check the complete entry constraints at one site, reading only its halo.

    Local validation has radius two for replica consistency. Expected parent
    values are diagnostic inputs, not reads performed by a physical transition.
    To establish the relation for a ring, validate every site and decode Info.
    """
    if type(parent_count) is not int or parent_count<1:raise ValueError('positive parent count required')
    size=parent_count*f.Q;position%=size;cell=read(position)
    if not isinstance(cell,f.Cell):raise TypeError('complete raw physical cells required')
    if cell.address!=position%f.Q or cell.age!=0:raise ValueError('noncanonical boundary geometry')
    if r.lift(r.project(cell))!=cell:raise ValueError('physical metadata differs from fixed ROM')
    if cell.f1 or cell.f2:raise ValueError('physical boundary flags must be zero')
    info=info_fields();parents={}
    for delta in f.OFFSETS:
        primary=(position+delta)%size;colony,address=divmod(primary,f.Q)
        if getattr(cell,f'w{delta+2}_wf1') or getattr(cell,f'w{delta+2}_wf2'):raise ValueError('boundary Wf must be zero')
        for name,_ in f.PROCEDURE:
            if name!='data' and getattr(cell,f's{delta+2}_{name}'):
                raise ValueError('physical boundary controller/mail must be zero')
        data=getattr(cell,f's{delta+2}_data')
        if data!=read(primary).s2_data:raise ValueError('Data replicas disagree')
        if r.record(address)['kind']!=c.MEM and data:raise ValueError('non-MEM Data must be zero')
        if parent is not None and address in info:
            if colony not in parents:parents[colony]=f.encode_cell(r.lift(parent(colony)))
            if data!=parents[colony][info[address]]:raise ValueError('Info omits or changes represented raw state')
    return True


def validate_ring(read,parent_count,*,parent=None):
    """Streaming full-ring validation with a bounded 64-cell diagnostic cache."""
    if type(parent_count) is not int or parent_count<1:raise ValueError('positive parent count required')
    cached=lru_cache(maxsize=64)(read)
    try:
        for position in range(parent_count*f.Q):validate_at(cached,parent_count,position,parent=parent)
        for col in range(parent_count):
            decoded=decode_colony(cached,parent_count,col)
            if parent is not None and decoded!=parent(col):raise ValueError('decoded parent mismatch')
        return dict(validated_sites=parent_count*f.Q,decoded_parents=parent_count,cell_cache_limit=64)
    finally:cached.cache_clear()


def layout_obligations(record=r.record):
    """Check the actual ROM's scratch erasure and adjacent Hold/Info layout."""
    info=info_fields();scratch=0
    for address in range(f.Q):
        row=record(address)
        reset_clears=bool(row['first'] or (row['kind']==c.MEM and row['a']&1))
        if address in info:
            assert row['kind']==c.MEM and not row['first'] and row['a']&c.INFO and not reset_clears
            assert p.layout().hold[info[address]]==address+1
        elif row['kind']==c.MEM:
            assert reset_clears,('MEM scratch survives first reset',address);scratch+=1
    assert len(info)==f.FIELDS and len(set(info.values()))==f.FIELDS
    return dict(info_words=len(info),projected_dynamic_words=len(r.SCHEMA),MEM_scratch_words=scratch,
                first_reset_erases_all_MEM_scratch=True,Info_retained_at_first_reset=True,
                commit_Hold_is_right_neighbor=True)
