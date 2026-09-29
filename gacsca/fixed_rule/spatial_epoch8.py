"""Fixed radius-one 8Q spatial evaluator with late output-latch routes.

This is a successor-rule candidate, not a closed self-simulator. Its 16-bit
Age gives a fixed 8Q evaluator window. A marked output gate stores its value
in source_value through later gate-slot reuse; a static leftward output route
can emit that value after all rightward operand traffic clears. The local
rule and state alphabet are independent of hierarchy depth.
"""
from dataclasses import dataclass,replace

from . import spatial_layer1 as base
from .wordcode_and import NAND,ADD,SHR,EQ,LT,LIT,AND,arithmetic

Q=base.Q
AGE_BITS=16
PERIOD=1<<AGE_BITS
ROUTE_SLOTS=base.ROUTE_SLOTS
GATE_SLOTS=3
INERT,SOURCE,GATE=base.INERT,base.SOURCE,base.GATE
OUTPUT=3
# Seven spare four-bit opcodes mark a result that must survive site reuse.
# The logical wire identifier stays in GateSpec.wire; no new state bit is used.
OUTPUT_OPCODE={NAND:0,ADD:7,SHR:8,EQ:9,LT:10,LIT:12,AND:13}
OUTPUT_BASE_OPCODE={marked:base for base,marked in OUTPUT_OPCODE.items()}


def base_opcode(opcode):
    return OUTPUT_BASE_OPCODE.get(opcode,opcode)


@dataclass(frozen=True)
class GateSpec:
    valid:int=0
    opcode:int=0
    literal:int=0
    wire:int=0
    preload0:int=0
    preload1:int=0
    preload_ready:int=0

    def __post_init__(self):
        if not (self.valid in (0,1) and 0<=self.opcode<16 and
                0<=self.literal<1<<64 and 0<=self.wire<1<<14 and
                0<=self.preload0<1<<64 and 0<=self.preload1<1<<64 and
                0<=self.preload_ready<4):
            raise ValueError('gate description outside fixed alphabet')


EMPTY_GATE=GateSpec()
EMPTY_GATES=(EMPTY_GATE,)*GATE_SLOTS


@dataclass(frozen=True)
class Route:
    valid:int=0
    target:int=0
    arg_slot:int=0
    target_gate_slot:int=0
    source_gate_slot:int=0
    launch:int=0

    def __post_init__(self):
        if not (self.valid in (0,1) and 0<=self.target<Q and
                self.arg_slot in (0,1) and 0<=self.target_gate_slot<4
                and 0<=self.source_gate_slot<GATE_SLOTS and
                0<=self.launch<PERIOD):
            raise ValueError('route outside fixed alphabet')


EMPTY_ROUTE=Route()
EMPTY_ROUTES=(EMPTY_ROUTE,)*ROUTE_SLOTS


@dataclass(frozen=True)
class Packet:
    valid:int=0
    target:int=0
    arg_slot:int=0
    target_gate_slot:int=0
    value:int=0

    def __post_init__(self):
        if not (self.valid in (0,1) and 0<=self.target<Q and
                self.arg_slot in (0,1) and 0<=self.target_gate_slot<4
                and 0<=self.value<1<<64):
            raise ValueError('packet outside fixed alphabet')


EMPTY_PACKET=Packet()


@dataclass(frozen=True)
class Cell:
    address:int=0
    age:int=0
    kind:int=INERT
    active_slot:int=0
    switch_ages:tuple=(0,0)
    gates:tuple=EMPTY_GATES
    routes:tuple=EMPTY_ROUTES
    source_value:int=0
    arg0:int=0
    arg1:int=0
    ready:int=0
    result:int=0
    done:int=0
    mail:Packet=EMPTY_PACKET
    collision:int=0

    def __post_init__(self):
        if not (0<=self.address<Q and 0<=self.age<PERIOD and
                self.kind in (INERT,SOURCE,GATE,OUTPUT) and
                0<=self.active_slot<GATE_SLOTS and len(self.switch_ages)==GATE_SLOTS-1
                and all(0<=age<PERIOD for age in self.switch_ages)
                and len(self.gates)==GATE_SLOTS and
                all(isinstance(gate,GateSpec) for gate in self.gates) and
                len(self.routes)==ROUTE_SLOTS and
                all(isinstance(route,Route) for route in self.routes) and
                0<=self.source_value<1<<64 and 0<=self.arg0<1<<64 and
                0<=self.arg1<1<<64 and 0<=self.ready<4 and
                0<=self.result<1<<64 and self.done in (0,1) and
                isinstance(self.mail,Packet) and self.collision in (0,1)):
            raise ValueError('cell outside fixed alphabet')


