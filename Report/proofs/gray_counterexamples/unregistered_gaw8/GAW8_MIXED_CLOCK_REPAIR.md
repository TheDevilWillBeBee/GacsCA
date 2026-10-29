# GAW8: 795 actual nonuniform clock/control histories recover completely

This is a finite, exact positive repair result for the **frozen changed GAW2R
rule**, not a counterexample. The rule has Q=8192, U=128Q=1048576, and the
original error-class parameters lambda=24 and c=104. Its radius8/WORD100,
immutable instruction dictionary, h1 Flag2 correction, early pass and 102Q
late birth remain departures from Gray. No rule, schedule or programme is
changed here. No Gray, G17, iid-memory or general-real1 theorem follows.

## Exact statement and initial physical history

Use the global recursively intact initializer H defined and proved in
[GAW4](../unregistered_gaw4/GAW4_INTACT_REAL1_MAIL.md) and its actual first-period
prefix in [GAW6](../unregistered_gaw6/GAW6_NATIVE_CONTROL_MAP.md). The authoritative
definitions are `I`, `H` in the frozen `check_gaw4_real1_mail.py`, and `bank`,
`row96` in the frozen `check_gaw6_actual_bank_map.py`. All later expressions
use that H and the actual emitted GAW2R ROM, rather than independently
selected upper cells, Histories or tapes.

Let T=96Q. At physical row T+n, overwrite the native Age, Flag1, Flag2,
Workspace.Flag1 and Workspace.Flag2 of the sixteen cells b..b+15. Retain
each cell's actual GF and all thirteen actual five-copy SF fields. The
replacement Age is T+n+l, with 1<=l<=16; four replacement flags are the four
bits of the recipe's nibble. Perform either one row or sixteen consecutive
rows n=0..15, with no errors before T or after the listed rows. `native_rows`
in the immutable original campaign JSON specifies every replacement l and
nibble for each of 795 cases, without random choices during replay. Allow
any simultaneous spatial translate b+gQ, g in Z, of any listed recipe.

**Theorem (specific histories, exact finite certificate).** Every such
history agrees with the complete global noiseless shadow by row T+8182,
and agrees at every subsequent physical row. In particular the raw first
period boundary, every later boundary and their decoders are exactly the
noiseless boundaries/decoders. The greatest observed/certified clock
recovery in this list is 5111; the greatest all-native recovery is 8182.
These are finite computer-assisted statements about the listed histories,
extended to all integer-Q translates by the proved factor. They are not
universal recovery bounds over all 16x16 replacement payloads.

Every listed fault history is one original-c104 real1. The actual changed
point set is obtained by comparing the chronological replacements with
their actual pre-overwrite native values. It contains the full first
sixteen-site row: each first Age differs from clean T. It is contained in
a 16x16 box. Any singleton/adjacent spatial pair has other first-row sites
within (24,24), so E0 is empty. Two distinct first-row singleton candidates
are linked. The entire set fits a QxU box, and any two nonempty subsets
have all point differences <104 in both coordinates; condition(iii) holds
for the printed level-1 candidates. Condition(iv) is vacuous because there
are no other errors. The classifier is run on each exact changed point set
and also each declared overwrite set. Equal-valued later overwrites are
recorded and excluded from the actual changed point set.

## 1. Actual clean row T — previously proved argument applies

GAW4 proves H=E(H,0) field by field, including mutable physical Programme
copies and all represented Info slots. Its recursive I terminates by strict
decrease of absolute spatial coordinate. All special primaries 3 and Q-3
have I=0 in every colony. The clean actual three-gather/early-evaluation
prefix gives, at row T and every physical x:

* native GF=x mod Q, Age=T, four flags=0;
* Info holders I(x+S[h]) and Programme holders beta((x+S[h]) mod Q);
* each of the three History banks has holder B(x+S[h]), where
  B(y)=sum_{j=-8}^8 I(y+jQ) 2^{100(j+8)};
* Head, Mem, Out, Scratch, both Mailboxes and both couriers are zero.

