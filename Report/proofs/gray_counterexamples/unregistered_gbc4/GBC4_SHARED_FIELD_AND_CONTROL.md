# GBC4: counted generic calls and shared field/control blocks

GBC4 is an isolated changed binary radius8 rule with Q=8192,
U=128Q=1,048,576, lambda24 and original integer c104. It retains GBC3's
stage endpoints, computed-SimBit/wipe order, native fields and state
layout. It adds generic CALL/RETURN using two existing mutable Work
words and shares actual field-access/output code. There is **no issued
complete own beta**: the complete encoders below reject Q. No shorter U,
faithful Gray implementation, noise theorem or Gray counterexample is
claimed. Active G17 and every earlier frozen asset remain unchanged.

## 1. Total generic control equations — proved

The rule source is [compact_completion_rule.py](compact_completion_rule.py).
Head553, Work407, K3087 and doubled layout6174 are unchanged. There is
no added stack or interpreter register. The return words are precisely
Work[360:380] and Work[380:400], both within the existing407 bits.

EXT sub2 with former-error PUSH marker30 now decodes CALL(target13,
bank1), length25. Former SELF selector15, which returned zero, now
decodes RETURN(bank1), length11. PUSH0..29 retains its previous encoding
(PUSH21..29 remains an error); SELF0..14 retains its prior semantics.
PUTWORD's marker31 is unchanged. These are explicit ISA/rule changes.
Fetch is still total zero-extended Q-bit immutable code at any raw PC,
including a PC that is not an instruction start.

For an actual decoded CALL, let r=pc+25 and o=360+20*bank. If r>=Q,
CALL returns the existing ERROR packet with all data, including Work,
unchanged. Otherwise it replaces exactly Work[o:o+20] with r and
continues at its target. Target13 is always in [0,Q). A, B, Fn, NC and
every other data field are preserved; continuation sets modeRUN and
move0. For an actual decoded RETURN, the target is the unmasked
Word20 at Work[o:o+20]. Existing continuation accepts it if target<Q,
and otherwise returns ERROR. No native-width projection or masked
decoder is used. CALL and RETURN require one CPU update each, when the
packet is in RUN and its controls permit that update.

These equations quantify every typed raw packet. The two storage masks
are disjoint, and both fit Work407. Hence nested calls using distinct
banks preserve both returns. Reusing one bank overwrites its previous
return; this ISA intentionally supplies no automatic unbounded stack.
Arbitrary programmes can loop. This primitive statement is neither
termination of every beta nor a whole evaluator deadline.

The existing incoming five-copy packet vote is unchanged. A raw Head
bit at output holder x/slot S[q], incoming displacement h in{-1,0,1}
and copy r is read at x+S[q]+h-S[r], within radius5. The new instructions
make no History/data input read. Every unchanged generic data read and
final computed-primary source remains within declared radius8.

[check_control_access_contract.py](check_control_access_contract.py)
records36 CALL-fetch and40 RETURN-fetch cofactors, including truncated
tags. When only the low opcode bit survives at pc=Q-1, the intended
instruction tag does not survive: actual decode is None and total CPU
ERROR is correct. The initial checker wrongly assumed CALL/RETURN
survived that truncation. Its exact source is retained as
[the failed checker](check_control_access_contract_truncated_fetch_failure.py),
with [the explicitly retrospective failure record](../../../../figs/gray_counterexamples/unregistered_gbc4/GBC4_truncated_fetch_checker_failure_record.json).
This was a checker defect, not a CA defect. The corrected
[attempt02 receipt](../../../../figs/gray_counterexamples/unregistered_gbc4/GBC4_control_access_contract_attempt02.json)
uses the actual decoded tag and preserves all raw inputs.

## 2. Generic shared Head-window reader — proved conditional contract

The counted caller sets physicalFn to source centre c, puts the
descriptor `offset+(width<<10)` in B, and CALLs bank1. Preconditions:
q in0..4, c in[-4,4], 1<=width<=20, offset+width<=553; the encoded
input bank is stable and exact, lower execution is coherent, and no
external overwrite/wipe interrupts the execution. Work80 (RAW) and
Work380 are declared scratch/return storage. Other Work words,
including live TEMP40/LENGTH340/ADDRESS320, must be preserved. The
full compiler's satisfaction of the RAW-dead premise at every call
site remains a separate composition obligation.

`shared_head_read_helper` stores the descriptor in RAW80, computes
`HeadBase+5*offset+q`, loads width, and invokes the actual aligned
READ-SPAN. It stores the result in RAW80 and RETURNs bank1. CALL
preserves descriptor B and Fn; the reader changes no other Work word,
Fn or NC. The result is also in physical A after RETURN. The caller's
explicit WGET(RAW) therefore returns the result independent of any
previous A. No old Head field is read through a host callback.

At consume column HeadBase+5*(offset+i)+q, aligned READ-SPAN's five
input bits have upper raw coordinates

```
c + S[q] - S[r],  r=0..4.
```

