"""Complete raw audit and saved literal capture/next-tick Signal witnesses."""
import argparse
from dataclasses import replace
import hashlib
import json
from pathlib import Path
import random
import resource
import time

import numpy as np
from gacsca.fixed_rule import small_holder_rule as f, small_holder_core as c, small_holder_native as native
from experiments.fixed_rule import certify_small_holder_signal_flag_boundaries as proof
from experiments.fixed_rule.audit_small_holder_clock_mail_factorization import ages
from experiments.fixed_rule.audit_small_holder_position_events import evaluate,sha


def capture_fixture(target,pattern,rng):
    cells={}
    for pos in range(-16,17):
        fields={name:rng.getrandbits(width) for name,width in f.SCHEMA}
        fields.update(address=(target+pos)%f.Q,age=c.CAPTURE_AGE-1)
        # Explicit initial Data replicas; all other raw fields remain arbitrary.
        for delta in f.OFFSETS:
            primary=pos+delta
            bit=(pattern>>(primary+2))&1 if -2<=primary<=2 else 0
            fields[f's{delta+2}_data']=bit
        cells[pos]=f.Cell(**fields)
    return cells


def capture_witness(target,pattern,rng):
    initial=capture_fixture(target,pattern,rng);first={};second={};count=0
    for before,after,positions in ((initial,first,range(-9,10)),(first,second,range(-2,3))):
        for pos in positions:
            neighbors=tuple(before[pos+j] for j in f.NEIGHBORHOOD)
            result=f.local_step(neighbors);assert result==native.local_step(neighbors)
            after[pos]=result;count+=1
    first_bits=[(first[e].signal>>(2-e))&1 for e in f.OFFSETS]
    assert first_bits==[(pattern>>(e+2))&1 for e in f.OFFSETS]
    final_bits=[(second[e].signal>>(2-e))&1 for e in f.OFFSETS]
    assert final_bits==[int(pattern.bit_count()>=3)]*5
    arrays={name:native.array_from_cells(tuple(cells[pos] for pos in sorted(cells)))
            for name,cells in (('initial',initial),('after_capture',first),('after_vote',second))}
    return dict(target=target,initial_pattern=pattern,captured_bits=first_bits,next_bits=final_bits,
                complete_outputs=count),arrays


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--certificate',required=True);parser.add_argument('--output',required=True)
    args=parser.parse_args();out=Path(args.output)
    for suffix in ('.json','.npz'):
        if out.with_suffix(suffix).exists():raise FileExistsError('preserve evidence')
    start=time.perf_counter();cert=json.loads(Path(args.certificate).read_text())
    assert cert['passed'] and cert['descriptor_sha256']==f.self_description().digest()
    for path,wanted in cert['source_sha256'].items():assert sha(path)==wanted,path
    t,raw,_,expected=proof.prepare();rows=[raw(pos) for pos in f.NEIGHBORHOOD];wanted=expected(0)
    rng=random.Random(2026092611);count=0;digest=hashlib.sha256()
    addresses=(0,1,2,3,4,5,f.Q//2,f.Q-6,f.Q-5,f.Q-3,f.Q-1)
    for age in ages():
        for address in addresses:
            for mode in ('raw','zero_wf','zero_flags_wf'):
                values={node[1]:rng.getrandbits(node[2]) for node in t.nodes if node[0]=='variable'}
                values.update(base_address=address,physical_age=age)
                if mode!='raw':
                    for name in values:
                        if name.startswith('raw_'):
                            field=name.split('_',2)[2]
                            if field.startswith('w') or (mode=='zero_flags_wf' and field in ('f1','f2')):values[name]=0
                evaluated=evaluate(t,values)
                cells=tuple(f.decode_cell(tuple(evaluated[x] for x in row)) for row in rows)
                actual=f.local_step(cells);assert actual==native.local_step(cells)
                for name,term in wanted.items():assert getattr(actual,name)==evaluated[term],(age,address,mode,name)
                if mode=='zero_flags_wf':assert actual.f1==actual.f2==0
                digest.update(native.array_from_cells((actual,)).tobytes());count+=1
    witnesses=[];arrays={}
    for target in (3,f.Q-3):
        for pattern in range(32):
            row,states=capture_witness(target,pattern,rng);witnesses.append(row)
            arrays.update({f'{target}_{pattern}_{name}':data for name,data in states.items()})
    np.savez_compressed(out.with_suffix('.npz'),**arrays)
    result=dict(passed=True,boundary_complete_scalar_native_outputs=count,
                capture_complete_scalar_native_outputs=sum(row['complete_outputs'] for row in witnesses),
                capture_witnesses=witnesses,physical_ticks_per_witness=2,
                boundary_output_sha256=digest.hexdigest(),artifact_sha256=sha(out.with_suffix('.npz')),
                certificate_sha256=sha(args.certificate),source_sha256={str(path):sha(path) for path in (Path(__file__),Path(proof.__file__),Path(native.__file__))},
                seconds=time.perf_counter()-start,host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                limitation='Finite full-state audits and two literal physical ticks at capture; arbitrary raw metadata/controller fields, not fixed-ROM program trajectories. Does not establish the program delivers correct buffers or nested/noise correctness.')
    out.with_suffix('.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='capture_witnesses'},indent=2),flush=True)


if __name__=='__main__':main()
