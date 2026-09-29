"""Replay saved raw witnesses and execute their fixed-ROM projected variants."""
import argparse
import hashlib
import json
from pathlib import Path
import resource
import time

import numpy as np
from gacsca.fixed_rule import small_holder_rule as f, small_holder_projected as r, small_holder_native as native
from experiments.fixed_rule.audit_small_holder_position_events import sha


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--execution',required=True);parser.add_argument('--output',required=True)
    args=parser.parse_args();source=Path(args.execution);out=Path(args.output)
    for ext in ('.json','.npz'):
        if out.with_suffix(ext).exists():raise FileExistsError('preserve evidence')
    started=time.perf_counter();run=json.loads(source.with_suffix('.json').read_text())
    assert run['passed'] and run['descriptor_sha256']==f.self_description().digest()
    for path,wanted in run['source_sha256'].items():assert sha(path)==wanted,path
    assert sha(source.with_suffix('.npz'))==run['artifact_sha256']
    records={};cases=[];raw_outputs=projected_outputs=0
    with np.load(source.with_suffix('.npz'),allow_pickle=False) as saved:
        old_positions=tuple(map(int,saved['initial_positions']))
        first_positions=tuple(map(int,saved['after_one_positions']))
        second_positions=tuple(map(int,saved['after_two_positions']))
        assert old_positions==tuple(range(-13,16)) and first_positions==tuple(range(-6,9)) and second_positions==(1,)
        for row in run['cases']:
            name=row['name'];old=dict(zip(old_positions,native.cells_from_array(saved[name+'_initial'])))
            first=dict(zip(first_positions,native.cells_from_array(saved[name+'_after_one'])))
            second=dict(zip(second_positions,native.cells_from_array(saved[name+'_after_two'])))
            for before,after in ((old,first),(first,second)):
                for position,wanted in after.items():
                    neighbors=tuple(before[position+j] for j in f.NEIGHBORHOOD)
                    result=f.local_step(neighbors);assert result==native.local_step(neighbors)==wanted
                    raw_outputs+=1
            # Host projection here defines a different initial fixture only.
            # All subsequent states are literal physical F outputs, never relifted.
            normalized={position:r.lift(r.project(cell)) for position,cell in old.items()}
            first_rom={};second_rom={}
            for before,after,positions,reference in ((normalized,first_rom,first_positions,first),(first_rom,second_rom,second_positions,second)):
                for position in positions:
                    neighbors=tuple(before[position+j] for j in f.NEIGHBORHOOD)
                    result=f.local_step(neighbors);assert result==native.local_step(neighbors)
                    assert result==r.lift(r.project(result)),('ROM consistency lost',name,position)
                    assert r.project(result)==r.project(reference[position]),('dynamic effect changed',name,position)
                    after[position]=result;projected_outputs+=1
            assert second_rom[1].s2_data==row['final_Data']
            records[name+'_initial']=native.array_from_cells(tuple(normalized[pos] for pos in old_positions))
            records[name+'_after_one']=native.array_from_cells(tuple(first_rom[pos] for pos in first_positions))
            records[name+'_after_two']=native.array_from_cells(tuple(second_rom[pos] for pos in second_positions))
            cases.append(dict(row,fixed_ROM_preserved_after_each_tick=True,projected_dynamic_effect_matches=True))
    assert raw_outputs==projected_outputs==run['complete_scalar_native_outputs']
    records.update(initial_positions=np.array(old_positions,dtype=np.int64),after_one_positions=np.array(first_positions,dtype=np.int64),after_two_positions=np.array(second_positions,dtype=np.int64))
    np.savez_compressed(out.with_suffix('.npz'),**records)
    paths=[Path(__file__),Path(r.__file__),Path(f.__file__),Path(native.__file__)]
    result=dict(passed=True,cases=cases,original_full_raw_outputs_replayed=raw_outputs,fixed_ROM_full_raw_outputs_executed=projected_outputs,
                complete_raw_words_per_cell=f.FIELDS,physical_ticks_per_case=2,descriptor_sha256=f.self_description().digest(),
                execution_manifest_sha256=sha(source.with_suffix('.json')),execution_artifact_sha256=sha(source.with_suffix('.npz')),
                source_sha256={str(path):sha(path) for path in paths},artifact_sha256=sha(out.with_suffix('.npz')),
                seconds=time.perf_counter()-started,host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                limitation='Independent saved-state replay plus actual fixed-ROM initialized local causal cones. Two physical ticks per case, not two hierarchy levels or a noise threshold.')
    out.with_suffix('.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2),flush=True)


if __name__=='__main__':main()
