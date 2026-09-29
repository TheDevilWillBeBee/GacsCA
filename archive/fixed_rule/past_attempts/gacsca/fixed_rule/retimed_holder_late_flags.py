"""Exact same-time flag representation for late canonical physical states.

This adapter does not repair flags or advance any transition. It preserves the
complete raw configuration while moving its flag bits into the existing exact
flag engine. Nonflag physical exceptions remain in the full G evaluator.
"""
import numpy as np
from . import retimed_holder_rule as f, retimed_holder_quotient as q
from . import retimed_holder_active_snapshot as active
from . import retimed_holder_cuda_general_snapshot as snapshots
from . import retimed_holder_flags_gpu as flags, retimed_holder_resident_period as period


def render(snapshot):
    """Complete late canonical reconstruction, including every physical flag."""
    age = int(snapshot['age'])
    if not f.WF_END+f.Q < age < f.U:
        raise ValueError('late nonforcing age required')
    planes = snapshot['flags']
    n = len(snapshot['bank'])
    if n*f.Q*(f.FIELDS+len(q.SCHEMA))*8 > 256*1024**2:
        raise ValueError('bounded complete reconstruction required')
    if not isinstance(planes, np.ndarray) or planes.dtype != np.uint64 or planes.shape != (n*f.Q//64, 2):
        raise ValueError('complete typed flag planes required')
    bits = ((planes[:, None, :] >> np.arange(64, dtype=np.uint64)[None, :, None]) & np.uint64(1)).reshape(n*f.Q, 2)
    unflagged = dict(snapshot)
    unflagged['flags'] = np.zeros_like(planes)
    rows = snapshot['active_rows'].copy()
    for col, count in enumerate(snapshot['counts']):
        count = int(count)
        positions = col*f.Q + rows[col, :count, q.COL['address']].astype(np.int64)
        if np.any(positions < col*f.Q) or np.any(positions >= (col+1)*f.Q):
            raise ValueError('canonical active addresses required')
        for index, name in enumerate(('f1', 'f2')):
            if not np.array_equal(rows[col, :count, q.COL[name]], bits[positions, index]):
                raise ValueError('active flag rows disagree with flag planes')
            rows[col, :count, q.COL[name]] = 0
    unflagged['active_rows'] = rows
    result = active.render(unflagged)
    result[:, f.COL['f1']] = bits[:, 0]
    result[:, f.COL['f2']] = bits[:, 1]
    return result


def physical(actual):
    """Diagnostic full reconstruction; upload/read only, no transition."""
    state = snapshots.snapshot(actual.reference)
    result = render(state) if actual.reference._flags is not None else active.render(state)
    positions = actual.positions
    for start in range(0, len(positions), 256):
        part = positions[start:start+256]
        result[list(part)] = np.array([f.encode_cell(cell) for cell in actual.read(part)], dtype=np.uint64)
    return result


def attach(actual):
    """Move exact flags to an owned sidecar and remove only identical exceptions.

Restricted to a late, mail-free reference and actual canonical geometry with
zero Wf. No extension of the old forcing-only absorption operation is made.
    """
    actual._check()
    background = actual.reference
    if background._flags is not None or not f.WF_END+f.Q < background.age < f.U:
        raise ValueError('unflagged late reference required')
    state = snapshots.snapshot(background)
    mail = [q.COL[name] for name, _ in q.SCHEMA if name.startswith(('lp_', 'rp_'))]
    if np.any(state['active_rows'][:, :, mail]):
        raise ValueError('mail-free canonical reference required')
    before = physical(actual)
    positions = np.arange(len(before))
    if not np.array_equal(before[:, f.COL['address']], positions % f.Q) or np.any(before[:, f.COL['age']] != background.age):
        raise ValueError('actual geometry must already be canonical')
    if np.any(before[:, [f.COL[f'w{k}_{name}'] for k in range(5) for name in ('wf1', 'wf2')]]):
        raise ValueError('actual Wf must be zero in the late domain')
    planes = np.zeros_like(state['flags'])
    for index, name in enumerate(('f1', 'f2')):
        values = before[:, f.COL[name]].reshape(-1, 64)
        planes[:, index] = np.bitwise_or.reduce(values << np.arange(64, dtype=np.uint64)[None, :], axis=1)
    sidecar = flags.World(tuple(map(int, state['signals'][:, 1])), tuple(map(int, state['signals'][:, 0])), age=background.age, initial=planes)
    initial_count = len(actual.positions)
    background._flags = sidecar
    background._snapshot = None
    actual._check()  # bind the complete flag plane at the unchanged clock
    if initial_count:
        different = np.empty(initial_count, dtype=np.uint64)
        code = actual.lib.rf_normalize(actual.background.handle, actual.handle, period.pointer(different))
        if code:
            raise RuntimeError(f'late flag normalization failed: {code}')
        selected = np.flatnonzero(different).astype(np.uint64)
        code = actual.lib.rf_commit(actual.handle, period.pointer(selected), len(selected))
        if code:
            raise RuntimeError(f'late flag compaction failed: {code}')
        actual._positions = actual._positions[selected.astype(np.intp)]
    after = physical(actual)
    np.testing.assert_array_equal(before, after)
    return dict(physical_transitions=0, complete_raw_words_verified=before.size, exceptions_before=initial_count, exceptions_after=len(actual.positions), flag1_sites=int(np.count_nonzero(before[:, f.COL['f1']])), flag2_sites=int(np.count_nonzero(before[:, f.COL['f2']])), extra_device_bytes=sidecar.device_bytes)
