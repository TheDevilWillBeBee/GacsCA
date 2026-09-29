"""Bounded complete raw views of late canonical multi-colony GPU snapshots.

Read-only reconstruction, including every controller/mail word and cross-colony
procedure copies. No physical or represented transition is evaluated here.
"""
import numpy as np
from . import retimed_holder_rule as f, retimed_holder_core as c
from . import retimed_holder_quotient as q, retimed_holder_program as p
from . import retimed_holder_packed as packed, retimed_holder_resident_period as period
from .retimed_holder_literal_cone import rom


class Window:
    def __init__(self, snapshot):
        g = p.layout()
        bank, rows, counts = snapshot['bank'], snapshot['active_rows'], snapshot['counts']
        if not isinstance(bank, np.ndarray) or bank.dtype != np.uint64 or bank.ndim != 2 or bank.shape[1] != g.memory_count+5 or not 1 <= len(bank) <= 128:
            raise ValueError('bounded complete canonical banks required')
        n = len(bank)
        for value, shape in ((rows, (n, period.SLOTS, len(q.SCHEMA))), (counts, (n,)), (snapshot['flags'], (n*f.Q//64, 2)), (snapshot['signals'], (n, 2))):
            if not isinstance(value, np.ndarray) or value.dtype != np.uint64 or value.shape != shape:
                raise ValueError('complete typed multi-colony snapshot required')
        self.age = int(snapshot['age'])
        if not f.WF_END+f.Q < self.age < f.U or int(snapshot['time']) % f.U != self.age or np.any(snapshot['flags']) or np.any(snapshot['signals'] > 1):
            raise ValueError('late zero-flag canonical context required')
        positions, records = [], []
        for col, count in enumerate(counts):
            count = int(count)
            if count > period.SLOTS or np.any(rows[col, count:]):
                raise ValueError('complete normalized active records required')
            part = rows[col, :count]
            packed.pack(part)
            addresses = part[:, q.COL['address']].astype(np.int64)
            if np.any(addresses >= f.Q) or (count > 1 and np.any(np.diff(addresses) <= 0)):
                raise ValueError('sorted canonical active addresses required')
            if np.any(part[:, q.COL['age']] != self.age) or np.any(part[:, [q.COL[n] for n in ('f1', 'f2', 'wf1', 'wf2')]]):
                raise ValueError('active geometry disagrees with the snapshot')
            expected_data = np.zeros(count, dtype=np.uint64)
            inside = (addresses < g.memory_count) | (addresses >= f.Q-5)
            indices = np.where(addresses < g.memory_count, addresses, g.memory_count+addresses-(f.Q-5))
            expected_data[inside] = bank[col, indices[inside]]
            if not np.array_equal(part[:, q.COL['data']], expected_data):
                raise ValueError('active Data differs from complete bank')
            required = {}
            for bit, sites in zip(snapshot['signals'][col], (range(1,6), range(f.Q-5, f.Q))):
                if bit:
                    required.update({a:1 << (5-a if a < 6 else f.Q-1-a) for a in sites})
            observed = {int(row[q.COL['address']]):int(row[q.COL['signal']]) for row in part if row[q.COL['signal']]}
            if observed != required:
                raise ValueError('localized Signal records are incomplete')
            positions.extend(col*f.Q+int(a) for a in addresses)
            records.extend(part[:, [q.COL[name] for name,_ in f.PROCEDURE]])
        self.bank, self.signals, self.size = bank, snapshot['signals'], n*f.Q
        self.positions = np.array(positions, dtype=np.int64)
        self.records = np.array(records, dtype=np.uint64).reshape(-1, len(f.PROCEDURE))

    def _procedure(self, positions):
        col, address = np.divmod(positions % self.size, f.Q)
        g = p.layout()
        out = np.zeros((len(positions), len(f.PROCEDURE)), dtype=np.uint64)
        inside = (address < g.memory_count) | (address >= f.Q-5)
        index = np.where(address < g.memory_count, address, g.memory_count+address-(f.Q-5))
        out[inside, [n for n,_ in f.PROCEDURE].index('data')] = self.bank[col[inside], index[inside]]
        at = np.searchsorted(self.positions, positions % self.size)
        valid = at < len(self.positions)
        selected = np.flatnonzero(valid)
        selected = selected[self.positions[at[selected]] == (positions[selected] % self.size)]
        out[selected] = self.records[at[selected]]
        return out

    def cells(self, positions):
        positions = np.asarray(positions, dtype=np.int64)
        if positions.ndim != 1 or len(positions) > 65536:
            raise ValueError('bounded physical position vector required')
        positions = positions % self.size
        col, address = np.divmod(positions, f.Q)
        out = np.zeros((len(positions), f.FIELDS), dtype=np.uint64)
        out[:, f.COL['address']], out[:, f.COL['age']] = address, self.age
        for d in f.STATIC_OFFSETS:
            for index,name in enumerate(c.STATIC):
                out[:, f.COL[f'p{d+3}_{name}']] = rom()[(address+d) % f.Q, index]
        for d in f.OFFSETS:
            out[:, [f.COL[f's{d+2}_{name}'] for name,_ in f.PROCEDURE]] = self._procedure(positions+d)
        left, right = (address >= 1) & (address <= 5), address >= f.Q-5
        out[left, f.COL['signal']] = self.signals[col[left], 0] << (5-address[left]).astype(np.uint64)
        out[right, f.COL['signal']] = self.signals[col[right], 1] << (f.Q-1-address[right]).astype(np.uint64)
        return out
