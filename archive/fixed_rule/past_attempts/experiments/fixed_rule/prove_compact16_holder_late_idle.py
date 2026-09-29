"""BDD proof of the late idle clock identity with arbitrary Data/ROM words."""
import json
from pathlib import Path
import time
from gacsca.fixed_rule import compact16_holder_core as c,compact16_holder_rule as f
from gacsca.fixed_rule import compact16_holder_core_clock_description as clock,compact16_holder_late_idle_gpu as idle
from gacsca.fixed_rule.wordcode import MASK
from experiments.fixed_rule.prove_compact16_holder_two_site_geometry import BoundedBDD
from experiments.fixed_rule.run_compact16_holder_streamed_depth2 import sha


def main():
    output=Path('figs/fixed_rule/compact16_holder_late_idle_proof_v1.json')
    if output.exists():raise FileExistsError(output)
    started=time.perf_counter();labels=[('age',i) for i in range(30)]+[('address',i) for i in range(14)]
    for j in range(-2,3):
        for name,width in c.SCHEMA:
            if name=='data' or (name in c.STATIC and -1<=j<=1):labels.extend((j,name,k) for k in range(width))
    b=BoundedBDD(len(labels));variables={label:b.variable(i) for i,label in enumerate(labels)};zero=b.const(0)
    age=tuple(variables['age',k] for k in range(30))+(0,)*34
    address=tuple(variables['address',k] for k in range(14))+(0,)*50
    records={};inputs=[]
    for j in range(-2,3):
        row={name:zero for name,_ in c.SCHEMA};row['age']=age;row['address']=b.add(address,b.const(j&MASK))[:14]+(0,)*50
        for name,width in c.SCHEMA:
            if name=='data' or (name in c.STATIC and -1<=j<=1):row[name]=tuple(variables[j,name,k] for k in range(width))+(0,)*(64-width)
        records[j]=row;inputs.extend(row[name] for name,_ in c.SCHEMA)
    try:
        program=clock.build(healthy_domain=True);actual=b.evaluate(program,tuple(inputs))
        domain=b.and_(b.less(b.const(idle.LAST_EVENT),age),b.less(age,b.const(f.U-1)))
        assert domain
        checked=[]
        for name,_ in f.PROCEDURE:
            expected=records[0]['data'] if name=='data' else zero
            for k,(x,y) in enumerate(zip(actual[c.COL[name]],expected)):
                difference=b.and_(domain,b.xor(x,y))
                assert not difference,(name,k,b.witness(difference))
            checked.append(name)
        # Removing the precommit bound must expose a genuine counterexample.
        outside=b.and_(b.less(b.const(idle.LAST_EVENT),age),b.inv(b.less(age,b.const(f.U-1))))
        mutation=0
        for x,y in zip(actual[c.COL['data']],records[0]['data']):mutation=b.or_(mutation,b.and_(outside,b.xor(x,y)))
        assert mutation,'commit boundary omission was not distinguished'
        result=dict(passed=True,independent_bits=len(labels),BDD_nodes=len(b.nodes),operations=len(program.operations),
                    all_addresses=f.Q,legal_idle_ages=[idle.LAST_EVENT+1,f.U-2],arbitrary_metadata=True,arbitrary_neighbor_Data=True,
                    complete_procedure_fields_checked=checked,missing_commit_boundary_mutation_witness=b.witness(mutation),
                    descriptor_sha256=f.self_description().digest(),clock_descriptor_sha256=program.digest(),seconds=time.perf_counter()-started,
                    source_sha256={str(Path(__file__)):sha(__file__)},
                    theorem='With every head/control/mail word zero and every virtual flag/Wf zero, the described core clock preserves all procedure words for LAST_EVENT<oldAge<U-1, regardless of typed metadata and neighboring Data. Together with canonical geometry, coherent Data/Signals and zero physical flags/Wf, full G changes only Age throughout this interval.',
                    limitation='Composition from core identity to full holder identity uses the documented fivefold-vote/Signal/Wf factorization. Not a universal compiler proof; no skip across commit or controller boot.')
        with output.open('x') as out:out.write(json.dumps(result,indent=2)+'\n')
        print(json.dumps(result),flush=True)
    finally:b.binary.cache_clear()


if __name__=='__main__':main()
