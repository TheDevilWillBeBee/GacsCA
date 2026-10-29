# SP30: a real2 fault at c16 reaches the finite translating class

This is a new history of unchanged frozen F30, Q1024/U475136/r37,
TF278401 and S284545. It changes no rule or classification constant.
It concerns this separately proposed construction, not active G17 or
Gray's literal rule. Positive iid reliability or failure remains unproved.

[Checker](check_sp30_16Q_actual_regeneration.py),
[certificate](../../../figs/robustness/unregistered_16Q_actual_regeneration/certificate.json),
[conditional source driver](probe_sp30_16Q_source_bootstrap.py), and
[retained bootstrap execution](../../../figs/robustness/SP30_16Q_source_bootstrap_unregistered_run.log).
The driver's receipts deliberately retain their conditional scope. This
document supplies the physical/infinite-line composition that they alone
do not prove. It does not replace an uncertain source bit with a chosen
value or a fresh encoding after a pulse.

## Exact initial history and original error class

Start at E30(z) with upper GF(j)=j modQ, Age0 and every upper field
other than GF/Info0; upper raw Info is arbitrary. The recursively intact
hierarchy is included by J189's nested encoding construction. At computed
lower row0 replace only GF/F1 as follows:

* Shift raw native GF by512 on[128Q-512,143Q).
* Set native F1 to1 on[127Q,128Q-512) and[143Q-512,143Q).
* Retain every other actual bit and introduce no later errors.

Every site in[127Q,143Q) changes GF or F1. Thus the original error
support is exactly one dense16Q row, not the earlier dense17Q row.
Its temporal extent is1 and its spatial extent16384.

Using Gray's original recursive definitions with lambda24 and c16,
this support is exactly one real level2 and has no real E0/E1.
A candidate0 is a singleton or adjacent pair; each such proper set
has a dense-row complement within24 sites. Every candidate1 fits a
Q-wide box, hence is proper, and the entire row has span16383<24Q;
its complement prevents level1 isolation. The whole row fits a
Q² by U² box and contains two linked candidate1 pairs. Its span
is16383<16Q, so no two candidate2 subsets can be(16Q,16U)-separated.
There is no exterior error, so the real2 isolation condition holds.
Once E2 is this entire history, no higher real errors remain.

In fact it is real2 for every integer c>=16 and real3 for1<=c<=15.
For the latter case its first four and last four points are disjoint
candidate2 subsets with minimum distance16Q-7=16377>=cQ, defeating
condition(iii) at level2. They are linked at24Q² and the whole row
fits a Q³ by U³ box; its span<Q²<=cQ² gives level3 condition(iii).
Whole-history isolation holds there. This classification observation
does not change the actual trajectory or prove reliability at c15.

## Variable-width prefix and store interfaces

For integers L<R, use T(L,R) and B(L,R) from
[J195](../SP30_GF_BANK_CLOSURE.md). That proof already supplies the
quiet prefix/suffix, common legal clock, reset and zero-bank implications
for every such L,R. To apply the physical protocol to the shorter
bootstrap, the K+6 occurrence in
[J214](SP30_QUIET_FRAME_PROTOCOL.md) is replaced by R and K by L.
This is a change of theorem geometry, not a transition-rule change.

Here are all affected protocol steps. Complete true frames are jQ for
j<=L-2 or j>=R. Complete foreign frames are hQ-512 for L<=h<R.
Their entire SF footprint is respectively left of(L-1)Q, right ofRQ,
or inside[LQ-512,RQ-512). Their computed relative GF and common clock
are the same as in J214. The four quiet Flag1 boundaries remain at
least512 apart. Five-holder vote/gate identities and speed-eight route
blocking consequently apply at each boundary with the same28 local
checks, regardless of the distance between the two edges. All three
captures still finish by25218, before25984. The842-bit normal layout,
131238-instruction programme, compact registers, turns, pending stores,
Match definedness and courier paths are unchanged inside each complete
frame. No computation step depends on the number of foreign frames.
Thus the same physical induction couples each complete frame to the
actual captured input assignment, including all free private/I bits.

At the special write, physical MF509 is1 exactly at L..R-1, because
B(L,R) makes every complete foreign frame's computed GF0/F1one.
True MF1021 is that frame's actual early F1 output. Partial primaries
MF509(L-1) and MF1021(R-1) have virtual phase509 and retain the zero
old alias. All interior MF1021 primaries are likewise virtual509.
The alias copies are three or more sites from a GF discontinuity, so
all five holders select the same branch. These are the same residue
identities as J214/J216, without fixing R-L=6.

