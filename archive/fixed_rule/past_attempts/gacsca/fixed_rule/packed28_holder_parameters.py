"""One globally fixed AND candidate; neither Q nor U depends on depth.

Address remains15bits and Age32bits; arithmetic uses explicit Q/U moduli.
"""
Q=1<<13
T=1000000
U=1<<28
RESET_AGES=(0,20000000,40000000,80000000,82000000)
ACTIVE_ENDS=(19000000,39000000,74000000,81000000,256000000)
VOTE_AGES=(60000000,82000000)
CAPTURE_AGE=76000000
WF_START=RESET_AGES[3]
WF_END=WF_START+2*Q
assert Q&(Q-1)==0 and U&(U-1)==0
