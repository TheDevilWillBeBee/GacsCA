"""One fixed Q8192, U=2^20 candidate clock for the dual-pass rule.

Three original 16Q stream frames remain disjoint. The early evaluator and
short SEND tail finish before the signal capture; the Wf interval ends before
the final evaluator. These are fixed rule constants, never depth selectors.
"""
Q=1<<13
T=1000000
U=1<<20
RESET_AGES=(0,16*Q,32*Q,84*Q,88*Q)
ACTIVE_ENDS=(16*Q,32*Q,79*Q,88*Q,127*Q)
VOTE_AGES=(48*Q,88*Q)
CAPTURE_AGE=80*Q
WF_START=84*Q
WF_END=86*Q

assert RESET_AGES[2]+16*Q<=VOTE_AGES[0]
assert VOTE_AGES[0]+2+8*Q<ACTIVE_ENDS[2]
assert ACTIVE_ENDS[2]<CAPTURE_AGE<WF_START<WF_END<RESET_AGES[4]
assert RESET_AGES[4]+2+8*Q<U
