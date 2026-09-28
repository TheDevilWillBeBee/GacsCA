"""Independent concrete semantics checks for the symbolic ROM certificate.

Evaluates symbolic terms against complete scalar/native projected transitions.
This is a proof-tool audit, not a physical execution or instruction-refinement run.
"""
import argparse,hashlib,json,random,resource,time
from pathlib import Path
import numpy as np
from gacsca.fixed_rule import small_holder_rule as f,small_holder_projected as r
from gacsca.fixed_rule import small_holder_program as p,small_holder_native as native,small_holder_core as c
from gacsca.fixed_rule.wordcode import arithmetic
from experiments.fixed_rule.certify_small_holder_rom_dataflow import Checker


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--certificate',required=True);parser.add_argument('--output',required=True);args=parser.parse_args();out=Path(args.output)
    if out.exists():raise FileExistsError('preserve evidence')
    start=time.perf_counter();manifest=json.loads(Path(args.certificate).read_text())
    assert sha('experiments/fixed_rule/certify_small_holder_rom_dataflow.py')==manifest['source_sha256']
    checker=Checker(p.base_rom());verified=checker.check()
    for key in verified:assert verified[key]==manifest[key],key
    rng=random.Random(2026092642);digest=hashlib.sha256();checked=0
    for trial in range(16):
        parents=tuple(r.Cell(**{name:rng.getrandbits(width) for name,width in r.SCHEMA}) for _ in range(15))
        raw=tuple(r.lift(x) for x in parents);values=[]
        for node in checker.t.nodes:
            if node[0]=='const':value=node[1]
            elif node[0]=='input':value=getattr(raw[node[1]],node[2])
            elif node[0]=='op':value=arithmetic(node[1],values[node[2]],values[node[3]])
            elif node[0]=='rom':
                address,selector=values[node[1]],node[2]
                value=int(p.base_rom()[address,selector]) if address<len(p.base_rom()) else c.fallback(address,selector)
            else:raise AssertionError('unexpected symbolic primitive')
            values.append(value)
        for col in range(15):
            neighborhood=tuple(raw[(col+j)%15] for j in f.NEIGHBORHOOD)
            scalar=f.local_step(neighborhood);machine=native.local_step(neighborhood)
            assert scalar==machine
            expected=r.lift(r.project(scalar))
            computed=tuple(values[checker.memory[col][at]] for at in p.layout().info)
            assert computed==f.encode_cell(expected),(trial,col)
            digest.update(np.array(computed,dtype=np.uint64).tobytes());checked+=1
    paths=[Path(__file__),Path('experiments/fixed_rule/certify_small_holder_rom_dataflow.py'),Path('tests/fixed_rule/test_small_holder_rom_dataflow.py'),Path(p.__file__),Path(f.__file__),Path(native.__file__)]
    result=dict(passed=True,certificate_recomputed=True,random_full_projected_rings=16,complete_raw_outputs_checked=checked,raw_words_per_output=f.FIELDS,primitive_set=['const','input','64-bit NAND/ADD/SHR/EQ/LT','same immutable ROM lookup'],all_controller_fields_randomized=True,output_sha256=digest.hexdigest(),certificate_sha256=sha(args.certificate),source_sha256={str(path):sha(path) for path in paths},seconds=time.perf_counter()-start,host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,limitation='Audits symbolic rewrite/lookup semantics against complete independent transitions; no physical work period is executed and all-input physical instruction refinement remains an explicit premise.')
    out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))

if __name__=='__main__':main()