The early-store part of
[J212](SP30_PULSE_STORE_PROTECTION.md) also extends as follows. Suppose
the checked pulse hull is contained in[LQ-7616,RQ), its endpoint is
T(L',R') with L'=L-6 and R'<=R-1, and it has binary raw/refined/computed
GF and common clock throughout. Normal GF59..68/F1phase88 stores all
materialize before TF; opposite512-phase stores issue afterS. The
literal actual ROM has no such destination kind during the pulse.
The five comb offsets differ by multiples of5 of magnitude<=20,
never512. Majority of surviving pending records therefore either
retains their common kind or issues no store. Wipes cannot create
a Hold kind. This argument is independent of the interval's width.

Consequently all five normal GF/F1 copies in recovered colonies
R'..R-1 are0 at commit: their old true Holds were reset0 and the old
foreign GF/F1 stores were at the opposite phase. No eligible normal
GF/F1 store occurs after the switch before commit. Late Age/WF1 in
these colonies is left unrestricted; its stores do occur afterS.
At left edge L-8 the GF/F1 reader's final native footprint is
LQ-8065, giving449 sites of clearance. At right edge R the first GF
footprint begins atRQ+20. These early values survive. Whole late
frames j<=L-9 or j>=R+1 have native footprints wholly outside the
pulse hull, so J214 stores their full31 native outputs, independently
of the arbitrary coherent Match word. Age/WF1 at the single right
edge R is conservatively left unrestricted in the bootstrap.

These premises are about the actual same history. The pulse certificates
below discharge their binary/common-clock/hull/endpoint premises;
the preceding quiet-prefix induction discharges their captures/reset.

## Six actual bootstrap periods, with uncertain words left free

Represent a boundary only by proven normal native-word bits: a full
canonical left prefix, a protected GF/F1-only left edge, a full
canonical far-right tail, and finite right records of known bits.
Every other bit denotes its actual but unrestricted value. Initially
all four represented fields GF/Age/F1/WF1 are canonical in E30(z),
with the other upper native/control fields0 as specified above.

For a true frame j, a source at col=j+d is captured as0 when its
actual speed-eight route intersects a native F1 strip. Otherwise
its GF/Age/F1/WF1 bit is its proven boundary value, or a free input
if no boundary value was established. Unmentioned upper fields and
the instruction input stay free. Occurrences of the same unknown
source bit use the same symbolic key. The complete actual full-net
cofactor therefore constrains every possible actual captured assignment.
A nonconstant output is retained as unknown, rather than declared0.

At each period the retained C wrapper includes the frozen corrected
domain factor verbatim. It changes only the prepared initial T(L,R)
and the signal domain obtained from those cofactors. J192's actual
restricted projection applies; J180's1062 primitive images/36 selector
images make the domain recurrence sound even for correlated free bits.
Every6145-row run has singleton GF throughout, zero wipe-transcription
disagreements, a singleton quiet native endpoint and the listed hull.

The exterior domain is the evolving canonical Q-periodic background
with both initial signal tracks0. The only deviations are in the
recorded finite seed. The identical factor's proved support bound is
seed±(8(r+1)+37). At every row the wrapper checks all coordinates
outside that cone against the same-residue background reference.
The reference and seam37-site collar remain outside the cone.
The seam induction from J192/J207 thus lifts these finite domain
calculations to Z; no periodic concrete-state hypothesis is used.

| Pulse input period p | Actual input T(L,R) | Actual endpoint T(L',R') | Full left prefix at(p+1)U | Proven right GF0 prefix at(p+1)U |
| ---: | --- | --- | --- | --- |
|0|T(128,143)|T(122,135)|j<=119, Age1|135..142|
|1|T(122,135)|T(116,127)|j<=113, Age2|127..139|
|2|T(116,127)|T(110,119)|j<=107, Age3|119..135|
|3|T(110,119)|T(104,111)|j<=101, Age4|111..130|
|4|T(104,111)|T(98,104)|j<=95, Age5|104..125|
|5|T(98,104)|T(92,98)|j<=89, Age6|98..120|

