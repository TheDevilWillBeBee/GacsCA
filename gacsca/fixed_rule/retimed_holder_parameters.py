"""One fixed shortened schedule; depth is not an input to these constants.

The physical Age field remains 32 bits. Both scalar and described maintenance
advance modulo U=2^31, so unused high-Age states fold back after one step.
"""
Q=1<<15
T=1000000
U=1<<31
RESET_AGES=(0,150000000,290000000,1230000000,1232000000)
ACTIVE_ENDS=(149000000,288000000,1228000000,1231000000,2025000000)
VOTE_AGES=(430000000,1232000000)
CAPTURE_AGE=1224000000
WF_START=RESET_AGES[3]
WF_END=WF_START+2*Q
assert U&(U-1)==0
