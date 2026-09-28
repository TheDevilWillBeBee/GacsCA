"""Bounded same-time restoration and flag packing across physical colonies.

No transition is evaluated here. Sparse exceptions retain complete raw fields;
conversion verifies every physical word in blocks before returning.
"""
import numpy as np
from . import retimed_holder_rule as f, retimed_holder_quotient as q
from . import retimed_holder_live_window as live
from . import retimed_holder_packed as packed, retimed_holder_resident_period as period
from . import retimed_holder_cuda_general_snapshot as snapshots


class View:
    def __init__(self, state, positions=(), values=None):
        self.planes = state['flags']
        n = len(state['bank'])
        if self.planes.dtype != np.uint64 or self.planes.shape != (n*f.Q//64, 2):
            raise ValueError('complete typed flag planes required')
        rows = state['active_rows'].copy()
        for col, count in enumerate(state['counts']):
            part = rows[col, :int(count)]
            addresses = part[:, q.COL['address']]
            if np.any(addresses >= f.Q):
                raise ValueError('canonical active addresses required')
            pos = col*f.Q+addresses.astype(np.int64)
            bits = (self.planes[pos//64] >> (pos%64).astype(np.uint64)[:, None]) & np.uint64(1)
            for k, name in enumerate(('f1', 'f2')):
                if not np.array_equal(part[:, q.COL[name]], bits[:, k]):
                    raise ValueError('active flags disagree with planes')
                part[:, q.COL[name]] = 0
        self.base = live.Window(dict(state, active_rows=rows, flags=np.zeros_like(self.planes)))
        self.positions = np.asarray(positions, dtype=np.int64)
        self.values = np.empty((0, f.FIELDS), dtype=np.uint64) if values is None else values
        if self.positions.ndim != 1 or self.values.dtype != np.uint64 or self.values.shape != (len(self.positions), f.FIELDS):
            raise ValueError('complete exception rows required')
        if np.any(self.positions < 0) or np.any(self.positions >= self.base.size) or np.any(np.diff(self.positions) <= 0):
            raise ValueError('sorted unique physical exceptions required')

    def cells(self, positions):
        positions = np.asarray(positions, dtype=np.int64)
        result = self.base.cells(positions)
        positions = positions % self.base.size
        bits = (self.planes[positions//64] >> (positions%64).astype(np.uint64)[:, None]) & np.uint64(1)
        result[:, [f.COL['f1'], f.COL['f2']]] = bits
        at = np.searchsorted(self.positions, positions)
        selected = np.flatnonzero(at < len(self.positions))
        selected = selected[self.positions[at[selected]] == positions[selected]]
        result[selected] = self.values[at[selected]]
        return result


def capture(actual):
    positions = np.asarray(actual.positions, dtype=np.int64)
    chunks = [np.array([f.encode_cell(c) for c in actual.read(positions[i:i+256].tolist())], dtype=np.uint64)
              for i in range(0, len(positions), 256)]
    values = np.concatenate(chunks) if chunks else np.empty((0, f.FIELDS), dtype=np.uint64)
    return snapshots.snapshot(actual.reference), positions, values


def restore(state, *, device_budget=32*1024**2):
    from . import retimed_holder_resident_general as general, retimed_holder_projected as r
    live.Window(state)
    rows, counts = state['active_rows'], state['counts']
    mail = [q.COL[name] for name, _ in q.SCHEMA if name.startswith(('lp_', 'rp_'))]
    if np.any(rows[:, :, mail]):
        raise ValueError('late mail-free reference required')
    world = general.World((r.Cell(),)*len(counts), device_budget=device_budget)
    try:
        core = world._core
        for col, count in enumerate(counts):
            count = int(count)
            records = np.zeros((1, period.SLOTS, packed.WORDS), dtype=np.uint64)
            records[0, :count] = packed.pack(rows[col, :count])
            sizes = np.array([count], dtype=np.uint64)
            if core.lib.rp_initial(core.handle, col, 1, period.pointer(records), period.pointer(sizes)):
                raise RuntimeError('controller upload failed')
            bank = np.ascontiguousarray(state['bank'][col])
            if core.lib.rp_bank(core.handle, col, period.pointer(bank)):
                raise RuntimeError('complete bank upload failed')
        age = int(state['age'])
        if core.lib.rp_restore_age(core.handle, age):
            raise ValueError('checkpoint outside resident domain')
        core.age = core.epoch = age
        core.time = int(state['time'])
        restored = snapshots.snapshot(world)
        for key in restored:
            np.testing.assert_array_equal(restored[key], state[key], err_msg=key)
        return world
    except BaseException:
        world.close()
        raise


def attach(actual):
    from . import retimed_holder_flags_gpu as flags
    actual._check()
    background = actual.reference
    state, positions, values = capture(actual)
    if background._flags is not None:
        raise ValueError('unflagged reference required')
    before = View(state, positions, values)
    mail = [q.COL[name] for name, _ in q.SCHEMA if name.startswith(('lp_', 'rp_'))]
    if np.any(state['active_rows'][:, :, mail]):
        raise ValueError('mail-free canonical reference required')
    planes = np.zeros_like(state['flags'])
    totals = [0, 0]
    for col in range(len(state['bank'])):
        sites = np.arange(col*f.Q, (col+1)*f.Q)
        raw = before.cells(sites)
        if not np.array_equal(raw[:, f.COL['address']], sites % f.Q) or np.any(raw[:, f.COL['age']] != background.age):
            raise ValueError('actual geometry must already be canonical')
        if np.any(raw[:, [f.COL[f'w{k}_{name}'] for k in range(5) for name in ('wf1', 'wf2')]]):
            raise ValueError('actual Wf must be zero')
        for index, name in enumerate(('f1', 'f2')):
            bits = raw[:, f.COL[name]].reshape(-1, 64)
            if np.any(bits > 1):
                raise ValueError('Boolean physical flags required')
            planes[col*f.Q//64:(col+1)*f.Q//64, index] = np.bitwise_or.reduce(bits << np.arange(64, dtype=np.uint64), axis=1)
            totals[index] += int(np.count_nonzero(bits))
    sidecar = flags.World(tuple(map(int, state['signals'][:, 1])), tuple(map(int, state['signals'][:, 0])), age=background.age, initial=planes)
    background._flags = sidecar
    background._snapshot = None
    actual._check()
    if len(positions):
        different = np.empty(len(positions), dtype=np.uint64)
        if actual.lib.rf_normalize(actual.background.handle, actual.handle, period.pointer(different)):
            raise RuntimeError('flag normalization failed')
        selected = np.flatnonzero(different).astype(np.uint64)
        if actual.lib.rf_commit(actual.handle, period.pointer(selected), len(selected)):
            raise RuntimeError('flag compaction failed')
        actual._positions = actual._positions[selected.astype(np.intp)]
    after = View(*capture(actual))
    for col in range(len(state['bank'])):
        sites = np.arange(col*f.Q, (col+1)*f.Q)
        np.testing.assert_array_equal(before.cells(sites), after.cells(sites))
    return dict(physical_transitions=0, complete_raw_words_verified=before.base.size*f.FIELDS,
                exceptions_before=len(positions), exceptions_after=len(actual.positions),
                flag1_sites=totals[0], flag2_sites=totals[1], extra_device_bytes=sidecar.device_bytes)
