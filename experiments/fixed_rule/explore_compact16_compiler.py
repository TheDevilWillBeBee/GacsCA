"""Bounded CPU search of complete-DAG rewrites, orders and scratch capacities."""
import json
from pathlib import Path
import time
from gacsca.fixed_rule import compact16_holder_program as p,word_boolean_cuts as cuts,word_dag_order as order
from gacsca.fixed_rule.compact16_compiler_candidate import Compilation,cost
from experiments.fixed_rule.certify_compact16_holder_rom import equivalence
from experiments.fixed_rule.run_compact16_holder_streamed_depth2 import sha


def main():
    out=Path('figs/fixed_rule/compact16_compiler_search_v1.json')
    if out.exists():raise FileExistsError(out)
    start=time.perf_counter();original=p.compiled_description();baseline_equivalence=equivalence()
    optimized,certificate=cuts.optimize(original);proof=cuts.verify(original,optimized,certificate)
    descriptions=[('baseline',original,None,None),('cuts',optimized,None,None)]
    for reverse in (False,True):
        for mode in ('original','reverse','deep_first','shallow_first'):
            desc,trace=order.reorder(optimized,reverse_outputs=reverse,children=mode)
            assert order.verify(optimized,desc,trace)
            descriptions.append(('cuts_order',desc,reverse,mode))
    results=[]
    for family,desc,reverse,mode in descriptions:
        for capacity in (240,250,260,270,280,290,300,320,340):
            row=dict(family=family,reverse_outputs=reverse,children=mode,capacity=capacity)
            try:row.update(cost(Compilation(desc,capacity)),accepted_layout=True)
            except (ValueError,AssertionError) as error:row.update(accepted_layout=False,error=repr(error))
            results.append(row)
    good=[x for x in results if x['accepted_layout'] and x['core_cells']<=p.layout().computation_cells]
    best=min(good,key=lambda x:(x['controller_path_ticks'],x['core_cells']))
    result=dict(passed=True,baseline_equivalence=baseline_equivalence,cut_equivalence=proof,
                original_operations=len(original.operations),optimized_operations=len(optimized.operations),
                accepted_cut_rewrites=len(certificate['rewrites']),rejected_shared=certificate['rejected_shared'],
                baseline=cost(Compilation(original,320)),best=best,trials=results,seconds=time.perf_counter()-start,
                source_sha256={str(Path(m.__file__)):sha(m.__file__) for m in (cuts,order)},
                scope='Exact complete-descriptor compiler equivalence and deterministic layout/travel cost search. Does not establish physical execution of a new ROM or smaller Q/U.')
    result['source_sha256'][str(Path(__file__))]=sha(__file__)
    with out.open('x') as stream:stream.write(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='trials'},indent=2))


if __name__=='__main__':main()
