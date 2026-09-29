"""Complete raw own-ROM calculation for the fixed optimized compiler candidate."""
import hashlib
import json
from pathlib import Path
import time
from types import FunctionType
import numpy as np
from gacsca.fixed_rule import compact16_holder_rule as f,compact16_holder_core as c
from gacsca.fixed_rule import compact16_holder_compiler_program as p
from gacsca.fixed_rule import compact16_holder_program as baseline
from gacsca.fixed_rule.compact16_compiler_candidate import cost
from experiments.fixed_rule import certify_compact16_holder_rom as original
from experiments.fixed_rule.run_compact16_holder_streamed_depth2 import sha


class Terms(original.Terms):
    def expression(self,program,inputs):
        if program.digest()==f.self_description().digest():
            # Composition of independently verified baseline equivalence and
            # exhaustive small-cut rewrite certificate. The old structural
            # term oracle has no canonicalization for general Boolean cuts.
            program=p.compiled_description()
        return super().expression(program,inputs)


def bind(function):
    namespace=dict(function.__globals__);namespace.update(p=p,Terms=Terms)
    return FunctionType(function.__code__,namespace,function.__name__,function.__defaults__,function.__closure__)


class Checker(original.Checker):
    __init__=bind(original.Checker.__init__)
    reset=bind(original.Checker.reset)
    mem=bind(original.Checker.mem)
    execute=bind(original.Checker.execute)
    deliver=bind(original.Checker.deliver)
    vote=bind(original.Checker.vote)
    check=bind(original.Checker.check)


def main():
    root=Path('figs/fixed_rule');out=root/'compact16_compiler_rom_v1.json'
    if out.exists():raise FileExistsError(out)
    started=time.perf_counter();search_path=root/'compact16_compiler_search_v1.json';search=json.loads(search_path.read_text())
    assert search['passed'] and search['best']['description_sha256']==p.compiled_description().digest()
    assert search['best']['capacity']==p.RESULT_CAPACITY and search['best']['reverse_outputs'] and search['best']['children']=='original'
    baseline_certificate=original.equivalence()
    desc,certificate,permutation=p.proof()
    cut_certificate=p.cuts.verify(baseline.compiled_description(),p.cuts.optimize(baseline.compiled_description())[0],certificate)
    ordered=p.order.verify(certificate['original'] if False else p.cuts.optimize(baseline.compiled_description())[0],desc,permutation)
    assert cut_certificate['complete_outputs']==f.FIELDS and ordered
    g=p.layout();rom=p.base_rom();assert g.computation_cells+5<=f.Q
    assert rom.shape==(g.computation_cells,len(c.STATIC))
    result_flow=Checker().check();assert result_flow['complete_raw_outputs_per_colony']==f.FIELDS
    timing=g.timing_certificate();assert timing['fits']
    costs=cost(p.compilation());assert costs=={k:search['best'][k] for k in costs}
    result=dict(passed=True,baseline_equivalence=baseline_certificate,
                cut_equivalence=cut_certificate,ordered_dependency_certificate=ordered,
                own_ROM_dataflow=result_flow,timing_certificate=timing,cost=costs,
                physical_descriptor_sha256=f.self_description().digest(),ROM_sha256=hashlib.sha256(rom.tobytes()).hexdigest(),
                complete_encoded_fields=f.FIELDS,depth_selection=False,
                physical_rule_unchanged=True,physical_alphabet_unchanged=True,
                prior_cost=search['baseline'],controller_ticks_saved=search['baseline']['controller_path_ticks']-costs['controller_path_ticks'],
                core_cells_saved=search['baseline']['core_cells']-costs['core_cells'],
                source_sha256={str(Path(m.__file__)):sha(m.__file__) for m in (p,p.cuts,p.order)},
                search_receipt_sha256=sha(search_path),seconds=time.perf_counter()-started,
                scope='Complete conditional own-ROM symbolic data flow on arbitrary typed raw inputs, including all controller fields, plus exact compiler rewrite and order certificates. Physical path composition, full work-period execution and noise behavior of this changed ROM are not transferred from the baseline.')
    result['source_sha256'][str(Path(__file__))]=sha(__file__)
    with out.open('x') as stream:stream.write(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('own_ROM_dataflow','source_sha256')},indent=2))


if __name__=='__main__':main()
