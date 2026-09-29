"""Exact synchronized right-one/left-zero flag trajectory from the prefix.

This restricted physical state family has a symbolic one-step certificate; it
is not a replacement for arbitrary flag dynamics. The physical rule is unchanged.
All colonies must start at Age WF_START-1 with zero flags/Wf, a coherent right Signal
one, left Signal zero, canonical geometry and mail-free coherent procedures.
"""
from . import retimed_holder_rule as f

START=f.WF_START-1


def interval(age):
    """Half-open interval of Flag1 ones in one colony, absolute suffix Age."""
    if not START<=age<=f.U:raise ValueError('suffix interval required')
    if age<=f.WF_START:return (0,0)
    if age<=f.WF_END:return (max(0,f.Q-8-3*(age-f.WF_START-1)),f.Q)
    return (0,max(0,f.Q-2*(age-f.WF_END)))


def bits(age,address):
    if not 0<=address<f.Q:raise ValueError('physical Address required')
    lo,hi=interval(age)
    return (int(lo<=address<hi),0,int(f.WF_START<=age<f.WF_END and address>=f.Q-5),0)


def signal(address):return 1<<(f.Q-1-address) if f.Q-5<=address<f.Q else 0
