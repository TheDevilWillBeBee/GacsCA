"""Private exact event-output slicing and scalar SSA CUDA emission.

The physical descriptor, ROM, neighborhood and event scheduling are unchanged.
Only independent/gather event calls use this emitter. Synchronous boundary steps
still use the frozen complete expression. No simulated transition runs on host.
"""
import ctypes
from functools import lru_cache
import hashlib
from pathlib import Path
import subprocess
import numpy as np
from . import small_holder_core as c, small_holder_rule as f
from . import small_holder_resident_period as period
from . import small_holder_resident_independent as independent
from . import small_holder_resident_gather as gather
from .small_holder_prefix_description import build
from .word_prune import prune
from .wordcode import Program, LIT, NAND, ADD, SHR, EQ, LT

EVENT_FIELDS = ('data', 'head', *c.CONTROL,
                *(n for n, _ in c.SCHEMA if n.startswith(('lp_', 'rp_'))))


@lru_cache(maxsize=1)
def event_program():
    original = build()
    return prune(Program(original.inputs, original.operations,
                         tuple(original.outputs[c.COL[n]] for n in EVENT_FIELDS)))


def scalar_source(program, name, *, stride=1, destinations=None):
    """Pure ordered-DAG emission. All intermediates retain uint64_t semantics."""
    if type(stride) is not int or stride < 1:
        raise ValueError('positive integral stride required')
    if destinations is None:
        destinations = tuple(range(len(program.outputs)))
    if len(destinations) != len(program.outputs) or any(type(k) is not int or k < 0 for k in destinations):
        raise ValueError('one nonnegative destination per output required')
    def ref(w):
        if not 0 <= w < program.wires:
            raise ValueError('invalid wire')
        return f'in[{w*stride}]' if w < program.inputs else f'v{w-program.inputs}'
    lines = [f'__device__ __noinline__ void {name}(const uint64_t *in, uint64_t *out, uint64_t *unused) {{']
    for i, (op, a, b) in enumerate(program.operations):
        if op != LIT and not (0 <= a < program.inputs+i and 0 <= b < program.inputs+i):
            raise ValueError('ordered expression required')
        aa, bb = (ref(a), ref(b)) if op != LIT else ('', '')
        if op == LIT: expr = f'UINT64_C(0x{a:016x})'
        elif op == NAND: expr = f'~({aa}&{bb})'
        elif op == ADD: expr = f'{aa}+{bb}'
        elif op == SHR: expr = f'{bb}<64?{aa}>>{bb}:0'
        elif op == EQ: expr = f'{aa}=={bb}'
        elif op == LT: expr = f'{aa}<{bb}'
        else: raise ValueError('unsupported operation')
        lines.append(f' const uint64_t v{i} = {expr};')
    lines.extend(f' out[{k*stride}] = {ref(w)};' for k, w in zip(destinations, program.outputs))
    return '\n'.join(lines + ['}']) + '\n'


@lru_cache(maxsize=1)
def library():
    original = Path(period.__file__).with_suffix('.cu').read_text()
    guard = 'if(suffix&&(left||right!=((sig(w,Q-3)>>2)&1)))return false;'
    if original.count(guard) != 1:
        raise AssertionError('frozen mixed-Signal guard changed')
    original = original.replace(guard, 'if(suffix&&left)return false;')
    sources = {'small_holder_resident_period.cu': original}
    for module in (independent, gather):
        source = Path(module.__file__).with_suffix('.cu')
        text = source.read_text()
        call = 'resident_prefix_local(in,out,tmp);++evaluations;'
        if text.count(call) != 1:
            raise AssertionError('review changed event call sites')
        sources[source.name] = text.replace(call, 'register_event_local(in,out,tmp);++evaluations;')
    sources['small_holder_resident_period_generated.h'] = period.header() + scalar_source(
        event_program(), 'register_event_local', stride=period.WORKERS,
        destinations=tuple(c.COL[n] for n in EVENT_FIELDS))
    identity = hashlib.sha256(('nvcc-O2-sm80-register-events-v1'+''.join(k+v for k,v in sorted(sources.items()))).encode()).hexdigest()[:20]
    directory = Path(__file__).resolve().parents[2]/'figs/fixed_rule/build'/('small_holder_register_events_'+identity)
    directory.mkdir(parents=True, exist_ok=True)
    target = directory/'events.so'
    if not target.exists():
        for name, text in sources.items():
            (directory/name).write_text(text)
        with (directory/'build.log').open('w') as log:
            subprocess.run(['/usr/local/cuda/bin/nvcc','-O2','-std=c++17','-arch=sm_80','--shared','-Xcompiler','-fPIC','--ptxas-options=-v',str(directory/'small_holder_resident_gather.cu'),'-o',str(target)], stdout=log, stderr=subprocess.STDOUT, check=True)
    lib = ctypes.CDLL(str(target))
    for name in ('rp_create','rp_free','rp_info','rp_initial','rp_bank','rp_restore_age','rp_jump','rp_step','rp_read'):
        new, old = getattr(lib,name), getattr(period.library(),name)
        new.argtypes, new.restype = old.argtypes, old.restype
    for name in ('ri_run','rg_run'):
        new = getattr(lib,name)
        new.argtypes, new.restype = independent.library().ri_run.argtypes, ctypes.c_int
    return lib


class World(gather.World):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        try: self.lib = library()
        except BaseException: self.close(); raise

    @classmethod
    def from_raw_chunks(cls,*args,**kwargs):
        world = super().from_raw_chunks(*args,**kwargs)
        try: world.lib = library(); return world
        except BaseException: world.close(); raise

    def batch(self,ticks,*,event_budget=200000,extra_device_budget=64*1024**2):
        if not self.handle: raise ValueError('closed resident world')
        before = self.age < c.VOTE_AGES[0]
        if type(ticks) is not int or not 0 < ticks < 1<<32 or (before and ticks > 8*f.Q):
            raise ValueError('bounded physical event interval required')
        if type(event_budget) is not int or not 0 < event_budget <= 1000000:
            raise ValueError('bounded event budget required')
        if type(extra_device_budget) is not int or not 0 < extra_device_budget <= 8*1024**3:
            raise ValueError('bounded extra device budget required')
        metrics = np.zeros(4,dtype=np.uint64)
        run = self.lib.rg_run if before else self.lib.ri_run
        code = run(self.handle,ticks,event_budget,extra_device_budget,period.pointer(metrics))
        if code: raise independent.BatchRejected(code)
        self.age += ticks; self.time += ticks; self.evaluations += int(metrics[3])
        return dict(physical_ticks=ticks,colony_literal_ticks=int(metrics[0]),
                    max_colony_literal_ticks=int(metrics[1]),
                    colony_transport_or_quiet_ticks=self.colonies*ticks-int(metrics[0]),
                    extra_device_bytes=int(metrics[2]),logical_evaluations=int(metrics[3]))
