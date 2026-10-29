# A conditional actual-Info shrinking pulse on the infinite line

This concerns the two existing, explicitly changed SP28 force durations
D=Q or2Q, at Q1024/U475136/TF278401. It adds no rule equation or interface
change and supplies no matching own programme. The native/Info factor is
[J164's exact factor](SP28_INFO_NATIVE_FACTOR.md).

## Statement and status

At common legal input clock TF on Z, prescribe GF=(x+512 L(x)) modQ,
where L is1 on [130560,147456) and0 elsewhere. Native Flag1 is1 on
[130048,130560) and [146944,147456), and0 elsewhere. Native Flag2,
Workspace flags, packet/code validities and backward pressure are0.
Invalid headers, other private data, instruction inputs and individual
Info copies may be arbitrary, subject to these majority constraints:

* M509(y)=1 exactly at logical primaries y congruent509 modQ inside the
  initial wrong-GF interval, and0 at the other509 primaries;
* M1021(y)=0 at all primaries congruent1021 modQ.

Assume no later errors. After6144 input updates, the wrong-GF interval
is [124416,139264), of width14848. The left boundary has moved−6144=−6Q,
and the right boundary−8192=−8Q, reducing width by2048=2Q. Flag1 is1
on the two corresponding preceding512-site strips; native Flag2,
WorkspaceFlag1, packet/code/backward fields and code positions are0.
The retained509-majority track has eight ones and the1021 track is0.

The claimed status is **proved by the exact factor, finite exhaustive
integer certificate and the lift below**, once the checker terminates
successfully. An incomplete or failing run does not establish the
statement. This is a specified pulse from specified data, not a theorem
for other widths/phases or a finite eroder from an intact hierarchy.

## Exact finite certificate

[The wrapper](certify_info_native_shrinking_pulse.c) includes the frozen
J164 C transition verbatim. It adds initialisation, row assertions and
receipt output, without altering `step`. [The checker](check_info_native_shrinking_pulse.py)
compiles it with assertions enabled and executes both durations on
the256Q-site quotient. At **every** row0,...,6144 it checks all GF sites,
the outward growth of their support hull is at most three sites per
update, and the full projected fields outside the interval below agree
with a Q-periodic background. At6144 it asserts every Flag1 site and all
zero fields in the statement. It also compares the complete endpoint
arrays with the earlier prepared-run arrays. Exact integer operations
and complete enumeration of the time interval, rather than random
input sampling, establish this finite instance of the recurrence.

The finite certificate alone would establish the quotient instance.
The projection identities and locality argument are necessary for the
universal omitted-data claim and the infinite-line conclusion.

## Infinite-line lift

Let I=[127Q,144Q) include all initial projected differences from the
canonical-GF, zero-Info background. The background may have nonzero
packet/code/Flag2 fields during the pulse; it is **not** incorrectly
replaced by a permanently quiet state. The canonical background is
Q-periodic and is advanced by the same exact factor at the same clock.

The GF region need not stay sharp: intermediate holes are present in
the actual trajectory. The following support-hull lemma needs no such
assumption. If all raw label1 sites lie in [a,b), then the joint-refined
label1 sites also lie in [a,b). For x<a, the two negative-centre blocks,
at x−30 and x−10 with radius2, are entirely label0. The other two block
votes can contribute at most two ones, which cannot replace the raw0
by a3/4 vote. The same argument uses the two positive-centre blocks
at x>=b. At either outer side, a two-versus-two tie retains raw0.

The five right or left refined-GF votes can then be1 only in
[a−3,b+3): beyond either end at most two of their five inputs can be1.
Both votes exist in the two-phase/common-clock alphabet. The native
selector chooses one of them regardless of flags, so new raw label1
support is contained in [a−3,b+3). This proves **outward** hull speed
at most3, for any arrangement of binary labels inside its finite hull.
It allows holes, arbitrary inward motion, and eventual empty support.
Induction confines GF differences here inside the initial interval
enlarged by3r at row r. Nonempty support throughout this particular
pulse is separately checked; it is not required by the hull lemma.

Differences in refined GF can seed another projected field only within
37 sites of the current GF interval. With that GF supplied, old Flag1
inputs range at most eight sites, other old native/header inputs at most
six, and the guarded WF1 source at most two. New GF uses these old
flags and its two directional GF candidates. Native/header differences
therefore spread at most eight sites per update apart from the37-site
GF seed allowance. The Info-majority recurrence cannot create a1, so
differences of the two retained majority tracks from the zero background
remain within their original support in I. Computing a holder's new keep
does not create an Info difference where the old majority was0.

Consequently all projected differences at row r lie within

    J_r = [127Q - (8*(r+1)+37), 144Q + (8*(r+1)+37)).

The finite checker also checks this bound at every row, comparing every
projected word outside J_r with the background representative at
16Q+(x modQ). That entire representative colony lies outside J_r even
at r=6144, and its raw dependency neighbourhood is periodic and outside
the seed. Thus its evolution is exactly the Q-periodic background's
evolution, with no private-data assumption beyond the factor premises.

For all r<=6144, J_r lies strictly inside [0,256Q), with a margin much
larger than the factor radius37. At the seam both finite and infinite
initial states equal the same periodic background. Induction on updates
now identifies the quotient and Z states on J_r and identifies both
with the background outside it. Wrapped inputs cannot carry a projected
defect into this interval. This lifts the complete finite pulse result
to Z. Translation of the initial data by an integer multiple of Q gives
the translated same pulse; arbitrary phase translations are not claimed.

Finally J164 proves that all full raw states with these native premises
and the same initial majority tracks have identical projected histories,
even when the initial Info copies disagree. This proves the stated
arbitrary-private-data and instruction-input quantifiers without
exhaustively enumerating those data.
Invalid initial header words are ignored by their zero validities and
canonicalised in the first output; the certificate uses their zero-word
representative. Equality of the header words themselves is asserted from
that first output, rather than for arbitrary invalid words at input row0.

## Failed sharp-shape strengthening and remaining reliability gap

The initial wrapper asserted that every intermediate GF support was a
single sharp interval. Its first duration failed that assertion; the
second run also stopped but its exception clause was not separately
retained. Their saved source, partial rows and logs establish no full
pulse. Complete corrected runs record the actual holes and use the
support-hull lemma above. Final contiguity is checked at6144; it does
not imply contiguity at earlier rows. This failure is a failure of the
attempted strengthening, rather than a counterexample to J164's exact
factor, Gray's construction or an iid theorem.

The result gives a genuine shrinking pulse under an explicit signal
premise. It does not show that intact damaged colonies supply that
premise. In the current Q1024 layout,509 is mutable upper h2 bit77,
whereas1021 is the special Flag1 primary. The pulse leaves only eight
ghost-track ones; another pulse cannot simply be given a fresh full
band of ones without proving how the intervening special write and
commit produce it. Neither replenishment nor a general-width/phase
eroder follows from this certificate. Matching own programmes, upper
data recovery, higher-error maps and an iid noise threshold remain open.

| Step | Status | Scope |
| --- | --- | --- |
| Actual factor and independence of omitted data | proved; J164 applies | Two GF phases/common clock/no writes during this interval |
| General binary-GF support-hull outward speed<=3 | proved | Common legal clock/two phases; no sharp-shape or private-data premise |
| Complete finite pulse and all-row hull/background checks | exact certificate required | Both specified durations and initial native/majority data |
| Infinite-line lift and Q-multiple translations | proved conditional on successful certificate | Hull/background reserve and quotient seam |
| Intact-history signal and replenishment | unproved | Prepared majority constraints do not supply their own history |
| Other widths/phases, finite eroder, own programme and iid theorem | unproved | No all-period composition claimed |
