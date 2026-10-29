"""EXPLICIT local clock proposal, not a rebuilt self-simulating candidate.

When the left Address majority is absent, accept a nonzero left Age
majority; otherwise retain the existing own-Age fallback. G17/SP1--SP10
are unchanged. Arbitrary higher Age islands and iid reliability unproved.
"""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from gacsca import maintenance
from gacsca.netlist import w_eq_const
from check_right_barrier import dominant_majority
import proposed_sparse_confined_source448 as base


def proposed_build(symbolic=False):
    _,source = base.proposed_build()
    old = """    age_l, _ = majority_word(n, [cells[j]['age'] for j in range(-1, -6, -1)], c['age'])
    age_l = w_mux(n, left_exists, age_l, c['age'])"""
    new = """    age_l, age_l_exists = majority_word(n, [cells[j]['age'] for j in range(-1, -6, -1)], c['age'])
    use_left_age = n.OR(left_exists, n.AND(age_l_exists, n.NOT(w_eq_const(n, age_l, 0))))
    age_l = w_mux(n, use_left_age, age_l, c['age'])"""
    assert source.count(old)==1
    source = source.replace(old,new)
    namespace = dict(maintenance.__dict__,w_eq_const=w_eq_const)
    if symbolic:
        namespace['majority_word'] = dominant_majority
    exec(compile(source,'<EXPLICIT nonzero modal-clock fallback proposal>', 'exec'),namespace)
    return namespace['build'],source
