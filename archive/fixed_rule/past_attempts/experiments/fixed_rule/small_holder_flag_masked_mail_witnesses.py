"""Saved raw two-tick physical witnesses for mail correction and Flag1 masking.

Finite radius-seven causal cones, not hierarchy macrosteps. Every transition is
literal F and independently checked against its compiled native description.
"""
import argparse
from functools import lru_cache
import hashlib
import json
from pathlib import Path
import resource
import time

import numpy as np
from gacsca.fixed_rule import small_holder_rule as f, small_holder_core as c, small_holder_native as native


def initial(*,corrupt=0,flags=False,age=1):
    @lru_cache(None)
    def cell(pos):
        words={name:0 for name,_ in f.SCHEMA}
        words.update(address=(100+pos)%f.Q,age=age,f1=int(flags and pos in (1,2,3)))
        for delta in f.STATIC_OFFSETS:words[f'p{delta+3}_index']=(100+pos+delta)%f.Q
        for delta in f.OFFSETS:
            words[f's{delta+2}_data']=7
            if pos+delta==-1:
                for suffix,value in (('target',101),('data',55),('remaining',0),('valid',1)):
                    name='rp_'+suffix
                    if pos in (-3,-2,-1)[:corrupt]:value^=(1<<dict(c.SCHEMA)[name])-1
                    words[f's{delta+2}_{name}']=value
        return f.Cell(**words)
    return cell


def physical_step(source,position):
    neighbors=tuple(source(position+j) for j in f.NEIGHBORHOOD)
    result=native.local_step(neighbors)
    assert result==f.local_step(neighbors)
    return result


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True);args=parser.parse_args();stem=Path(args.output)
    for ext in ('.json','.npz'):
        if stem.with_suffix(ext).exists():raise FileExistsError('preserve evidence')
    started=time.perf_counter();rows=[];arrays={};outputs=0
    scenarios=(('clean',0,False,1,55),('two_corrupt_copies',2,False,1,55),
               ('three_corrupt_copies',3,False,1,7),('Flag1_mask',0,True,1,7),
               ('rest_repairs_copies',2,False,c.ACTIVE_ENDS[0],7))
    old_positions=tuple(range(-13,16));first_positions=tuple(range(-6,9))
    for name,corrupt,flags,age,wanted in scenarios:
        source=initial(corrupt=corrupt,flags=flags,age=age)
        first={pos:physical_step(source,pos) for pos in first_positions}
        second=physical_step(first.__getitem__,1);outputs+=len(first)+1
        assert second.s2_data==wanted,(name,'final Data')
        target_primary=-1 if age==c.ACTIVE_ENDS[0] else 0
        copies=tuple(getattr(first[target_primary+e],f's{2-e}_rp_valid') for e in f.OFFSETS)
        if flags:assert set(copies)=={0,1}
        elif corrupt==3:assert copies==(0,)*5
        else:assert copies==(1,)*5
        expected_initial=initial(age=age)
        changed_words=flips=0
        for pos in old_positions:
            for actual,clean in zip(f.encode_cell(source(pos)),f.encode_cell(expected_initial(pos))):
                changed_words+=int(actual!=clean);flips+=(actual^clean).bit_count()
        arrays[name+'_initial']=native.array_from_cells(tuple(source(pos) for pos in old_positions))
        arrays[name+'_after_one']=native.array_from_cells(tuple(first[pos] for pos in first_positions))
        arrays[name+'_after_two']=native.array_from_cells((second,))
        rows.append(dict(name=name,initial_age=age,corrupted_mail_copies=corrupt,initial_Flag1_positions=[1,2,3] if flags else [],
                         altered_raw_words=changed_words,initial_bit_flips=flips,
                         first_step_packet_primary=target_primary,first_step_valid_replicas=copies,
                         final_primary=1,final_Data=second.s2_data,final_Age=second.age))
    arrays.update(initial_positions=np.array(old_positions,dtype=np.int64),after_one_positions=np.array(first_positions,dtype=np.int64),after_two_positions=np.array([1],dtype=np.int64))
    np.savez_compressed(stem.with_suffix('.npz'),**arrays)
    paths=[Path(__file__),Path(f.__file__),Path(c.__file__),Path(native.__file__)]
    result=dict(passed=True,cases=rows,complete_raw_words_per_cell=f.FIELDS,complete_scalar_native_outputs=outputs,
                physical_ticks_per_case=2,descriptor_sha256=f.self_description().digest(),
                source_sha256={str(path):hashlib.sha256(path.read_bytes()).hexdigest() for path in paths},
                artifact_sha256=hashlib.sha256(stem.with_suffix('.npz').read_bytes()).hexdigest(),
                seconds=time.perf_counter()-started,host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                limitation='Five finite raw causal-cone witnesses. Two physical ticks, not two hierarchy levels. No stochastic noise law or cross-level suppression claim.')
    stem.with_suffix('.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2),flush=True)


if __name__=='__main__':main()
