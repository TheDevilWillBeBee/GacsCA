"""Shared early/final spatial overlay description for the fixed dual pass."""
from functools import lru_cache

from .. import spatial_epoch8 as spatial
from .. import spatial_description8
from .. import stream28_dual_pass20 as physical
from .. import stream28_dual_holder_rule20 as holder
from .. import stream28_spatial_description20 as helpers
from .. import stream28_spatial_overlay20 as late
from ..word_prune import prune
from ..wordcode_and import Builder,Program,LIT
from . import holder_description


@lru_cache(maxsize=1)
def build():
    span=physical.FIELDS
    b=Builder(len(physical.NEIGHBORHOOD)*span)
    zero=b.const(0)
    def embed(program,inputs):
        if len(inputs)!=program.inputs:raise AssertionError('embedded arity')
        values=list(inputs)
        for opcode,a,d in program.operations:
            values.append(b.const(a) if opcode==LIT else
                          b.op(opcode,values[a],values[d]))
        return tuple(values[wire] for wire in program.outputs)
    hrows={j:{name:(j+7)*span+i
              for i,(name,_) in enumerate(holder.SCHEMA)}
           for j in physical.NEIGHBORHOOD}
    srows={j:helpers.spatial_named_row((j+7)*span+holder.FIELDS)
           for j in physical.NEIGHBORHOOD}
    hprogram=holder_description.build()
    hinputs=tuple(hrows[j][name] for j in physical.NEIGHBORHOOD
                  for name,_ in holder.SCHEMA)
    next_holder=dict(zip((name for name,_ in holder.SCHEMA),
                         embed(hprogram,hinputs)))
    own=hrows[0]
    age=own['age']
    early_suppression=b.all(
        b.not_(b.lt(age,b.const(physical.EARLY_SUPPRESS_START))),
        b.lt(age,b.const(physical.EARLY_RUN_STOP)))
    late_suppression=b.all(
        b.not_(b.lt(age,b.const(holder.RESET_AGES[4]))),
        b.lt(age,b.const(late.RUN_STOP)))
    suppress=b.any(early_suppression,late_suppression)
    trigger_age=b.eq(age,b.const(physical.EARLY_RUN_STOP))
    clear=b.all(next_holder['f1'],
                b.not_(b.eq(next_holder['address'],own['address'])))
    for slot in range(5):
        key=f's{slot}_head'
        next_holder[key]=b.select(suppress,zero,next_holder[key])
        trigger=b.all(trigger_age,b.not_(clear),
                      b.nonzero(own[f'p{slot+1}_first']))
        next_holder[key]=b.select(trigger,b.const(1),next_holder[key])

    sprogram=spatial_description8.build()
    names=helpers.spatial_field_names()
    def spatial_at(offset):
        inputs=tuple(srows[j][name] for j in range(offset-1,offset+2)
                     for name in names)
        return dict(zip(names,embed(sprogram,inputs)))
    spatial_results={offset:spatial_at(offset) for offset in range(-2,3)}
    current=spatial_results[0]
    center=srows[0]
    capture=b.any(b.eq(age,b.const(physical.EARLY_CAPTURE_AGE)),
                  b.eq(age,b.const(late.CAPTURE_AGE)))
    early_run=b.all(
        b.not_(b.lt(age,b.const(physical.EARLY_RUN_START))),
        b.lt(age,b.const(physical.EARLY_RUN_STOP)))
    late_run=b.all(b.not_(b.lt(age,b.const(late.RUN_START))),
                   b.lt(age,b.const(late.RUN_STOP)))
    running=b.any(early_run,late_run)
    source=b.eq(center['kind'],b.const(spatial.SOURCE))
    corrected=helpers.corrected_data(b,hrows,0)
    capture_value=b.select(source,corrected,zero)
    gate=b.eq(center['kind'],b.const(spatial.GATE))
    reset={'age':zero,'active':zero,
           'source':capture_value,
           'arg0':b.select(gate,center['gate0_preload0'],zero),
           'arg1':b.select(gate,center['gate0_preload1'],zero),
           'ready':b.select(gate,center['gate0_preload_ready'],zero),
           'result':zero,'done':zero,'collision':zero}
    for name in ('valid','target','arg_slot','target_gate_slot','value'):
        reset['mail_'+name]=zero
    for offset in range(-2,3):
        old=srows[offset]
        new=spatial_results[offset]
        flag_site=b.any(*(b.eq(old['address'],b.const(site))
                          for site in physical.EARLY_FLAG_HOLD_ADDRESSES))
        eligible=b.any(late_run,b.all(early_run,flag_site))
        accepted=b.all(eligible,
                       b.eq(old['kind'],b.const(spatial.OUTPUT)),
                       b.not_(old['done']),new['done'])
        clear=b.all(next_holder['f1'],
                    b.not_(b.eq(next_holder['address'],own['address'])))
        commit=b.all(accepted,b.not_(clear))
        key=f's{offset+2}_data'
        next_holder[key]=b.select(commit,new['source'],next_holder[key])
    spatial_outputs=[]
    for name in names:
        if name in reset:
            value=b.select(capture,reset[name],
                           b.select(running,current[name],center[name]))
        else:
            value=b.select(running,current[name],center[name])
        spatial_outputs.append(value)
    outputs=tuple(next_holder[name] for name,_ in holder.SCHEMA)+tuple(spatial_outputs)
    compact=prune(b.finish(outputs))
    return Program(compact.inputs,compact.operations,compact.outputs)
