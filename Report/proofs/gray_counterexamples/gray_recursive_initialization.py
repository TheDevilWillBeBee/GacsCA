"""An explicit stationary all-level initial hierarchy for fixed GR1.

This is an initialization for the isolated hardwired-ROM GR1 rule. It
does not compile Gray's one-ProgramBit-per-Address interpreter. The
universal termination and encoding proof is in GR1_INTACT_CLOCK_COMMIT.md.
"""
from functools import lru_cache


class RecursiveInitial:
    def __init__(self,candidate):
        self.candidate=candidate
        self.Q=candidate.p.Q
        self.tags={int(candidate.layout[row]):tag for tag,row in candidate.row.items()}
        assert len(self.tags)==candidate.W
        self.info_residues=tuple(sorted(a for a,(f,b) in self.tags.items() if f=='info'))
        self.minimum_info_absolute_coordinate=min(min(self.info_residues),
                                                  self.Q-max(self.info_residues))
        # A recursive Info call has |next| <= |x|/Q+3. This is strictly
        # smaller at every possible Info-tag coordinate, including x<0.
        assert self.minimum_info_absolute_coordinate>=4
        assert self.minimum_info_absolute_coordinate/self.Q+3 < self.minimum_info_absolute_coordinate
        assert not set(self.tags)&{0,1,2,3,self.Q-3,self.Q-2,self.Q-1}

    @lru_cache(maxsize=None)
    def logical_Info(self,x):
        colony,residue=divmod(int(x),self.Q)
        tag=self.tags.get(residue)
        if tag is None:
            return 0
        field,bit=tag
        if field=='addr':
            return ((colony%self.Q)>>bit)&1
        if field=='info':
            nxt=colony+bit-2
            assert abs(nxt)<abs(x)
            return self.logical_Info(nxt)
        return 0

    def raw(self,x,field,bit):
        if field=='addr':
            return ((int(x)%self.Q)>>bit)&1
        if field=='info':
            return self.logical_Info(int(x)+bit-2)
        return 0

    def encoded_primary(self,upper_x,field,bit):
        a=int(self.candidate.layout[self.candidate.row[field,bit]])
        return self.logical_Info(int(upper_x)*self.Q+a)
