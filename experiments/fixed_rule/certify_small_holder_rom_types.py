"""Finite typing proof for the fixed hard-wired metadata and its fallback."""
import argparse
import hashlib
import json
from pathlib import Path
import resource
import time

from gacsca.fixed_rule import small_holder_core as c, small_holder_rule as f
from gacsca.fixed_rule import small_holder_projected as r, small_holder_program as p
from experiments.fixed_rule.audit_small_holder_position_events import sha


def check(record=r.record):
    widths=dict(c.SCHEMA);maximum={name:0 for name in c.STATIC}
    for address in range(f.Q):
        row=record(address)
        for name in c.STATIC:
            value=row[name]
            assert isinstance(value,int) and 0<=value<1<<widths[name],('ROM value outside alphabet',address,name,value)
            maximum[name]=max(maximum[name],value)
    return dict(passed=True,addresses=f.Q,values_checked=f.Q*len(c.STATIC),maximum=maximum,
                all_seven_Address_offset_records_typed=True)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True);args=parser.parse_args();out=Path(args.output)
    if out.exists():raise FileExistsError('preserve evidence')
    start=time.perf_counter();result=check()
    for name in c.STATIC:
        def invalid(address):
            row=dict(r.record(address))
            if address==f.Q-1:row[name]=1<<dict(c.SCHEMA)[name]
            return row
        try:check(invalid)
        except AssertionError:pass
        else:raise AssertionError(('overwide metadata mutation accepted',name))
    result.update(rejected_overwide_field_mutations=len(c.STATIC),
                  rom_sha256=hashlib.sha256(p.base_rom().tobytes()).hexdigest(),
                  source_sha256={str(path):sha(path) for path in (Path(__file__),Path(r.__file__),Path(p.__file__),Path(c.__file__))},
                  seconds=time.perf_counter()-start,host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2),flush=True)


if __name__=='__main__':main()
