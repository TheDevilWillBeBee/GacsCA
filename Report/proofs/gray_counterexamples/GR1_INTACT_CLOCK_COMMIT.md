The five-site clock/commit and three-colony Mailbox witness can start in
an intact recursive hierarchy of the fixed, explicitly changed GR1 rule.
This strengthens its initialization premise. It does not give a decoded
memory failure or a counterexample to a faithful Gray completion. In fact,
the same proof below gives the correct first decoded boundary for this
particular error.

Use GR1's existing Q=8192, U=1048576, lambda24/c104, pinned386-bit schema,
layout and hardwired two-index ROM. Let E be the broad encoding family in
GR1_NOISELESS_PERIOD.md. No source, ROM, constant or active rule changes in
this certificate. GR1's h1 Flag2 correction, current-corrected-SimBit
Workspace equation, private rest convention and uncompiled Gray
ProgramBits remain its explicit departures.

**Stationary all-level initialization: proved.** Write ell(f,b) for the
represented primary of upper field bit(f,b). These386 primaries are
distinct and lie strictly between3850 and4342. In particular they exclude
the near-boundary residues0,1,2,3,Q−3,Q−2,Q−1. The five Info primaries are
3891,3989,4092,4188,4286.

Define a Boolean D(x) on every integer x. Put i=floor(x/Q), a=x modQ.
If a is an Address-bit primary ell(addr,b), let

    D(x) = bit_b(i mod Q).

If a is an Info-slot primary ell(info,b), b=0,...,4, let

    D(x) = D(i+b−2).

At every other represented or unrepresented primary let D(x)=0.
This is a well-defined recursion on |x|. Any Info-tag argument has
|x|>=min(3891,Q−4286)=3891. Its next argument satisfies
|floor(x/Q)+b−2|<=|x|/Q+3<|x|. This bound covers negative integers under
floor division as well as positive integers. Thus each call terminates
and defines a unique D on the whole integer line. The construction does
not depend on a hierarchy level or a finite spatial boundary.

Define the raw configuration H at every level by

    H_x.Address = x mod Q;
    H_x.Info[b] = D(x+b−2), b=0,...,4;
    H_x.Age = H_x.Flag1 = H_x.Flag2 = 0;
    H_x.Workspace.Flag1 = H_x.Workspace.Flag2 = 0;
    every other raw simulation/private bit = 0.

All five holders of logical Info x read exactly D(x): holder x−s,
slot s+2 reads D(x−s+s)=D(x). For every upper position i and every
represented bit(f,b), the defining cases give

    D(iQ+ell(f,b)) = H_i[f,b].

For Address this is the first case; for all five Info slots it is the
recursive case; for Age, four flags and all remaining simulation/private
fields both sides are0. This proves H in E(H), including the redundant
Info copies. Choosing X^(n)_0=H for every level n supplies an actual
intact infinite recursive GR1 initialization. The accepted noiseless
encoding theorem also proves its continuing noiseless hierarchy at
macro-boundaries. It is not an initialization for an unproved Gray
single-ProgramBit physical interpreter.

Unused logical primaries and both special pulse primaries3,Q−3 are0 by
definition. D(−2),...,D(2)=0 because their residues are unused. Consequently
the complete raw cell H_0 is0, including Address and all five Info slots.
Every logical Info bit in lower colony0 encodes a bit of this H_0 or an
unused0, so is0. Its backup holders at the two edges also see unused0
residues outside the colony. The retained512-site initial cone of the
old clock checker therefore agrees bit for bit with H. Outside colony0
other colonies recursively encode their parents; they are not assumed
to have zero simulation information.

**Error and transfer of the native trajectory: proved.** At physical
time1, overwrite only Age=U−1 and all five Hold bits=1 at positions
3865,...,3869. This is the unchanged original real1 location set in
GR1_REAL1_CLOCK_COMMIT.md. It is globally real1 in the complete error set
consisting of these five points: there are no earlier or later errors.
It needs no independently supplied upper error. The actual errors do
not overwrite Address or Info.

The old finite full-net cone applies verbatim because all of its initial
ancestors lie in colony0 and equal H there. At clean time2 the wrong Age
island is3868,...,3872 at Age0. At time3 Info is coherent with D changed
only at3868 and3869. The old620-cofactor native/count induction transfers
to the entire line: native decisions use only Address, Age and the four
flags; all initial flags are0; both Workspace outputs are0 before96Q,
independently of the nonzero recursive Info elsewhere. The wrong clock
labels are t−2 and t, and never enter the Workspace pulse during recovery.
Address is canonical even before Age healing, hence every GF-dependent
simulation wipe is0. The island stays in colony0 and disappears by1444.
Canonical/common native closure then holds globally. The clean Flag
clearing proof gives native flags0 by9636<32Q. No additional spurious
Age0 commit or simulation front window occurs before native recovery.

