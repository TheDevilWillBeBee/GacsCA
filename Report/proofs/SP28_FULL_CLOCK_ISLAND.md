# A full-SP28 finite clock island travels forever

The existing isolated SP28 rule has a noiseless travelling native-clock
island after one finite physical error burst. This is a theorem about
the full rule, with its actual packet/code transitions and arbitrary
simulation/workspace evolution. The externally auxiliary-zero operator
of J150 is not used during the active pulses. SP28, G17, all constants,
ROMs, compilers and backends remain unchanged.

The theorem refutes fixed finite space-time confinement of every finite
higher error for SP28. It does not refute G17, Gray or Gacs, or prove iid
unreliability: the native Address is always correct in this trajectory,
every fixed site eventually recovers its clock, and the error history
has no later errors. An alternative probabilistic proof allowing such
travelling defects is not excluded. No smallest sufficient reliability
change is proved.

## Exact statement

Use SP28's Q=1024, U=475136, TF=278401, epoch force length4096 and
packet/code lifetime1792. At initial time0 take canonical raw GF,
Age0 outside [a,b), Age TF inside it, where a=128Q, b=144Q. Raw Flag1
is1 on [a-Q,a) and [b-Q,b), zero elsewhere; raw Flag2 is0. Initialize
both Workspace flags, packet/code headers and backward pressure to0.
Every other simulation field may be arbitrary. Apply the actual fixed
SP28 rule thereafter with no errors.

At every nU, n>=0, its raw native state is the initial native state
translated by -23nQ. The auxiliary flags/headers/backward pressure are
zero at those boundaries. In particular the wrong-clock interval is

    [a-23nQ,b-23nQ),

still16Q wide, for every n. Actual private simulation fields need not
return to their initial values. The proof allows arbitrary values of
every instruction input at every update, so in particular applies to
SP28's actual fixed own ROM.

This state can be produced by one finite error at time U from an intact
recursive initialization, described below. At separation c=16 its full
error set is one actual real3; at c=104 it is one actual real2. The
trajectory therefore contradicts any assertion confining all damage
from this event to a fixed finite spatial interval or a finite time box.
It does not contradict the proved E0/real1 native theorem.

## Full-rule closure and temporal bounds already proved

J152 proves canonical GF/keep=1 closure even for arbitrary raw Ages and
auxiliary fields. It also proves closure of the two legal clock labels:
at time t every raw/computed current Age is either t or t+TF moduloU.
Thus the complete native state can use a binary clock label, with all
native GF votes existing and canonical. Those are full-rule conclusions,
not prescribed native controls.

Under the stated initially empty auxiliary headers, births occur only
in rows0 andTF moduloU, separated by at least196735. Every surviving
valid packet/code counter is the batch's age. No valid record survives
past state b0+1792 for birth row b0; all headers are zero at b0+1793.
WorkspaceFlag1 is supported only at true colony ends and in states
b0+1,...,b0+2048, whatever the actual corrected Info signal. Computed
backward forcing is contained in [b0,b0+1792]. On every row outside the
two4096-row force slabs, full native updates equal the auxiliary-zero
operator on the same native input. J150's force-free aligned-template
invariant is consequently available after, but not within, each slab.

## Exact packet/code quotient during a pulse

Each packet birth is at true GF1,...,5 with tag GF-1. A qualified packet
output preserves its integer origin r=x-tag. To see this without a
modular assumption, raw tags lie in [0,5), and subtracting an offset
in[-5,5] can wrap only into the excluded gap [5,16). Therefore an
accepted adjusted tag in[0,5) has no wrap and preserves r exactly.
Every valid packet origin is jQ+1, and its support stays within
[jQ+1,jQ+5]. A radius5 neighborhood sees at most one such origin.
All live counters in a batch agree. The packet quorum is therefore
exactly a count of at least three raw valid packets in eleven sites;
qualification additionally requires the reader's GF in1..5 and counter
<1791. The unchecked packet-any-cohort force retains its final expired
row, as in J152. Raw WF2 equals packet_valid throughout.

An eligible packet contributes a code position tag+6. Its integer code
origin is consequently jQ-5. An eligible code record contributes its
stored position. Both have the same batch counter, so the within-cell
minimum-counter tie selects the packet, exactly as the literal helper
does. A selected code output preserves its input code origin. Here the
position modulus2048 exceeds the frame size1029 by1019>10, which again
excludes wrap for every qualified radius5 ancestry step. Thus all valid
code origins are jQ-5 and their supports lie in [jQ-5,jQ+Q-1].