Full left prefixes have GF=jmodQ/F1WF1zero and the listed legal mixed
Age code; their next edge has only GF/F1 asserted. The checker repeats
the full-net source cofactors, verifies every source-domain transition,
the generated wrappers, all-row bounds and complete endpoint arrays.
The old true right GF outputs and recovered zero cohorts are combined
only where the store reservations above apply. Each next boundary has
its actual807 reset bits0, B(L',R') zero and all3/509/515/1021 alias
copies0 by the literal commit mask in both possible GF phases.

This proves the table by induction from the original fault. It does
not assert equality of the unobserved private trajectory with any
old17Q history. At6U, however, the **same invariant H6** required by
[J216](SP30_FINITE_REGENERATION.md) has now been supplied: T(92,98),
full left through89, GF/F1 edge90, right GF0 at98..120, zero bank,
aliases and reset. The seventh conditional run is supplementary;
the six-period bootstrap suffices.

## Finite recurrence from this new original real2 history

J216's H_p=>H_(p+1) induction uses exactly those invariant bits and
allows every other actual Info bit to be arbitrary. Its proof does
not use the earlier17Q support after the H6 bootstrap. Apply that
implication verbatim, with K_p=128-6p/R_p=K_p+6, for6<=p<TF.
The upper Age contract is age_code(p)<age_code(TF); the left corner
p=192mod512 has nonzero Age, as in J216. Thus this **new** actual
history has278395 proved translating pulse endpoints:

    I_p=[(122-6p)Q-512,(128-6p)Q),
    t_p=pU+284545, 6<=p<278401.

Each interval has6656 wrong-GF sites and moves left6144 per period.
The final proved endpoint is132278146945; H_TF is obtained at
132278337536. The next upper-WF clock is outside the contract.
No permanent glider, general eroder or all-time failure is inferred.

## The proposed c16 repair envelopes are false for F30

The original history is exactly one real2 at c16. Its clean native
shadow is canonical by the already proved F30 native/noiseless
theorem. Hence the endpoint comparisons in J217 apply verbatim:
the wrong sites at p6 and p347 require spatial width2101760, greater
than2Q²=2097152; endpoints p6 and p29703 have temporal difference
14110113792, greater thanU²/16=14109638656. A single literal Gray
Proposition5 box cannot contain this real2 history's Address damage,
even with an arbitrary unaligned origin.

The sufficient deterministic statement R in ROBUSTNESS§11 also fails
when transplanted to F30 at c16. At p1706 the left endpoint

    x=(122-6*1706)Q-512

has wrong native GF at time1706U+284545. Every original error q has
q_x>=127Q, so its spatial distance to x is at least

    (5+6*1706)Q+512 =10487296 >10Q²=10485760.

The point is not a direct error, and this history has only one real2
set; no real0/1/higher set is available for another association.
Thus the10Q² coordinate-distance requirement is impossible. This
is a direct distance comparison with the original errors, not merely
a comparison of two damaged endpoints. The probabilistic reduction
conditional on R remains valid; its repair premise is false for F30.

These are deterministic counterexamples to the stated F30 envelopes,
not to Gray's actual automaton or G17, and not proofs that every
possible iid memory theorem for F30 is false. Additional faults,+higher activity and a sufficient successor remain unproved. Decreasing
c16 to15 promotes this particular dense row to real3; that is an exact
classification boundary, not a smallest sufficient construction change.
For any supplied initial native/header/signal state, changing only
private programme/data updates while retaining the closed native factor
cannot alter that6144-update projected segment. A change that alters
the supplied signals at another period requires a separate analysis.

| Step | Status | Scope |
| --- | --- | --- |
| Dense16Q original error is real2 at c16 | proved | Exact GF/F1 payload, one row, no other errors |
| Variable-width quiet-frame/store interfaces | proved above, existing arguments apply | Actual reset/clock/ROM/capture and checked pulse premises |
| Six-period actual H6 bootstrap on Z | proved by composition | Full-net cofactors, exact domain runs and physical store lift |
|278395 actual subsequent translating endpoints | J216 induction applies verbatim | H6 supplied by this new history; stops before upperWF |
| Literal Proposition5 and stated R envelopes for F30/c16 | refuted | Finite native witnesses and original real2 classification |
| General alternative envelope, all-time or iid memory failure | unproved | Neither finite translation nor a failed sufficient premise proves these |
| Reliable successor or globally sufficient minimum change | unproved | Rule changes must repair the identified native/source mechanism |
