"""Recheck actual retimed ROM paths through transferred local procedure lemmas.

Only proof constructors/check methods receive explicit new ROM/clock bindings.
Frozen local templates are retained: the complete clock-transfer identity
justifies their non-Age outputs at matching new clock modes. Original modules
and globals are never mutated. This is a diagnostic, not a trajectory executor.
"""
import argparse
import hashlib
import json
from pathlib import Path
import resource
import time
from types import FunctionType,SimpleNamespace

import numpy as np
from gacsca.fixed_rule import retimed_holder_rule as f,retimed_holder_core as c,retimed_holder_program as p
from experiments.fixed_rule import certify_small_holder_instruction_paths as ordinary
from experiments.fixed_rule import certify_small_holder_meta_paths as meta
from experiments.fixed_rule import certify_small_holder_dispatch_paths as dispatch
from experiments.fixed_rule import certify_small_holder_mail_schedule as old_schedule
from experiments.fixed_rule.audit_small_holder_position_events import sha


def regular_intervals():
    excluded=set(c.RESET_AGES)|set(c.VOTE_AGES)|{c.CAPTURE_AGE-1,f.U-1};result=[]
    for lo,hi in zip(c.RESET_AGES,c.ACTIVE_ENDS):
        at=lo
        for value in sorted(x for x in excluded if lo<=x<hi):
            if at<value:result.append((at,value-1))
            at=value+1
        if at<hi:result.append((at,hi-1))
    return tuple(result)


def bind(function):
    globals_=dict(function.__globals__)
    globals_.update(p=p,c=c,f=f,clock=SimpleNamespace(regular_intervals=regular_intervals))
    result=FunctionType(function.__code__,globals_,function.__name__,function.__defaults__,function.__closure__)
    result.__kwdefaults__=function.__kwdefaults__
    return result


class Ordinary(ordinary.InstructionPath):
    __init__=bind(ordinary.InstructionPath.__init__)
    check=bind(ordinary.InstructionPath.check)


class Metadata(meta.MetaPath):
    __init__=bind(meta.MetaPath.__init__)
    check=bind(meta.MetaPath.check)


class Dispatch(dispatch.DispatchPath):
    __init__=bind(dispatch.DispatchPath.__init__)
    check=bind(dispatch.DispatchPath.check)


def verify_dependencies(path):
    bridge=json.loads(Path(path).read_text())
    assert bridge['passed'] and bridge['physical_descriptor_sha256']==f.self_description().digest()
    assert bridge['legal_new_ages']==f.U and bridge['all_Ages_covered_without_sampling']
    for source,wanted in bridge['source_sha256'].items():assert sha(source)==wanted,source
    # This revalidates all baseline instruction/dispatch/local audits and packet
    # leaves. Those numerical path catalogs are not used as new-ROM results.
    old_schedule.load_inputs()
    assert f.SCHEMA==ordinary.f.SCHEMA and c.SCHEMA==ordinary.c.SCHEMA
    assert f.Q==ordinary.f.Q and c.CONTROL==ordinary.c.CONTROL
    for address in range(f.Q):
        assert all(c.fallback(address,k)==meta.c.fallback(address,k) for k in range(7))
    rom=p.base_rom();g=p.layout()
    assert np.flatnonzero(rom[:,5]).tolist()==[0]
    assert np.flatnonzero(rom[:,6]).tolist()==[len(rom)-1]
    assert np.all(rom[:g.memory_count,0]==c.MEM)
    assert np.array_equal(rom[:g.memory_count,1],np.arange(g.memory_count,dtype=np.uint64))
    return bridge


def certify(bridge_path):
    verify_dependencies(bridge_path);start=time.perf_counter();trace=hashlib.sha256();rows=[]
    for pc,op in enumerate(p.layout().instructions):
        if op.kind==c.META:continue
        for third in ((False,True) if op.kind==c.IF_THIRD else (False,)):
            path=Ordinary(pc,third=third);row=path.check()
            rows.append((pc,op.kind,int(third),row['duration'],-1 if row['final_head'] is None else row['final_head'],row['leaf_segments']))
            trace.update(json.dumps(dict(result=row,steps=path.steps),sort_keys=True).encode())
        if pc%2048==0:print(json.dumps(dict(pc=pc,ordinary_paths=len(rows),seconds=time.perf_counter()-start)),flush=True)
    L=len(p.base_rom());domains=((0,L-2),(L-1,L-1),(L,f.Q-6),(f.Q-5,f.Q-1));metadata=[]
    for pc,op in enumerate(p.layout().instructions):
        if op.kind==c.META:
            for domain in domains:
                row=Metadata(pc,domain).check();trace.update(json.dumps(row,sort_keys=True).encode())
                metadata.append({key:value for key,value in row.items() if key!='steps'})
    routes=[]
    for route in bind(dispatch.routes)({'ordinary':{'rows':rows},'meta':{'paths':metadata}}):
        row=Dispatch(route['start'],route['pc']).check()
        routes.append((route['origin'],route['origin_id'],route['start'],route['pc'],row['duration'],int(route['requires_mail_composition'])))
        trace.update(json.dumps(dict(route=route,result=row),sort_keys=True).encode())
    return dict(passed=True,ordinary_rows=rows,ordinary_path_count=len(rows),metadata_paths=metadata,
                metadata_path_count=len(metadata),dispatch_rows=routes,dispatch_path_count=len(routes),
                new_regular_clock_intervals=regular_intervals(),trace_sha256=trace.hexdigest(),
                query_domains=domains,local_lemma_transfer='Full non-Age clock-signature identity; new Age separately modulo U; actual new ROM guards and durations rechecked.',
                limitation='Conditional isolated instruction/dispatch paths, including every controller word. SEND ends at packet birth. Complete timed transport, barriers and new-ROM period execution still require composition.')


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--clock-transfer',required=True);parser.add_argument('--output',required=True);args=parser.parse_args();out=Path(args.output)
    if out.exists():raise FileExistsError('preserve evidence')
    start=time.perf_counter();result=certify(args.clock_transfer)
    result.update(physical_descriptor_sha256=f.self_description().digest(),rom_sha256=hashlib.sha256(p.base_rom().tobytes()).hexdigest(),
                  input_sha256={args.clock_transfer:sha(args.clock_transfer)},
                  source_sha256={str(path):sha(path) for path in (Path(__file__),Path(ordinary.__file__),Path(meta.__file__),Path(dispatch.__file__),Path(old_schedule.__file__),Path(p.__file__))},
                  seconds=time.perf_counter()-start,host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss)
    out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps({key:value for key,value in result.items() if key not in ('ordinary_rows','metadata_paths','dispatch_rows')},indent=2),flush=True)


if __name__=='__main__':main()
