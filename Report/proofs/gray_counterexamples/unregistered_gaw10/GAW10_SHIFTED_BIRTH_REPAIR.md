# GAW10: actual shifted late birth and its permitted two-period repair

The frozen **GAW2R** rule, ROM, Q8192, U128Q1048576, lambda24 and c104
are unchanged. This checkpoint follows the exact birth-near history excluded
from GAW9's zero-Head reduction. It proves a positive repair instance, not a
counterexample to Gray, G17, an operational error relation, or iid memory.
All previously accepted and registered assets remain unchanged.

## Exact initial state, error and statement

Use the recursively intact infinite-line H and its actual clean row
T=96Q=786432 proved in frozen GAW4/GAW6/GAW8. Logical Info is I(y),
Programme is the actual emitted beta, and every retained History bank is

    B(y) = sum_{j=-8}^8 I(y+jQ) * 2^((j+8)*100).

Native GF is x modQ, AgeT, flags and Workspace0. Head, Mem, Out, Scratch,
Mail and couriers are0. Copies use S=(0,-2,-1,1,2): holder h of logical
y is x=y-S[h]. At this one physical row, for b=P-6=3842 and j=0..15,
replace the native GF by (b+j+1) modQ and Age by102Q=835584. Retain
all four flags and **all actual SF words**. No other physical errors occur,
before or after. The receipt contains the sixteen complete old/replacement
496-word records and original-c104 classification.

Every replacement changes its cell. The sixteen-site row has extent16x1
and diameter15; no singleton or spatial adjacent pair is24-isolated from
the remaining points, so E0 is empty. Linked level0 candidates exist and
the row fits a QxU box. No candidate level1 nonempty subsets can be
separated by104 within this diameter. With no external errors it is one
actual original-c104 **real1**. No independent upper fault or future
Workspace/command/tape is introduced.

**Selected-history theorem.** Under this exact fault, the extra logical
Head at P-1 has5,2,0 raw copies at elapsed ticks1,2,3 and never writes
Out or a courier. Global native geometry is clean by elapsed1450 and
native/workspace flags by5545. At the first physical U boundary the
configuration is exactly E(Cprime,0), where Cprime equals F(H) except
for Flag1 at upper cell0, which is1. At2U the full physical configuration
equals the noiseless shadow E(F^2(H),0), and hence remains equal to the
shadow at every later site and tick. The proof combines actual full local
prefix checks, a proved factor, an exact finite trajectory and the frozen
universal own-programme/physical-period arguments. It is not an exhaustive
real1 theorem or a whole-grid simulation through2U.

## 1. Actual full prefix and extra head — exact finite proof

[trace_gaw10_birth.py](trace_gaw10_birth.py) applies the frozen full
`local_transition` to every affected radius8 cone at each of32 updates.
Outside the affected interval it synthesizes the actual clean row96+t:
canonical geometry, common clock, I/beta/three B banks, and reset work.
This reference is exact during the clean96Q..102Q rest segment. Its source
Info at3/Q-3 is0, all flags remain0, and no gather or Head birth occurs.
An affected set enlarged by8 contains every possible next discrepancy.
Every retained dirty cell includes all496 words; the complete prefix and
its digest are replayed without changing the receipt.

At elapsed1, all five holders of P-1 have computed service AddressP and
Age102Q+1, so the actual birth equation creates the pc0 packet. Their
actual Mem is B(P-1)=0. At elapsed2, wipes leave only two pc1 copies.
The only executed instruction is pc0, `MOVI(11,0)`, which writes neither
Out nor Scratch. At elapsed3 the five-holder vote for the packet has at
most two nonzero copies, so every incoming packet is0. No other logical
head is born. The full prefix records exact holder coordinates and
packets, rather than head-centre substitutions.

All later Ages through the certified short trajectory are selected from
96Q+n or102Q+n: native majority/fallback selects one old label and then
increments. For3<=n<=8195 neither label meets72Q+4 or102Q+1. Thus no
second erroneous birth is possible in that interval. Head0 is preserved
by hold, reset, wipe and incoming-packet equations. Out and Scratch remain0
because no packet writes them. Courier seeds read Out0 and their route,
hold, reset and wipe equations preserve0. Mail starts0 and both clock
labels are beyond the three gathering intervals, so Mail remains0.

