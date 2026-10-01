"""Explicit-input WordCode description of the 8Q combined local rule.

All holder and spatial static fields remain inputs. This describes the exact
full-state transition; it is not yet the address-projected own ROM fixed point.
"""
from functools import lru_cache

from . import spatial_codec8 as spatial_codec
from . import spatial_description8 as spatial_description
from . import spatial_epoch8 as spatial_epoch
from . import stream28_dual_holder_description20 as stream28_holder_description,stream28_dual_holder_rule20 as stream28_holder_rule
from . import stream28_spatial_overlay20 as combined
from .wordcode_and import Builder,Program,LIT
from .word_prune import prune


@lru_cache(maxsize=1)
def build():
    holder=stream28_holder_rule
    span=combined.FIELDS
    b=Builder(len(combined.NEIGHBORHOOD)*span)
    zero=b.const(0)

    def embed(program,inputs):
        if len(inputs)!=program.inputs:raise AssertionError('embedded input arity')
        values=list(inputs)
        for opcode,a,d in program.operations:
            values.append(b.const(a) if opcode==LIT else
                          b.op(opcode,values[a],values[d]))
        return tuple(values[wire] for wire in program.outputs)

    hrows={j:{name:(j+7)*span+i
              for i,(name,_) in enumerate(holder.SCHEMA)}
           for j in combined.NEIGHBORHOOD}
    srows={j:spatial_named_row((j+7)*span+holder.FIELDS)
           for j in combined.NEIGHBORHOOD}
    hprogram=stream28_holder_description.build()
    hinputs=tuple(hrows[j][name] for j in combined.NEIGHBORHOOD
                  for name,_ in holder.SCHEMA)
    hvalues=embed(hprogram,hinputs)
    next_holder=dict(zip((name for name,_ in holder.SCHEMA),hvalues))
    own=hrows[0]
    age=own['age']
    stage=b.all(b.not_(b.lt(age,b.const(holder.RESET_AGES[4]))),
                b.lt(age,b.const(combined.RUN_STOP)))
    for slot in range(5):
        key=f's{slot}_head'
        next_holder[key]=b.select(stage,zero,next_holder[key])

    sprogram=spatial_description.build()
    def spatial_at(offset):
        inputs=tuple(srows[j][name] for j in range(offset-1,offset+2)
                     for name in spatial_field_names())
        return dict(zip(spatial_field_names(),embed(sprogram,inputs)))

    # Spatial output field order is the exact spatial codec order.
    center=srows[0]
    capture=b.eq(age,b.const(combined.CAPTURE_AGE))
    running=b.all(b.not_(b.lt(age,b.const(combined.RUN_START))),
                  b.lt(age,b.const(combined.RUN_STOP)))
    source=b.eq(center['kind'],b.const(spatial_epoch.SOURCE))
    corrected=corrected_data(b,hrows,0)
    capture_value=b.select(source,corrected,zero)
    gate=b.eq(center['kind'],b.const(spatial_epoch.GATE))
    reset={'age':zero,'active':zero,
           'source':capture_value,
           'arg0':b.select(gate,center['gate0_preload0'],zero),
           'arg1':b.select(gate,center['gate0_preload1'],zero),
           'ready':b.select(gate,center['gate0_preload_ready'],zero),
           'result':zero,'done':zero,'collision':zero}
    for name in ('valid','target','arg_slot','target_gate_slot','value'):
        reset['mail_'+name]=zero

    # Evaluate the center and four output-neighbor cells with the same fixed
    # spatial local F. Neighbor evaluations contribute only their output latch
    # to the appropriate holder replica.
    spatial_results={d:spatial_at(d) for d in range(-2,3)}
    current=spatial_results[0]
    for d in range(-2,3):
        old=srows[d]
        new=spatial_results[d]
        accepted=b.all(running,
                       b.eq(old['kind'],b.const(spatial_epoch.OUTPUT)),
                       b.not_(old['done']),new['done'])
        clear=b.all(next_holder['f1'],
                    b.not_(b.eq(next_holder['address'],own['address'])))
        commit=b.all(accepted,b.not_(clear))
        key=f's{d+2}_data'
        next_holder[key]=b.select(commit,new['source'],next_holder[key])

    spatial_outputs=[]
    for name in spatial_field_names():
        if name in reset:
            value=b.select(capture,reset[name],
                           b.select(running,current[name],center[name]))
        else:
            value=b.select(running,current[name],center[name])
        spatial_outputs.append(value)
    outputs=tuple(next_holder[name] for name,_ in holder.SCHEMA)+tuple(spatial_outputs)
    if len(outputs)!=combined.FIELDS:raise AssertionError('combined output arity')
    compact=prune(b.finish(outputs))
    return Program(compact.inputs,compact.operations,compact.outputs)


def spatial_field_names():
    return ('address','age','kind','active',
            'switch0','switch1',
            *(f'gate{slot}_{field}' for slot in range(spatial_epoch.GATE_SLOTS)
              for field in ('valid','opcode','literal','wire','preload0',
                            'preload1','preload_ready')),
            *(f'route{slot}_{field}' for slot in range(spatial_epoch.ROUTE_SLOTS)
              for field in ('valid','target','arg_slot','target_gate_slot',
                            'source_gate_slot','launch')),
            'source','arg0','arg1','ready','result','done',
            *(f'mail_{field}' for field in
              ('valid','target','arg_slot','target_gate_slot','value')),
            'collision')


def spatial_named_row(start):
    row=spatial_description._row(start)
    values=(row['address'],row['age'],row['kind'],row['active'],
            *row['switches'],
            *(spec[name] for spec in row['gates'] for name in
              ('valid','opcode','literal','wire','preload0','preload1',
               'preload_ready')),
            *(route[name] for route in row['routes'] for name in
              ('valid','target','arg_slot','target_gate_slot',
               'source_gate_slot','launch')),
            row['source'],row['arg0'],row['arg1'],row['ready'],
            row['result'],row['done'],
            *(row['mail'][name] for name in
              ('valid','target','arg_slot','target_gate_slot','value')),
            row['collision'])
    assert len(values)==spatial_codec.FIELDS
    return dict(zip(spatial_field_names(),values))


def corrected_data(builder,rows,target):
    values=[rows[target+e][f's{2-e}_data'] for e in holder_offsets()]
    a,c,d,e,f=values
    triple=builder.band(builder.band(a,c),d)
    pairs=builder.bor(builder.bor(builder.band(a,c),builder.band(a,d)),
                      builder.band(c,d))
    any3=builder.bor(builder.bor(a,c),d)
    return builder.bor(builder.bor(triple,builder.band(pairs,builder.bor(e,f))),
                       builder.band(any3,builder.band(e,f)))


def holder_offsets():
    return stream28_holder_rule.OFFSETS