These are actual held fields after the reset, with all three gathers and
the early programme in the same noiseless history. The campaign does not
initialize a simulation directly with those banks. It uses the proved
prefix to derive them. The immutable dependency manifest pins that prefix,
initializer, rule source, full own programme and ROM equivalence receipt.

## 2. Held-SF phase invariant — proved, actual full local transition

For any canonical GF geometry, both left/right adjusted GF votes equal
the correct self GF, for arbitrary native Ages and four native flags.
Every branch in `scalar_native` therefore returns canonical GF. GAW2R's
wipe is `newF1 && newGF != rawSelfGF`; it is false. For every raw holder x
and offset S[h], the SF service Address is exactly
`(computedGF(x)+S[h]) mod Q = (x+S[h]) mod Q`. Thus its five-copy vote reads
the same logical coordinate at every holder. Coherent held SF copies vote
to their held value.

Age refinement only chooses an old directional majority or the old self
fallback, then increments modulo U. Assign label0 offset0 and label l
offset l for l=1..16. Different labels have different Ages. At row T+n all
Ages are T+n+label; the four native flags may be arbitrary. Faults at n<16
insert another label in1..16. Consequently, for 1<=n<=4Q every newly
computed Age lies in

    T+n <= Age <= T+n+16 < 102Q < U.

No wrap or illegal 20-bit clock word occurs in this interval. This
conclusion is an induction over the actual refinement, not a precondition
that damaged clocks are common or that upper Ages are correct.

Now inspect **every** SF equation in the frozen `local_transition`:

* No History reset/capture occurs after the last capture72Q+2 and before
  reset102Q. Each coherent B vote is held.
* No Mem reset or reconstruction occurs strictly between96Q and102Q.
  Its initial zero vote is held.
* No Head birth/reset/active interval is entered. The heads are held zero;
  no nonzero packet, output or scratch write can be produced.
* Info holds its I vote. The phase0 Out commit and phase80Q-1 special writes
  are absent. Programme is hardwired to the same beta bit at the exact
  canonical service Address.
* Mail starts zero. All LOAD/shift windows precede80Q and no reset/load
  occurs here. Holding zero or erasing it on newF1 produces zero.
* Couriers start zero. Seed75Q, guarded forwarding75Q..80Q and special
  store80Q-1 are absent. They remain zero.
* `computed_primary` has no phase0/80Q-1 write and no wipe in its own
  radius5 computation. At the two source primaries its held I is zero.
  Both newly computed Workspace flags are therefore zero, even during
  the actual half-open gate96Q<=computedAge<98Q and with arbitrary newF1.

These equations prove all thirteen raw SF tuples remain exactly their row
T values through T+4Q. Noise does not change those fields. This is a
global interval invariant, independent of colony index and of any
particular shape of the native damage. It supersedes the first campaign's
3844-tick source-cone limit for the stated offsets1..16 only. Larger raw
Age offsets, GF/SF errors and intervals reaching102Q are not covered.

The actual-rule cofactor checks exercise all native boundary predicate
classes, both special-source regions and every normal represented primary,
with freely chosen Flag1/Flag2/Workspace inputs and clock labels. They
supplement this equation proof; sampling does not supply its universal
quantifier.

## 3. Exact categorical native factor — proved reduction and finite replay

Encode a native cell by its Age label in low16 bits and its four raw flags
in bits16..19. Canonical GF is supplied by position; newly computed
Workspace flags are zero by section2. The C `local` function implements
the frozen actual native rule: directional five-vote existence/fallback,
in-colony Age mismatch, Flag1 sources/right threshold, and corrected h1
Flag2 propagation/erasure, then chooses R or L label. No replacement
payload silently clears a surviving raw Workspace flag before its native
use. The same fault rows are inserted after computing the next row.

Equality of actual Ages is equality of labels. All arithmetic dependence
on x reduces to x mod Q and the inside-colony predicates. The finite
cofactor receipt checks the C factor against actual `scalar_native` with
arbitrary modular phases and distinct offset labels. Section2 establishes
its newly-zero-Workspace premise for the complete physical history here.

