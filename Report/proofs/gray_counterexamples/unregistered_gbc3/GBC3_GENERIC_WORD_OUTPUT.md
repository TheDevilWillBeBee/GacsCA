# GBC3: generic word output, complete encoder rejection and selected deadline

This is an explicitly changed isolated binary rule, with Q=8192,
U=128Q=1,048,576, lambda=24 and original integer error-class constant
c=104. It preserves the GBC2 stage endpoints, native equations and
computed-SimBit/wipe order. No active repository rule was modified.
The new generic output primitive is proved below. A complete listing is
emitted, but this encoder still exceeds Q and its universal semantic
equivalence is **unproved**. The separate-code diagnostic is measured
evidence only. There is no faithful-Gray, positive-noise or memory-loss
conclusion.

The source is [compact_completion_rule.py](compact_completion_rule.py).
GBC2 remains frozen; its rejection is the earlier control, not a source
to modify. GBC3 adds no state bits: Head553, mutable Work407, frame
K=3087 and doubled layout width6174 are unchanged. The immutable target
programme remains exactly Q binary bits. There is no issued own beta.

## 1. Total generic instruction and pending mode — proved

Mode6, formerly an error mode, is now WORDOUT. Mode7 and movement3 remain
errors. EXT sub2 with width marker31 fetches a further width5 and stride1
argument, giving `PUTWORD(n,wide)` of length17 bits. PUSH widths0..30
retain their prior11-bit encoding; PUSH21..30 are errors. The former
width31 encoding is intentionally changed. Fetch from any raw PC uses
the same zero-extended Q-bit code function; it need not lie on an
instruction boundary.

For an instruction with n in1..20, A is the data word, B is the first
target address and stride s is1 or5. For n=0, B is a generic descriptor:
low13 address bits, next5 length bits and two required-zero high bits;
A remains data. All other lengths, B outside its permitted range, last
target outside [0,Q), or nextPC outside [0,Q) yield the existing ERROR
packet and no write. Valid entry sets pending start, index=n-1,
kind=wide, B=A and ret=nextPC, then chooses movement toward start. It
does not change the other fields or write a bit on that entry update.

For every raw pending packet, the guard is exactly

```
kind in {0,1}, index < 20, start + index*(1+4*kind) < Q.
```

All words are the typed raw fields in META: start/index/ret13, B20,
kind2, and the other declared widths. For a failing guard, ERROR is
returned with no write. At a different current address, only movement
is changed toward start. At start, one write B&1 occurs, B is shifted
right one, and either the packet continues at ret (index0), or start
increases by s, index decreases by1 and movement becomes right. Even a
malformed pending packet has a defined output. Pending ret is a13-bit
raw value and hence within Q; the generic continuation still performs
its check.

Let entry succeed with data v and n bits. By induction on consumed bits
i, immediately before consumption i, B=v>>i and start=b+i*s; index is
n-1-i. The written bit is therefore `(v>>i)&1`. On a travel update these
quantities do not change. After n consumptions, B=v>>n and no other
packet data changed except the declared control fields. This proves
the word output for **every** Word20 value, not only the payloads tested
by the checker. The span guard is preserved because the last target is
constant. Entry never changes mutable Work or native-buffer NC.

With a coherent unique packet, stable controls, no external overwrites
or wipes, and pending clock updates permitted throughout, the number
of updates from instruction entry through its last write is

```
1 + max(1, |initialAddress-start|) + (n-1)*s <= 8287.
```

The first term is entry; at most max(1,distance) following updates reach
and consume the first target; each subsequent stride costs exactly s
updates. This is a universal primitive bound under these stated
execution premises, not a whole-period deadline or noise proof.

WORDOUT reads no History data. Its packet is the same selected incoming
five-copy packet as before: holder x, output slot S[q], incoming shift
h in{-1,0,1}, and raw input copy r have physical coordinate
`x+S[q]+h-S[r]`, within radius5. Its address uses the holder's computed
native Address and S[q], with native radius5. All unchanged data reads
remain within the declared radius8; specifically their History holder
coordinates are `x+S[q]+d-S[r]`, d in[-4,4]. No whole-rule evaluation
opcode, supplied callback, host CPU evaluation or stored dictionary is
introduced by this primitive.

[check_wordout_contract.py](check_wordout_contract.py) records64
encode/decode,4270 pending,2511 entry and1792 actual-holder cofactors in
[the primitive receipt](../../../../figs/gray_counterexamples/unregistered_gbc3/GBC3_wordout_contract_attempt01.json).
Those finite checks support the stated equations; the induction above
supplies the arbitrary-data quantifier. They do not certify the entire
compiler or an E0 copy invariant.

## 2. Physical compiler helpers — proved with their execution premises

The new `head_write` moves the current data A into B, computes the actual
target `HeadBase+5*offset+q` from the counted Work copy index q, restores
data A and issues PUTWORD(width,1). For q in0..4, positive width<=20,
and a window within Head553, every actual target is in the existing
frame and below Q. Section1 gives exactly those real output bits at
stride5. Mutable Work and physicalFn/NC are unchanged by this block.
The returned physical A is the original data; B is shifted by width.
This is an intentional scratch-register difference from GBC2. Subsequent
compiler branches reload their required operands; a universal proof of
that full composition is still open.

The generic `write_word` helper takes counted Work VALUE, ADDRESS and
LENGTH, requiring1<=LENGTH<=20 and a valid entire stride5 span. It packs
`(LENGTH<<13)|ADDRESS` into B, loads VALUE into A, issues PUTWORD(0,1),
then restores the old helper's relevant Work postconditions:

```
VALUE := oldVALUE >> oldLENGTH
ADDRESS := oldADDRESS + 5*oldLENGTH
LENGTH := 0
```

The descriptor uses at most18 bits and has the required zero padding.
These arithmetic operations do not wrap Word20 for the declared target
range. RETURN360 is not overwritten, and the helper returns through
that counted word. This proves this helper's data/Work contract whenever
the underlying real code locations and controls are valid. The rejected
Q listing cannot supply that code-validity premise. The diagnostic's
separate larger table supplies it explicitly instead.

## 3. Complete structural emission — proved count; equivalence unproved

[complete_branch_emitter.py](complete_branch_emitter.py) emits all stage,
incoming collision, raw mode, opcode, literal/error, pending IO/SPAN/
STREAM/WORDOUT, descriptor, final-source and wipe branches. In particular
it emits WORDOUT's raw guard/travel/consume branches and PUTWORD's
fixed/dynamic entry branches. The latter is not omitted when the physical
programme uses only the former.

The exact complete listing is **46,155 bits /3487 instructions**, with
**315 out-of-Q branch references**. The count and whole listing are in
[structural attempt01](../../../../figs/gray_counterexamples/unregistered_gbc3/GBC3_complete_structural_attempt01.json).
The separately counted shared-continuation encoder gives **42,394 bits
/3228 instructions**, with **316 out-of-Q references**, in
[tailmerge attempt01](../../../../figs/gray_counterexamples/unregistered_gbc3/GBC3_complete_tailmerge_attempt01.json).
Both are rejected by Q=8192. Wrapped low13-bit branch words are retained
only as rejected serialization evidence and are never run as valid beta.
These are exact failures of these specified encoders, not lower bounds
for all possible encodings or failures of Gray's sufficiently-large-Q
theorem. The constant display Q>=8192 alone does not provide our beta.

## 4. Separate finite-table diagnostic — measured only

[check_complete_listing_diagnostic.py](check_complete_listing_diagnostic.py)
uses the exact unwrapped listing in a separate immutable finite
instruction table, with a wider physical PC/ret and table-size
continuations. CODE still reads the stipulated Q-bit *target* beta.
Generic arithmetic, travel, actual17-lane input bank, five-copy input
votes and local output updates are retained. This is an explicitly
different diagnostic architecture; it is not F_beta's own programme.
Its lower input tape/controls are prepared and coherent, not an intact
hierarchy or a chronological noise history.

A conservative fixed table at2^16 bit-addresses, including valid1,
decoded tag5, argument24 and length6, costs2,359,296 bits, plus8192 target
beta bits. This counted diagnostic storage is not hidden behind a claim
that46,155 bits fits Q. Its mode/PC fields are wider than the declared
physical553-bit packet and its trace records those fields separately.

All14 stage cases,27 opcode-family cases,52 previous raw-branch cases
and22 new WORDOUT cases pass exact comparison of all3087 output bits.
The receipts retain each complete raw17-cell input, target-code hash,
desired output, actual output and complete trace digest. These are
115 selected successful checks, plus one redundant HLT check; they are
not universal complete-emitter equivalence.

## 5. Exact selected deadline — measured only

[the cutoff checker](check_complete_deadline_diagnostic.py) uses the same
prepared five simultaneous PUSH20 packets as frozen GBC2. GBC3 completes
in **94,394 updates**, with all raw outputs correct, versus GBC2's126,614.
The immutable target instruction/initial raw inputs are retained in
[the receipt](../../../../figs/gray_counterexamples/unregistered_gbc3/GBC3_complete_deadline_diagnostic_attempt01.json).

The declared late execution outputs are112Q+2 through120Q-1, giving
**65,534 usable updates**. At that exact cutoff, all3087 columns have
been written but8 raw bits disagree:355,356,365,366,375,376,380,381.
The decoded copied Head PCs are(42,42,42,31,31), while the target output
has(42,42,42,42,42). Info and every other decoded field agree. Thus this
selected diagnostic misses that stipulated8Q computation window. It
does not disprove U=128Q by itself, a period for an issued own beta, bit
memory or Gray's theorem. An earlier birth would change the rule and
require fresh native quiet/reset/gather/source/bank/runtime proofs.

## 6. Remaining obligations and scope

| Step | Status |
|---|---|
| Total declared WORDOUT/PUTWORD equations and typed raw semantics | proved |
| Primitive arbitrary-data correctness, locality and conditional runtime | proved |
| Counted helper output/Work contracts under coherent execution | proved |
| Exact two complete encoder sizes/out-of-Q references | proved |
| Selected full-raw diagnostic outputs and selected missed deadline | measured only |
| Universal complete-emitter equality and usable whole-pass deadline | unproved |
| Issued own beta<=Q, hardwirer, whole physical period or intact recursive initialization | unproved |
| E0, general original-real1/higher recovery, positive iid rate or memory failure | unproved |
| Refinement of literal/corrected Gray and Gács | unproved |
| Any shorter U | unproved |

Material departures remain explicit: h1 Flag2 correction, radius8 and
17 gathered lanes, this binary moving-head ISA/state/layout and service
Address convention, immutable Q-bit code, concrete collector/courier
controls, final-source implementation and new WORDOUT instruction. Q/U
and error-class constants remain the requested baseline. This checkpoint
contains no physical error locations and no admissible Gray noise
counterexample. The next size bottleneck is duplicated field-access and
control code; the generic output primitive improves travel/runtime but
does not establish code fit.
