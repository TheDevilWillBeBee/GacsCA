"""Independent emitted-C differential and frozen trajectory provenance audit.

This audits expression compilation and complete-checkpoint evidence. It does not
claim a theorem for arbitrary noisy resident states or replay the full trajectory.
"""
import argparse
import ctypes
import hashlib
import json
from pathlib import Path
import random
import re
import resource
import subprocess
import time
import numpy as np
from gacsca.fixed_rule import small_holder_register_events as reg
from gacsca.fixed_rule import small_holder_supported_events as sup
from gacsca.fixed_rule import small_holder_core as c, small_holder_rule as f
from gacsca.fixed_rule import small_holder_program as rom
from gacsca.fixed_rule.small_holder_prefix_description import build
from gacsca.fixed_rule.wordcode import LIT


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def terms(program):
    """Hash-consing-free structural signatures of the ordered expression DAG."""
    values=[hashlib.sha256(f'input:{i}'.encode()).digest() for i in range(program.inputs)]
    for op,a,b in program.operations:
        term=f'literal:{a}'.encode() if op==LIT else str(op).encode()+b':'+values[a]+values[b]
        values.append(hashlib.sha256(term).digest())
    return tuple(values[w].hex() for w in program.outputs)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--register-result',required=True);parser.add_argument('--supported-result',required=True);parser.add_argument('--output',required=True);args=parser.parse_args()
    out=Path(args.output)
    if out.exists():raise FileExistsError('preserve evidence')
    started=time.perf_counter();original=build();sliced=reg.event_program()
    assert terms(sliced)==tuple(terms(original)[c.COL[n]] for n in reg.EVENT_FIELDS)
    loaded=tuple(map(int,re.findall(r'in\[(\d+)\]=',sup.input_source())))
    assert loaded==tuple(i*256 for i in sup.support())
    used=set(sup.support());rng=random.Random(2026092631)
    emitted=reg.scalar_source(sliced,'event',destinations=tuple(c.COL[n] for n in reg.EVENT_FIELDS)).replace('__device__ __noinline__','extern "C"')
    source='#include <stdint.h>\n'+emitted
    codehash=hashlib.sha256(source.encode()).hexdigest()
    directory=Path('figs/fixed_rule/build')/('event_emission_audit_'+codehash[:20]);directory.mkdir(parents=True,exist_ok=True)
    target=directory/'audit.so'
    if not target.exists():
        (directory/'audit.cpp').write_text(source)
        subprocess.run(['g++','-O2','-std=c++17','-shared','-fPIC',str(directory/'audit.cpp'),'-o',str(target)],check=True)
    lib=ctypes.CDLL(str(target));pointer=ctypes.POINTER(ctypes.c_uint64)
    lib.event.argtypes=[pointer,pointer,pointer];lib.event.restype=None
    sentinel=0x12349876ABCDEF01;trace=hashlib.sha256();count=0
    ages=tuple(sorted({0,1,c.U-1,*(max(0,a-1) for a in (*c.RESET_AGES,*c.ACTIVE_ENDS,*c.VOTE_AGES)),*c.RESET_AGES,*c.ACTIVE_ENDS,*c.VOTE_AGES,c.CAPTURE_AGE-1,c.WF_START,c.WF_END}))
    for trial in range(1024):
        words=np.array([rng.getrandbits(w) for _ in range(11) for _,w in c.SCHEMA],dtype=np.uint64)
        # Exercise clock boundaries explicitly as well as arbitrary local states.
        if trial%2==0:
            for row in range(11):words[row*c.FIELDS+c.COL['age']]=ages[(trial//2)%len(ages)]
        expected=original.evaluate(words)
        for poison in (False,True):
            if poison:
                for i in range(len(words)):
                    if i not in used:words[i]=rng.getrandbits(64)
            result=np.full(c.FIELDS+2,sentinel,dtype=np.uint64)
            lib.event(words.ctypes.data_as(pointer),result[1:].ctypes.data_as(pointer),None)
            wanted=np.full(c.FIELDS+2,sentinel,dtype=np.uint64)
            for name in reg.EVENT_FIELDS:wanted[1+c.COL[name]]=expected[c.COL[name]]
            np.testing.assert_array_equal(result,wanted)
            trace.update(result.tobytes());count+=1
    records=[]
    for path,module in ((args.register_result,reg),(args.supported_result,sup)):
        row=json.loads(Path(path).read_text());assert row['passed']
        for file,wanted in row['source_sha256'].items():assert digest(file)==wanted,file
        assert digest(module.library()._name)==row['binary_sha256']
        assert row['descriptor_sha256']==f.self_description().digest()
        assert row['rom_sha256']==hashlib.sha256(rom.base_rom().tobytes()).hexdigest()
        assert row['event_expression_sha256']==sliced.digest()
        assert row['metrics']['physical_ticks']==2*c.U
        assert sum(x['ticks'] for x in row['intervals'])==2*c.U
        for cp in row['checkpoints']:assert cp['all_decoded_fields_match'] and cp['complete_physical_checkpoint_matches']
        records.append(dict(path=path,sha256=digest(path),gpu_seconds=row['gpu_seconds'],speedup=row['speedup']))
    a=json.loads(Path(args.register_result).read_text());b=json.loads(Path(args.supported_result).read_text())
    assert a['metrics']==b['metrics']
    assert [(x['stored_sha256'],x['gap_sha256']) for x in a['checkpoints']]==[(x['stored_sha256'],x['gap_sha256']) for x in b['checkpoints']]
    paths=[Path(__file__),Path(reg.__file__),Path(sup.__file__),Path('experiments/fixed_rule/small_holder_supported_periods.py'),Path('tests/fixed_rule/test_small_holder_register_events.py'),Path('tests/fixed_rule/test_small_holder_supported_events.py')]
    result=dict(passed=True,structurally_identical_selected_outputs=True,event_fields=list(reg.EVENT_FIELDS),input_words=len(sup.support()),original_input_words=original.inputs,original_operations=len(original.operations),sliced_operations=len(sliced.operations),compiled_C_comparisons=count,arbitrary_and_boundary_neighborhoods=1024,unused_inputs_poisoned=True,untouched_output_words_and_canaries=True,output_sha256=trace.hexdigest(),records=records,compiler_binary_sha256=digest(target),emitted_source_sha256=codehash,seconds=time.perf_counter()-started,host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,source_sha256={str(path):digest(path) for path in paths},limitation='CPU compilation independently checks expression emission; GPU complete-trajectory equality is checked by the hashed drivers, not independently replayed by this audit; this is not a general resident-domain or noise theorem')
    out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))

if __name__=='__main__':main()
