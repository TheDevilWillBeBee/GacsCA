This is a deterministic robustness theorem for the explicitly changed
GR1 rule. It permits original Gray level-0 errors only. It gives no
positive iid noise rate and proves no real1 or higher recovery lemma.

Use F, Π, M, A, Q=8192, U=128Q, the decoder and the broad encoding family
E(s) from GR1_NOISELESS_PERIOD.md. Use a robust decoder Δ5 that reads
the majority of the five Info copies instead of just its primary copy.
The two decoders coincide on E. All immutable Π entries are part of the
fixed local transition function, not noisy state fields.

An allowed error set C is a union of groups, each consisting of one site
or two adjacent sites at one tick. Distinct groups are (24,24)-separated:
every pair of their points has spatial distance at least24 or temporal
distance at least24. This is exactly a set consisting solely of original
E0 errors. Let C_t be its spatial section at tick t. Errors replace any
bits of the complete state at their points after that tick's transition.
Write N_D(B) for configurations agreeing outside D with some member of B.
No independence or replacement-value restriction is assumed.

**Theorem (GR1 pure-E0 encoded periods).** Starting from E(s), with any
allowed C and arbitrary replacement states at C, the physical state X
satisfies, at every integer n≥0,

    X_{nU} ∈ N_{C_{nU}}(E(F^n(s))),
    Δ5(X_{nU}) = F^n(s).

The first assertion also holds for a first boundary state already in
N_{C_0}(E(s)); the current C_0 groups must obey the same global isolation
from all later groups. The theorem applies to bi-infinite configurations
and finite or infinite allowed C. It does not apply to iid errors without
a further theorem controlling non-E0 groups.

**Lemma1: local capacity and majority.** Any interval of spatial diameter
at most10, over two adjacent time sections C_t and C_{t−1}, meets at most
one error group. Otherwise points from distinct groups would differ by
less than24 in both coordinates. That group contains at most two sites.
In any five-copy vote the correct bit therefore wins whenever all
differences belong to those two sections. The 80 majority cofactors in
the tracked-transport certificate cover every choice of two holders and
every correct/replacement bit; this is an exhaustive Boolean lemma.

For a five-word vote, if three words equal w then the bitwise majority
is w, at least three words equal that result, and the `exists` test in
the actual `majority_word` helper is1. Its selected value is w. This
argument handles arbitrary full replacements of the other two words,
simultaneously in all13 Address bits and all20 clock bits.

**Lemma2: geometry despite errors.** At every tick, outside C_t the
physical Address is canonical and Age equals the common clock t mod U.
Indeed each left or right five-word vote has at most two erroneous
inputs at that tick. After the spatial Address adjustment, three
remaining words equal the canonical Address; three remaining Age words
equal the common clock. Lemma1 restores both directional values and
their existence tests. Either flag-controlled direction therefore gives
the same correct Address and incremented Age. Inconsistency is false:
at most two in-colony left positions can mismatch either restored word.
Fresh errors produce the only geometry differences in the new state.
Native and Workspace Flags may otherwise be arbitrary in this lemma.

Consequently every procedure uses the correct computed Address and Age.
The mandatory simulation wipe can fire only at a current input error
site: at every other site stored and computed Address are identical.
An Address error can still fire that wipe where computed Flag1=1. The
wipe-wake certificate explicitly demonstrates this; we do not assume
one-tick raw transparency there.

**Lemma3: flag quieting with continuing E0.** Before96Q in a period,
computed Workspace flags are0 because the computed clock is correct.
Outside C_t their current values are therefore0. Initially native Flags
are also0 outside C_0. The exact flag-front cofactors prove that a quiet
Flag1 region cannot gain a computed1 from at most two replacements:
three positive flagged neighbours, or a flagged self plus two positive
flagged neighbours, require three distinct fault sites. Workspace forcing
also needs three sites. Geometry inconsistency is false by Lemma2.
Thus computed Flag1 stays0 before the pulse. With h1, a quiet Flag2
region similarly cannot gain a computed1: turning on a0 needs four
left flags, and keeping an erroneous1 needs two left flags in addition
to the erroneous self. Workspace forcing again needs three sites.
Computed Flag2 therefore stays0. In particular no wipe or mail blocking
is active during the gathers, early programme or couriers.

Both Workspace outputs are0 at Age98Q and afterwards, apart from fresh
errors, since the computed clock is outside the pulse. Start a guaranteed
Flag1 zero suffix at the right edge of each colony, permitting exceptions
at current C_t sites. The suffix never retreats. A cell within it has
otherwise-zero positive neighbours and self; two errors cannot meet
either Flag1 threshold. If the first zero site is b, the suffix advances
by at least two sites on any row whose current errors avoid[b,b+4].
With no such errors, the two new targets have at most zero and one
positive flagged neighbour respectively. On a charged row we retain
the guaranteed suffix, advancing the boundary by zero. This conservative
boundary consequently moves at most two sites per row, even if actual
quieting is faster.

Two charged rows separated by Δ≤9 would have error points within
2Δ+4≤22 sites and Δ≤9 ticks. They would be(24,24)-linked, contradicting
distinct original-E0 group isolation. Charges are therefore at least10
rows apart. Among n rows at most ceil(n/10) are charged, so guaranteed
growth is at least2(n−ceil(n/10)). Its first value reachingQ is n=4552.
At that time computed Flag1 is0 everywhere. This condition is stable
under E0 by the earlier quiet-region argument.