At a reader with true phase p, a qualified code position has the form
p+5+kQ in[0,Q+5). Only k=0 is possible throughout a colony; k=-1 is
also possible in its last five sites. There are exactly two possible
qualified origins: the reader's own colony, and the next colony in
that five-site overlap. Count their eligible combined-record votes
among eleven physical inputs. A three-vote cohort is eligible; if both
cohorts qualify, the literal iteration chooses the one whose first
supporting offset is smaller, because their counts tie. This is precisely
the two-origin quotient in native_clock_island_auxiliary_bounds.c.
Unqualified origins cannot win and can be ignored in those two counts.

The computed service force is new_code_valid OR packet_any_cohort.
Computed backward signal implies right-epoch force on every legal
two-clock input: its identical RF clock vote lies in the smaller
[TF,TF+1792] window. Omitting the backward bit from this projected
native force changes no native output. Its actual raw output is allowed
to evolve, and J152 ensures it is zero before a quiet jump/boundary.
Actual packet/code birth, selection, eligibility and commit clearing
are retained in the quotient. No header is externally cleared.

## Universal workspace enclosure and native-flag monotonicity

The only unspecified native input is raw WorkspaceFlag1. Bound it below
by0 and above by its literal previous-output guard: true GF in[Q-5,Q)
and selected current clock in[TF,TF+2Q). No assumption is made on the
corrected Info signal, its redundancy or its programme-produced value.
Different holders may independently choose any value within that bound.
This is a superset of the actual full-rule histories.

Keep lower and upper arrays for native Flag1 and Flag2. For fixed clock
labels, the Flag1 equation is monotone in raw Flag1 and WorkspaceFlag1:
every flag-count/self-support term increases, and increasing raw flags
can only reduce the quiet-majority count, increasing its complement.
Clock inconsistency and GF/inside predicates are fixed.

With canonical GF, d3=0. Let s be self Flag2, A the in-colony left
Flag2 count and B the full five-left count. Apart from positive source
d4/service terms, the Flag2 equation is

    s=0: A>=4 OR (newFlag1 AND B>=4);
    s=1: (NOT newFlag1 AND A>=2) OR (newFlag1 AND B>0).

Since A<=B, both branches are monotone in newFlag1 and every left
Flag2, and the s=0 branch implies the s=1 branch. The full equation is
therefore monotone in all flag/source inputs. Positive d4/service forcing
preserves this property. The checker exhausts this exact literal native
fragment for all six inside masks, every Boolean input and every upward
single-bit change. Its guard/source wiring is pinned to the full netlist.

Evaluate the actual flag equations at the two endpoints each row. These
give valid bounds for every full-rule history, provided the clock output
is common. If RF and LF voted labels agree, it is automatically common.
If they differ, the selector is necessarily RF when upperFlag1=0 or
lowerFlag2=1, and necessarily LF when lowerFlag1=1 and upperFlag2=0.
Otherwise the checker stops; it does not guess a label. When a common
clock is certified, its literal commit mask is common too and can be
applied to both flag bounds and to actual headers. The new upper WF1
guard is then known. Induction proves the enclosure for every row.

## Exact pulse computation and infinite-line lift

The retained C loop evaluates every site/row of two6144-row pulse
segments on256Q cells. It checks the selector obligation at all147456
sites/rows where RF/LF labels differ. There is no ambiguous output.
Both flag bounds collapse to the same aligned template with empty
headers/workspace by the endpoints:

    time6144:        label1 interval [117Q,132Q), width15Q;
    timeTF+6144:     label1 interval [105Q,121Q), width16Q.

The preceding whole Flag1 colonies and Flag2=0 are exactly J150's
template at both endpoints. Since actual auxiliaries are zero on the
subsequent quiet rows by J152, the full native state advances by the
proved template invariant through [6144,TF) and [TF+6144,U). At U it
is the initial native state translated by -23Q, with auxiliaries empty.

The periodic calculation has an exact infinite-line interpretation.
Outside the current label1 support, two outward distant blocks have
label0, so refinement cannot create label1 there. At a reader more
than3 beyond that interval, each five-clock directional vote still has
at least three label0 words. Either selector choice is label0. Thus
the clock support expands by at most3 per evaluated row, even with
arbitrary workspace/flags/service.

For the interval arrays and packet/code fields, compare with the
uniform label0 reference driven by the same lower/upper WF guards.
That reference is Q-periodic. Native flag discrepancies propagate at
most8 sites per row, header discrepancies at most5, and a WF-guard
discrepancy is confined to the new label support. Their clock-sensitive
votes/refinement have no exceptional input outside the clock interval
just bounded. Hence all projected exceptions are contained in the
initial interval [127Q,144Q) enlarged by8 per evaluated row. There are
12288 evaluated rows, giving96Q extra margin. Both ring margins exceed
96Q. No wrapping input can affect the exceptional computation. The
reference bounds may differ during a pulse; both collapse to zero on
the endpoint, so this argument does not assume arbitrary real workspace
signals outside the island are periodic.

