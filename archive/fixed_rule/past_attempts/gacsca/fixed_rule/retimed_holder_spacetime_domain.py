"""Diagnostics for a conditional continuing-noise invariant, never transitions.

`previous` bounds procedure-only residuals before the current replacements.
The healthy geometry, flag, Signal and procedure premises are separate.
"""
from .retimed_holder_pulse_domain import locally_two_sparse


def eligible(previous, current, *, size):
    """Current faults: <=2 per 11 sites; previous union current: <=2 per 5."""
    previous, current = tuple(previous), tuple(current)
    # Reuse the validated position domain; previous need not itself be 11-sparse.
    locally_two_sparse(previous, size=size)
    if not locally_two_sparse(current, size=size):
        return False
    sites = sorted(set(previous) | set(current))
    if len(sites) < 3:
        return True
    extended = sites + [x + size for x in sites[:2]]
    return all(extended[i + 2] - extended[i] >= 5 for i in range(len(sites)))