Start a Flag2 zero prefix from the left colony edge once global computed
Flag1 is quiet. With computed Flag1=0, only in-colony left flags enter
the h1 healthy rule. The prefix never retreats: a clean zero cannot turn
on from two erroneous left flags, and an erroneous self1 has at most one
other erroneous left flag. If the last guaranteed zero site is a, an
uncharged row avoiding[a−4,a] advances by two sites. The new targets
have at most zero and one left flags. The same charge-distance proof
gives a further4552 rows. The exact616 native cofactors cover all11
native Address boundary classes, a free20-bit common clock, every pair
location in the local cone and every replacement Flag/Workspace bit.
They certify non-invention and uncharged growth for both fronts. Lemma2
separately accounts for arbitrary Address/Age replacements.

Thus computed native Flags are quiet by

    98Q+9104 = 811920 < 100Q < 112Q.

They remain quiet, apart from fresh raw errors, until the next pulse.
This bound applies independently to every colony, with arbitrary pulse
values and arbitrary native Flags when the pulse ends. It is not a
measured speed estimate or a real1 recovery assertion.

**Lemma4: the two-section data invariant.** Compare each noisy period
to its noiseless evolution from the matching E(s) state. The data fields
are all tracked fivefold simulation fields and the register/pending
interpreter fields; native/Workspace Flags are excluded. At every tick
their differences are supported in

    C_t ∪ C_{t−1}.

Where computed Flag1 is quiet they are supported just in C_t.

We prove this by induction. The base follows from N_{C_0}(E(s)). At a
next transition Lemma1 restores every five-copy tracked-bit read to its
noiseless value. For Hold/scratch the three corrected pending components
and the corrected stored bit are all recovered first, so their forwarding
branch and value are also correct. The actual integration/coupling proof
and complete route partition therefore give the same tracked outputs
before masks.

Before96Q computed Flag1 is0 by Lemma3, so Mailbox masking cannot differ.
At96Q both mail tracks reset to0. There are no later courier loads or
mail movements in the period. Their corrected input remains0 even if
fresh errors write mail bits, so later nonuniform Flag1 masks are harmless.
Every other data mask is the GF-mismatch wipe; by Lemma2 its support is
within the current input error section C_t. This may erase two holders,
but not a third. An older wake cannot cause another wipe: its stored
geometry has already been restored. Fresh output errors add C_{t+1}.
This establishes the stated support with the time index advanced.

For compact registers, votes at arbitrary nonfront positions need not
restore an unrelated register vector. We only need the selected register
source of an arriving front. Its five physical holders form a coherent
cohort in the noiseless evolution. Lemma1 restores that vector. The
exact nonmatch route classes then give identical lookup keys, ALU operands,
register updates and pending outputs on all arriving holders. No other
slot arrives, and nonarriving outputs are0; their possibly different
lookup is I-irrelevant. The Match certificate likewise restores its
selected carried key/selector and loaded instruction. The immutable
Π lookup therefore matches on every relevant visit.

In fact both interpreter windows are entirely quiet: the early one lies
in[70Q,72Q), before the pulse, and the final one lies in[112Q,120Q), after
Lemma3's noisy flag clearing. The current-GF wipe never fires in either.
During the intervening pulse interval all register/pending outputs are
inactive0. Thus no native wipe can create an interpreter-counter or
instruction-buffer wake during its active operation. The full front and
write identities apply with only fresh current-error copies to correct.

All stage/capture/reset times are computed-clock times, so Lemma2 also
prevents an error from skipping or moving a required reset. Two-section
data restoration includes the boundary sources used by those resets.
This proves Lemma4 without assuming that a wipe wake is itself an error
location, or silently enlarging the original E0 set.

**Theorem proof.** By Lemmas2–4 all three gathers supply the exact encoded
upper input bits at the locations proved by the33 gather-coordinate
identities. In particular the entire gather/courier intervals are before
the first possible legitimate Flag1 source. The retained histories and
fifth-stage vote remain majority-correct even during two-holder wipes.
The early prefix has its universally correct inputs, executes with the
restored five-copy register/pending fields, and loads both correct flags
into the couriers before their proved deadlines.

The fresh fifth-stage replay similarly has its exact voted inputs.
Its selected fronts and physical Match/fetch have their proved values;
the outside-work lookup case remains I-irrelevant as in the clean proof.
The universal own-programme identity gives F(s)_i[b] in the corrected
Hold at each layout position. Both windows are wipe-free by Lemma3.
Every Hold/scratch write and one-tick pending application precedes120Q,
and no stage reset occurs inside either evaluator window. Later Hold
votes preserve these values through the final rest.

At computed Age0, corrected Hold commits into Info while all other
tracked private fields reset. Fronts/pending fields are inactive0 and
Workspace flags are0. Computed native Flags are quiet and geometry is
canonical/common. There is no wipe at this boundary, even at an erroneous
stored Address. Therefore the entire computed output, before fresh C_U
replacements, equals the matching noiseless state in E(F(s)). After the
replacements it is in N_{C_U}(E(F(s))). Each layout's five-copy majority
has at most two erroneous holders and returns F(s) exactly. This proves
the first period's two assertions.

The same argument starts from that boundary state: its only differences
from an E(F(s)) member are the current C_U errors. Global original-E0
isolation still relates those groups to subsequent ones. Induction gives
the result at every boundary. Every assertion at a fixed site and finite
time involves finitely many inputs; the argument consequently applies
to infinite C without any compactness or independence assumption. ∎

**Scope.** The wake certificate refutes unconditional one-step raw-field
transparency but is compatible with this two-section invariant and exact
boundary decoding. The conditional primitive/coherent-front lemmas alone
did not imply this theorem; the noisy flag fronts, clock restoration and
explicit wake induction are additional arguments. GR1 still replaces
computed SimBit by corrected current SimBit, corrects erasure to h1,
uses its large two-index hardwired ROM and has an unproved literal-Gray
rest/ProgramBit refinement. No claim about real1 localization, higher
error classes, iid reliability or ε>0 follows from this theorem.
