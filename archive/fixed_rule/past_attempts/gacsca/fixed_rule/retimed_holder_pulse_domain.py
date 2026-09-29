"""Diagnostic spatial premise for the conditional two-tick repair theorem.

This is a predicate on external fault data, not a transition or recovery action.
Canonical geometry/coherence/clock premises must be checked separately.
"""


def locally_two_sparse(positions,*,size):
    """Every cyclic interval of eleven sites contains at most two fault sites."""
    positions=tuple(positions)
    if type(size) is not int or size<11 or any(type(x) is not int or not 0<=x<size for x in positions):raise ValueError('valid finite ring positions required')
    sites=sorted(set(positions))
    if len(sites)<3:return True
    extended=sites+[x+size for x in sites[:2]]
    return all(extended[i+2]-extended[i]>=11 for i in range(len(sites)))
