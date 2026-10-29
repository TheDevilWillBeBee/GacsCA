# First authentic Workspace/native pulse, conditional on the GE0 prefix

This audits the first96Q..98Q command window after the actual shared
clock-only row0 fault on[0,17Q). Q=8192, U=128Q=1048576, lambda=24 and
c=104 are unchanged. It adds **no candidate or schedule**. It computes a
conditional native prefix using Gray p41's literal Workspace equations
and the already derived GE0 flag SimBits. Full own beta/final layout and
whole-rule refinement remain premises, and no later-period or iid result
is claimed.

Sources: Gray pp20–22 and41 in the pinned primary text;
[all-receiver first native-bank proof](GE0_GLOBAL_FIRST_FLAGS.md),
[early native evaluator](GE0_EARLY_NATIVE_FLAGS.md),
[frozen GT0 equations](gray_raw_gather.py),
[literal native equations](literal_maintenance.py),
[new finite interval kernel](ge0_first_workspace_native.c),
[checker](check_ge0_first_workspace_native.py) and
[receipt](../../../figs/gray_counterexamples/GE0_first_workspace_native_certificate.json).

## Exact conditional claim

Retain the intact-completion/own-programme premises and initial error
history of GE0. In addition, the completion must implement both of
Gray p41's Workspace equations using the **final computed SimBit** at
the stated source coordinate. This is an explicit extra refinement
premise; GE0 alone has finite late Workspace ports. Do not identify an
arbitrary port setting with a completed physical rule.

Then the native fields through physical row100Q have the exact trajectory
given by the receipt's event-compressed recurrence. At100Q they are

    GF(x)=x modQ;
    Age(x)=(100Q+1) on[0,20Q), and100Q elsewhere;
    Flag1=1 exactly on[−Q,0) union[19Q,20Q);
    Flag2=Workspace1=Workspace2=0.

The first command has grown the offset-clock interval from17Q to20Q.
It has not yet supplied a Flag2 command or recovered a common clock.
This is **not a counterexample** to Gray's reliability or a deterministic
lemma: this prefix is compatible with later repair. The receipt records
the exact first row with the20Q clock interval and the first quiet native
row of that form. Neither is a whole-rule halt or decoded-recovery time.

## Held physical source bits, rather than a preloaded command

The accepted first-bank and early-evaluation proofs deliver all five
special SimBits at Q−3 by physical80Q−1. Their value is1 precisely in
colonies

    D={−3,−2,−1,13,14,15,16,17,18,19}.

All five special SimBits at3 are0 in every colony. These are actual
outputs of the emitted native programme on the derived three History
banks, not separately prepared native commands.

GF remains canonical under arbitrary evolving private fields and flags:
both adjusted GF majorities equal x modQ, so choosing left or right gives
that GF. Consequently the mandatory wipe comparison with old raw self
GF is false. On the prefix under consideration, Ages are t or t+1;
they neither wrap to0 nor repeat80Q after this delivery. The frozen GT0
SimBit rule then only votes its held old copies: its Age0 and80Q writes
are inactive. Thus the five source copies remain equal to their delivered
value. This is a simultaneous induction with the native quotient below,
not an assumption of a globally clean new snapshot.

In particular the **computed final** SimBit at the p41 source equals the
same constant, since its actual update is this same held vote and has
no wipe. It would also equal a pre-wipe intermediate on this particular
prefix. The equality does not repair the earlier all-raw locality/order
obstruction: no radius-five completion or unconditional interpretation
change is asserted here.

Workspace2 is0 because its source SimBit3 is0, irrespective of the
computed Flag1 condition. Therefore native Flag2 remains0: canonical GF
makes the apparent colony exist, all old Flag2 inputs are0, Workspace2
is0 and neither remaining Flag2 source applies. The printed and h1
Flag2 predicates agree on this trajectory.

## Exact binary native quotient and row convention

Let L(x,t) in{0,1} denote the clock offset from the common physical
base t, F the native Flag1 and W the old Workspace1. GF is canonical;
Flag2 and Workspace2 are0. Define

    R = majority_5(L(x+1),...,L(x+5));
    A = majority_5(L(x−1),...,L(x−5));
    C = {j in[−5,5] : 0<= (x modQ)+j <Q};
    I = count{j in C, j<0 : L(x+j)!=R};
    H = count{j in C, j>0 : F(x+j)=1};
    Z = count{j in C : W(x+j)=1}.

