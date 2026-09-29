"""Initializer-only trial: encode stream metadata in existing MEM static fields.

This leaves the current physical ROM *shape* and alphabet widths unchanged,
but the resulting rows are not an own-ROM for packed28_holder's transition.
An integrated successor must describe the stream transition and compile its
own new self-ROM before these rows can be used for self-simulation.
"""
import numpy as np

from . import packed28_holder_core as c
from . import packed28_holder_program as p
from . import stream_gather as stream

MASK_SELECTOR=c.STATIC.index('b')
ACCEPT_SELECTOR=c.STATIC.index('d')
ACCEPT_STAGE_SHIFT=12


def encode_accept(wire,stage):
    if not 0<=wire<stream.WIRE_LIMIT or not 0<=stage<stream.STAGES:
        raise ValueError('invalid acceptance tag')
    return 1+wire+(stage<<ACCEPT_STAGE_SHIFT)


def decode_accept(tag):
    tag=int(tag)
    if not tag:return stream.NO_WIRE,stream.NO_STAGE
    tag-=1;wire=tag&((1<<ACCEPT_STAGE_SHIFT)-1);stage=tag>>ACCEPT_STAGE_SHIFT
    if wire>=stream.WIRE_LIMIT or stage>=stream.STAGES:
        raise ValueError('invalid encoded acceptance tag')
    return wire,stage


def encode_existing_mail(packet):
    """Fit a stream packet in one existing target/data/hops/valid register."""
    return dict(target=packet.wire,data=packet.value,
                remaining=packet.hops,valid=packet.valid)


def decode_existing_mail(*,target,data,remaining,valid,age):
    """Stage is inferred from physical Age; late packets require clearing."""
    stage=age//stream.FRAME
    if stage>=stream.STAGES:
        if valid:raise ValueError('moving mail outside a gather stage')
        stage=0
    return stream.Packet(int(valid),int(target),int(remaining),stage,int(data))


def trial_rom():
    """Existing Q8192 layout with an encoded stream program in vacant slots."""
    layout=p.layout();rom=p.base_rom().copy();masks,accepts,sources=stream.static_layout()
    assert rom.shape==(layout.computation_cells,len(c.STATIC))
    for address,field in sources.items():
        assert rom[address,0]==c.MEM and rom[address,MASK_SELECTOR]==0
        rom[address,MASK_SELECTOR]=masks[field]
    for address,(wire,stage) in accepts.items():
        assert rom[address,0]==c.MEM and rom[address,ACCEPT_SELECTOR]==0
        rom[address,ACCEPT_SELECTOR]=encode_accept(wire,stage)
    assert len(sources)==stream.FIELDS
    assert len(accepts)==stream.STAGES*len(layout.gathered_inputs)
    rom.flags.writeable=False
    return rom


def footprint():
    old=p.base_rom();new=trial_rom();changed=np.argwhere(old!=new)
    return dict(Q=stream.Q,physical_rom_rows=len(new),old_core_cells=p.layout().computation_cells,
                changed_static_words=len(changed),source_masks=len(stream.static_layout()[2]),
                accept_tags=len(stream.static_layout()[1]),
                widened_physical_fields=0,existing_mail_registers_reused=2,
                unused_ROM_columns_preserved=all(selector in (MASK_SELECTOR,ACCEPT_SELECTOR)
                                                 for _,selector in changed),
                rule_recompiled=False,self_reference_closed=False)
