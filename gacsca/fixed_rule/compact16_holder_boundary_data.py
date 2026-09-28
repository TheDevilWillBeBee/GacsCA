"""Noiseless terminal initial data for the unchanged retimed holder rule.

This is an ordinary homogeneous configuration, not a transition or a robust
colony. Its reset/vote pulses are part of the represented raw controller state.
"""
from . import compact16_holder_rule as f, compact16_holder_core as c
from . import compact16_holder_projected as r, compact16_holder_program as p


def pulse_entries():
    entries = p.layout().entries
    return tuple(zip((age + 1 for age in c.RESET_AGES), entries)) + (
        (c.VOTE_AGES[0] + 1, entries[4]),
    )


def cell(age=0):
    if type(age) is not int or not 0 <= age < f.U:
        raise ValueError('normalized physical clock required')
    hits = [pc for when, pc in pulse_entries() if when == age]
    return r.Cell(address=f.Q - 1, age=age, f1=1, f2=1,
                  s3_head=int(bool(hits)), s3_pc=hits[0] if hits else 0)
