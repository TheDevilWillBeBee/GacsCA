"""All-clock obstruction to single-Address repair in the homogeneous terminal cap.

A diagnostic theorem about the unchanged complete descriptor, not an executor.
The proof leaves controller, Data, Signal and every unused field unrestricted.
"""
import argparse
import hashlib
import json
from pathlib import Path
import resource
import time
from gacsca.fixed_rule import small_holder_rule as f
from gacsca.fixed_rule.wordcode import Program, LIT, EQ
from gacsca.fixed_rule.word_prune import prune
from gacsca.fixed_rule.word_bdd import BDD
from experiments.fixed_rule.prove_small_holder_boundary import validate

NAMES=('address','age','f1','f2')
ALLOWED=frozenset(('address','age','f1','f2','w2_wf1','w2_wf2'))


def geometry_program(description):
    validate(description)
    p=prune(Program(description.inputs,description.operations,
                    tuple(description.outputs[f.COL[n]] for n in NAMES)))
    used={w for op,a,b in p.operations if op!=LIT for w in (a,b) if w<p.inputs}
    used.update(w for w in p.outputs if w<p.inputs)
    support=tuple(sorted((w//f.FIELDS-7,f.SCHEMA[w%f.FIELDS][0]) for w in used))
    if any(not -5<=offset<=5 or name not in ALLOWED for offset,name in support):
        raise AssertionError('unexpected geometry dependency: review quantification')
    return p,support


def prove_case(defect_offset,description=None):
    if defect_offset not in range(-5,6) and defect_offset is not None:
        raise ValueError('one local defect or an unaffected neighborhood required')
    desc=f.self_description() if description is None else description
    program,support=geometry_program(desc)
    # 32 clock bits, 15 arbitrary replacement Address bits, 22 arbitrary primary Wf bits.
    width_age=dict(f.SCHEMA)['age']; width_address=dict(f.SCHEMA)['address']
    variables=width_age+width_address+22;b=BDD(variables)
    age=tuple(b.variable(i) for i in range(width_age))+(0,)*(64-width_age)
    replacement=tuple(b.variable(width_age+i) for i in range(width_address))+(0,)*(64-width_address)
    zero=b.const(0);one=b.const(1);background=b.const(f.Q-1)
    words=[]
    for offset in f.NEIGHBORHOOD:
        values={n:zero for n,_ in f.SCHEMA}
        values.update(address=replacement if offset==defect_offset else background,age=age,f1=one,f2=one)
        if -5<=offset<=5:
            for kind in (1,2):
                bit=b.variable(width_age+width_address+2*(offset+5)+kind-1)
                values[f'w2_wf{kind}']=(bit,)+(0,)*63
        words.extend(values[n] for n,_ in f.SCHEMA)
    actual=b.evaluate(program,tuple(words))
    expected=(replacement if defect_offset==0 else background,
              b.add(age,one)[:width_age]+(0,)*(64-width_age),one,one)
    for name,got,want in zip(NAMES,actual,expected):
        for bit,(a,c) in enumerate(zip(got,want)):
            if a!=c:
                witness=b.witness(b.xor(a,c));b.binary.cache_clear()
                raise AssertionError((defect_offset,name,bit,witness))
    result=dict(defect_offset=defect_offset,passed=True,independent_bits=variables,
                BDD_nodes=len(b.nodes),checked_outputs=NAMES,operations=len(program.operations),
                support=support,descriptor_sha256=desc.digest())
    b.binary.cache_clear()
    return result


def prove(description=None):
    desc=f.self_description() if description is None else description
    cases=[prove_case(offset,desc) for offset in (None,*range(-5,6))]
    return dict(passed=True,cases=cases,all_ages=f.U,all_replacement_addresses=f.Q,
        primary_wf_assignments=1<<22,unrestricted_unused_raw_fields=True,
        descriptor_sha256=desc.digest(),physical_radius=7,geometry_radius=5,
        theorem='On an infinite line or a periodic ring of at least 11 cells, homogeneous Address Q-1 except one arbitrary replacement Address, uniform Age and F1=F2=1 have exactly the same Address map and flags after every step, with Age incremented modulo U. This holds for arbitrary controller/Data/Signal/Wf fields. Consequently a single Address-bit fault in the ordinary homogeneous cap never repairs.',
        limitation='Geometry invariant and counterexample only; no claim that all other raw fields follow the healthy cap orbit. Does not rule out other boundary data or finite-horizon hierarchical reliability.')


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True);args=parser.parse_args();out=Path(args.output)
    if out.exists():raise FileExistsError('preserve evidence')
    start=time.perf_counter();result=prove();result.update(seconds=time.perf_counter()-start,host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    paths=[Path(__file__),Path(f.__file__),Path('gacsca/fixed_rule/small_holder_description.py'),Path('gacsca/fixed_rule/word_bdd.py'),Path('gacsca/fixed_rule/word_prune.py')]
    result['source_sha256']={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))

if __name__=='__main__':main()
