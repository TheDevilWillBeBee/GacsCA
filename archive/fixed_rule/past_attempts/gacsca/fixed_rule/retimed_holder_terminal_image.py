"""Read-only complete physical reconstruction of a terminal formula.

This does not advance a physical world, recursively interpret hierarchy levels,
or install diagnostic output. The same accessor describes either endpoint age.
"""
from . import retimed_holder_terminal_checks as checks,retimed_holder_quotient as q
from . import retimed_holder_rule as f,retimed_holder_program as p
from .retimed_holder_initial import coherent_cell


class Image:
    def __init__(self,terminal,*,precommit):
        self.bank=terminal['precommit_bank' if precommit else 'committed_bank']
        self.signals=terminal['signals'];self.age=f.U-1 if precommit else 0
        assert self.bank.shape==(len(self.signals),p.layout().memory_count+5)
        assert self.signals.shape==(len(self.bank),2)
        self.size=len(self.bank)*f.Q
    def logical(self,position):
        col,a=divmod(position%self.size,f.Q);m=p.layout().memory_count
        data=int(self.bank[col,a]) if a<m else int(self.bank[col,m+a-(f.Q-5)]) if a>=f.Q-5 else 0
        return q.Cell(data=data,address=a,age=self.age,signal=checks.signal_word(a,*self.signals[col]))
    def cell(self,position):
        return coherent_cell(self.logical,position%self.size)