HeadBase is a multiple of5, so the actual column residue is q. The
physical local History columns are r-q in[-4,4], and their lane indices
are `8+c+S[q]-S[r]` in0..16. The majority is precisely bit offset+i
of the voted upper Head at logical c+S[q]. READ-SPAN accumulates these
bits in increasing bit order; no incoming Head-centre substitution is
made. The previous generic SPAN contract gives this result for every
raw Head-bit assignment under the exact bank premise. The largest
source coordinate magnitude is8, consistent with the17-lane bank.

The standalone checker actually issues small Q-bit component
programmes through the unmodified GBC4 CPU; it does not use the large
diagnostic table for these runs. All75 selected centre/copy/window
checks agree, with all other Work outside RAW80/QCOL100/return380 and
NC preserved. The largest selected component is287 bits and the
largest observed runtime is3109 updates. These measured counts are
component facts, not a complete own-beta or period theorem.

## 3. Complete encoder and exact tail sharing

[complete_branch_emitter.py](complete_branch_emitter.py) emits every
stage, incoming collision, raw mode0..7, opcode/extension, literal
error, pending IO/SPAN/STREAM/WORDOUT, raw CALL/RETURN, final-source
and wipe branch. It emits simulated CALL's conditional Work write and
simulated RETURN's full20-bit target check. The implementation never
substitutes a whole-R/CPU oracle for these branches.

The full initial listing has **46,407 bits /3447 instructions** and
**365 out-of-Q references**, in
[structural attempt01](../../../../figs/gray_counterexamples/unregistered_gbc4/GBC4_complete_structural_attempt01.json).
The complete shared-control listing has **41,047 bits /3071
instructions**, also **365 out-of-Q references**, in
[shared attempt01](../../../../figs/gray_counterexamples/unregistered_gbc4/GBC4_complete_shared_control_attempt01.json).
Both are exact failures of these encoders at Q. Wrapped low13-bit
references are rejected serialization evidence, not an executable
own beta. This does not establish a lower bound for all encodings or
contradict Gray's sufficiently-large-Q theorem.

[shared_control_emitter.py](shared_control_emitter.py) shares the
continue_pc tail and merges19 exactly matching terminating header
sequences. It removes no interior label. Each replaced sequence was
SWAP/WGET(q)/add(HeadBase)/SWAP/PUTWORD(6,1)/BR(cpu_next); its replacement
enters one copy of that same output sequence. Entry A is the same
header, all Work inputs are the same, and all actual output columns
are the same. Internal physical code/ret addresses differ, but this
tail never reads them as data before cpu_next. Generic CALL relocations
are computed from the final listing. This proves this specific tail
rewrite's output contract under valid-code/coherent execution; it does
not prove the entire emitter equivalent on every upper input.

## 4. Selected complete diagnostics — measured only

The initial full listing passes29 opcode-family,52 old raw-branch and
22 WORDOUT cases, each comparing all3087 output bits to the total host
rule. The shared listing passes104 selected cases:14 stage,52 old
raw-branch,22 WORDOUT and16 CALL/RETURN cases. Full raw inputs, target
code hashes, desired/actual outputs and trace digests are retained.
These are207 selected successful diagnostic comparisons, not a
universal proof of the complete compiler.

These rejected full listings run only in the explicit separate
instruction-table diagnostic, with wider physical PC/ret and actual
unwrapped targets. CODE still reads the stipulated Q-bit target beta.
The conservative finite table costs2^16*(valid1+tag5+args24+length6)
=2,359,296 bits, plus8192 target-code bits. This counted larger table
is not hidden behind a Q-fit claim. The input bank and lower controls
are prepared and stable; no chronological noise or intact recursive
initialization is asserted for these diagnostics.

## 5. Proof status and next bottleneck

| Obligation | Status |
|---|---|
| Typed total CALL/RETURN semantics, counted storage and locality | proved |
| Shared Head-reader contract with exact bank and declared scratch premises | proved |
| Exact continuation/header rewrite contract with valid-code premises | proved |
| Complete two listing counts and Q rejection | proved |
| Selected issued component and complete diagnostic replays | measured only |
| Global RAW/return liveness and universal complete-emitter equality | unproved |
| Universal full runtime, deadline and whole physical period | unproved |
| Own beta<=Q, hardwirer and intact recursive realization | unproved |
| Original E0/real1/higher recovery or positive iid rate | unproved |
| Faithful corrected/literal Gray or Gács implementation/refutation | unproved |
| Shorter U | unproved |

The explicit rule departures remain h1, radius8/17 lanes, immutable
binary code, moving-head state/ISA/layout, service Address controls,
collector/courier implementation and computed-source realization;
CALL/RETURN adds a further generic control convention. Matching Q/U/
c104 does not remove these obligations. The useful result is a counted,
issued reusable component plus a complete encoder rejection. Further
size reduction needs fewer duplicated semantic/control blocks, not an
uncounted stack, dictionary or whole-rule opcode.
