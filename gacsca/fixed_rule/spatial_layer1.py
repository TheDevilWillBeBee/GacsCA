"""Fixed local CA pilot for prefixes of the own-rule evaluator DAG.

This is an isolated executable feasibility experiment, not a complete
self-simulator.  The one physical transition scans 38 encoded outgoing
routes, moves one 64-bit packet one site to the right, receives operands, and
evaluates a binary ALU or local literal gate.  The rule and finite alphabet
do not depend on the chosen dependency-DAG prefix.  A host compiler supplies
only initial static route/opcode data; it never supplies evolving transitions.
Here ``max_depth`` denotes circuit dependency depth, not hierarchy depth.
"""
from dataclasses import dataclass,replace
from functools import lru_cache

from . import stream28_holder_program as reference
from . import stream28_holder_rule as raw
from .wordcode_and import LIT,arithmetic

Q=raw.Q
PERIOD=8*Q
ROUTE_SLOTS=38
SOURCE,GATE,INERT=1,2,0
EMPTY_TARGET=Q


@dataclass(frozen=True)
class Route:
    valid:int=0
    target:int=0
    slot:int=0
    launch:int=0

    def __post_init__(self):
        if self.valid not in (0,1) or not 0<=self.target<Q or self.slot not in (0,1) or not 0<=self.launch<PERIOD:
            raise ValueError('route outside fixed alphabet')


EMPTY_ROUTE=Route()
EMPTY_ROUTES=(EMPTY_ROUTE,)*ROUTE_SLOTS


@dataclass(frozen=True)
class Packet:
    valid:int=0
    target:int=0
    slot:int=0
    value:int=0

    def __post_init__(self):
        if self.valid not in (0,1) or not 0<=self.target<Q or self.slot not in (0,1) or not 0<=self.value<1<<64:
            raise ValueError('packet outside fixed alphabet')


EMPTY_PACKET=Packet()


@dataclass(frozen=True)
class Cell:
    address:int=0
    age:int=0
    kind:int=INERT
    opcode:int=0
    literal:int=0
    gate_wire:int=0
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
        if not (0<=self.address<Q and 0<=self.age<PERIOD and self.kind in (INERT,SOURCE,GATE)
                and 0<=self.opcode<16 and 0<=self.literal<1<<64
                and 0<=self.gate_wire<1<<14 and len(self.routes)==ROUTE_SLOTS
                and all(isinstance(route,Route) for route in self.routes)
                and 0<=self.source_value<1<<64 and 0<=self.arg0<1<<64
                and 0<=self.arg1<1<<64 and 0<=self.ready<4
                and 0<=self.result<1<<64 and self.done in (0,1)
                and isinstance(self.mail,Packet) and self.collision in (0,1)):
            raise ValueError('cell outside fixed alphabet')


WIDTH=(13+16+2+4+64+14+ROUTE_SLOTS*(1+13+1+16)+64+64+64+2+64+1+
       (1+13+1+64)+1)
NEIGHBORHOOD=(-1,0,1)


def local_step(neighbors):
    """Exactly one radius-one physical transition; no host DAG lookup."""
    if len(neighbors)!=3:raise ValueError('exact radius-one neighborhood required')
    left,c,_=neighbors
    packet=left.mail if left.mail.valid else EMPTY_PACKET
    collision=c.collision
    arg0,arg1,ready=c.arg0,c.arg1,c.ready
    if packet.valid and c.kind==GATE and packet.target==c.address:
        bit=1<<packet.slot
        prior=arg1 if packet.slot else arg0
        if ready&bit and prior!=packet.value:collision=1
        if packet.slot:arg1=packet.value
        else:arg0=packet.value
        ready|=bit
        packet=EMPTY_PACKET
    emitted=EMPTY_PACKET
    if c.kind==SOURCE or (c.kind==GATE and c.done):
        payload=c.source_value if c.kind==SOURCE else c.result
        for route in c.routes:
            if route.valid and route.launch==c.age+1:
                if emitted.valid:collision=1
                else:emitted=Packet(1,route.target,route.slot,payload)
    if packet.valid and emitted.valid:collision=1
    mail=packet if packet.valid else emitted
    result,done=c.result,c.done
    if c.kind==GATE and not c.done:
        if c.opcode==LIT:result,done=c.literal,1
        elif c.ready==3:result,done=arithmetic(c.opcode,c.arg0,c.arg1),1
    return replace(c,age=(c.age+1)%PERIOD,arg0=arg0,arg1=arg1,ready=ready,
                   result=result,done=done,mail=mail,collision=collision)


def step_ring(cells):
    if len(cells)!=Q:raise ValueError('one complete fixed Q-cell ring required')
    return tuple(local_step((cells[(at-1)%Q],cells[at],cells[(at+1)%Q]))
                 for at in range(Q))


@dataclass(frozen=True)
class Edge:
    source:int
    target:int
    slot:int
    launch:int
    source_wire:int
    gate_wire:int

    @property
    def arrival(self):return self.launch+self.target-self.source

    @property
    def phase(self):return (self.source-self.launch)%Q


@dataclass(frozen=True)
class Layout:
    max_depth:int
    phase_policy:str
    gate_operations:tuple
    gate_addresses:tuple
    gate_completion:tuple
    edges:tuple
    max_routes_per_source:int
    last_arrival:int
    last_completion:int
    literal_preloads:int
    description_sha256:str


