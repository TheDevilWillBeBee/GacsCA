# What authentic simulated Flag2 repair requires

This is a **conditional native/interface lemma**, followed by a proved
first-window interface gap for the explicitly changed GMW7 rule. It is
not a counterexample to Gray's construction or his Address proposition,
and it proves no clock eroder, decoded recovery or iid theorem.
Q=8192, U=128Q=1048576, lambda=24 and c=104 are retained. No rule,
programme, schedule, dictionary or accepted certificate is changed.

The original sources are Gray's reader's guide, pp21–22 (native flags
and votes), pp33–35 (mail erasure, gathers and early simulated flags),
pp37–40 (higher-level repair hypotheses), and pp41–43 (Workspace pulses
and the two opposing waves). Its [local text](../../../papers_txt/gray_readers_guide.txt)
is pinned by the [checker](check_gray_flag_command_contract.py).
The [read-only validator](validate_gray_flag_command_contract.py) replays
the [receipt](../../../figs/gray_counterexamples/Gray_flag_command_contract_certificate.json).
The first unregistered checker incorrectly applied the SF bitwise vote
helper to a native whole-word vote. Its
[source](../../../figs/gray_counterexamples/Gray_flag_command_contract_initial_checker.py.txt)
and [failure](../../../figs/gray_counterexamples/Gray_flag_command_contract_initial_checker_failure.txt)
are retained; the supplementary assertion was removed. This was a
checker defect, not an error in Gray or the conditional lemma.

## 1. A bank that forces a native upper Flag2 (proved conditionally)

Let a prospective upper cell have logical coordinate g, and let the
eleven raw input records to its simulated native transition be C[j],
j=-5..5. All native fields have their legal widths. Assume:

* C[0].Flag2 and all five left Flag2 inputs are zero, and all incoming
  Workspace.Flag2 bits are zero.
* At least four of the five right Address words are zero. The fifth,
  if present, is arbitrary. These are **decoded raw words**, not adjusted
  Address values or already computed upper fields.
* C[j].Address=(g+j) mod Q at the five left inputs.
* All five left Age words have the same value A in [0,U).

Then the computed upper Address is g mod Q, the computed upper Age is
(A+1) mod U, computed Flag1 is 1, and

    computed Flag2 = 1 iff (A+1) mod 16 = 0.

To prove this, zero raw Address at right offset j contributes -j mod Q
to the adjusted right vote. The four or five such values are distinct
because Q>5. An arbitrary fifth value can raise a multiplicity to at
most two. Hence the apparent colony does not exist. This forces Flag1
and forces the Address/Age votes to use the left inputs, even if Flag2
is 1. Their votes give the asserted computed fields. With no old Flag2
ones and no Workspace2 source, the only Flag2 on-source is the printed
missing-colony/divisible-by-16 clause. It is therefore exactly the
predicate stated above. The printed healthy-erasure clause and the h1
correction give the same answer here: the old self Flag2 is zero.

The missing-colony conclusion also holds with only three null right
words if the other two adjusted values coincide and differ from every
null adjusted value, but **three arbitrary null inputs alone are not
sufficient**: the two other inputs could coincide with one of the three
null adjusted values and manufacture a majority. No argument below
silently substitutes three arbitrary null words for four.

The checker exhausts every position of the possible non-null right word
and all8192 of its values, and compares both actual native scalar readings
on finite phase/Age representatives. The extensions to arbitrary g and
all20-bit A are the modular distinctness and increment arguments above.
The result requires neither a clean global snapshot nor correct clocks
outside this eleven-record bank. It does require the stated bank.

## 2. A correctly installed flag forces the Workspace seed (proved conditionally)

Let b be the left endpoint of a lower colony. In one prospective
Workspace update assume:

* Computed lower Address at b+i is i, i=0..4, and computed lower Age at
  those five sites belongs to [96Q,98Q).
* Computed lower Flag1 is zero at those sites.
* The **final computed primary SimBit** at b+3 is one. This is the
  value after the ordinary simulation update and mandatory wipe, not an
  old SimBit, an intermediate pre-wipe value or a host-evaluated flag.

