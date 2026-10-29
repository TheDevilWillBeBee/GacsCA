# SP28: coherent unused Info is allowed at the initial boundary

This proves an extension of ROBUSTNESS J138 for the existing isolated
SP28 artifact. It changes no transition equation, parameter, ROM or
registered candidate. It does not prove an iid noise threshold.

Write F for the fixed SP28 rule, Q=1024 and U=475136. Its 842 normal
Info primaries have phases 59 through 900, in its certified layout.
Let B(z,b) be the following computed lower configuration. GF(x)=x mod Q,
Age(x)=0, and every field other than GF and Info is zero. At each normal
primary jQ+a, Info has the corresponding bit of upper configuration z(j).
At the other 182 primary phases per colony, Info has an arbitrary bit
b(j,a). Each logical Info value has five coherent physical copies in
the prescribed slots. This includes copies straddling colony edges.

The narrow encoding E(z) in J138 is a member of this family: b at phase
58 equals z(j).Flag2, b at 965 equals z(j).Flag1, and every other unused
primary is zero. J139's tilde-E(z,a2,a1), with independent auxiliary
flags, is also a member of B(z,b). Membership says nothing about whether
z is the original undamaged upper data.

**Theorem.** Let w0=B(z,b), X_t=N_t(w_t), and w_(t+1)=F(X_t). Suppose
the complete overwrite location set, including input time zero, is an
actual global E0 set: singleton or spatial adjacent-pair groups at one
tick, separated 24 from every other error. Payloads are arbitrary. Then
for all n>=1,

    w_(nU) = E(F^n(z)).

At all nU, including n=0, the raw five-copy decoder of the normal
primaries returns F^n(z). The identity concerns computed states before
fresh overwrites. No real level-1 or higher errors are allowed.

**Proof.** J138's native induction permits arbitrary other fields and
instruction inputs under E0. Consequently every refined raw GF/Age
pair is the correct canonical/common pair. The actual copy keep is one
at every holder, even during native Flag1 pulses. The proof therefore
does not require that unused Info be initially zero in order to prevent
GF-dependent erasure. Native epoch births/force and the remaining
service circuit have no direct Info input.

Until clock T_wf=278401, the literal WF1 output is zero, regardless of
the Info read. Computed Flag1 remains zero before that window: initially
Flag1 and WF1 are zero, correct native geometry has no diagnostic
source, and E0 cannot supply three flag faults in a five-vote input.
This is the same pre-pulse induction as J138, with the now explicit
observation that its WF1 premise uses the clock guard, rather than a
zero Info3 or Info1021 premise.

Away from commit and the special signal write, every Info primary is
replaced by its own fivefold majority. The only pre-commit special writes
are at phases 3 and 1021, both outside the normal layout. All normal
Info values are therefore constant until commit. Every current E0 set
has at most two corrupt holders in each such vote, so all five next
computed copies of each primary agree on its previous logical bit.
This argument also holds for arbitrary unused primaries and for their
copies across a colony edge.

Each gather loads the current logical Info into mail. The corrected
SP28 fast window performs exactly |d|Q/8 shifts of speed eight before
an offset d capture. Hence a capture at normal primary jQ+a reads the
reference primary (j+d)Q+a, with exactly the same phase a. All 25,284
requested gather coordinates in the three gathers preserve a normal
phase. No auxiliary or unused primary enters a requested history input.
Current E0 faults are corrected by the five-holder votes throughout
this physical transport, exactly as in J138.

The audit of all 130,974 actual nonzero instructions checks both operands,
261,948 reads. Of these, 1,368 direct Info reads and 17,715 history reads
are at normal primaries, with every history selector in its certified
profile. All other operands are registers, scratch or constants. No
instruction reads unused Info, the old auxiliary flags, or an initially
unspecified Hold. As in J138, zero instruction words preserve register
0, and the abstract certificate proves that each used register and
scratch operand has the required prior value. Thus the physical
register/pending/scratch induction has exactly the same input values
and visits as for E(z). The existing own-programme certificate gives
all 842 final Hold outputs and the two early auxiliary Hold stores as
F(z), for every z.

Both early stores precede the courier loads at 278343 and 278344. Those
loads replace the relevant mail references with the newly computed
flag values, independently of old mail from unused Info. The certified
courier paths reach phases 3 and 1021 at signal clock T_sig=278400.
The special write creates their new Info values in computed state
T_sig+1=T_wf. Thus the first enabled WF1 read already sees the newly
computed flag source, even if either special Info primary was one at
time zero. The protected Flag2 courier and all later source/flag
arguments of J138 apply without a changed premise.

Later Flag1 can gate mail but cannot erase already completed histories,
registers, scratch or Hold, since keep is one. J138's source-free flag
quieting and literal commit identities apply. At commit, all fields
other than GF/Age/Flag1/Info are zero, native GF/Age/Flag1 are
canonical/zero/zero, and all unused Info primaries except the two
reserved flag copies are zero. Normal outputs and both auxiliary
outputs are the certified values of F(z). This is precisely E(F(z)).
J138 supplies every subsequent complete-start period, proving the
computed identity for all n>=1. At a boundary, each normal primary
has five coherent copies and at most two current corrupted holders,
so raw decoding is exact, also at n=0. QED.

The checker pins the existing physical/abstract certificates and exact
generated source, and audits every instruction operand and every gather
reference. It is an exhaustive symbolic/source interface audit, not a
sampled C or CUDA trajectory. Its receipt is
`figs/robustness/SP28_encoding_family_certificate.json`.

**Limits.** J139 supplies B-shaped data on a recovered half-line, not
globally, and gives unspecified upper z. Applying this global theorem
to a half-line requires an additional physical locality/native boundary
argument. This document proves neither that extra argument, original
data recovery, a confined upper overwrite map, higher-island repair nor
a positive iid noise rate. In particular, it does not reassert J139's
withdrawn immediate narrow-encoding identity from arbitrary work.
