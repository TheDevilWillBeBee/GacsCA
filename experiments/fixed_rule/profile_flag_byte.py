"""Bounded allocation/error diagnostic of the unchanged native flag evaluator."""
import argparse
import ctypes
import hashlib
import json
from pathlib import Path
import resource
import subprocess
import time
import numpy as np
from gacsca.fixed_rule.flag_byte_native import pointer
from gacsca.fixed_rule.delivery_rule import Q


def execute(checkpoint,ticks,limit,output):
    output=Path(output)
    if output.exists():raise FileExistsError('preserve evidence')
    root=Path(__file__).resolve().parents[2];source=root/'gacsca/fixed_rule/flag_byte_profile.cpp';dependency=root/'gacsca/fixed_rule/flag_byte_native.cpp'
    digest=hashlib.sha256(source.read_bytes()+dependency.read_bytes()).hexdigest();build=root/'figs/fixed_rule/build'/('flag_profile_'+digest[:16]);build.mkdir(parents=True,exist_ok=True);target=build/'flags.so'
    if not target.exists():subprocess.run(['c++','-O3','-std=c++17','-Wall','-Wextra','-Werror','-shared','-fPIC',str(source),'-o',str(target)],check=True)
    lib=ctypes.CDLL(str(target));ptr=ctypes.POINTER(ctypes.c_uint64)
    lib.profile_evolve.argtypes=[ptr,ctypes.c_size_t,ctypes.c_size_t,ctypes.c_uint64,ctypes.c_uint32];lib.profile_evolve.restype=ctypes.c_void_p
    lib.profile_status.argtypes=[ptr];lib.profile_status.restype=ctypes.c_int;lib.profile_error.restype=ctypes.c_char_p;lib.fh_free.argtypes=[ctypes.c_void_p]
    with np.load(checkpoint,allow_pickle=False) as a:runs=a['runs'];colonies=len(a['right_signals'])
    # Load dependencies first. Keep enough address space for Python itself.
    resource.setrlimit(resource.RLIMIT_CORE,(0,0));resource.setrlimit(resource.RLIMIT_AS,(limit*1024**2,limit*1024**2))
    started=time.monotonic();handle=lib.profile_evolve(pointer(runs),len(runs),colonies,98*Q,ticks);elapsed=time.monotonic()-started
    metrics=np.zeros(8,dtype=np.uint64);code=lib.profile_status(pointer(metrics));error=lib.profile_error().decode()
    if handle:lib.fh_free(handle)
    result=dict(success=bool(handle),code=code,error=error,ticks=ticks,limit_mib=limit,seconds=elapsed,metrics=dict(zip(('nodes','node_capacity','queries','query_capacity','intern_used','intern_capacity','leaf_evaluations','period_bytes'),map(int,metrics))),source_sha256={str(path.relative_to(root)):hashlib.sha256(path.read_bytes()).hexdigest() for path in (source,dependency,Path(__file__).resolve())},checkpoint_sha256=hashlib.sha256(Path(checkpoint).read_bytes()).hexdigest())
    output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--input',required=True);p.add_argument('--ticks',required=True,type=int);p.add_argument('--limit-mib',type=int,default=2048);p.add_argument('--output',required=True);a=p.parse_args();execute(a.input,a.ticks,a.limit_mib,a.output)
