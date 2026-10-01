"""Oracle-free lower-ring initializer for the corrected U20 candidate.

Only each physical site's own Address chooses immutable lower ROM. Represented
upper state is limited to the complete 119 evolving words. Upper static SOURCE
Data starts zero and must be fetched by a future physical transition.
"""
import hashlib
import random

import numpy as np

from .. import spatial_codec8
from .. import spatial_epoch8 as spatial
from .. import spatial_projected8
from .. import stream28_compact_layout as layout_module
from .. import stream28_dual_holder_rom as holder_rom
from .. import stream28_dual_holder_rule20 as holder
from .. import stream28_dual_pass20 as physical
from .. import stream28_dual_projected20 as projected
from .. import stream28_holder_projected as projected_holder
from experiments.fixed_rule.compact8_address_rom import template
from experiments.fixed_rule.build_compact8_circuit import static_plan
from .corrected_circuit import corrected_initial_data


def upper_states(colonies, seed, *, random_raw=True):
    rng=random.Random(seed)
    states=[]
    for col in range(colonies):
        hwords=[rng.getrandbits(width) for _,width in projected_holder.SCHEMA]
        hwords[projected_holder.COL['address']]=(173+577*col)%physical.Q
        hwords[projected_holder.COL['age']]=0
        if not random_raw:
            hwords=[0]*len(hwords)
            hwords[projected_holder.COL['address']]=(173+577*col)%physical.Q
            hwords[projected_holder.COL['s2_data']]=rng.getrandbits(64)
        swords=[rng.getrandbits(width) for width in spatial_projected8.WIDTHS]
        swords[0]=0
        swords[1]=rng.randrange(spatial.GATE_SLOTS)
        swords[11]=rng.randrange(spatial.GATE_SLOTS)
        if not random_raw:swords=[0]*len(swords)
        states.append(projected.Cell(projected_holder.decode_cell(hwords),
                                     spatial_projected8.decode_cell(swords)))
    return tuple(states)


def initialize(colonies=15,seed=20260929,*,random_raw=True):
    if colonies<15:raise ValueError('closed ring needs at least fifteen colonies')
    q=physical.Q
    with corrected_initial_data():
        lower_rom=template(True,True)
        raw_sources=static_plan(True,True)['raw_sources']
    upper=upper_states(colonies,seed,random_raw=random_raw)
    layout=layout_module.build()
    base=np.zeros((q,physical.FIELDS),dtype=np.uint64)
    for site in range(q):
        for name,value in holder_rom.holder_static_fields(site).items():
            base[site,holder.COL[name]]=value
        base[site,holder.COL['address']]=site
        base[site,holder.FIELDS:]=spatial_codec8.encode_cell(lower_rom[site])
    raw=np.tile(base,(colonies,1))
    data=np.zeros(colonies*q,dtype=np.uint64)
    for col,state in enumerate(upper):
        encoded=projected.encode_cell(state)
        data[col*q+np.asarray(layout.info)]=encoded
        data[col*q+np.asarray(layout.hold)]=encoded
    # The initializer never reads the represented Address to fill SOURCE Data.
    static_wires=set(layout.static_inputs)
    for col in range(colonies):
        for site,wire in raw_sources.items():
            if wire in static_wires:
                data[col*q+site]=0
    for offset in holder.OFFSETS:
        raw[:,holder.COL[f's{offset+2}_data']]=np.roll(data,-offset)
    return raw,upper


def decode_info(raw):
    if raw.ndim!=2 or raw.shape[1]!=physical.FIELDS or len(raw)%physical.Q:
        raise ValueError('complete lower ring required')
    sites=np.asarray(layout_module.build().info)
    return tuple(tuple(map(int,raw[col*physical.Q+sites,
                                  holder.COL['s2_data']]))
                 for col in range(len(raw)//physical.Q))


def state_sha256(raw):
    return hashlib.sha256(memoryview(np.ascontiguousarray(raw))).hexdigest()
