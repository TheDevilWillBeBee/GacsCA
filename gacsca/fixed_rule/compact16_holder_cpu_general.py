"""Complete physical CPU events with both Signal sides and arbitrary raw flags.

Canonical geometry, coherent procedures/Signals and derived Wf remain required.
Physical flags evolve by the exact packed recurrence, without a front ansatz.
Nonzero-flag/forcing intervals reject packets; no physical rule is changed.
"""
import ctypes
from dataclasses import replace
from functools import lru_cache
import hashlib
from pathlib import Path
import subprocess

import numpy as np

from . import compact16_holder_cpu_boundary as boundary, compact16_holder_cpu_events as base
from . import compact16_holder_flags_cpu as flags_cpu, compact16_holder_native as native
from . import compact16_holder_rule as f, compact16_holder_core as c


def source():
    old = base.source(); marker = 'extern "C" int run_events('
    assert old.count(marker) == 1
    header = old[:old.index(marker)]
    values = dict(RAW_ADDRESS=f.COL['address'], RAW_AGE=f.COL['age'], RAW_F1=f.COL['f1'],
                  RAW_F2=f.COL['f2'], RAW_SIGNAL=f.COL['signal'], PERIOD=f.U,
                  WF_START=f.WF_START, WF_END=f.WF_END, CAPTURE=c.CAPTURE_AGE)
    for name, value in values.items():
        header += f'\n#define {name} UINT64_C({value})\n'
    for name in ('wf1', 'wf2'):
        header += 'static const int RAW_'+name.upper()+'[]={'+','.join(str(f.COL[f'w{k}_{name}']) for k in range(5))+'};\n'
    return header + Path(__file__).with_suffix('.cpp').read_text()


@lru_cache(None)
def library():
    text = source(); digest = hashlib.sha256((text+f.self_description().digest()+'cpu-general-O2-v1').encode()).hexdigest()[:20]
    directory = Path(__file__).resolve().parents[2]/'figs/fixed_rule/build'/('compact16_holder_cpu_general_'+digest)
    directory.mkdir(parents=True, exist_ok=True)
    cpp, target = directory/'general.cpp', directory/'general.so'
    if cpp.exists():
        assert cpp.read_text() == text
    else:
        cpp.write_text(text)
    if not target.exists():
        with (directory/'build.log').open('w') as log:
            subprocess.run(['c++', '-O2', '-std=c++17', '-Wall', '-Wextra', '-Werror', '-shared', '-fPIC', str(cpp), '-o', str(target)], stdout=log, stderr=subprocess.STDOUT, check=True)
    lib = ctypes.CDLL(str(target)); ptr = ctypes.c_void_p; u = ctypes.c_uint64
    lib.general_step.argtypes = [ptr]*5+[u,u]+[ptr]*9
    lib.general_step.restype = ctypes.c_int
    return lib


def pack_runs(flags):
    """Lossless physical-word run compression; no dynamical assumption."""
    rows = []; old = None
    for index, pair in enumerate(flags):
        pair = tuple(map(int, pair))
        if pair == old:
            rows[-1] = (index+1, *pair)
        else:
            rows.append((index+1, *pair)); old = pair
    return rows


class World(boundary.World):
    def __init__(self, *args, right=None, left=None, flags=None, **kwargs):
        super().__init__(*args, **kwargs)
        def signal(value):
            value = tuple([0]*self.n if value is None else value)
            if len(value) != self.n or any(v not in (0,1) for v in value):
                raise ValueError('one coherent Boolean Signal per colony and side required')
            return np.array(value, dtype=np.uint64)
        self.right, self.left = signal(right), signal(left)
        shape = (self.n*f.Q//64, 2)
        if flags is None:
            flags = np.zeros(shape, dtype=np.uint64)
        if not isinstance(flags, np.ndarray) or flags.dtype != np.uint64 or flags.shape != shape:
            raise ValueError('complete packed raw Flag1/Flag2 words required')
        self.flags = flags.copy()
        if len(self.packets) and (np.any(self.flags) or c.WF_START-1 <= self.age < c.WF_END+f.Q):
            raise ValueError('mail must be absent in nonzero-flag/forcing domain')

    def _flags_after(self, ticks):
        with flags_cpu.World(tuple(map(int, self.right)), tuple(map(int, self.left)),
                             age=self.age, runs=pack_runs(self.flags)) as world:
            metrics = world.run(ticks)
            result = np.empty_like(self.flags); start = 0
            for end, one, two in world.runs:
                result[start:int(end)] = (one, two); start = int(end)
        return result, {('flag_'+key):metrics[key] for key in ('literal_ticks','quiet_ticks','word_evaluations')}

    def step(self):
        if len(self.packets):
            raise ValueError('literal boundary step requires empty old mail')
        data = np.empty_like(self.data); heads = np.zeros_like(self.heads)
        where = np.zeros_like(self.where); right = np.empty_like(self.right)
        left = np.empty_like(self.left); flags = np.empty_like(self.flags)
        function = ctypes.cast(native.library().compact16_holder_local, ctypes.c_void_p)
        arrays = (self.right,self.left,self.flags,data,heads,where,right,left,flags)
        code = library().general_step(function, base.rom().ctypes.data, self.data.ctypes.data,
                                      self.heads.ctypes.data, self.where.ctypes.data, self.n, self.age,
                                      *(a.ctypes.data for a in arrays))
        if code:
            raise RuntimeError(f'physical general-context domain rejected ({code}); state unchanged')
        self.data,self.heads,self.where,self.right,self.left,self.flags = data,heads,where,right,left,flags
        self.age = (self.age+1)%f.U; self.time += 1
        return dict(physical_ticks=1, full_raw_evaluations=self.n*f.Q)

    def advance(self, ticks, **kwargs):
        unsafe = bool(np.any(self.flags)) or (self.age < c.WF_END+f.Q and self.age+ticks > c.WF_START-1)
        if unsafe and len(self.packets):
            raise ValueError('mail absent during nonzero-flag/forcing interval required')
        saved = self.data,self.heads,self.where,self.packets,self.age,self.time
        # Compute both staged factors before publishing either one.
        flags, metrics = self._flags_after(ticks)
        row = super().advance(ticks, **kwargs)
        if unsafe and (row['packets_emitted'] or len(self.packets)):
            self.data,self.heads,self.where,self.packets,self.age,self.time = saved
            raise RuntimeError('packet emission during nonzero-flag/forcing interval; state unchanged')
        self.flags = flags
        return dict(row, **metrics)

    def quiet_advance(self, ticks):
        flags, metrics = self._flags_after(ticks)
        row = super().quiet_advance(ticks)
        self.flags = flags
        return dict(row, **metrics)

    def cell(self, position):
        cell = super().cell(position); size = self.n*f.Q; position %= size
        col, at = divmod(position, f.Q)
        def flag(pos, kind):
            return (int(self.flags[pos//64,kind]) >> (pos%64)) & 1
        signal = (int(self.right[col]) << (f.Q-1-at)) if at >= f.Q-5 else 0
        if 1 <= at <= 5:
            signal |= int(self.left[col]) << (5-at)
        changes = dict(f1=flag(position,0), f2=flag(position,1), signal=signal)
        on = c.WF_START <= self.age < c.WF_END
        for delta in f.OFFSETS:
            primary = (position+delta)%size; other, address = divmod(primary,f.Q)
            changes[f'w{delta+2}_wf1'] = int(on and address>=f.Q-5 and self.right[other])
            changes[f'w{delta+2}_wf2'] = int(on and address<=4 and self.left[other] and not flag(primary,0))
        return replace(cell, **changes)
