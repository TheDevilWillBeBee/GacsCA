# GBD4: counted native software on a literal packed bank

This is an isolated component for the requested **Q=8192, U=128Q=1,048,576,
λ=24, c=104** investigation. It changes GBD3's READ by adding one bank
selector bit and supplies actual software for the native calculation. It
does **not** supply a full own programme or a complete automaton. No active
repository rule, previous component or error-class definition was changed.

The component addresses the whole-rule bottleneck more concretely than a
native-evaluation oracle: the programme obtains every input through ordinary
raw-holder READs, tests equality using bounded loops, writes intermediate
words to actual Out sites, and emits the four native outputs. The remaining
Workspace/SF/controller/packing calculation is absent. The unoccupied
programme bits are an arithmetic remainder, not a fit certificate for those
missing calculations.

## Exact theorem and premises

Let `R[-8]..R[8]` be arbitrary **3387-bit raw upper records**, with the field
order in [layout.py](layout.py). Every bit pattern is allowed: Address is
any 13-bit word, Age any 20-bit word, all four native flags any bits, and
upper simulation-field holders may be incoherent. This is not a restriction
to canonical upper geometry, quiet upper flags, or a recursively encoded
upper state. The software ignores upper simulation fields in this theorem.

Assume the lower execution has:

- canonical, common quiet **computed native ports**, so each holder supplies
  `(physical Address+copy offset) mod Q` as the service Address;
- coherent immutable Mem340 words at logical sites `P+h`, whose 17 lanes
  are the actual twenty-bit slices of `R[-8]..R[8]`, with zero padding after
  bit K, for `0<=h<170`; Mem is arbitrary elsewhere;
- exactly one coherent five-copy Head at logical Address `P+2=2405`, present,
  RUN mode, PC0; its registers, return link and old target may be arbitrary;
- arbitrary coherent old Out20 words and no competing Heads, no reset,
  stage disable, GF wipe, external SF action or errors during execution.

Run the literal [controller.py](controller.py) Head and balanced WRITE
equations with `base=-2, cap=20`, and the emitted programme. The emitted
**h1** programme writes Address/Age/Flag1/Flag2 equal to
`maintenance_scalar(R[-5..5],Q,U)` at output raw bits0..34. The **printed**
programme writes the same four fields as the preserved literal Gray
transcription in [literal_maintenance.py](../literal_maintenance.py).
Both halt within **33,937 actual updates**, including all one-site travel
and target settling; neither ever places a Head outside `[2405,2600]`.
Both have identical coherent five-copy output words after every update.

These are universal prepared-bank component statements. The lower premises
are **assumptions**, not consequences of this programme. Native ports,
gather origins, reset/birth, mandatory wipe, whole-period composition and
intact recursive initialization are not proved here. The no-error premise
is substantial; no c104-class or random-noise repair theorem is obtained.

## Exact programme, storage and interface change

[native_emitter.py](native_emitter.py) emits ordinary LIT, ALU, BR, READ,
WRITE, MOVE, CALL, RET, GETHEAD and SETHEAD instructions. Neither listing
contains a native/full-rule opcode, callback, dictionary or host evaluator.
Expected native outputs are calculated only by the independent checker.

| Item | h1 programme | printed programme |
|---|---:|---:|
| Emitted binary bits | 7,051 | 7,106 |
| Instructions | 408 | 411 |
| Main, including HALT | 5,561 | 5,616 |
| RAW helper | 463 | 463 |
| RAMLOAD / RAMLOAD5 / RAMSTORE | 100 / 100 / 96 | 100 / 100 / 96 |
| Q5 helper | 731 | 731 |
| Out-of-Q branch/call targets | 0 | 0 |
| Q minus native-only listing | 1,141 | 1,086 |

The beta file is the entire counted immutable binary stream for this
component. Arbitrary/nonaligned PC decoding, truncation and invalid LIT
lengths retain total ISA behavior. The execution theorem begins at PC0 and
does not assert termination from arbitrary raw Head state. Immutable code
is an explicit departure from Gray's mutable ProgrammeBits/hardwirer.

READ now occupies **18 bits**, rather than GBD3's17: opcode4, destination3,
lane3, phase3, count3, stride1, bank1. Bank0 reads old voted Mem340. Bank1
reads old voted Out20 and permits only lane0; any invalid descriptor returns
zero. READQ remains17 bits and retains bank0. READ's bank1 equation reads
each bit from exactly the same five actual lower holder slots as bank0.
For arbitrary raw controls its source coordinates are

`x + S[q] - 2 + floor((phase+stride*i)/20) + S[h]`,

