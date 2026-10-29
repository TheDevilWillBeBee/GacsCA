# GAW0: complete wider word-rule attempt, and its specified storage failure

**Status: total changed local rule and complete own-programme emission; exact
emission-specific storage obstruction; larger-ROM prepared executions measured.
No faithful Gray rule, universal own-programme identity, full-period theorem,
positive iid rate, or Gray/Gács counterexample is claimed.** The accepted GE2
report/checkpoint and GE3/GE4/GI0 sources are unchanged.

This is an explicit response to [GI0's eleven-lane blindness obstruction](../unregistered_gi0/GI0_TOTAL_SOURCE_INTERFACE.md). It
keeps `Q=8192`, `U=128Q=1048576`, and the original error-class parameters
`lambda=24`, `c=104`. It defines an autonomous finite rule, including every
interpreter, service, tape, mailbox, courier, output, and native field on every
legal raw state. It then emits the complete transition as an actual programme
of that interpreter. The stipulated baseline programme does **not** fit Q.
The separately declared GAW0D instance permits a larger immutable code table
so that the emitted programme's physical execution can be examined.

## 1. Changes and state alphabet

The kernel is [gray_wider_word_gaw0.py](gray_wider_word_gaw0.py), and its full
emitter is [build_gray_wider_word_gaw0.py](build_gray_wider_word_gaw0.py).
Both are isolated: neither active G17 nor the accepted GMW7/GE/GT0 modules
were edited.

The changes from the printed Gray protocol are material:

* The previously explicit h1 Flag2 erasure correction is retained.
* Radius is eight, with seventeen mutable input lanes `-8..8`.
* Info, Out, Scratch, Programme, and two couriers contain 100-bit words.
* A single snapshot at `32Q` replaces three gathers and temporal majority;
  these lanes do not implement Gray's Mailbox erasure on Flag1.
* A holder uses `(new native GF + copy offset) mod Q` for physical service.
* One full early pass is reset at `42Q`, born at `42Q+1`, and runs through
  `75Q-1`; the late pass keeps the `112Q..120Q` window. This early schedule
  is a change even though Q, U and late-window endpoints are unchanged.
* A fixed token/dictionary lookup implements CODE; it is immutable code,
  not Gray's mutable ProgrammeBits/hardwirer protocol. Mutable Programme
  words remain real state and are read by the physical IO instruction.
* READ5 gains an immediate centre lane; FULLCOL is opcode 14. Opcode 15
  deterministically fails. The descriptor lane expands from four to five
  bits; source/destination/side fields move accordingly.

The raw alphabet has 22,537 bits: native fields have widths 13,20,1,1,1,1;
there are five copies of a 22-word head, seventeen-word Mem, and six ordinary
word fields (`Out,Info,Scratch,Programme,CourierL,CourierR`). Each word is
100 bits. The encoding uses six native rows followed by five rows per SF
word, hence **231 word primaries `[3981,4212)`**. This uses word-valued Info
and cannot be called a 231-bit Gray encoding of the raw alphabet. The
100-bit-word encoding and the counted immutable dictionary are explicit
additional resources. There is no hidden layout port or host rule evaluator.

## 2. Total local transition and ordering

All old native inputs are width-normalized. The h1 native operator reads
old GF/Age/Flag1/Flag2/Workspace in radius five. Its new GF/Age/Flag1/Flag2
are determined before any new Workspace field. Thus new native fields do
not recursively depend on new Workspace.

Let `V_f(y)` be bitwise three-of-five voting of field f at its actual five
old holders `y-s`, with copy offsets `s=(0,-2,-1,1,2)` and the matching copy
index. The new primary Info at source y is computed with that **source's**
new native GF/Age/Flag1:

1. A source wipe (`new F1 && new GF != raw self GF`) makes it zero.
2. Source new Age zero commits `V_Out(y)`.
3. Source new Age `80Q-1` and GF 3 or Q-3 selects the corresponding **old**
   voted CourierL or CourierR.
4. Otherwise it is `V_Info(y)`.

Reader wipe has priority. With reader new Age in `[96Q,98Q)`, new WF1 reads
the low bit of that final primary at `Q-3-newGF` when `Q-5<=newGF<Q`;
new WF2 reads at `3-newGF` when `newGF<=4 && newF1=0`. Otherwise each is zero.
This is the literal final-primary interpretation of the stipulated source
interface, with no pre-wipe substitution. The omitted Gray mechanisms listed
above prevent attributing this completion to his entire construction.

For each of the five output SF copies, the new native phase controls:

* At `32Q`, all seventeen Mem lanes load the old voted Info word.
* During the next `8Q` ticks, lane d shifts one physical site in the
  sign(d) direction while elapsed gather age is at most `abs(d)Q`; otherwise
  it votes and holds. Each actual lane exists in the state alphabet.
* Info commits the old voted Out at Age zero and receives the old voted
  courier at the two special addresses at `80Q-1`.
* Couriers clear at zero and `32Q`; at `75Q` they seed from the low bit of
  old Out at the represented native F2/F1 primary, respectively. During
  `(75Q,80Q)` they shift one site left/right with five-holder votes. These
  equations are total even if the early programme did not finish.
* Heads/Out/Scratch reset at zero, `42Q`, `112Q`; a head is born only at the
  logical entry address on the next row. The two active windows are exactly
  `(42Q+1,75Q)` and `(112Q+1,120Q]`.
* Incoming head candidates are stationary self, old left moving right,
  old right moving left, in that priority. Multiple candidates cause ERROR.
  Malformed move/mode/opcode/PC/IO arguments deterministically cause ERROR;
  missing heads stay absent. HALT/ERROR are stationary. All other times
  vote and hold the packet.
* Programme receives the immutable beta bit at the service address. A
  wipe zeros every SF output copy. No fifth-output or nonnative completion
  port remains in this kernel.

Every formula is finite on bounded inputs. The Python calls to the native
scalar and arithmetic helpers name finite local functions, not a syscall
that evaluates the whole rule. The CODE primitive returns one decoded
immutable instruction word in one head update. Its implementation never
calls `local_transition`.

## 3. Radius and layout

**Proved from the displayed total equations.** Native update has radius
five; SF copy voting at y in `[-2,2]`, with at most one neighbour for head,
mail or courier motion, has radius at most five. The final Workspace source
is at most three sites from the reader and its native update uses radius
five. Its Info/Out/courier vote uses radius two. Thus the complete local
transition has radius at most eight. All source offsets exist in the
seventeen-record input bank, including every raw source-native input.

The descriptor has disjoint fields: kind bits0..1, destination register
bits2..5, lane bits6..10, source bits11..12, destination-track bit13, side
bit14. READ5 admits only centres5..11, making all five selected operands
valid lanes0..16. READMASK returns the inner eleven low bits, while FULLCOL
returns all seventeen. No lane16 truncation occurs.

Conditionally on canonical GF, common clock, no wipe and coherent stable
Info throughout the gather, the single snapshot has farthest travel `8Q`; all lanes are
frozen by `40Q`, before the `42Q` reset/birth. This is a conditional routing
identity, not a noisy preparation theorem or a full-period composition.
The late head has exactly `8Q-1=65535` execution updates. The early head has
`33Q-2=270334` updates before the `75Q` courier seed. Courier source primaries
3984/3983 have distances3981/4206 to 3/Q-3, both less than5Q. These arithmetic
margins do not prove that code finishes, that its simulated flags are correct,
or that arbitrary clock-damaged mail supplies an intact upper input.

## 4. Complete own emission: exact architecture-specific obstruction

The emitter handles the native operator, **each final-source native operator**,
SF voting, actual gathers/couriers, both resets/births, all head candidate
selection, every virtual opcode/operand/IO branch, special Info writes,
commit, and wipe. Source-native branches are expanded for the six possible
source centres; these expansions are part of this specified emitter, not a
lower bound on all possible programmes.

The nine-bit-token attempt emits **1,979 instruction/data tokens**, requiring
**17,811 beta bits**. It contains **605 distinct 100-bit words**, exceeding the
specified 512-word dictionary. The complete emitted listing and immutable
ROM are retained in `GAW0_emission_01_*` receipts, with exact source snapshots.
Those errors occur before a Q-sized own evaluator can be instantiated.

**Proved for this exact emission:** 1,979 nine-bit token slots exceed Q;
605 distinct values cannot be named by a nine-bit dictionary index. Merely
raising dictionary capacity to605 still needs at least ten token bits, so
this same uncompressed token sequence requires **19,790 beta bits**. Raising
only U cannot remove this storage obstruction. No assertion about optimal
compression, alternative loops/native-source factorization, or all Gray
completions follows.

GAW0D explicitly changes fixed storage to **32,768 beta bits plus 1,024 x100
=102,400 dictionary bits, total135,168 bits**. It keeps Q/U and PC13. There
are no out-of-range branch/operand references in this emission. The decoder
replays every emitted instruction exactly under its ten-bit-token table.
CODE on raw PC addresses0..8191 reads the corresponding fixed token; missing
bits yield zero token, whose dictionary entry is HLT. Out-of-range PC reads
return zero; invalid running PC causes ERROR. BITCODE returns the fixed bit
or zero. The physical Programme tape stores only those bits addressed within
Q; it is not how GAW0D accesses the larger immutable table.

## 5. Physical execution evidence and limits

[check_gray_wider_word_gaw0.py](check_gray_wider_word_gaw0.py) retains exact
seventeen input raw words per output primary, complete output words, actual
head travel extrema, execution counts and source/listing/table hashes. It
prepares coherent lower copies and the actual input tape from the supplied
upper records, resets the lower head/work, then executes the emitted code
with the physical finite head/IO equations. This is not an intact hierarchy
or a real noise history.

The final retained finite campaign compares **124 entire output cells**:
24 arbitrary legal native/head/tape neighbourhoods, all listed gather,
reset, birth, execution, source/commit/special-write boundaries, every virtual
opcode including FULLCOL, and malformed/valid descriptor lanes. All match
the separately specified local transition and halt. The maximum retained
execution is **53,747 updates**, below65,535; the minimum and each input are
in the receipt. This establishes those measurements, not all-raw equivalence
or a universal deadline. A universal copy-cost overapproximation was separately attempted. Its first
range-analysis failure and the later explicitly interrupted run are retained
in `GAW0_bound_01.log` and `GAW0_bound_02.log`. The latter was stopped with
SIGINT/exit130 after several minutes (observed at4min36s,938224KiB RSS),
without a certified cost result. This is an analysis-resource limitation,
not a measured deadline failure. The universal fifth/early deadline remains
unproved, and the standalone validator does not replay that interrupted
analysis as though it were a certificate.

Two reconstruction failures are retained: initial import omitted the repo
root, and an accidental scalar source window extended native radius five
to eight before it was passed to the radius-five scalar. They occurred
before or during checking; both are corrected. Neither is Gray's defect.
The first abstract travel audit lost a checked centre-lane range because a
scratch copy was saved before the guard. Its failure is retained; moving
that save after the guard preserves final outputs and allows a fresh audit.
The earlier successful100-case emission/table/replay are retained separately
before this change. Accepted prior components were never altered.

## 6. What remains open

| Step | Status |
|---|---|
| Total bounded raw transition with no ports | Proved by the emitted finite equations |
| Radius8, expanded descriptor and231-word layout | Proved |
| Exact complete1979-token/605-word fit failure | Proved for this emitter |
| GAW0D every instruction decodes as emitted | Proved by exhaustive listing replay |
|124 complete prepared output comparisons | Measured only |
| Universal all-raw own-programme equivalence | Unproved; the GMW6 contracts suggest a proof route but do not apply verbatim after these changes |
| Universal fifth/early execution deadline | Unproved; exact cost attempt interrupted, no bound promoted |
| Actual prepared gather/early flags/commit and full clean period | Unproved |
| Gray's mutable programme, three-gather erasure/majority, final layout | Unproved, with explicit changed interfaces |
| Radius8 reuse of lambda24/c104 deterministic/noisy lemmas | Unproved; error-class geometry itself is unchanged, propagation estimates must be checked anew |
| Intact shared-history finite counterexample to this full instance | Unproved |
| Gray/Gács reliability flaw, iid unreliability, positive iid noise rate | Unproved |
| Smaller U | Not established; all emitted periods remain128Q |

The immediate fit bottleneck is this whole-emission representation, not
missing future ports. A later compact source-native subroutine or different
physical evaluator may reduce it, but would need a new total transition,
self-code, storage accounting and deadline proof. The GAW0D diagnostic is
not the requested Q-bit faithful completion and supplies no Gray theorem
refutation.