## 2. Derived actual History/Info keeper factor — proved reduction

During this same clock-label interval, no History reset or capture occurs:
all starts/captures are at most72Q+2, while both labels exceed96Q. All
three banks therefore follow the same voted-hold/wipe equation. For each
logical y every old holder contains either B(y) or0. A bitwise majority
of such copies is exactly B(y) times the majority of five Boolean keeper
bits. The same statement holds for the full100-bit Info word I(y).

Let K_t(x,h) be the keeper at holder x/copy h. Before the fault K_0=1;
the noise retains SF. At each actual native update define

    wipe_t(x) = newFlag1(x) AND newGF(x) != rawOldGF(x),
    K_{t+1}(x,h) = NOT wipe_t(x) AND
        majority_{q=0..4} K_t(x+S[h]-S[q],q).

There is no phase0 or80Q-1 Info commit in this clock interval. Consequently
Historyg_t(x,h)=B(x+S[h])*K_t(x,h) for g=1,2,3, and
Info_t(x,h)=I(x+S[h])*K_t(x,h). The first three keepers are derived and
checked against the full actual prefix, including every wiped holder.
They are not independently selected initial banks.

[gaw10_postbirth_factor.c](gaw10_postbirth_factor.c) copies the accepted
GAW9 native/actual-Info/Workspace equations and adds this keeper recurrence.
It starts at the actual elapsed3 state. Every future Workspace source is
computed from its actual displaced source's native tuple, wipe and Info
low bit. It retains source3's left-Age modulo16 and the h1 Flag2 equation.
Out/Head/courier omissions are justified by section1, not silent commands.
Free-Mem/Scratch/Mail/Programme full-local_R cofactors additionally check
the native, Info, Workspace and three tagged History outputs1024 times.
These samples supplement the algebraic reduction; they do not establish
universal correctness by sampling.

The retained binary is rebuilt identically. Its dynamic affected interval
includes native, Info and keeper damage. Exterior sites use actual I,
canonical GF/common Age and keeper1; the radius8 enlargement is exact on
the infinite line. A strict16-site finite-array margin is checked on every
row; a guard exit would be rejected. No boundary or finite-ring behaviour
is used. The query changes neither the CA nor its ROM.

The8192 post-prefix updates require51,493,604 actual factor-site updates.
Geometry is clean at total elapsed1450, all native/workspace flags by5545.
As in GAW9, global canonical/common geometry is absorbing with no further
native errors, regardless of flags/SF. Wipes cease once raw old geometry
is canonical. Coherent keepers remain coherent and held. At elapsed8195
the exact coherent erased logical interval is **[3842,8190)**,4348 sites.
All other logical keepers are1. This is a union of erased logical History
words, not an instantaneous native island width or an error support.

The entire normal frame [P,P+496) of colony0 is erased. Every other
colony's normal frame is intact. True special Info at3/Q-3 is0 both
before and after erasure, so no later first-window Workspace source is
created once geometry is canonical. Zero native/workspace flags persist
after quietness. Programme copies are rewritten from the correct service
Address once geometry heals, so the actual lower evaluator code is correct.
No new physical noise occurs.

## 3. Actual late reset, birth, evaluation and first boundary

The next actual common reset is102Q. It clears old Mem, Head, Out,
Scratch, Mail and couriers, independently of old Mem. History is retained;
Info remains I(y) times its now-coherent keeper; Programme is beta. The
102Q+1 row reconstructs Mem as the temporal majority of the three equal
actual tagged B banks, and births exactly one five-copy pc0 head atP in
each colony. Lower geometry/flags are already clean, so no wipes or
asynchronous controls enter the physical interpreter.

The checker applies full local_R to actual tagged History/Info reset and
birth cones, with three distinct arbitrary old-Mem probes. The universal
old-Mem independence follows directly from the actual stage-start branch,
not these probes. Native and special-primary boundary cases and all five
physical copies are included. Scratch/Head/other reset independence follows
from the same literal branches. This discharges the preparation used here;
it does not assert a reset theorem for arbitrary damaged controllers.

The actual affected late tape of colony0 is0 at every normal primary and
every one of its17 lanes. This is the derived erased B bank. Other colonies
retain their exact normal tapes from H. The actual own ROM executes this
colony0 tape in **65,117** physical head updates, within147,455 available
after102Q+1. It stays inside the normal frame. The frozen whole-beta and
five-copy physical-head contracts apply: each actual lower operation reads
this retained bank and writes the distinct Out/Scratch tracks; no future
prepared tape or whole-rule intrinsic is substituted. Every output word
and the actual packet/Scratch trace digest is retained.