with slot `INV[h]`, where `S=(0,-2,-1,1,2)`, `INV=(0,4,3,2,1)`.
For phase0..19, count0..20, stride1 or5, the largest absolute offset is7.
The existing actual Head movement uses radius3, and balanced WRITE20 uses
radius7. Therefore this whole **port-level Head/Out component** has radius
at most7, within the radius8 proposal budget, on every raw state. This does
not certify the undeclared native/source/other-field composition.

The K3387 layout is unchanged from GBD3: native37 bits, five copies of670
simulation bits, including Head204, Mem340 and Out20. No additional field
or array was inserted. Head204 contains eight Word20 registers and one
13-bit return link. Q5 temporarily saves that link in register R3 bits6..18;
bits0..2 contain a candidate index, bits3..5 its equality count. This is
19 actual bits of an existing Word20, not a stack or uncounted controller.

There are **nine** used scratch Out20 words, explicitly at
`2589,2590,2591,2592,2593,2594,2595,2596,2598`. The inclusive bounding
interval2589..2598 has ten positions; **2597 is unused**. These store RG,
LG, RA, LA, RA-existence, two count words, newFlag1 and newFlag2. RG packs
the 13-bit value plus one existence bit; RA's20 bits require a separate
existence word. Every used scratch word is overwritten before any read.
The lower Mem bank ends at2572, and the two output words are at2403/2404;
these refer to separate real fields even when a coordinate is shared.

## Universal equivalence proof

**Status: proved as a software/component theorem under the stated premises.**
The proof is compositional; full-run examples supplement it and do not
replace its arbitrary-word quantifier.

1. **Literal physical execution factor.** Coherent five-copy Head, Mem and
   Out votes reproduce their logical words. For every output role q, the
   source centre is `y=x+S[q]`; canonical computed ports give service
   Address y mod Q. Stationary execution consequently agrees across all
   five holders. The Head's target is strictly inside the same colony:
   actual actor equations advance one site toward it, settle on arrival,
   or settle for one tick if already there. No competing incoming Head is
   present. An old stationary WRITE has the same decoded request at all
   holders; its literal receiver equation writes identical five copies at
   each addressed Out word. Unaddressed words remain voted old words.
   This is induction on actual local updates, not a host MOVE operation.

2. **RAW helper and input coordinates.** The descriptor supplies raw base
   b (12 bits), width w (5 bits), and optional Address adjustment (bit17).
   RAW physically moves to `P+floor(b/20)+2`, computes phase `b mod20`, and
   READs lane l at stride1. For bit i it therefore reads actual logical
   Mem container `P+floor((b+i)/20)` and lane l's bit `(b+i) mod20` through
   its five lower backups. With the stipulated packed bank this is exactly
   `R[l-8]`'s raw bit b+i. Native b values0,13,33..36 and widths13,20,1
   stay within the actual K-bit records, including cross-container Age.
   If requested, the helper returns `(Address-(l-8)) mod8192`; all unsigned
   20-bit intermediates and the final 8191 mask give that identity also
   for negative offsets. RAW preserves R1..R5 and the saved link in R3.

3. **Actual mutable RAM.** RAMLOAD/LOAD5/STORE move to `2589+index+2`.
   Bank1 READ obtains the old voted Out20 at Head−2. Balanced stride1
   WRITE phase0/count20 replaces that one real word. LOAD5 preserves R0,
   for comparing a freshly read raw value against a stored quorum. All
   three preserve R1..R4. No RAM helper nests a CALL, so the one return
   link suffices. Mem is not modified by any store.

4. **Q5 arbitrary-word quorum/fallback.** The outer index visits at most
   five candidates. For each it calls RAW once for the candidate, then
   five times for all tested words; the packed match counter increases
   by8 exactly when equality holds. A count>=3 is a unique whole-word
   quorum. If none exists, RAW reads lane8 (the actual self word), and
   the helper returns it with existence0. The saved13-bit link and both
   three-bit counters do not overlap or overflow: the largest value is
   less than2^19. Clearing bits3..5 restores the candidate index before
   its increment. Extracting R3>>6 and SETHEAD restores the exact caller
   return. This proves all13-bit Address and all20-bit clock patterns;
   fallback is the raw self value, without an unstated legal projection.

5. **Native count loop and liveness.** Four Q5 calls obtain adjusted right
   and left Address and unadjusted right and left Age quora, including
   existence and self fallbacks. The CELL loop runs exactly eleven times,
   with i=0..10 and j=i−5. R1/R2 store counts, R3=i, and R4 stores the
   inside bit in bit18 plus the RAW descriptor in bits0..17. RAW and RAM
   preserve the registers each caller needs. Right eligibility is exactly
   `RG-exists && 0<=RG+j<Q`: negative values wrap above Q in Word20, while
   nonnegative values are at most8196 and are compared directly with8192.
   Left mismatch compares adjusted raw Addresses with RG, equivalently
   rawAddress!=(RG+j)modQ. The loop collects the exact four left/right/WF
   count fields required by each native clause. Each count is at most11,
   so four nibble fields never carry into one another or overflow Word20.

