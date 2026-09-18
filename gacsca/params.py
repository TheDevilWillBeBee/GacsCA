"""Global parameters and rule-interpretation variants.

References:
  Gray (2001) "A Reader's Guide to Gacs's Positive Rates Paper", Sec. 5.
  Masumori, Sinapayen, Ikegami (2024) "Simulation of Gacs' Automaton", arXiv:2405.04060.
"""
from dataclasses import dataclass, field

RANGE = 5  # Gray's interaction radius: N(x) = {x-5..x+5}


@dataclass(frozen=True)
class Params:
    Q: int                 # colony size (Gray: power of 2 >= 2^13; Masumori: 271)
    U: int = None          # work period (Gray: U = 128 Q)
    ncol: int = 8          # number of colonies on the ring; total length L = ncol*Q

    def __post_init__(self):
        if self.U is None:
            object.__setattr__(self, "U", 128 * self.Q)

    @property
    def L(self):
        return self.ncol * self.Q


@dataclass(frozen=True)
class Variant:
    """Interpretation choices where Gray's prose is ambiguous or where Masumori et al. deviate.

    flag1_ii_in_colony: Gray p.21 cond (ii): 'at least three sites in R(x) & C(x) have Flag1 = 1'.
        Masumori p.3 drops the '& C(x)' (counts all of R(x)).
    flag2_iii_age: Gray p.21 cond (iii) uses the *computed* Age at x (well defined because when
        C(x) does not exist the Age vote is taken in L(x) regardless of Flag2 -- no true
        circularity). Masumori replaced it by the *current* Age at x.
    majority: 'strict' = a value held by >=3 of the 5 voters (Gray: 'clear majority'), else the
        current value at x is kept. 'plurality' = most frequent value, ties -> current value.
    age_increment_always: Gray: the majority Age value is incremented by 1 mod U. When the vote
        has no clear majority the outcome is the current value at x; we still increment (a cell
        always advances its clock).  Masumori's code (ageThisCell()) increments unconditionally.
    """
    flag1_ii_in_colony: bool = True
    flag2_iii_age: str = "computed"      # or "current"
    majority: str = "strict"             # or "plurality"
    age_increment_always: bool = True

    @staticmethod
    def gray():
        return Variant()

    @staticmethod
    def masumori():
        return Variant(flag1_ii_in_colony=False, flag2_iii_age="current")