The full496-word result is exactly F(H[0]) except Flag1=1. Its native
words are [0,1,1,0,0,0]; all other fields, including own Programme copies,
match F(H[0]). Only colony0 has an affected normal bank, which is derived
by enumerating the complete erased interval. All other receivers execute
the clean own programme and yield F(H[g]).

After completion, the actual halted head/Out/Scratch are held untilU.
No later reset or command seed occurs. Out outside every normal frame is0,
since the102Q reset was global and the programme writes only represented
primaries. At the U boundary, new Age0 copies old voted Out into Info
before clearing the work fields. History, Mem, Head, Out, Scratch, Mail
and couriers all reset; Programme remains beta; lower native flags remain0.
The checker verifies the actual full-local_R commit against E(Cprime,0),
including normal-frame edges, all five holders and special primaries.
Old Head/Scratch/History/Mem values cannot affect that reset/commit branch.
Thus the first boundary is literal raw E equality, with no boundary noise.

## 4. Actual second period and exact repair relation

The first boundary is a valid global encoding: upper native words have
legal widths and flags, and the sole upper difference is Flag1 at cell0.
The frozen GAW2R noiseless period theorem quantifies **every** infinite
upper raw configuration, including this Cprime. It derives all next
three gathers, early evaluator/couriers, Workspace and late preparation
from E(Cprime,0). Its quiet/rest/controller premises are therefore not
independently assumed or preloaded here.

Only upper sites -8..8 can depend on the one changed cell. The checker
applies the actual full radius8 local transition at each of these seventeen
sites and obtains F(Cprime)[g]=F^2(H)[g] in all496 words. Outside this
finite cone the neighbourhood equals the clean one. Therefore the actual
second physical boundary is E(F^2(H),0), exactly the full noiseless
shadow. The autonomous deterministic rule then gives equality at every
later physical site and tick without any remaining repair premise.

One sacrificed decoded upper cell for one lower real1 is ordinarily
permitted by the intended operational simulation relation. This history
produces precisely that pattern and heals at2U. History corruption or
the temporary extra head is not a violation of a recovery claim.

| Step | Status |
|---|---|
| Intact H, actual row96, total frozen rule/ROM and universal physical interpreter | Prior frozen proved arguments apply |
| Sixteen whole-cell replacements and original-c104 real1 | Proved; exact classifier/payload receipt |
| Full prefix,5/2/0 head copies, no extra output write | Exact finite full-local_R proof/replay |
| Post-prefix zero Head/Out/courier and tagged History/Info factor | Proved from actual equations |
| Selected native quietness and coherent4348-site erased bank | Exact finite factor proof/replay |
| Actual102Q reset/birth, late evaluation, U boundary | Proved composition; actual local/execution checks |
| Only one upper Flag1 difference, complete2U/all-later shadow | Proved for this one actual history |
| Arbitrary birth-near/native-control real1 repair | Unproved |
| Faithful Gray construction/refutation, iid reliability/failure, shorterU | Unproved |

## Rule departures and reproduction

GAW2R retains h1 erasure, radius8/17 lanes/FULLCOL, WORD100, computed-holder
service Address, immutable token/dictionary code, route-bounded couriers,
an early native-only pass and102Q late start. Its diagnostic immutable storage
is270349 bits; beta<=Q/dictionary512 and Gray's literal bit layout fail for
the specified emission. Its102Q start executes during Gray's fourth-stage
rest. No real1 stage-separation or higher/iid proof is borrowed unchanged.
All statements above concern this changed implementation. U is not shortened.

Run `python3 Report/proofs/gray_counterexamples/unregistered_gaw10/validate_gaw10_shifted_birth.py`.
The standalone manifest pins the unchanged accepted GAW9/prior dependency
closure, exact new source/binary, prefix, error/payload, factor, full actual
ROM, execution and reset/birth/commit receipts. The validator writes only
temporary compiler outputs and performs a read-only replay. Generation01
and the more extensive generation02 logs are retained; no failed rule run
or finite-domain guard is promoted to a counterexample.
