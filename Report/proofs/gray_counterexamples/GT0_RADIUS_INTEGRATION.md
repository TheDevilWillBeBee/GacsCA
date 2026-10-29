GT0's late SimBit equation cannot be combined literally with Gray's
native equations and computed-SimBit Workspace.Flag2 read in a radius5
rule on every raw state. This is an exact local-component obstruction,
not a counterexample from an intact hierarchy or an iid-memory result.
It discharges the earlier conditional witness's no-other-SimBit-write
premise for GT0's actual emitted component only. It does not establish
that every possible implementation of Gray must have that equation.

Let Q=8192, U=128Q and t=96Q. Take the two raw native configurations
from check_computed_simbit_radius.py: Age=t and both native and Workspace
Flags0 everywhere; Address=x modQ except Address(-2), Address(-1) and
Address(0) are increased by1, Address(4) and Address(5) are increased by2,
and Address(8) is8 in A and10 in B. Extend both configurations identically
to all other sites. Make every stored SimBit copy1 and every other GT0
data bit0. In particular the two full raw configurations agree at every
site except8, so their radius7 neighbourhoods about0 are identical.

Exact native Boolean evaluation gives, in both A and B, computed
Address(0)=0, computed Age(0)=t+1 and computed Flags(0)=(0,0). At site3,
the computed Age is t+1 in both. In A the computed Address is3 and
Flag1=0; in B the computed Address is4 and Flag1=1. Raw Address(3)=3
in both. Thus the p33 mandatory simulation wipe is false in A and true
in B at site3. All raw Flag2 inputs are0, so the printed predicate and
the explicitly corrected h1 predicate agree on these native evaluations.

Now use GT0's actual emitted equation for primary SimBit3. At computed
Age t+1, its Age0 commit and selected special-source write at80Q-1 are
both disabled. Its value is exactly the five-holder vote of current
SimBit3, followed by the native wipe mask. That vote is1. The emitted
netlist therefore gives computed primary SimBit3=1 in A and0 in B, for
every choice of the still-unimplemented early flag and final programme
ports. The checker leaves all those ports symbolic; no no-other-write
assumption is supplied for GT0.

Gray's printed p41 Workspace.Flag2 equation at0 now reads that computed
SimBit3: computed Address0 is in[0,4], computed Age0 is in[96Q,98Q), and
computed Flag1(0)=0. It gives Workspace.Flag2(0)=1 in A and0 in B.
The computed native wipe at0 is false, so the p33 mask there cannot
erase this difference. A radius5 rule, and even a radius7 rule, cannot
distinguish A and B at0. Hence any full raw-state transition preserving
these three component equations requires radius at least8. This bound
is necessary, not sufficient: neither a radius8 completion nor the
complete dependency radius has been constructed here.

The older conditional one-tick location set [-5,8] at time96Q is one
original lambda24/c104 real1. That combinatorial classification does
not establish that either raw state is reachable at that clock from
Gray's initialization under one admissible physical history. This
certificate makes no such reachability claim and does not substitute
current SimBit for computed SimBit. A faithful completion must explicitly
resolve this local integration conflict; a changed Workspace read,
changed SimBit equation or enlarged neighbourhood is a rule change.