Gray's p41 equations then set all five Workspace.Flag2 values at b..b+4
to one. This is a direct substitution into his four printed predicates.
They do not require a globally common clock: a locally common computed
clock in that pulse window suffices.

On the next native update, if Address is canonical in the needed
neighbourhoods, all five native Flag2 values at b..b+4 become one. Each
site's N(x) intersects all five seed sites within its apparent colony,
so its Workspace2 on-source is true. This remains true under arbitrary
whole-cell replacement at at most two sites in each relevant eleven-site
neighbourhood: three good right Address words preserve the apparent
colony, and at least three of the five Workspace2 seed words remain one.
Every other field in those replacements is arbitrary. This is a
**single-row seed implication**, not a continuing-noise repair proof.
The checker retains finite actual-scalar payload cofactors; the two
majority/count lower bounds prove the arbitrary-payload extension.
The enumerated two-site supports test this stronger algebraic density
premise; nonadjacent supports in that short interval need not be E0
under Gray's isolation definition. No E0 classification is claimed for
every enumerated support. Genuine original E0 rows are covered when
their local row density obeys the same bound.

Workspace bits computed for output row t+1 are read by the native flags
when producing row t+2. Thus the seed has one further native-update
latency. The statement does not identify a pre-wipe SimBit with the final
one. It supplies no radius-five completion for that composite expression;
the previously pinned [computed-SimBit order audit](GRAY_COMPUTED_SIMBIT_ORDER.md)
remains in force.

## 3. What is required to connect these two lemmas (unproved refinement)

Gray's p35 special procedure computes both upper flags near the end of
the third active stage and writes their redundant lower SimBits at
Address3 and AddressQ-3. At this schedule the third active interval is
[64Q,80Q), and the pulse interval is [96Q,98Q). A stored upper Flag2 must
therefore be ready by80Q and survive the intervening rest and the final
computed-SimBit/wipe equation at the relevant pulse update. Finishing an
evaluator at120Q cannot justify that early command.

To force a command by the preceding native lemma, an implementation must
establish all of the following without assuming the clocks already repaired:

1. Actual third-stage transport, resets, destinations and retained bits
   yield the claimed eleven-record bank. In particular a blocked message
   must decode to null **Address words** at four or more right inputs;
   zeroing a channel or observing a clock jump alone is insufficient.
   Which retained bank or temporal vote feeds the early flag evaluation
   must be specified: p35 describes readiness near the third-stage end,
   while p34 places the described three-bank vote in the fifth stage.
   No choice of early voting implementation is assumed here.
2. The left Age inputs needed by the missing-colony vote remain common
   and progress through a divisible-by-16 computed value. For example,
   A_n=(A_0+n) mod U for sixteen consecutive evaluations would suffice,
   since U is divisible by16. This progression is a premise here; it is
   not deduced from the level-zero clock labels.
3. The physical early evaluator finishes with the correct computed flag
   and the two five-copy flag couriers finish before80Q. The source must
   be the stored result of that evaluator, not an immutable-ROM answer
   substituted for the actual gathered input.
4. The five source copies survive resets/rest and any mandatory wipe;
   the final computed SimBit at the pulse source is consequently one.
5. At least three left-end pulse readers have the required computed
   Address/Age and zero computed Flag1 long enough to seed the next
   native update. The simpler lemma above assumes all five.

For his right-end picture on p40 Gray additionally assumes organized,
relatively aligned full higher-level cells next to an information-blocking
partial cell. Those assumptions matter: he does not say that every
canonical-Address clock jump by itself makes Flag2 one. His p42 three-cell
wave illustration assumes both upper flags were computed and installed;
it does not prove those facts for every possible damaged history.

In particular, even a missing apparent colony does not force Flag2 when
the five left raw Ages are zero: the selected computed Age is1 and the
divisibility source is false. With canonical right Address inputs, the
missing-colony source is false at every Age. These are native conditional
examples, not asserted reachable encoded counterexamples. They show why
the communication and Age-progression premises cannot be discarded.

The original p33 rule erases *all* Mailbox bits where computed Flag1 is
one. A persistent whole-colony Flag1 region is therefore an intended
information barrier. Deriving particular null input banks still requires
the actual five-copy routing, the snapshot and capture clocks, reset
semantics, treatment of self inputs and retained histories. Those
equations are not supplied by a claim that a barrier exists. Our GT0/GH
component proofs and GR1 witnesses retain their original conditional
scopes; they do not discharge this whole-rule refinement.

