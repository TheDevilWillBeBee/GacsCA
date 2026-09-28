"""Late coherent-Signal identity and complete-controller independence certificate."""
import json
from pathlib import Path
import time
from gacsca.fixed_rule import compact16_holder_rule as f,compact16_holder_core as c
from gacsca.fixed_rule import compact16_holder_prefix_description as prefix,compact16_holder_late_events as events
from gacsca.fixed_rule.wordcode import Program,LIT,MASK
from gacsca.fixed_rule.word_prune import prune
from experiments.fixed_rule.prove_compact16_holder_two_site_geometry import BoundedBDD
from experiments.fixed_rule.run_compact16_holder_streamed_depth2 import sha


def support(program,outputs):
    pending=list(outputs);seen=set();inputs=set()
    while pending:
        wire=pending.pop()
        if wire in seen:continue
        seen.add(wire)
        if wire<program.inputs:inputs.add(wire)
        else:
            op,a,b=program.operations[wire-program.inputs]
            if op!=LIT:pending.extend((a,b))
    return inputs


def main():
    output=Path('figs/fixed_rule/compact16_holder_stationary_signals_v1.json')
    if output.exists():raise FileExistsError(output)
    start=time.perf_counter();desc=f.self_description()
    procedure_outputs=[desc.outputs[f.COL[f's{k}_{name}']] for k in range(5) for name,_ in f.PROCEDURE]
    reached=support(desc,procedure_outputs)
    assert all(wire%f.FIELDS!=f.COL['signal'] for wire in reached)
    full=prefix.build();program=prune(Program(full.inputs,full.operations,(full.outputs[c.COL['signal']],)))
    used=support(program,program.outputs)
    assert all(c.SCHEMA[wire%c.FIELDS][0] in ('address','age','data','signal') for wire in used)
    labels=[('age',k) for k in range(30)]+[('address',k) for k in range(14)]+[('signal',j) for j in range(-7,8)]+[('data',k) for k in range(64)]
    b=BoundedBDD(len(labels));variables={key:b.variable(i) for i,key in enumerate(labels)};zero=b.const(0)
    age=tuple(variables['age',k] for k in range(30))+(0,)*34;address=tuple(variables['address',k] for k in range(14))+(0,)*50
    data=tuple(variables['data',k] for k in range(64));inputs=[]
    for j in range(-5,6):
        row={name:zero for name,_ in c.SCHEMA};row['age']=age;row['address']=b.add(address,b.const(j&MASK))[:14]+(0,)*50
        row['signal']=tuple(variables['signal',j+d] for d in range(-2,3))+(0,)*59
        if j==0:row['data']=data
        inputs.extend(row[name] for name,_ in c.SCHEMA)
    try:
        actual=b.evaluate(program,tuple(inputs))[0];wanted=tuple(variables['signal',d] for d in range(-2,3))+(0,)*59
        domain=b.less(b.const(events.LAST_EVENT),age)
        assert domain
        for bit,(x,y) in enumerate(zip(actual,wanted)):assert not b.and_(domain,b.xor(x,y)),bit
        # A mismatched coherent bit is not vacuously admitted by the age domain.
        assert b.and_(domain,b.xor(wanted[0],wanted[1]))
        original=Path(events.period.__file__).with_suffix('.cu').read_text();first=original.index('__device__ bool signal_shape(');last=original.index('__device__ uint64_t physical_flag(',first)
        widened=events.source_text();assert widened==original[:first]+events.SIGNAL_GUARD+original[last:]
        result=dict(passed=True,independent_bits=len(labels),BDD_nodes=len(b.nodes),all_late_ages=[events.LAST_EVENT+1,f.U-1],
                    all_addresses=f.Q,stationary_signal_output_bits=5,complete_procedure_outputs_checked=len(procedure_outputs),
                    complete_procedure_Signal_input_dependencies=0,only_resident_source_change='signal_shape guard',
                    original_guard_sha256=__import__('hashlib').sha256(original[first:last].encode()).hexdigest(),
                    descriptor_sha256=desc.digest(),prefix_descriptor_sha256=full.digest(),seconds=time.perf_counter()-start,
                    source_sha256={str(Path(x)):sha(x) for x in (__file__,events.__file__)},
                    theorem='All coherent five-bit Signal patterns are stationary throughout the late interval including commit. Complete F procedure outputs have no old Signal dependencies. The resident transition and controller-event sources are unchanged; only their stationary-Signal acceptance guard is widened.',
                    limitation='Composes with canonical zero-flag coherent-procedure domain and existing event-distance correctness; not a universal event-kernel proof or arbitrary-noise invariant.')
        with output.open('x') as out:out.write(json.dumps(result,indent=2)+'\n')
        print(json.dumps(result),flush=True)
    finally:b.binary.cache_clear()


if __name__=='__main__':main()
