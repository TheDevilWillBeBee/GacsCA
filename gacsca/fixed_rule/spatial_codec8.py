"""Exact full-state encoding of the fixed 8Q spatial successor."""
from . import spatial_epoch8 as rule

GATE_WIDTHS=(1,4,64,14,64,64,2)
ROUTE_WIDTHS=(1,13,1,2,2,16)
PACKET_WIDTHS=(1,13,1,2,64)
WIDTHS=((13,16,2,2,16,16)+GATE_WIDTHS*rule.GATE_SLOTS+
        ROUTE_WIDTHS*rule.ROUTE_SLOTS+
        (64,64,64,2,64,1)+PACKET_WIDTHS+(1,))
FIELDS=len(WIDTHS)
assert sum(WIDTHS)==rule.WIDTH


def encode_cell(cell):
    words=[cell.address,cell.age,cell.kind,cell.active_slot,
           *cell.switch_ages]
    for gate in cell.gates:
        words.extend((gate.valid,gate.opcode,gate.literal,gate.wire,
                      gate.preload0,gate.preload1,gate.preload_ready))
    for route in cell.routes:
        words.extend((route.valid,route.target,route.arg_slot,
                      route.target_gate_slot,route.source_gate_slot,
                      route.launch))
    words.extend((cell.source_value,cell.arg0,cell.arg1,cell.ready,
                  cell.result,cell.done,cell.mail.valid,cell.mail.target,
                  cell.mail.arg_slot,cell.mail.target_gate_slot,
                  cell.mail.value,cell.collision))
    if len(words)!=FIELDS:raise AssertionError('spatial field layout drift')
    return tuple(words)


def decode_cell(words):
    if len(words)!=FIELDS:raise ValueError('all spatial fields required')
    if any(not isinstance(value,int) or not 0<=value<1<<width
           for value,width in zip(words,WIDTHS)):
        raise ValueError('spatial word outside fixed field width')
    take=iter(words)
    def group(n):return tuple(next(take) for _ in range(n))
    address,age,kind,active=group(4)
    switches=group(2)
    gates=tuple(rule.GateSpec(*group(len(GATE_WIDTHS)))
                for _ in range(rule.GATE_SLOTS))
    routes=tuple(rule.Route(*group(len(ROUTE_WIDTHS)))
                 for _ in range(rule.ROUTE_SLOTS))
    source,arg0,arg1,ready,result,done=group(6)
    packet=rule.Packet(*group(len(PACKET_WIDTHS)))
    collision,=group(1)
    return rule.Cell(address,age,kind,active,switches,gates,routes,
                     source,arg0,arg1,ready,result,done,packet,collision)
