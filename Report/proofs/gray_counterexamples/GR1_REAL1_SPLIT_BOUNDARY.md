This proves a counterexample to an arbitrary-upper-state real1-to-two-cell
boundary map for the explicitly changed GR1 rule. It does not refute
Gray's intact recursive construction, the accepted GR1 pure-E0 theorem,
or iid memory reliability. No rule or constants are changed.

Use F, Q8192, U1048576, the pinned GR1 ROM, broad encoding E and decoder
Δ5 from GR1_E0_PERIOD.md. Let z be the following upper raw configuration.
All upper native Address/Age fields are canonical/0 and all Flags0.
All other upper bits are0 except these four raw Info copies:

    holder−3 Info slot4 =1,
    holder−2 Info slot3 =1,
    holder−2 Info slot4 =1,
    holder−1 Info slot3 =1.

Upper Info slot b stores the copy of logical Info at holder+b−2. Logical
Info−1 and Info0 therefore each have two1 and three0 copies. Their copy
held at upper holder0 (slots1/2 respectively) is0. The four other holders
split two0/two1. This upper z is deliberately incoherent in its Info
backups; E(z) nevertheless exists because E encodes every arbitrary raw
upper configuration in coherent lower Info copies. It is not an intact
recursive hierarchy initialization.

Start any E(z) member with unrepresented lower logical Info0 and run
cleanly until the second gather snapshot time

    T=32Q+1=262145.

In lower colony0 every represented Info bit is0, because the entire raw
upper cell0 is0. In particular upper Info slots1/2 have pinned primaries
a1=3989 and a2=4092. Apply errors at

    (3988,T), (3989,T), (3990,T),
    (4091,T), (4092,T), (4093,T).

At each holder x=a+d, d∈{−1,0,1}, modify only the components that copy
logical lower bit a: its Info and Mailbox.R copies become1, its
History2 own-input (lane5) copy becomes1. Leave Mailbox.L at its correct0
and leave every other field/bit untouched. The copy slot is2−d. Age and
Address are never overwritten.

**Error classification: proved.** The six points form one original
real1 error with λ24/c104. There is no E0 point: within each three-point
core every singleton/adjacent pair has another linked point. Candidate1
subsets must include at least two points in one core, since the two cores
are more than24 apart. Every such left/right pair of minimal candidate1
subsets has two points less than104 apart: the worst nearest distance
is4092−3989=103. Condition(iii) therefore holds, even though the total
point width106 exceeds the sufficient104-wide test. Condition(iv) is
vacuous because there are no other errors. The exact classifier agrees.

**One-clean-tick injection/coherence: proved.** At T the clean lower
Info and both mail snapshots are0 near the two primaries. History2 has
just captured the own input0. Retained History1 is coherent, with the
already gathered upper z bits. In the next clean update the three wrong
holders win each five-copy vote. Logical Info(a)=1, Mailbox.R(a+1)=1
and History2-own(a)=1 have five coherent copies. All other output
components agree with the clean transition. The two cores do not interact
in this one-step dependency cone. The checker evaluates64 complete
literal GR1 cofactors with free coherent retained History1 and proves
13120 output/lookup identities. Its changed-output list fixes every
altered component; this is a universal local Boolean certificate, not
a sampled long trajectory.

Native controls stay correct and Flags quiet throughout the period.
There is no native error at the injection. Only simulated upper Info
bits differ in the gathered inputs; upper native fields remain canonical,
Age0, Flags0. Both versions of the early native-Flag computation are0.
Consequently the couriers write0 and the lower Workspace pulse never
creates a source. The five-copy transport/frame lemmas apply after the
one-step coherence certificate, with wipe0 and unblocked mail. The only
intermediate lower Info writes have logical Address3 and Q−3 and do not
change a1/a2.

**Three histories and local simulated inputs: proved.** History1 was
gathered before the errors and sees upper holder0's Info slots1/2 as0.
The second snapshot's right-moving packet has been changed to1 and
its left-moving packet remains0. By the33 exact gather coordinates,
History2 sees those two source bits as0 at receivers j<0 and1 at
receivers j>0. For j=0, the explicit History2-own overwrite supplies1;
this is needed because GR1's own capture precedes fresh errors at T.
History3 sees the persistent new Info1 in both directions and at self.
All other simulated input bits retain their clean values.

The temporal vote therefore sees upper cell0's two changed bits as0 for
receiver j<0 and1 for receiver j≥0. Define q^(j) as z with cell0 Info
slots1/2 changed to1 if j≥0, otherwise z. The physical final replay at
receiver j supplies exactly the window of q^(j) to the universal own
programme. Its key/fetch and front/pending-store lemmas are unchanged;
the early residue is not used. Define

    Y_j = F(q^(j))_j.

At the usual boundary every colony commits the computed Y_j, all private
fields reset and native controls/Flags are canonical/quiet. Thus the
actual noisy lower state X_U belongs to E(Y) and Δ5(X_U)=Y. This physical
composition reuses the exact clean route/frame/programme certificates
after the proved injection; it does not reuse a pure-E0 hypothesis for
this real1 error. There is no million-tick sampled run in this proof.

**Upper copy patterns: proved.** The upper computed Age is1, with correct
Address and Flag1=0, so upper Info simply takes its fixed five-holder
majority. Six complete upper netlist cofactors give:

    logical Info0, holders−2,…,2:   (0,0,1,1,1),
    logical Info−1, holders−3,…,1:  (0,0,0,1,1).

Each vote is decided by holder0's perceived copy: its other four raw
copies split two0/two1. Different receivers have therefore computed
different values for copies of the same logical upper bit.

**No common adjacent exception pair: proved.** Suppose v differs from z
only in a singleton or adjacent pair P of arbitrary upper full states.
Three correct directional Address/Age words restore the canonical
Address/common Age. At most two in-colony mismatches cannot create
inconsistency; Flag1 forcing needs three distinct positive sites, and
the h1 Flag2 rule also cannot retain/create a positive bit from only
two errors. Thus every computed upper Flag is0, computed Age1, and the
GF-dependent wipe is0. These assertions do not require upper simulation
copies to be coherent. Every Info output of F(v) is consequently the same
five-holder vote for its logical group, at every holder of that group.

Suppose further Y differs from F(v) only inside an output adjacent pair R.
For logical Info0 a common vote0 would leave three wrong output holders,
which two exceptions cannot cover. Its common vote must be1, forcing
R={−2,−1}. For logical Info−1, outside that pair both holder−3's0 and
holders0/1's1 remain. No common vote matches them. This excludes R,
independently of P or its replacement states. Therefore there are no v,
P,R such that

    v = z outside P,       Y = F(v) outside R,
    P,R each singleton or one adjacent pair.

The contradiction also excludes using the same pair for input/output.
It refutes that map for arbitrary upper raw states in E(z), for the
fixed GR1 rule and one valid real1 error. It does not establish a decoded
memory failure from an intact hierarchy: z's four incoherent Info copies
are outside that initialization. Gray faithfulness remains unproved,
including the gather layout, two-index ROM, current-SimBit Workspace
adaptation, h1 correction and damaged-state rest semantics. No positive
iid rate or iid unreliability conclusion follows.

The receipt pins the written composition and every reused physical
certificate. All states and choices are explicit, and all purported
universal local claims use Boolean identities or the stated whole-word
majority/count argument. This is not a proof-assistant formalization.
