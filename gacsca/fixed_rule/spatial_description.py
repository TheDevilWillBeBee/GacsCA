"""WordCode description of the *physical spatial evaluator's own* local F.

Static gates and routes are explicit inputs here. A later combined projected
ROM must supply their fixed address-indexed values and describe its holder
coupling too. This descriptor nevertheless covers the evaluator's actual
bidirectional packet, reset, gate, output, and collision semantics rather
than treating them as an opaque supported opcode.
"""
from functools import lru_cache

from . import spatial_codec as codec
from . import spatial_epoch as physical
from .wordcode_and import Builder,Program,LIT,NAND,ADD,SHR,EQ,LT,AND,AND_ALU
from .word_prune import prune


def _row(start):
    index=start
    def get():
        nonlocal index
        answer=index
        index+=1
        return answer
    row=dict(address=get(),age=get(),kind=get(),active=get(),
             switches=(get(),get()))
    row['gates']=tuple(dict(valid=get(),opcode=get(),literal=get(),
                            wire=get(),preload0=get(),preload1=get(),
                            preload_ready=get())
                       for _ in range(physical.GATE_SLOTS))
    row['routes']=tuple(dict(valid=get(),target=get(),arg_slot=get(),
                             target_gate_slot=get(),source_gate_slot=get(),
                             launch=get())
                        for _ in range(physical.ROUTE_SLOTS))
    row.update(source=get(),arg0=get(),arg1=get(),ready=get(),
               result=get(),done=get())
    row['mail']=dict(valid=get(),target=get(),arg_slot=get(),
                     target_gate_slot=get(),value=get())
    row['collision']=get()
    assert index-start==codec.FIELDS
    return row