After time3 Info evolves by the same coherent five-holder vote until the
ordinary boundary, except for the special pulse sources3,Q−3. The two
changed logical primaries are neither special source. Thus their values1
persist. No raw-GF wipe is possible, even if a native flag is temporarily
nonzero. Retained first histories can be wrong; no first-gather correctness
assumption is made.

**Later histories and early flags: proved.** Stage2's reset at32Q occurs
after geometry and both native flags recover. Stage3's reset at64Q also
has correct controls. Each gathers the coherent logical configuration
D' obtained by flipping D(3868)=D(3869)=0 to1. The exact stage routes and
copy votes apply globally, including every receiver tuple used by the
early and final own programmes. All later histories finish by565245,
before the early interpreter starts at70Q=573440.

Only3868 is represented, as upper Reg bit2 at position0;3869 is unused.
Let q be H with that one raw upper Reg bit changed to1. Both later
history banks therefore encode q for every represented field and all11
input offsets. In particular their native Address, Age and four flag
bits are precisely those of H. Hist1 may be any bit; the Boolean
identity majority3(a,b,b)=b makes both early temporal votes and the fresh
112Q+1 voted bank exact for every bit of q. A retained history's five
copies become coherent after recovery by one vote update; later resets
and snapshots then use the proved clean transport identities.

The compiled Flag1/Flag2 output support contains only the native fields,
with no simulation-data or instruction-bit dependence. For canonical
Address, common upper Age0 and four native/Workspace flags0, the literal
native transition has Flag1=Flag2=0 at every one of the8192 Address
phases. The checker certifies these actual equations and the support
restriction, rather than assuming the early flag results. Hence the
own-programme prefix stores both early outputs0 at every receiver. Both
flag couriers carry0, the special Info pulse primaries stay0, and the
physical Workspace outputs are0 throughout96Q..98Q. Native flags remain0
after their early clearing. The final interpreter has correct clocks,
votes and cleared service fields; its standard route/Fetch/Match/pending
composition is the already certified GR1 composition, with input q.

**Pointwise footprint from an intact hierarchy: proved.** At32Q+1 the
second Mailboxes snapshot D'. At

    T = 32Q+1+4325 = 266470 < 48Q,

the changed Info3868 is still1 and the two coherent streams carrying it
are at Mailbox.L(−457) and Mailbox.R(8193), also1. The noiseless reference
from H has0 at all three corresponding fields. The geometry and flag
recovery proof and the certified stage2 route give this exact finite
coupling; no million-tick simulation is used. These simultaneous sites
are in colonies−1,0,1. No fixed adjacent two-colony interval contains
all pointwise simulation-field differences. This refutes the analogous
literal all-SF envelope for GR1 even with the intact recursive initial
hierarchy just constructed. The time/space location set satisfies the
original real1 isolation hypotheses because it is the entire physical
error set. It strengthens the old witness's initialization scope only.

**First decoded boundary is correct for this error: proved.** Both good
history banks encode q, so the same physical programme composition gives
X_U in E(F(q)). The changed q bit is a single raw compact-register copy
at upper cell0. All upper registers initially0. Every GR1 register read
is a five-holder majority, which remains0 under that singleton raw
change; no raw register bypass is used by the pinned mux-front operator.
All other inputs are identical. Equivalently, the checker evaluates the
complete pinned upper netlist at positions−5,...,5 with shared symbolic
instruction bits and obtains equality of every output for q and H.
Outside that interval local radius5 proves equality directly. Thus

    F(q)=F(H), and X_U in E(F(H)).

The represented wrong Reg copy and unused Info bit produce a real
temporary transport footprint, but this first decoded boundary is
correct. With no later errors, the accepted noiseless encoded-period
theorem gives the correct continuing boundary hierarchy. This result
does not prove a recovery theorem for arbitrary real1 errors.

The initializer and checker are gray_recursive_initialization.py and
check_gray_staged_intact_clock_commit.py. The receipt pins the old cone,
620 native cofactors, all8192 new native flag cofactors, all-field
recursive encoding cases, full upper counterfactual equalities and
transport/programme dependencies. The universal recursive and temporal
composition arguments above are part of the proof; finite examples of
large coordinates are corroboration, not its basis. Literal Gray
refinement, Gray ProgramBits, higher errors and iid reliability remain
unproved.