6. **Native flags and selector.** The straight-line code forms Flag1 from
   missing right Address/Age quorum, three eligible left Address or Age
   mismatches, three eligible WF1, three eligible right Flag1, or old-self
   Flag1 with two eligible right flags. Source3 is absence of right Address
   quorum and `(leftAge+1) mod16==0`; source4 is three eligible WF2. Old
   Flag2=0 uses the two four-left-flag tests or either source. For old
   Flag2=1, the printed programme's healthy erase is
   `eligibleLeftF2count==eligibleLeftCount`, faithfully preserving Gray's
   printed “no left zero” predicate. The **explicitly changed h1** version
   instead erases when eligibleLeftF2count<=1. When newFlag1=1 both erase
   exactly when all five left raw Flag2 bits are zero. Neither predicate
   is silently substituted for the other. The final selector is right
   quorum existence AND (NOT newFlag1 OR newFlag2), exactly the stipulated
   native Address/Age clause. It writes the chosen13-bit Address and
   chosen Age+1 modulo2^20, then both flags. The output writes mask only
   their actual35 native bits; other old Out bits are held.

This agrees with Gray's local native equations as transcribed, for the
printed version, and with the explicitly corrected h1 equations for h1.
It does not prove that this software's state/schedule/immutable-code choice
refines Gray's full construction. The previously accepted literal Flag2
printing contradiction remains separate; this work produces no new Gray
counterexample.

## Universal bound and schedule scope

**Status: proved as a prepared software bound; autonomous deadlines unproved.**
[cost_contract.py](cost_contract.py) checks all listing targets and expands
both possibilities of every nonconstant conditional branch. The only
backward targets are CELL, Q5_TEST and Q5_CANDIDATE. The proved loop
invariants bound CELL by11 and each Q5 by5 candidates×5 comparisons.
Calls are composed with helper contracts, not evaluated on a sampled bank.

Every physical MOVE target lies in2405..2600. A movement requires at most
195 travel updates, or one settling update for distance0. A Q5's first RAW
may travel195; all following RAW calls use the same native base container
at2405, so each costs one settling update. The branch overapproximation
even permits left and right count clauses simultaneously on every CELL
iteration; this safely exceeds the actual branch costs.

The resulting bounds are8077 stationary instruction updates plus25860
travel updates, totaling **33,937** for either listing. It admits192 RAW
calls,56 RAM calls and4 Q5 calls. Its helper maximum is1136 instructions
and225 travel updates for Q5. The listing fits a mathematical 8Q−1
execution budget and also6Q−1, but **no stage birth, bank preparation,
quiet-window or total-period deadline is concluded from this comparison**.
U has not been shortened or any active schedule instantiated.

## Checks, receipts and remaining work

[check_native.py](check_native.py) recomputes the literal listings, validates
instruction boundaries, checks the new READ bank's independent raw-holder
equation, all52 equality partitions of five words, packed-link algebra,
all2048 left eligibility/Flag2 predicate cases, and all12^4 packed counters.
It retains twenty complete selected native software runs (ten per printed/
h1 choice) from arbitrary coherent old Out/registers and genuine packed raw
records. Those are **measured checks**, not exhaustive tests of the native
input space. [execution.py](execution.py) calls actual actor/write equations
and retains input records, actual READ coordinates, execution counts, all
written Out words and selected raw five-holder identities.
[check_arithmetic_liveness.py](check_arithmetic_liveness.py) separately
checks180,224 unsigned Address-adjustment/eligibility identities and the
literal helper register-write sets; those establish the preservation
claims used by the actual callers.

Attempt01's successful first execution was followed by a relative-path
serialization exception. Its exact sources, log and resulting artifacts
are retained; attempt02 corrects only the output-directory normalization.
There is no native-equivalence failure hidden by that checker repair.
Attempt03 additionally makes receipt filenames portable to an independent
temporary-directory replay; its mathematical traces agree with attempt02.
The initial manifest generator accidentally pinned its own redirected log
before that log was written. The old generator/manifest/log are retained
under `retained_freeze01`; the corrected generator excludes its active log.
This provenance-only defect changes no programme or mathematical receipt.

Remaining **unproved** obligations are full WF/source/final-computed-SimBit
order, software for all simulation/controller/reset/birth/packing branches,
own-programme simulation of this changed READ selector and immutable code,
authentic History origin and temporal loading, final hardwirer/layout,
all-raw whole-rule locality, complete period and any error map. The six
native fields include WF1/WF2, but this programme emits only the other four;
its native input records' WF bits are actual READ data, not future commands.
Full beta<=8192, original Gray faithfulness, general real1/higher recovery,
positive iid noise rate and a shorter U all remain **unproved**.