@lru_cache(maxsize=24)
def layout(max_depth=1,phase_policy='earliest'):
    if type(max_depth) is not int or max_depth<1:raise ValueError('positive evaluator DAG prefix depth required')
    if phase_policy not in ('earliest','ordinal'):raise ValueError('unknown encoded phase schedule')
    program=reference.compiled_description();rom=reference.layout()
    depth=[0]*program.inputs;gates=[]
    for index,(opcode,a,b) in enumerate(program.operations):
        layer=1 if opcode==LIT else 1+max(depth[a],depth[b])
        depth.append(layer)
        if layer<=max_depth:gates.append(index)
    addresses=tuple(rom.memory_count+index for index in range(len(gates)))
    if not addresses or addresses[-1]>=Q-5:raise AssertionError('prefix gates exceed fixed colony')
    placement={program.inputs+index:address for index,address in zip(gates,addresses)}
    edges=[];phase=0;used_phases=set();counts={};completion={};preloads=0
    for index,target in zip(gates,addresses):
        opcode,a,b=program.operations[index]
        wire_out=program.inputs+index
        if opcode==LIT:
            completion[wire_out]=1
            continue
        arrivals=[]
        for slot,wire in enumerate((a,b)):
            if wire>=program.inputs and program.operations[wire-program.inputs][0]==LIT:
                preloads+=1
                continue
            source=rom.wires[wire] if wire<program.inputs else placement[wire]
            ready=0 if wire<program.inputs else completion[wire]
            if source is None or not 0<=source<target:
                raise AssertionError('operand source not left of gate')
            if phase_policy=='ordinal':
                launch=1+((source-phase-1)%Q)
                while launch<=ready:launch+=Q
            else:
                launch=ready+1
                while (source-launch)%Q in used_phases:launch+=1
            if launch>=PERIOD:raise AssertionError('launch exceeds fixed Age alphabet')
            lane_phase=(source-launch)%Q
            if lane_phase in used_phases:raise AssertionError('phase collision')
            used_phases.add(lane_phase)
            edge=Edge(source,target,slot,launch,wire,wire_out)
            edges.append(edge);arrivals.append(edge.arrival)
            counts[source]=counts.get(source,0)+1
            phase+=1
        completion[wire_out]=max(arrivals,default=0)+1
    if phase>=Q or max(counts.values(),default=0)>ROUTE_SLOTS:
        raise AssertionError('fixed lane or source route capacity exceeded')
    result=Layout(max_depth,phase_policy,tuple(gates),addresses,
                  tuple(completion[program.inputs+index] for index in gates),
                  tuple(edges),max(counts.values(),default=0),
                  max((edge.arrival for edge in edges),default=0),
                  max(completion.values()),preloads,program.digest())
    if max_depth==1:assert len(gates)==1020 and len(edges)==1876
    assert len({edge.phase for edge in edges})==len(edges)
    assert result.last_completion<PERIOD
    return result


def initial_cells(raw_words,max_depth=1,phase_policy='earliest'):
    """Host encodes initial inputs and immutable routes; evolution is local."""
    program=reference.compiled_description();placement=layout(max_depth,phase_policy)
    if len(raw_words)!=program.inputs or any(not 0<=int(word)<1<<64 for word in raw_words):
        raise ValueError('complete raw descriptor input words required')
    rows=[Cell(address=at) for at in range(Q)]
    source_wires={}
    for edge in placement.edges:
        if edge.source_wire>=program.inputs:continue
        prior=source_wires.setdefault(edge.source,edge.source_wire)
        if prior!=edge.source_wire:raise AssertionError('two raw words share a source site')
    for source,wire in source_wires.items():
        rows[source]=replace(rows[source],kind=SOURCE,source_value=int(raw_words[wire]))
    buckets={source:[] for source in {edge.source for edge in placement.edges}}
    for edge in placement.edges:buckets[edge.source].append(Route(1,edge.target,edge.slot,edge.launch))
    for index,address in zip(placement.gate_operations,placement.gate_addresses):
        opcode,a,b=program.operations[index]
        preloaded={}
        if opcode!=LIT:
            for slot,wire in enumerate((a,b)):
                if wire>=program.inputs and program.operations[wire-program.inputs][0]==LIT:
                    preloaded['arg'+str(slot)]=program.operations[wire-program.inputs][1]
                    preloaded['ready']=preloaded.get('ready',0)|(1<<slot)
        rows[address]=replace(rows[address],kind=GATE,opcode=opcode,
                              literal=a if opcode==LIT else 0,
                              gate_wire=program.inputs+index,**preloaded)
    for source,routes in buckets.items():
        rows[source]=replace(rows[source],routes=tuple(routes)+(EMPTY_ROUTE,)*(ROUTE_SLOTS-len(routes)))
    return tuple(rows)


def expected_prefix(raw_words,max_depth=1,phase_policy='earliest'):
    program=reference.compiled_description();placement=layout(max_depth,phase_policy)
    if len(raw_words)!=program.inputs:raise ValueError('complete descriptor input required')
    values=list(map(int,raw_words))
    for opcode,a,b in program.operations:
        values.append(a if opcode==LIT else arithmetic(opcode,values[a],values[b]))
    return {program.inputs+index:values[program.inputs+index]
            for index in placement.gate_operations}


def expected_first_layer(raw_words):return expected_prefix(raw_words,1)


def schedule_certificate(max_depth=1,phase_policy='earliest'):
    g=layout(max_depth,phase_policy);counts={}
    for edge in g.edges:counts[edge.source]=counts.get(edge.source,0)+1
    return dict(Q=Q,rule_width_bits=WIDTH,rule_radius=1,max_depth=max_depth,
                phase_policy=phase_policy,
                gate_count=len(g.gate_operations),operand_packets=len(g.edges),
                local_constant_operands=g.literal_preloads,
                source_sites=len(counts),max_routes_per_source=g.max_routes_per_source,
                phase_count=len({edge.phase for edge in g.edges}),
                last_arrival=g.last_arrival,last_completion=g.last_completion,
                Gray_late_budget=8*Q,margin=8*Q-g.last_completion,
                description_sha256=g.description_sha256)
