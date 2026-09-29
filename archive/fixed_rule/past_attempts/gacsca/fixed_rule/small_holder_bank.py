"""Lossless physical snapshots: dense MEM Data, sparse logical/raw exceptions.

Storage only; no new alphabet, level kernel, transition or coherence assertion.
The default geometry is canonical and Age uniform. Every deviation, including
all seven raw program records and broken backups, can be stored explicitly.
A sparse entry is an absolute field value (zero is meaningful), not a fault mask.
"""
from dataclasses import dataclass
import numpy as np
from . import small_holder_rule as f, small_holder_program as p
from . import small_holder_quotient as q, small_holder_projected as projected
from .small_holder_initial import coherent_cell

MAX_BANK_BYTES = 64 * 1024**2


def _position(position, sites):
    if not isinstance(position, int) or not 0 <= position < sites:
        raise ValueError('physical position outside ring')
    return position


@dataclass(frozen=True)
class Snapshot:
    colonies: int
    age: int
    data: np.ndarray
    logical_keys: np.ndarray
    logical_values: np.ndarray
    raw_keys: np.ndarray
    raw_values: np.ndarray

    def __post_init__(self):
        if type(self.colonies) is not int or self.colonies < 1:
            raise ValueError('positive colony count required')
        if type(self.age) is not int or not 0 <= self.age < f.U:
            raise ValueError('Age outside alphabet')
        if self.sites * f.FIELDS >= 1 << 64:
            raise ValueError('sparse key overflow')
        rows = p.layout().memory_count
        if not isinstance(self.data, np.ndarray) or self.data.dtype != np.uint64 or self.data.shape != (self.colonies, rows):
            raise ValueError('complete MEM Data bank required')
        arrays = [self.data, self.logical_keys, self.logical_values, self.raw_keys, self.raw_values]
        for a in arrays:
            if not isinstance(a, np.ndarray) or a.dtype != np.uint64 or not a.flags.c_contiguous:
                raise ValueError('contiguous uint64 storage required')
        if sum(a.nbytes for a in arrays) > MAX_BANK_BYTES:
            raise ValueError('bounded reference snapshot exceeds 64 MiB')
        for keys, values, schema in ((self.logical_keys, self.logical_values, q.SCHEMA), (self.raw_keys, self.raw_values, f.SCHEMA)):
            if keys.ndim != 1 or values.shape != keys.shape:
                raise ValueError('complete sparse key/value pairs required')
            if len(keys) and (int(keys[-1]) >= self.sites * len(schema) or np.any(keys[1:] <= keys[:-1])):
                raise ValueError('sparse keys must be sorted, unique and in ring')
            for key, value in zip(keys.tolist(), values.tolist()):
                if value >= 1 << schema[key % len(schema)][1]:
                    raise ValueError('sparse value outside physical field width')
        # Own immutable copies: caller mutation cannot silently change a snapshot.
        for name, a in zip(('data','logical_keys','logical_values','raw_keys','raw_values'), arrays):
            copy = a.copy(); copy.flags.writeable = False
            object.__setattr__(self, name, copy)

    @property
    def sites(self): return self.colonies * f.Q

    @property
    def storage_bytes(self):
        return sum(getattr(self, n).nbytes for n in ('data','logical_keys','logical_values','raw_keys','raw_values'))

    @staticmethod
    def _entries(keys, values, start, count):
        lo, hi = np.searchsorted(keys, (start, start + count))
        return ((int(k)-start, int(v)) for k,v in zip(keys[lo:hi], values[lo:hi]))

    def logical_cell(self, position):
        _position(position, self.sites)
        colony, address = divmod(position, f.Q)
        fields = dict(address=address, age=self.age)
        if address < self.data.shape[1]: fields['data'] = int(self.data[colony,address])
        for index, value in self._entries(self.logical_keys, self.logical_values, position*len(q.SCHEMA), len(q.SCHEMA)):
            fields[q.SCHEMA[index][0]] = value
        return q.Cell(**fields)

    def cell(self, position):
        _position(position, self.sites)
        logical = lambda x: self.logical_cell(x % self.sites)
        raw = projected.lift(coherent_cell(logical, position))
        fields = dict(zip((n for n,_ in f.SCHEMA), f.encode_cell(raw)))
        for index, value in self._entries(self.raw_keys, self.raw_values, position*f.FIELDS, f.FIELDS):
            fields[f.SCHEMA[index][0]] = value
        return f.Cell(**fields)


class Builder:
    """Host initialization/diagnostics only; never substitutes upper transitions."""
    def __init__(self, colonies, age=0):
        if type(colonies) is not int or colonies < 1 or colonies*p.layout().memory_count*8 > MAX_BANK_BYTES:
            raise ValueError('bounded positive colony count required')
        if type(age) is not int or not 0 <= age < f.U: raise ValueError('Age outside alphabet')
        self.colonies, self.age = colonies, age
        self.data = np.zeros((colonies, p.layout().memory_count), dtype=np.uint64)
        self.logical, self.raw = {}, {}

    def set_logical(self, position, cell):
        _position(position, self.colonies*f.Q)
        if not isinstance(cell, q.Cell): raise ValueError('complete logical controller required')
        colony, address = divmod(position, f.Q)
        if address < self.data.shape[1]: self.data[colony,address] = cell.data
        for index,(name,_) in enumerate(q.SCHEMA):
            key = position*len(q.SCHEMA)+index
            default = address if name == 'address' else self.age if name == 'age' else 0
            value = getattr(cell, name)
            if name == 'data' and address < self.data.shape[1]: self.logical.pop(key, None)
            elif value != default: self.logical[key] = value
            else: self.logical.pop(key, None)

    def set_raw_fields(self, position, **fields):
        _position(position, self.colonies*f.Q)
        widths = dict(f.SCHEMA)
        for name,value in fields.items():
            if name not in widths or type(value) is not int or not 0 <= value < 1 << widths[name]:
                raise ValueError('invalid raw physical field')
        self.raw.update({position*f.FIELDS+f.COL[name]:value for name,value in fields.items()})

    def freeze(self):
        def arrays(d):
            keys = sorted(d)
            return np.array(keys,dtype=np.uint64),np.array([d[k] for k in keys],dtype=np.uint64)
        return Snapshot(self.colonies,self.age,self.data,*arrays(self.logical),*arrays(self.raw))
