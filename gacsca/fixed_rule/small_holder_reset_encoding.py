"""Explicit complete clean reset encoding C(x), for initialization/diagnostics only.

Never used to replace evolving physical state. Includes Info, actual reset head,
all controller fields, and retained fivefold Signals. Depth is not a parameter.
"""
import hashlib
import numpy as np
from . import small_holder_rule as f, small_holder_projected as r
from . import small_holder_program as p, small_holder_quotient as q
from .small_holder_initial import coherent_cell


class Encoding:
    def __init__(self,parents,*,left=None,right=None):
        self.parents=tuple(parents)
        if not self.parents or any(not isinstance(x,r.Cell) for x in self.parents):
            raise ValueError('complete projected parents required')
        self.left=tuple(x.f2 for x in self.parents) if left is None else tuple(left)
        self.right=tuple(x.f1 for x in self.parents) if right is None else tuple(right)
        if any(len(x)!=len(self.parents) or any(type(bit) is not int or bit not in (0,1) for bit in x) for x in (self.left,self.right)):
            raise ValueError('one actual bit per colony side required')
        self.raw=tuple(f.encode_cell(r.lift(x)) for x in self.parents)
        self.info={a:k for k,a in enumerate(p.layout().info)}
        self.sites=len(self.parents)*f.Q

    def array(self,positions,*,age=1):
        positions=tuple(positions)
        if not 1<=len(positions)<=256 or any(type(x) is not int for x in positions) or age not in (0,1):
            raise ValueError('bounded integral positions and boundary Age required')
        out=np.zeros((len(positions),len(q.SCHEMA)),dtype=np.uint64)
        for i,pos in enumerate(positions):
            col,a=divmod(pos%self.sites,f.Q)
            out[i,q.COL['address']]=a;out[i,q.COL['age']]=age
            if a in self.info:out[i,q.COL['data']]=self.raw[col][self.info[a]]
            if a==0 and age==1:
                out[i,q.COL['head']]=1;out[i,q.COL['pc']]=p.layout().entries[0]
            if 1<=a<=5:out[i,q.COL['signal']]=self.left[col]<<(5-a)
            elif a>=f.Q-5:out[i,q.COL['signal']]=self.right[col]<<(f.Q-1-a)
        return out

    def logical(self,position):return q.decode_cell(self.array((position,))[0])

    def physical(self,position):
        return r.lift(coherent_cell(self.logical,position%self.sites))

    def initial_records(self):
        """Sparse non-Data records for a new resident world at Age one."""
        out={}
        for col in range(len(self.parents)):
            for a in (0,*range(1,6),*range(f.Q-5,f.Q)):
                cell=self.logical(col*f.Q+a)
                if cell.head or cell.signal:out[col*f.Q+a]=cell
        return out

    def verify(self,world,*,before_reset=False):
        """Read every coherent row; retain a bounded chunk only.

        Before reset, allow arbitrary scratch MEM Data but require all Info,
        non-MEM Data, controllers, flags, mail, Signals and geometry explicitly.
        After reset, compare the entire C(x) state, with no ignored field.
        """
        age=0 if before_reset else 1
        if world.colonies!=len(self.parents) or world.age!=age:
            raise ValueError('wrong world size or checkpoint Age')
        h=hashlib.sha256();checked=0;g=p.layout()
        for first in range(0,self.sites,256):
            positions=tuple(range(first,min(self.sites,first+256)))
            actual=q.array_from_cells(world.logical_cells(positions))
            expected=self.array(positions,age=age)
            if before_reset:
                for i,pos in enumerate(positions):
                    a=pos%f.Q
                    if (a<g.memory_count or a>=f.Q-5) and a not in self.info:
                        expected[i,q.COL['data']]=actual[i,q.COL['data']]
            np.testing.assert_array_equal(actual,expected)
            h.update(actual.tobytes());checked+=len(actual)
        return dict(passed=True,age=age,coherent_rows_checked=checked,words_per_row=len(q.SCHEMA),sha256=h.hexdigest(),scratch_memory_unconstrained=before_reset,complete_physical_states_implied_by_coherent_representation=True)