@lru_cache(maxsize=1)
def build():
    b=Builder(3*codec.FIELDS)
    left,center,right=(_row(i*codec.FIELDS) for i in range(3))
    z,o=b.const(0),b.const(1)
    def eq(x,y):return b.eq(x,b.const(y))
    def choose(conditions,values,default=z):
        answer=default
        for condition,value in reversed(tuple(zip(conditions,values))):
            answer=b.select(condition,value,answer)
        return answer
    def merged_packet(source,condition):
        return {name:b.select(condition,source[name],z)
                for name in ('valid','target','arg_slot','target_gate_slot','value')}

    age=b.mask(b.add(center['age'],o),15)
    gate=eq(center['kind'],physical.GATE)
    source_kind=eq(center['kind'],physical.SOURCE)
    output=eq(center['kind'],physical.OUTPUT)
    wrap_gate=b.all(gate,eq(age,0))
    wrap_output=b.all(output,eq(age,0))
    old_slot=center['active']
    switch_age=choose((eq(old_slot,0),eq(old_slot,1)),
                      center['switches'],z)
    requested=b.all(gate,b.not_(wrap_gate),b.lt(old_slot,b.const(2)),
                    b.nonzero(switch_age),b.eq(switch_age,age))
    next_valid=choose((eq(old_slot,0),eq(old_slot,1)),
                      (center['gates'][1]['valid'],
                       center['gates'][2]['valid']),z)
    switch=b.all(requested,next_valid)
    collision=b.bor(center['collision'],
                    b.all(requested,b.not_(next_valid)))
    active=b.select(wrap_gate,z,
                    b.select(switch,b.add(old_slot,o),old_slot))
    selected_gate={name:choose(tuple(eq(active,slot) for slot in range(3)),
                               tuple(spec[name] for spec in center['gates']))
                   for name in center['gates'][0]}
    reset=b.bor(wrap_gate,switch)
    arg0=b.select(reset,selected_gate['preload0'],center['arg0'])
    arg1=b.select(reset,selected_gate['preload1'],center['arg1'])
    ready=b.select(reset,selected_gate['preload_ready'],center['ready'])
    result=b.select(reset,z,center['result'])
    done=b.select(b.bor(reset,wrap_output),z,center['done'])
    source_value=b.select(b.bor(wrap_gate,wrap_output),z,center['source'])
    compute_ready=ready

    from_left=b.all(left['mail']['valid'],
                    b.not_(eq(left['mail']['target_gate_slot'],3)))
    from_right=b.all(right['mail']['valid'],
                     eq(right['mail']['target_gate_slot'],3))
    collision=b.bor(collision,b.all(from_left,from_right))
    incoming={name:choose((from_left,from_right),
                          (left['mail'][name],right['mail'][name]))
              for name in left['mail']}
    gate_target=b.all(incoming['valid'],gate,
                      b.eq(incoming['target'],center['address']),
                      b.eq(incoming['target_gate_slot'],active))
    output_target=b.all(incoming['valid'],output,
                        b.eq(incoming['target'],center['address']))
    arg_one=b.nonzero(incoming['arg_slot'])
    bit=b.select(arg_one,b.const(2),o)
    old_arg=b.select(arg_one,arg1,arg0)
    collision=b.bor(collision,b.all(gate_target,
                    b.nonzero(b.band(ready,bit)),
                    b.not_(b.eq(old_arg,incoming['value']))))
    arg0=b.select(b.all(gate_target,b.not_(arg_one)),incoming['value'],arg0)
    arg1=b.select(b.all(gate_target,arg_one),incoming['value'],arg1)
    ready=b.select(gate_target,b.bor(ready,bit),ready)
    collision=b.bor(collision,b.all(output_target,done,
                    b.not_(b.eq(source_value,incoming['value']))))
    source_value=b.select(output_target,incoming['value'],source_value)
    done=b.select(output_target,o,done)
    consumed=b.bor(gate_target,output_target)
    packet={name:b.select(consumed,z,value)
            for name,value in incoming.items()}

    emitted={name:z for name in packet}
    for route in center['routes']:
        scheduled=b.all(route['valid'],b.eq(route['launch'],age))
        selected_source=b.eq(route['source_gate_slot'],active)
        can_gate=b.all(selected_source,done)
        bad_gate=b.all(scheduled,gate,b.not_(can_gate))
        collision=b.bor(collision,bad_gate)
        candidate=b.all(scheduled,b.any(source_kind,b.all(gate,can_gate)))
        collision=b.bor(collision,b.all(candidate,emitted['valid']))
        use=b.all(candidate,b.not_(emitted['valid']))
        value=b.select(source_kind,center['source'],result)
        for name,word in (('valid',o),('target',route['target']),
                          ('arg_slot',route['arg_slot']),
                          ('target_gate_slot',route['target_gate_slot']),
                          ('value',value)):
            emitted[name]=b.select(use,word,emitted[name])
    collision=b.bor(collision,b.all(packet['valid'],emitted['valid']))
    mail={name:b.select(packet['valid'],packet[name],emitted[name])
          for name in packet}

    opcode=selected_gate['opcode']
    marked=b.any(*(eq(opcode,mark) for mark in physical.OUTPUT_BASE_OPCODE))
    base_opcode=opcode
    for mark,plain in physical.OUTPUT_BASE_OPCODE.items():
        base_opcode=b.select(eq(opcode,mark),b.const(plain),base_opcode)
    literal=eq(base_opcode,LIT)
    compute=b.all(gate,b.not_(done),selected_gate['valid'],
                  b.any(literal,eq(compute_ready,3)))
    arith=z
    for operation in (NAND,ADD,SHR,EQ,LT,AND,AND_ALU):
        arith=b.select(eq(base_opcode,operation),
                       b.op(operation,arg0,arg1),arith)
    computed=b.select(literal,selected_gate['literal'],arith)
    result=b.select(compute,computed,result)
    done=b.select(compute,o,done)
    source_value=b.select(b.all(compute,marked),computed,source_value)

    outputs=[center['address'],age,center['kind'],active,
             *center['switches']]
    for spec in center['gates']:
        outputs.extend(spec[name] for name in
                       ('valid','opcode','literal','wire','preload0',
                        'preload1','preload_ready'))
    for route in center['routes']:
        outputs.extend(route[name] for name in
                       ('valid','target','arg_slot','target_gate_slot',
                        'source_gate_slot','launch'))
    outputs.extend((source_value,arg0,arg1,ready,result,done,
                    *(mail[name] for name in
                      ('valid','target','arg_slot','target_gate_slot','value')),
                    collision))
    assert len(outputs)==codec.FIELDS
    # word_prune is opcode-agnostic, but its return type is the older Program
    # whose diagnostic evaluator has no AND opcode. Retain its pruned graph
    # with the AND-capable evaluator used by the actual physical ALU.
    compact=prune(b.finish(tuple(outputs)))
    return Program(compact.inputs,compact.operations,compact.outputs)