Translation by Q preserves the rule/true phases; the two legal clock
and birth schedules repeat every U. After one period the same native
template and empty auxiliaries therefore reestablish the theorem's
initial conditions at shifted endpoints, with arbitrary current private
simulation data. Induction gives the travelling island for every n.
At intermediate times its clock support is contained in the corresponding
shifted interval enlarged by96Q; consequently each fixed site eventually
lies to its right forever and has the correct clock. No clock extinction
or fixed global spatial confinement follows from this pointwise recovery.

## Intact initialization and the physical error class

An intact SP28 initializer can be defined with a terminating recursion,
independently of the travelling-state computation. Let ell(f,b) be the
normal represented primary at59,...,900. Define D(iQ+ell(addr,b)) as
bit b of i modQ, D(iQ+ell(info,b))=D(i+b-2), and all other normal or
unused primaries0. The five Info residues are92,...,96. An Info-tag
argument has absolute value at least92; its next argument is at most
|x|/Q+3<|x|, including negative integers. D is therefore defined on Z.
Set H_x.GF=x modQ, H_x.Info[b]=D(x+b-2), every other raw field0.
The defining case split gives every normal represented bit of H,
coherent five-holder copies, and zero auxiliary Flag aliases58/965.
Thus H∈E28(H). Every hierarchy level may start in H. This is the
existing SP28 encoding, including its actual instruction/ROM model.

Noiseless encoded simulation gives the physical state at U in E28(F(H)),
with canonical GF/Age0/flags0 and empty auxiliary/private fields. At that
time overwrite only Age on[a,b) toTF and Flag1 on[a-Q,a) and[b-Q,b)
to1. Every point of [a-Q,b) is an actual altered site, and there are no
other errors. The native/auxiliary state now has the theorem's exact
initial form; other simulation data are allowed arbitrary. Hence its
full future native trajectory is the travelling island just proved.

The complete error set is a dense17Q-site row. No point is E0: each
singleton/adjacent pair has a nearby exterior point. The row is connected
by unit links. Any proper nonempty candidate1 or candidate2 subset is
linked to its exterior and fails isolation(iv); the whole row is too
wide for candidate1. Therefore E0=E1=empty, and any real2 would have
to be the whole row. It is a candidate2: it fits Q^2 and contains two
disjoint linked candidate1 pairs.

At c16, its first four and last four points are disjoint candidate2
subsets, separated by at least17Q-7>=16Q. Each four-point subset has
two disjoint linked candidate1 pairs. Thus the whole row fails real2
condition(iii), and E2 remains empty. It is candidate3, since those two
candidate2 subsets are linked at24Q^2. All row distances are less than
16Q^2, so no two candidate3 subsets can be separated at that scale;
condition(iii) holds, and condition(iv) is vacuous. The row is one real3.
At c104, its diameter is already less than104Q, so candidate2 condition
(iii) holds immediately and it is one real2. These are the original
Gray definitions with their stated separation constant, not a visual
burst-size classification. Restoring c104 does not remove this orbit.

## Status and consequences

| Step | Status | Limit |
| --- | --- | --- |
| Full native/auxiliary projection and universal WF1 enclosure | proved | Canonical GF/two legal phases/initial headers empty/no further errors |
| Both pulse computations, infinite-line lift and all-period native translation | proved | Exact finite Boolean computation plus written quotient/monotonicity/influence arguments |
| Intact recursive SP28 initializer and one actual real3(c16)/real2(c104) realization | proved | Specified finite physical error; no later errors |
| Finite fixed-box confinement for all higher errors in SP28 | refuted | Wrong-clock island leaves every fixed finite box |
| G17, faithful Gray or Gacs refutation; iid unreliability; smallest sufficient reliability change | unproved | Native GF unchanged; pointwise clock recovery; later random errors not covered |

The checker retains exact initial/boundary/critical states, source and
executable hashes, literal netlist corner comparisons, monotonicity
cofactors, projection dependencies and the error-class arithmetic.
The supplementary local comparisons do not replace the universal
projection/enclosure proof. No GPU or noisy full-state experiment is
used. The earlier exploratory output is retained separately; the final
certificate is for the pinned source/proof and complete pulse run.

The first checker invocation had a parse typo; the second completed the
pulse run and literal corner comparisons but lacked the local c=cells[0]
binding in its extracted Flag2 wrapper. Both checker snapshots and
failure receipts are retained separately. These corrections affect the
checker only, without changing the C kernel, rule or mathematical statement.
