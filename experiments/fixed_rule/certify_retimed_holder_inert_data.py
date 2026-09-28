"""Complete-descriptor invariant for explicitly retained out-of-bank Data.

Canonical Address and uniform legal Age; fixed ROM; arbitrary other raw fields.
Only the five copies of each selected Data word must agree. Verify that every
output is independent of those words except the same five unchanged copies.
"""
import argparse
from functools import lru_cache
import json
from pathlib import Path
import resource
import time
from gacsca.fixed_rule import retimed_holder_rule as f,retimed_holder_core as c
from gacsca.fixed_rule import retimed_holder_program as p
from gacsca.fixed_rule.retimed_holder_literal_cone import rom
from experiments.fixed_rule.certify_small_holder_clock_mail_factorization import ClockTerms
from experiments.fixed_rule.run_retimed_holder_streamed_repair import sha


def certify(targets=(30960,30961,30962),description=None):
    targets = tuple(sorted(set(targets)))
    if not targets or len(targets)>8 or any(type(a) is not int or not 0<=a<f.Q for a in targets) or targets[-1]-targets[0]>32:
        raise ValueError('bounded explicit Data support required')
    desc = f.self_description() if description is None else description
    assert desc.inputs == 15*f.FIELDS and len(desc.outputs) == f.FIELDS
    t = ClockTerms(p.base_rom())
    age = t.variable('legal_uniform_age',31)
    values = {a:t.variable(f'retained_data_{a}',64) for a in targets}
    affected = set(values.values())
    @lru_cache(maxsize=None)
    def depends(word):
        if word in affected:
            return True
        node = t.nodes[word]
        if node[0] in ('variable','const'):
            return False
        if node[0] == 'op':
            return depends(node[2]) or depends(node[3])
        if node[0] in ('not','modadd'):
            return depends(node[1])
        raise AssertionError(('unreviewed symbolic node',node))
    data_fields = {f's{k}_data':k-2 for k in range(5)}
    def raw(site):
        row = []
        for name,width in f.SCHEMA:
            if name.startswith('p'):
                prefix,field = name.split('_',1)
                offset = int(prefix[1:])-3
                value = t.const(int(rom()[(site+offset)%f.Q,c.STATIC.index(field)]))
            elif name == 'address':
                value = t.const(site%f.Q)
            elif name == 'age':
                value = age
            elif name in data_fields and site+data_fields[name] in values:
                value = values[site+data_fields[name]]
            else:
                value = t.variable(f'raw_{site}_{name}',width)
            row.append(value)
        return tuple(row)
    # Each modified logical Data word occupies five physical holders. Radius
    # seven then bounds all possibly affected outputs to distance nine.
    outputs = sorted({a+d for a in targets for d in range(-9,10)})
    retained = independent = 0
    for site in outputs:
        out = t.expression(desc,tuple(value for d in f.NEIGHBORHOOD for value in raw(site+d)))
        assert out[f.COL['address']] == t.const(site%f.Q),'canonical Address not preserved'
        assert out[f.COL['age']] == t.modular_add(age,1,31),'uniform legal Age not preserved'
        for index,(name,_) in enumerate(f.SCHEMA):
            target = site+data_fields[name] if name in data_fields else None
            if target in values:
                assert out[index] == values[target],('selected Data is not unchanged',site,name,t.nodes[out[index]])
                retained += 1
            else:
                assert not depends(out[index]),('retained Data affects another output',site,name)
                independent += 1
    assert retained == 5*len(targets)
    return dict(passed=True,selected_addresses=list(targets),causal_output_sites=outputs,complete_raw_outputs=len(outputs)*f.FIELDS,unchanged_Data_copies=retained,independent_raw_outputs=independent,all_legal_ages=f.U,unrestricted_Data_word_bits=64,arbitrary_other_raw_controller_mail_flags_Signals_Wf=True,no_controller_head_count_or_phase_assumption=True,only_selected_Data_copies_required_coherent=True,canonical_geometry_preserved=True,symbolic_terms=len(t.nodes),relation='For these selected logical Data sites, F commutes with changing their five equal copies; those words remain unchanged and all other raw outputs are independent of them. G has the same property because canonical Address and fixed ROM are preserved.',limitation='Canonical Address, common legal Age and fixed ROM are essential hypotheses. Other raw fields are arbitrary. Composition over time additionally requires these geometry/ROM hypotheses to continue; no noisy arbitrary-geometry invariant is asserted.')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output',required=True)
    args = parser.parse_args()
    out = Path(args.output)
    if out.exists():
        raise FileExistsError(out)
    started = time.perf_counter()
    result = certify()
    sources = (Path(__file__),Path(f.__file__),Path(c.__file__),Path(p.__file__),Path('gacsca/fixed_rule/retimed_holder_description.py'),Path('experiments/fixed_rule/certify_small_holder_clock_mail_factorization.py'),Path('experiments/fixed_rule/certify_small_holder_mail_factorization.py'))
    result.update(descriptor_sha256=f.self_description().digest(),source_sha256={str(path):sha(path) for path in sources},seconds=time.perf_counter()-started,host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    out.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2),flush=True)


if __name__ == '__main__':
    main()
