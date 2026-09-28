"""One globally fixed AND candidate; neither Q nor U depends on depth.

Address remains15bits and Age32bits; arithmetic uses explicit Q/U moduli.
"""
Q=1<<14
T=1000000
U=1<<29
RESET_AGES=(0,28000000,56000000,114000000,116000000)
ACTIVE_ENDS=(27000000,55000000,113000000,115000000,500000000)
VOTE_AGES=(84000000,116000000)
CAPTURE_AGE=110000000
WF_START=RESET_AGES[3]
WF_END=WF_START+2*Q
assert Q&(Q-1)==0 and U&(U-1)==0