WIDTH=(13+AGE_BITS+2+2+(GATE_SLOTS-1)*AGE_BITS+GATE_SLOTS*(1+4+64+14+64+64+2)+
       ROUTE_SLOTS*(1+13+1+2+2+AGE_BITS)+64+64+64+2+64+1+
       (1+13+1+2+64)+1)
NEIGHBORHOOD=(-1,0,1)


def local_step(neighbors):
    """The single local transition, independent of encoded DAG prefix."""
    if len(neighbors)!=3:raise ValueError('exact radius-one neighborhood required')
    left,c,right=neighbors
    age=(c.age+1)%PERIOD
    active=c.active_slot
    arg0,arg1,ready=c.arg0,c.arg1,c.ready
    result,done=c.result,c.done
    source_value=c.source_value
    collision=c.collision
    if c.kind==OUTPUT and age==0:
        source_value,done=0,0
    if c.kind==GATE and age==0:
        source_value=0
        active=0
        spec=c.gates[0]
        arg0,arg1,ready=spec.preload0,spec.preload1,spec.preload_ready
        result,done=0,0
    else:
        switch=c.switch_ages[active] if active<GATE_SLOTS-1 else 0
        if c.kind==GATE and switch==age and switch!=0:
            if not c.gates[active+1].valid:
                collision=1
            else:
                active+=1
                spec=c.gates[active]
                arg0,arg1,ready=spec.preload0,spec.preload1,spec.preload_ready
                result,done=0,0
    compute_ready=ready
    from_left=(left.mail if left.mail.valid and
               left.mail.target_gate_slot!=3 else EMPTY_PACKET)
    from_right=(right.mail if right.mail.valid and
                right.mail.target_gate_slot==3 else EMPTY_PACKET)
    if from_left.valid and from_right.valid:collision=1
    packet=from_left if from_left.valid else from_right
    if packet.valid and c.kind==GATE and packet.target==c.address:
        if packet.target_gate_slot==active:
            bit=1<<packet.arg_slot
            old=arg1 if packet.arg_slot else arg0
            if ready&bit and old!=packet.value:collision=1
            if packet.arg_slot:arg1=packet.value
            else:arg0=packet.value
            ready|=bit
            packet=EMPTY_PACKET
    elif packet.valid and c.kind==OUTPUT and packet.target==c.address:
        if done and source_value!=packet.value:collision=1
        source_value,done=packet.value,1
        packet=EMPTY_PACKET
    emitted=EMPTY_PACKET
    if c.kind in (SOURCE,GATE):
        for route in c.routes:
            if not route.valid or route.launch!=age:continue
            if c.kind==SOURCE:
                value=c.source_value
            elif (route.target_gate_slot==3 and
                  c.gates[route.source_gate_slot].opcode in OUTPUT_BASE_OPCODE):
                value=c.source_value
            elif route.source_gate_slot==active and done:
                value=result
            else:
                collision=1
                continue
            if emitted.valid:collision=1
            else:emitted=Packet(1,route.target,route.arg_slot,
                                route.target_gate_slot,value)
    if packet.valid and emitted.valid:collision=1
    mail=packet if packet.valid else emitted
    if c.kind==GATE and not done:
        spec=c.gates[active]
        if spec.valid:
            opcode=base_opcode(spec.opcode)
            if opcode==LIT:result,done=spec.literal,1
            elif compute_ready==3:
                result,done=arithmetic(opcode,arg0,arg1),1
            if done and spec.opcode in OUTPUT_BASE_OPCODE:
                source_value=result
    return replace(c,age=age,active_slot=active,source_value=source_value,arg0=arg0,arg1=arg1,
                   ready=ready,result=result,done=done,mail=mail,
                   collision=collision)