The factor is simulated on Z with zero categorical exterior, not on a
periodic or clipped finite domain. A nonzero tuple can only reach distance
five from old nonzero support; zero exterior maps to zero at every colony
phase. At each tick split the enlarged finite interval at all old segment
endpoints shifted by -5..5 and colony boundaries shifted by -5..5. On each
half-open piece all eleven old tuples and inside predicates are constant;
the native label/flag result is therefore constant. The implementation
asserts the endpoint tuples, predicates and local outputs agree. This
event partition exactly computes the infinite-line step.

The initial source used linear segment lookup. The extended source uses
binary lookup for the first segment with hi>x. Segments are sorted,
nonoverlapping and coalesced; the result is its value exactly when lo<=x,
otherwise zero. This is the same lookup equation. The two implementations'
native cofactors and all 795 initial-horizon result records are reproduced.
The preserved initial source, binary, campaign and initial log retain the
first result: case628 stopped at3844 with unresolved clocks. That was a
query-horizon stop, not an actual failed-repair witness.

With the proved4Q source/phase interval, exact extended simulation gives
zero entire native disagreement for every listed case by8182< Q<4Q.
Case628 has clock recovery5111 and all-native recovery8182, with at most
1824 nonzero constant segments. The old query stopped at3844 with1450
segments. Its complete original payload, final old query state and extended
record remain pinned. No MAX4096 capacity or event-consistency assertion
fails in any certified replay.

GF/Age/flags reduction and SF interval proof are translation equivariant
under integer multiples of Q. Although I and B themselves can vary by
colony, their held-coherence and special-zero properties hold in every
colony. Thus every listed translated physical history has exactly the same
native recovery record; its own actual SF remains its own clean held SF.

## 4. Full physical and decoded repair — proved composition

At each case's native recovery row (at mostT+8182), all native fields equal
the clean reference globally. Its raw SF fields equal rowT SF by section2;
the clean reference is in the same held-SF interval and also equals rowT SF.
Hence the **entire global raw configuration** equals the noiseless shadow.
There are no subsequent errors. Determinism gives equality at every later
physical tick, not just equality of majority critical fields. Applying any
decoder to equal configurations gives equal decoded configurations.

The frozen all-raw noiseless period theorem identifies the clean nU
boundaries as E(F^n(H),0). Therefore every listed fault history has exactly
that complete encoding at every nU, n>=1. There is no sacrificed upper
error in these cases, no raw boundary residue, and no need to invent a
later prepared tape. All late inputs and execution follow from exact
pre-102Q global equality and the already proved noiseless theorem.

## Status and limits

| Step | Status |
|---|---|
| Intact H, actual row96Q and frozen own-rule/noiseless period | Previously proved arguments apply; hashes pinned |
| Canonical GF for arbitrary native clock/flag inputs | Proved by actual directional GF equations |
| All-SF interval invariant and actual zero Workspace output | Proved from every frozen local SF guard, offsets1..16 |
| C categorical factor/event compression/infinite exterior | Proved reduction, actual-rule cofactor and exact event checks |
| 795 cases recover by8182; case628 clock5111 | Exact finite computer-assisted proof/replay |
| Original-c104 class of actual shared error histories | Proved dense-first-row/16x16 argument; exact classifier replay |
| Whole raw shadow equality and all subsequent decodes | Proved composition, no later errors |
| Arbitrary Age payloads, mixed GF/clock/SF or all real1 histories | Unproved |
| Literal/corrected Gray full refinement or Gray theorem failure | Unproved; material GAW2R changes retained |
| Positive iid rate, iid failure, all-noise reliability or smaller U | Unproved |

The certificate is evidence that this search family repairs, rather than
evidence that the intended higher-error theorem is false. In particular it
does not settle the behaviour of clocks placed outside the held-SF phase
interval or faults that damage GF, Programme, Head, Out or History.