## 4. GMW7 cannot provide the first authentic pulse as currently compiled (proved gap)

Use the intact infinite-line X and the one shared clock-only real2 error
from the [accepted stationary-clock proof](GMW7_WF0_CLOCK_ISLAND.md):
at tick0 change Age to1 on [0,17Q), leave every other field intact, and
make no later errors. This section uses that already proved full-rule
native orbit; it introduces neither an independent upper error history
nor a prepared replacement initialization.

Until any first commit, actual F7 Info copies remain exactly those of X.
Indeed F7's only Info update is voted old Info, except at computed Age0,
when it commits old Out; its mandatory SF wipe additionally requires a
changed computed Address. Here Address is canonical forever, so there is
no wipe. For output rows1..98Q neither clock phase t nor t+1 equals0
mod U, so no commit occurs. Every five-copy vote reconstructs the same
old logical Info; induction proves this globally, irrespective of Mem,
Head, Out, Scratch or Programme evolution.

In X every logical Info word at colony residue3 or Q-3 is zero. These
unused near-boundary residues are disjoint from the normal representation
primaries4001..4191, including the five recursive Info rows4177..4181.
Their final computed Info values are therefore zero throughout the first
pulse window. This holds for all five raw holders of each primary.

GMW7 writes native Workspace outputs identically zero, and contains no
third-stage flag evaluator, special source write or flag courier. Its
head is born only at112Q+1 and its execution begins at112Q+2. Thus its
current programme cannot put a computed flag at either authentic source
before the first96Q pulse. Even merely substituting the p41 pulse
predicates with GMW7's unchanged final computed Info source values would
still give zero during that first window. This is a pointwise interface
observation, **not an emitted modified rule** and not a claim about its
later periods or its radius.

For a colony inside the clock island the pulse predicate on the update
from physical row t uses computed Age t+2, so its first-window input rows
are96Q-2..98Q-3 inclusive. Outside it uses t+1, giving96Q-1..98Q-2.
Both ranges are entirely before the first commit and head birth. The
checker verifies these exact discrete endpoints and finite actual F7
source cofactors, supplementing the universal held-Info induction.

The single-middle-gather architecture could host an additional early
evaluator and dedicated flag transport, but its existence, own programme,
code/dictionary size, authentic input bank, deadlines and noisy closure
must be proved afresh. GMW7's Q-bit token stream already relies on a
separate51200-bit immutable dictionary, for59392 total immutable bits;
adding gathers alone would not make it Gray's programme construction.
Its ready37Q gather and prepared execution bound49068<6Q leave numerical
room for an additional early pass, for example after a new38Q birth,
with short word-to-end couriers before80Q. This is only a conditional
engineering route: it needs actual early reset/birth/run equations, source
stores, preservation across the pulse, another late pass or retained
commit outputs, and a newly emitted own programme. It does not assume
that the existing gather or execution is correct on the clock island.
No new schedule or rule is emitted or certified in this checkpoint.

## Status

| Step | Status |
| --- | --- |
| Four null right GF words + correct left GF/common Age imply the stated native upper flag | **proved conditional lemma; printed and h1 scalars checked** |
| Final computed source1 + five eligible left readers implies a Workspace2 seed | **Gray's equations apply by substitution** |
| Such a seed forces native Flag2 on the next update, including one-row E0 replacements | **proved conditional count/majority lemma** |
| Null input bank and progressing left Age obtained from an actual damaged Gray hierarchy | **unproved** |
| Early physical evaluator, five-copy source writes and final computed-source persistence | **unproved for a complete faithful Gray rule** |
| Intact GMW7 Info stays fixed through its first pulse; both unused source words stay0 | **proved from actual F7 and accepted clock orbit** |
| GMW7's late-only programme supplies the authentic first command | **false for the unchanged interface** |
| Authentic Flag1/Flag2 waves remove all allowed clock islands | **unproved** |
| Gray/Address/decoded-memory or iid counterexample; smaller U | **not established** |