The literal native equations reduce exactly to

    F_new = (I>=3) or (Z>=3) or (H>=3) or (F(x) and H>=2);
    L_new = A if F_new else R;
    W_new = 1 iff floor(x/Q) in D, x modQ>=Q−5,
                    and96Q<=t+1+L_new<98Q.

The last equation is the literal p41 Workspace1 predicate. The numerical
Age used in that predicate is the **computed output** Age. An input row
t therefore produces output row t+1, and new Workspace enters the native
Flag1 rule only on the following update. The source gate is half-open;
no98Q endpoint is silently included.

Both Age majorities exist because the five values are drawn from two
distinct legal Ages. For this finite prefix t+1<=100Q<U, modulo wrap
does not change their binary labels. GF mismatch contributes nothing,
and apparent-colony existence is automatic. These facts prove the
quotient directly from the literal scalar equations. Arbitrary private
fields cannot enter it once the held command and literal Workspace
premises are established. It covers arbitrary binary labels/F/W on the
line; its use here does not assume a sharp clock interval at intermediate
rows.

At physical row96Q−2, the command window has not begun and the accepted
native prefix supplies

    L=1 on[0,17Q);
    F=1 on[−Q,0) union[16Q,17Q);
    W=0.

The interval kernel updates from that exact row through100Q. The earliest
new Workspace1 in an offset colony may occur at physical96Q−1, because
its computed Age is96Q. This phase offset and the old/new Workspace lag
are explicitly included.

## Infinite-line event compression and its certificate

Encode the triple(L,F,W) as L+2F+4W on maximal integer intervals, with
zero exterior. This is a finite representation of a configuration on
the **infinite line**, with no ring or imposed boundary values. At any
row the new nonzero support lies in the union of

1. the old nonzero hull enlarged by5 sites at each end; and
2. the finite fixed source strips[gQ+Q−5,(g+1)Q), g in D.

Outside that union all eleven old label/flag/Workspace triples are0 and
the command gate is off, so the new triple is exactly0. The C kernel
chooses this derived hull anew on each update; it does not assume a fixed
spatial envelope. Its implicit exterior therefore equals the true
infinite-line exterior by induction.

Within the hull, cut at every old interval boundary shifted by each
integer d from−5 through5. Also cut at every colony boundary shifted
by those d, and at each colony's source-strip start Q−5. On each integer
interval between consecutive cuts, all eleven old triples, the in-colony
membership predicates, the source command and source-strip predicate are
constant. The displayed quotient hence returns one constant new triple.
Evaluating one representative is exact for every site of that interval.
Adjacent equal intervals can be merged without changing the infinite
configuration. This proves the kernel's event-compression step and its
composition over all retained finite rows.

The kernel uses signed floor division for negative colonies. Capacities
are checked by assertions; the receipt records their attained maxima,
not an assumption that overflow is harmless. The trace checksum records
every row's complete normalized interval state. It is an instrument for
replay, not a cryptographic or mathematical proof by itself.

The independent Python checker invokes the actual literal scalar native
transition on both endpoints of every event interval at retained rows.
It also checks consecutive retained rows and final exact segments. This
supplements the quotient/partition proof and catches source-lag, phase,
negative-coordinate and endpoint mistakes. The retained C output is
pinned with the compiler flags/version and binary/source hashes. A
replay reconstructs the same deterministic finite result.

The output at100Q is exactly the displayed three normalized segments.
The two flag strips and offset clock interval match the accepted quiet
aligned native-family form with m=20. A later Workspace command or
programme/commit event may alter that state; none is assumed absent for
all future time. The mathematical stationary-form observation is not a
continuing full-GE0 orbit theorem.

## Status

| Step | Status |
| --- | --- |
| Actual first bank/early programme/source bits from one original real2 | **previously proved conditional components; reused** |
| Held computed final SimBit and canonical GF on this prefix | **proved conditional on retained GT0 and literal late Workspace equations** |
| Binary native/Workspace quotient and old/new row convention | **proved algebraically from printed equations** |
| Infinite-line event compression and all-row finite prefix to100Q | **proved exact finite computation with pinned receipt** |
| Actual scalar endpoint checks at retained event rows | **finite checks; supplementary to the quotient proof** |
| First pulse gives20Q offset interval/common-clock recovery absent | **proved conditional prefix; not a theorem refutation** |
| Complete own beta<=Q, final hierarchy/layout and all-raw late order | **unproved completion premises** |
| Later native banks, eventual Flag2 repair, full period or higher errors | **unproved** |
| Literal Gray counterexample, iid reliability/memory failure or shorter U | **unproved; not claimed** |

No previously accepted source/receipt, active rule or schedule is changed.
