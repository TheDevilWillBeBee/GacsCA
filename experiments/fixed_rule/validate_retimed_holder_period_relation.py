"""Bounded-memory entry relation validation and literal first-reset witnesses."""
import argparse
import hashlib
import json
from pathlib import Path
import random
import resource
import time

from gacsca.fixed_rule import retimed_holder_rule as f, retimed_holder_core as c, retimed_holder_projected as r
from gacsca.fixed_rule import retimed_holder_program as p, retimed_holder_period_relation as relation, retimed_holder_native as native
from experiments.fixed_rule.audit_small_holder_position_events import sha


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True);args=parser.parse_args();out=Path(args.output)
    if out.exists():raise FileExistsError('preserve evidence')
    start=time.perf_counter();rng=random.Random(2026092613)
    parent=r.Cell(**{name:rng.getrandbits(width) for name,width in r.SCHEMA})
    def upper(col):assert col==0;return parent
    def scratch(position):return (((position+1)*0x9E3779B97F4A7C15)^0x123456789ABCDEF0) & ((1<<64)-1)
    def read(position):
        return relation.encode_at(upper,1,position,scratch=scratch,signal=lambda i:(17*i+3)%32)
    layout=relation.layout_obligations();ring=relation.validate_ring(read,1,parent=upper)
    assert relation.decode_colony(read,1,0)==parent
    addresses=sorted({0,1,5,p.layout().memory_count-1,p.layout().memory_count,len(p.base_rom())-1,
                      len(p.base_rom()),f.Q-5,f.Q-1,*p.layout().info,*p.layout().hold})
    digest=hashlib.sha256()
    for address in addresses:
        cells=tuple(read((address+j)%f.Q) for j in f.NEIGHBORHOOD)
        actual=f.local_step(cells);assert actual==native.local_step(cells)
        assert actual.address==address and actual.age==1 and not actual.f1 and not actual.f2
        for delta in f.OFFSETS:
            site=(address+delta)%f.Q;record=r.record(site)
            wanted=f.encode_cell(r.lift(parent))[relation.info_fields()[site]] if site in relation.info_fields() else 0
            assert getattr(actual,f's{delta+2}_data')==wanted,('first reset Data',address,delta)
            assert getattr(actual,f's{delta+2}_head')==int(site==0)
            assert getattr(actual,f's{delta+2}_pc')==(p.layout().entries[0] if site==0 else 0)
            for name in c.CONTROL:
                if name!='pc':assert getattr(actual,f's{delta+2}_{name}')==0
        digest.update(json.dumps(f.encode_cell(actual)).encode())
    result=dict(passed=True,layout=layout,full_ring=ring,first_reset_complete_scalar_native_outputs=len(addresses),
                represented_raw_fields=f.FIELDS,represented_projected_fields=len(r.SCHEMA),
                nonzero_initial_scratch=True,nonzero_retained_Signals=True,output_sha256=digest.hexdigest(),
                descriptor_sha256=f.self_description().digest(),source_sha256={str(path):sha(path) for path in (Path(__file__),Path(relation.__file__),Path(native.__file__))},
                seconds=time.perf_counter()-start,host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                limitation='Complete one-colony entry validation and selected literal first-reset outputs. No evolution of an entire work period, second level or noisy hierarchy.')
    out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2),flush=True)


if __name__=='__main__':main()
