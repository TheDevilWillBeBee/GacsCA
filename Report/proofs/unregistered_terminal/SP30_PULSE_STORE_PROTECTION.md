# SP30: uniform conditional protection of early Hold sources

This concerns the unchanged frozen F30, Q1024/U475136/radius37,
TF278401 and S=TF+6144. It is a conditional physical-store lemma,
not an accepted actual-history induction. The missing uniform
gather/controller premise supply in
[the regeneration draft](SP30_PERIOD_REGENERATION_DRAFT.md) remains
unproved. No rule, programme or accepted receipt is changed.

## Statement

Let K be any integer. Run the actual F30 with its frozen own ROM,
without further errors, from a period boundary. Assume:

1. All807 reset fields are initially zero. Before TF the native
   state is the quiet T(K,K+6), with the common legal lower clock.
2. During TF..S every computed Address used by the actual front
   equations is either x modQ or (x+512) modQ. The lower clock is
   common and legal, and advances through the actual period. No
   arbitrary pending record or instruction is substituted. Wipes
   and all other evolving private/payload values may be arbitrary.
3. From S through the U boundary the native state is quiet
   T(K-6,K), with that same clock. At every row, all noncanonical
   raw and computed GF sites are in the closed hull
   [KQ-7616,(K+6)Q]. Whenever canonical protection is invoked,
   its five holders and their radius37 neighbourhoods lie outside
   this hull. These are explicit native-history premises.

Write A={59,...,68,88}, the normal GF and F1 Hold phases.
Then every one of the330 physical Info copies at

    jQ+a, K<=j<K+6, a in A

is zero at the next period boundary, regardless of every other
payload. No own evaluator result in these recovered frames is
assumed. The assertion includes the normal F1 source as well as GF.

Additionally, suppose all five Hold copies at a normal primary
y=jQ+a, a in A, have a common value v by TF. If all those holders
and their radius37 neighbourhoods stay outside the hull, and their
computed GF is canonical throughout, those copies retain v until
commit and write v into Info at the next boundary. Here v may be
arbitrary; it need not come from a correct evaluator.

The protected instances relevant to regeneration are j=K-8 for
all a in A and j=K+6,...,K+23 for a=59,...,68. Their clearances
are verified below. They give a renewal implication once the
pre-TF Hold values are actually supplied. They do not supply them.

## Why malformed work cannot invent a Hold destination

At a logical physical primary y, the five copies belong to that
same y even if its GF changes phase. The copy-index formula for
lv reads positions y-e for e in SLOTS. GF changes affect the
arrival/ROM key and keep mask; they do not reattach a stored copy
to a different physical primary.

For a common clock, the comb arrival targets are base+j*5 modQ,
j=0,...,4. A holder's logical Address for y is either y modQ or
(y+512) modQ. Both phases cannot arrive in the same row: their
difference512 is absent from every comb-tooth difference, whose
signed magnitude is at most20. Within one phase the tooth is
unique. The actual all-raw single-arrival lemma also excludes a
second logical slot competing for the holder's instruction lookup.

Outside a Match pass, page/tooth and hence the ROM selector depend
only on that common clock and the arriving phase. All simultaneous
records for y therefore have the same opcode and destination kind.
On a Match pass the actual executing guard is false, irrespective
of the damaged register-dependent lookup selector. No pending store
is generated there. This is why a raw ROM audit alone would not
have been enough.

Each new absent pending copy has kind0. A present one has the
common kind k. Wipe may remove it and zero its kind. If the old
presence vote is1, at least three copies have that same k, so every
voted kind bit is k. Otherwise the voted presence is0 and the
payload/kind is unused. Bitwise majority cannot turn a scratch
destination into a Hold destination under these conditions. The
argument covers all k in0..7 and arbitrary pending values. Initial
reset and the actual recurrence exclude an unexplained pending
seed. Registers, scratch and old upper data can change the value
of a permitted store, but cannot change these destination times.

## The actual22 store phases

For each a in A the frozen listing and all4096 raw selector keys
have exactly one Hold opcode at virtual phase a and exactly one
at a+512. The former materializes before TF; the latter issues
after S. The six recovered colonies initially have phase a+512,
so no eligible pre-TF write has targeted their normal Hold groups.
Their initial zero survives voting, clear-Hold and wipes. During
TF..S neither possible phase can issue a Hold write there, including
the actual pending forwarding/materialization latency. Afterwards
their phase is a. Its only Hold issue has already passed; the
later a+512 opcode cannot arrive at these now canonical holders.
Thus all five copies stay zero until commit.

For a protected canonical primary, its common v was already
materialized by TF. The sole same-phase Hold issue has passed.
It cannot acquire an opposite-phase issue. Canonical raw geometry
in the radius37 reserve makes refined self GF canonical too;
computed GF agrees, so keep=1 regardless of Flag1 or payload.
Five votes preserve v. No later same-phase Hold write exists.
This proves preservation through U-1. The actual commit identity
forwards that voted Hold, and A lies in the allowed Info mask.
All807 non-Info private fields reset at this same boundary.

The protected left edge has largest reservation endpoint

    (K-8)Q+88+2+37 = KQ-8065 < KQ-7616,

with449 cells of clearance. The right prefix's smallest endpoint is

    (K+6)Q+59-2-37 = (K+6)Q+20 > (K+6)Q.

Integer K cancels from both inequalities. The recovered cohort
has6*11*5=330 copies. If right receivers K+6..K+23 have stored
GF0 by TF, the lemma gives GF0 at K..K+23 at the next boundary.
For K'=K-6, trimming to K..K+22 gives precisely
K'+6..K'+28, with one spare colony. This last implication is
conditional on the actual right stores, not merely circuit outputs.

## Status

The destination exclusion and protected Hold implications above are
proved under the explicit native-history/initial-reset hypotheses.
The accompanying checker audits the22 actual ROM phases, timing,
comb separation, pending-vote cases, commit mask and translation
arithmetic. The all-period supply of those hypotheses and of the
correct pre-TF stores remains **unproved**. No full decoded data,
permanent defect, general repair, iid rate or Gray counterexample
follows from this lemma.
