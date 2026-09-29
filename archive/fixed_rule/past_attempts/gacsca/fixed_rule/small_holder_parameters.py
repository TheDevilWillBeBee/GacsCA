"""One fixed smaller-colony schedule, independent of requested hierarchy depth.

Time is measured in literal local updates. T is a convenient constant for
placing phases; it is not the colony length or an externally selected level.
"""
Q=1<<15
T=1<<25
U=1<<32
RESET_AGES=(0,8*T,16*T,64*T,68*T)
ACTIVE_ENDS=(6*T,14*T,60*T,66*T,104*T)
VOTE_AGES=(22*T,68*T)
CAPTURE_AGE=59*T
WF_START=RESET_AGES[3]
WF_END=WF_START+2*Q
