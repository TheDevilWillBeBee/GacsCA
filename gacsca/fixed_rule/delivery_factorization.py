"""Checked domain factorization, not an executor or a simulated transition.

On canonical Address/uniform Age, flags cannot change geometry. All controller,
Data and Signal outputs are independent of old flags. Mail outputs equal the
zero-flag computation followed by computed-Flag1 clearing; Wf2 is additionally
gated by computed Flag1. Actual flags must still be evolved and represented.
This local oracle supports a future composed executor; no speedup is claimed.
"""
from dataclasses import replace
from . import delivery_rule as r
from .canonical_flags import transition as flag_transition

FLAGS=('f1','f2','wf1','wf2')
MAIL=tuple(name for name,_ in r.SCHEMA if name.startswith(('lp_','rp_')))
INDEPENDENT=tuple(name for name,_ in r.SCHEMA if name not in (*FLAGS,*MAIL))


def local_step(cells):
    flags=flag_transition(cells)  # also rejects noncanonical geometry
    clean=tuple(replace(c,**{name:0 for name in FLAGS}) for c in cells)
    out=r.local_step(clean)
    updates=dict(flags,wf2=out.wf2 if not flags['f1'] else 0)
    if flags['f1']:updates.update({name:0 for name in MAIL})
    return replace(out,**updates)
