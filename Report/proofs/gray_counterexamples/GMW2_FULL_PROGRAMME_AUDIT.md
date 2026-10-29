# GMW1/GMW2: full emission, explicit ROM departure and a fifth-stage failure

This checkpoint retains **Q=8192, U=128Q=1048576, lambda=24 and c=104**.
It defines a complete finite local component rule and emits a proposed
programme for all of its fields. It does **not** complete Gray's physical
simulation protocol or prove that the emitted programme computes every raw
input correctly. The actual fifth-stage schedule fails on a specified,
preloaded, noiseless input. No faster U is used. All files are isolated;
the active G17 rule is unchanged.

Sources and retained evidence:

- [GMW1 kernel](gray_moving_word_v1.py),
  [GMW1 builder](build_gray_moving_word_v1.py),
  [Q-code overflow receipt](../../../figs/gray_counterexamples/GMW1_full_own_overflow.json),
  [failed listing](../../../figs/gray_counterexamples/GMW1_full_own_attempt_listing.json)
  and [invalid masked bits](../../../figs/gray_counterexamples/GMW1_full_own_invalid_masked_beta.bin).
- [GMW2 kernel](gray_moving_word_v2.py),
  [full-field builder](build_gray_moving_word_v2.py),
  [execution checker](check_gray_moving_word_v2.py),
  [execution receipt](../../../figs/gray_counterexamples/GMW2_full_own_certificate.json),
  [beta](../../../figs/gray_counterexamples/GMW2_full_own_beta.bin),
  [listing](../../../figs/gray_counterexamples/GMW2_full_own_listing.json)
  and [inputs/outputs/65535-update prefix](../../../figs/gray_counterexamples/GMW2_full_own_replays.npz).
- [Audit checker](check_gray_moving_word_v2_audit.py) and
  [audit receipt](../../../figs/gray_counterexamples/GMW2_full_programme_audit_certificate.json)
  pin the proof, emitted identities, prefix recurrence and scope.

## Changes and exact status

Gray p31 describes beta as a bit programme of length at most Q. His p34
schedule gives the fifth stage eight active Q ticks and eight rest Q ticks.
Neither an unknown asymptotic evaluator constant nor an instruction count
proves that a particular evaluator fits these bounds. See the retained
[source/encoding audit](GPN0_PROGRAMME_OBSTRUCTION.md) for the programme-source
version issue; the following is a concrete different representation.

GMW1's first full-field emission has42850 bits,1829 instructions and268
out-of-range references for its Q-sized code/13-bit PC. The masked failed
bitstream is retained as **invalid**, not called a self-programme. This is
a proved size/reference obstruction for that specified emission, not a
lower bound on all word/loop implementations. Its semantic correctness
was not established.

GMW2 explicitly changes code capacity to65536 bits and PC/branch targets
to16 bits. Instruction fetch is an **instantaneous immutable ROM lookup**;
the logical mutable ProgramBit fields are not used to fetch instructions.
Native Flag2 uses the h1 erasure correction. Workspace.Flag1/2 outputs are
fixed0. Simulation service Address for holder x and copy offset s is
`(computed native GF(x)+s) mod Q`, rather than raw GF(x+s) as in GMW0.
These are rule changes, not a faithful instantiation of Gray's programme,
hardwirer, pulse or last-stage evaluator. The printed-clause counterexample
and previous GT0/GV0/radius results retain their original, separate scopes.

GMW2's proposed beta has44730 bits and1863 instructions, with no out-of-range
references. It fits this separate64K ROM; it exceeds Gray's Q programme
capacity by36538 bits. Every service/interpreter field has a total local
equation. Every instruction is a generic finite word/bit/IO operation,
not an intrinsic native/head/whole-rule transition. Seventy finite full-field
comparisons match the independently defined local kernel; that is
**measured evidence**, not universal programme equivalence. Universal
equivalence, a faithful physical gather, and an encoded whole-period map
remain **unproved**. The schedule failure below does not depend on
universal programme equivalence: its expected ProgramBit is a direct
immutable-bit equation of the actual local rule.

## Finite alphabet and physical layout

Native fields have13 Address bits,20 Age bits and four one-bit flags.
All stored raw Ages0..2^20-1 are legal; U=2^20. The logical head has:

    p1, move2, mode3, pc16, start13, width5, index5,
    kind3, dst4, lane4, source2, dest1, r0..r15 each20 bits.

Its59 metadata bits plus320 register bits total379. Each physical cell
has five head words, five11-bit memory-column words, and five one-bit
copies of each of Out, Info, Scratch and ProgramBit. Consequently

    K=37+5*379+5*11+4*5=2007; 2K=4014<=8192.

The represented strip is3093..5099 inclusive. Native bit coordinates are
Address3093..3105, Age3106..3125, Flag1/2 at3126/3127, and Workspace.Flag1/2
at3128/3129. The head fields and registers use **interleaved per-field
five-copy banks**: for field f of width w and first coordinate b, copy q
is at b+qw..b+(q+1)w-1. There are28 head fields and33 total SF fields.
Mem, Out, Info, Scratch and ProgramBit follow them. The ProgramBit bank
begins5095; copy q=4 is primary5099, frame bit2006. This is a final layout
for the defined GMW2 component alphabet, not a completed Gray layout.

Copies use S=(0,-2,-1,1,2). Physical holder x's slot s represents logical
site y=x+s. A coherent SF word V(y) therefore has identical slot-s values
at its five holders y-s. Bitwise voting is OR over the ten triple-ANDs;
it returns V(y) when at least three holder words equal V(y).

## Total local transition and update order

Let B be a fixed65536-bit ROM. The kernel defines F_B on **every** raw
configuration of the finite alphabet. It first calculates the h1 native
fields at x using the existing literal scalar calculation plus the
explicitly corrected erasure predicate. Its Workspace outputs are0.
The copy controls use those native outputs; they never read a source's
computed fields. Let a be computed Age at x and g computed GF at x.

For each s in S, calculate old voted Mem, Out, Scratch and Info at y=x+s.
At a=0, new Info uses **old voted Out**; otherwise it uses old voted Info.
New ProgramBit is B[(g+s) mod Q]. Then:

1. At a in {0,112Q}, reset head, Out and Scratch to0.
2. At a=112Q+1, initialize a p=1 zero-register RUN/PC0 head iff
   `(g+s) mod Q=3093`; elsewhere the head is0.
3. At112Q+1<a<=120Q, bit-vote incoming heads at y-1,y,y+1,
   select candidates and perform one head step at service Address
   `(g+s) mod Q`. Write optional Out/Scratch bits after their old votes.
4. Otherwise hold the old voted head, Out and Scratch.
5. Finally, if computed Flag1=1 and computed GF differs from holder x's
   **old raw** GF, wipe every SF output, including the new ProgramBit.

Candidate precedence is stationary self, left-moving-right, then
right-moving-left. Missing heads give zero. Two or three candidates give
the selected packet with p=1, movement0, modeERROR. Movement3 and modes6/7
also produce ERROR. HALT/ERROR packets are stationary. These definitions
apply even to raw data with many heads or inconsistent copies; they do
not assert that such data become a valid computation.

Instruction opcode is five bits. Opcode31 has an extra discriminator:
CODE is14 bits, ALU is26 bits. The other instruction lengths are listed
in `ARGS`; at most29 fetched bits are needed. PC overflow beyond65536,
invalid IO width/start/lane/kind/index and invalid legacy window/count
arguments have defined ERROR behavior. PC is retained when an IO
instruction fails validation; HALT retains its old PC. Valid PC65536
advances modulo65536. There is no unspecified invalid-state fallback.

RUN decodes B[pc..pc+28] in the same local update. CODE is the exact
finite primitive

    ROM20_B(i)=sum_{0<=i+k<65536, 0<=k<20} B[i+k]*2^k.

Its input i is a20-bit register; out-of-range bits are0. ALU has explicit
finite20-bit arithmetic, comparisons, bit selection, signed shifts and
window counting. It has no access to a physical cell, F_B, or a native
transition. Thus ROM20_B may be compiled as a finite constant Boolean
lookup; the mathematical rule does not delegate to an external evaluator.

The head physically travels between mutable input, Out and Scratch
addresses. SEEK/LOAD/WRITE read or write one addressed column/update.
LOADR can select voted old Mem, Out, Scratch or ProgramBit; WRITER selects
Out or Scratch. The mutable ProgramBit bank **is** part of the noisy
alphabet and participates in simulated data loads, but it does not
control instruction fetch. Immutable code is consequently a substantial
change from Gray's stored programme protocol, not a reliability shortcut
that has already been justified for his proof.

**Radius theorem (proved, all raw states).** Each SF output at holder x
uses logical y=x+s. Each incoming head vote is at y+j, |j|<=1, with
holders y+j-t, |t|<=2. Hence its offsets s+j-t are in[-5,5]. All other
SF votes use offsets s-t in[-4,4]. Native fields/wipe use[-5,5]. Service
Address reuses g at x; immutable code lookup introduces no spatial read.
Therefore F_B has radius at most5 for every raw input. This proof does
not reinterpret Gray's final computed-SimBit source equation: the
Workspace outputs are the stated0 interface.

## Proposed own programme and the ROM self-reference

The emitted beta first runs the native word recipe with relocated input
columns and the explicit h1 alteration. It stores native outputs in Out.
The main routine implements wipe/reset/birth/active/rest and loops over
five copies. Software `vote`, `getfield`, `putfield` and virtual-head
handlers are emitted ordinary instructions. The field, length, scalar-ALU
and opcode-dispatch tables are part of the44730 emitted bits; zero padding
extends the same B to65536 bits. They are accessed through ROM20_B.

The rule family F_B is defined before selecting B. The assembler chooses
a specific finite B and uses **that same B** for physical instruction
decoding, CODE, output ProgramBits and the proposed evaluator's virtual
instruction fetch. The assembler resolves addresses of labels/tables;
it does not call F_B while forming the code. There is no circular
whole-transition syscall or external host oracle. An interpreter reading
its own fixed syntax through a generic ROM primitive is a defined finite
component. Nevertheless, the identity

    Eval_B(all eleven raw GMW2 input words)=F_B(their central word)

for all inputs is **unproved**. Exact agreement of immutable ROM identity
and finite syntax is a necessary condition, not a proof of this identity.
The proposed evaluation also needs mutable preloaded scratch/input tape
and physical execution time; their actual boundary production is open.

Three unsuccessful emitted implementations are retained, with exact
input/output bits, beta and source snapshots:

- [Failure01](../../../figs/gray_counterexamples/GMW2_semantic_failure_01.json):
  a virtual WINCNT incorrectly truncated an arbitrary20-bit register
  Address to13 bits. The generic WINDOW now keeps the full address and
  uses a separate existence bit.
- [Failure02](../../../figs/gray_counterexamples/GMW2_semantic_failure_02.json):
  extracting a cross-word instruction argument into R6 also overwrote
  its crossing temporary. A separate temporary now handles this case.
- [Failure03](../../../figs/gray_counterexamples/GMW2_semantic_failure_03.json):
  invalid virtual LOADR kept an advanced PC instead of its old PC.
  The old PC is saved and restored on IO-validation failure; HALT's
  old-PC behavior is also explicit.

These are **our implementation bugs**, not failures of Gray. A further
MI5 argument-cache fix was made before the final comparisons; the
strict-MI5 fixture distinguishes it. The original56-comparison receipt,
beta/listing/input copies and checker snapshot are also retained.
The first56 receipt's `physical_preloaded_evaluator_replays` label is
superseded: those runs continue after the physical gate closes and are
uninterrupted head-machine comparisons, not successful physical executions.
The final receipt separates those runs from actual65535 active updates.
The final70 comparisons include every emitted opcode, all memory modes
and kinds, invalid movement/modes, wrap/reset/birth, strict MI5, dense
stationary heads and eight arbitrary misaligned PCs. They do not cover
every raw native flag/data/packet combination and do not prove an
all-input running-time bound.

## Quiet physical coupling and a defined E0 repair component

Consider any logical SF configuration, canonically encoded in its five
holder slots, with physical GF=x mod Q, a common legal Age and all four
physical native flags0. No head uniqueness or logical-data assumption is
needed for the following closure. Native majority votes give canonical
GF and incremented common Age, all flag sources are0, and no SF wipe
fires. For each logical output y, its five holders have the same service
GF=y mod Q and computed Age. They vote the same old words, select the
same incoming packets and apply the same head equation. The outputs are
therefore coherent. This proves one-step quiet-copy closure, and its
iteration, directly from F_B's equations.

In the prepared one-head case, every valid IO target is in[0,Q), movement
is toward that target, and each instruction is decoded at the head's
current site. Thus an isolated head stays in its colony and cannot create
a second head. Reset/birth creates exactly one head per canonical colony.
The colony's logical tape and Out/Scratch evolve exactly by `step_packet`.
Rest stutters even a pending moving head; it does **not** execute the
uninterrupted host runner. Info commits old Out before reset at Age0.

There is a separate component E0 transparency theorem for this changed
interface. Let the entire error history consist solely of original Gray
E0 groups: one site or an adjacent spatial pair at one tick, distinct
groups (24,24)-separated. Errors overwrite arbitrary complete cells after
the update. A spatial interval of diameter10 in one row meets at most
one group and at most two overwritten sites. Suppose a reference row
has canonical GF, a common legal Age, native flags0 and coherent SF words.
Its perturbed row differs only on that row's E0 sites. Then

    F_B(perturbed row)=F_B(reference row).

**Proof.** Three of every directional five-word GF/Age vote remain
correct, so both directional votes and their existence bits are correct.
There are at most two left discrepancies. Workspace1 forcing and the
right Flag1 threshold3 need three distinct fault sites. The self-Flag1
threshold needs a faulty center and two faulty right sites, again three.
Computed Flag1 is therefore0. Flag2 off-to-on needs four faulty left
sites or three Workspace2 sources; source3 is false. If the raw center
Flag2 is1, that center is a fault, so at most one left Flag2 can be1;
the explicit h1 predicate erases it. Computed Flag2 is0. Wipe is absent
even at a faulty raw-GF holder, because computed Flag1 is0.
Each SF vote has at least three correct holder words; candidate selection
and IO therefore equal the reference. Repaired holder GF plus copy
offset supplies the correct logical service Address for all five
copies, including the birth predicate. Immutable ROM bits are unchanged.
Every field equals the quiet output, proving the assertion. Iterating
quiet closure gives equality outside the current overwrite sites at
every tick. This argument is valid for an infinite E0-only history;
it does not permit real1 or higher clusters and does not yield an iid
rate. The [audit checker](check_gray_moving_word_v2_audit.py) exhausts the
finite native-flag thresholds and three-of-five Boolean identities;
unrestricted native word replacement is handled by the three-correct-
words argument, not sampled values. GMW0's raw-GF birth hole remains
unchanged in its frozen implementation; this theorem uses the explicitly
different GMW2 service convention. It also does not repair the deadline.

## Exact prepared no-error deadline counterexample

Let the intended simulated configuration z have GF(j)=j mod Q, common
Age0, native flags0 and every SF bit0. It is a legal upper configuration,
**not an intact recursive hierarchy**: its ProgramBits do not encode its
own parent. Prepare physical common Age112Q+1, native flags0 and canonical
GF. Put one coherent initial head at3093 in each colony. All eleven lanes
of its Mem tape hold the corresponding full2007-bit z words in their
represented columns; Out, Scratch and Info are0. The ProgramBit copies
hold B at their logical service addresses. No errors occur. This is a
**preloaded fifth-stage context**, not a proved result of Gray's gathers
or the GMW2 earlier stages.

For colony0, the intended upper output ProgramBit slot4 is exactly

    F_B(z)(0).program[4]=B[(computed GF(0)+2) mod Q]=B[2]=1.

GF(0) computes0 and its flags remain0. B[2]=1 is a direct decoded bit
of the first native LOADC opcode, independently of universal beta
correctness. Slot4 is frame bit2006 and physical Out/Info primary5099.

The birth row is112Q+1. Subsequent active output rows are
112Q+2..120Q, a total **8Q-1=65535** updates, not65536. The retained
trace verifies every packet/movement/write recurrence on all these
updates. All65535 local transitions were additionally replayed, rotating
the five holders equally13107 times each. Quiet-copy induction above
lifts the retained logical trace to every holder in the infinite physical
configuration; all tape reads/writes stay in its colony. At the last
active row its mode isLOAD and Out[5099]=0; its wrong output list is
exactly[2006]. During120Q+1..U-1, the actual local rule votes and stutters
the pending head and Out. On the update producing Age0, all five Info
holders of5099 read old Out0 before Out is reset. The decoded output
ProgramBit copy4 is therefore0, whereas the actual intended F_B output
is1. This is a finite deterministic failure of the specified component's
baseline fifth-stage evaluation from its prepared context.

The uninterrupted `execute()` runner needs102026 updates to halt and
then agrees with all2007 expected output bits on this input. It exceeds
the usable budget by36491 ticks. After65535 it is **not** an execution
of the gated GMW2 physical rule; the102026 value cannot be described as
a successful physical period. The empty error set obeys the original
class conventions trivially. No error is attributed to a simulator,
an intact hierarchy or Gray, and no decoded-memory or iid result follows.

The [full uninterrupted cost traces](../../../figs/gray_counterexamples/GMW2_uninterrupted_cost_traces.npz)
pin the following exact finite decomposition. The audit rechecks every
packet and write recurrence in both traces; no all-input runtime bound
is inferred from them.

| Prepared simulated input | Total head updates | Instruction updates | Mutable-column updates | Operand-travel updates |
|---|---:|---:|---:|---:|
| Canonical zero-SF tuple |102026|21951|12425|67650|
| Dense stationary RUN/HLT tuple below |132803|26539|14105|92159|

Every instruction, including CODE, is already fetched/decoded in **one
update**. There is no44730-tick serial-code-fetch component. Instruction
counts include emitted helper loops; column updates read/write mutable
operands; travel updates move toward a requested column without reading
or writing it. A faster implementation must reduce these actual costs,
not subtract the emitted programme's bit length from its runtime.
The traces continue past the active gate and retain the same explicit
uninterrupted-runner scope.

## Why merely extending the fifth active end to125Q is insufficient here

A different, arbitrary-raw upper input has canonical GF, common
Age112Q+1, flags0, all other SF0, and the same stationary p=1 RUN head
at **every logical site**, with PC equal to the actual emitted last HLT
instruction and registers0. Its heads are coherent, but this is not an
intact one-head-per-colony hierarchy. An all-raw own evaluator must still
describe its local transition.

The uninterrupted emitted evaluator takes132803 ticks to produce its
correct2007 output bits and halt. At13Q-1=106495 updates (a proposed end
125Q after the current birth tick),14 outputs are wrong. At16Q-1=131071,
bit66 alone is still wrong: it is the high mode bit of upper head copy4,
expected1 forHALT but unwritten0. Before the mandatory Age0 reset, an
actual schedule starting with birth112Q+1 has at most16Q-2=131070 execution
updates. The audit also replays that exact131070 endpoint: bit66 is still0
instead of1 there. Thus even using the entire remaining16Q interval cannot compute
all raw inputs with this emitted evaluator. This is a **specified
implementation timing obstruction**, not a lower bound for every possible
evaluator or Gray.

No schedule was changed in this checkpoint. Extending the active interval
would alter F_B's stage predicate, its own beta and every affected gather,
flag, rest and special-write deadline; it needs recompilation and fresh
composition proofs. A shorter U or a sufficient replacement schedule has
not been established.

## Remaining construction obligations

| Obligation | Status | Precise limit |
|---|---|---|
| GMW1 Q-code length/reference failure | **proved** | This42850-bit emission only; not an evaluator lower bound. |
| GMW2 finite alphabet, all-raw transition and radius5 | **proved** | Explicit h1/zero-Workspace/immutable-ROM/holder-control variant. |
| Emitted beta/listing identity and64K fit | **proved** |44730bits/1863instructions; does not fit Gray's Q storage. |
| Generic ROM self-reference defined without Apply syscall | **proved** | Same finite B parameter at both levels; mutable code protocol changed. |
| Proposed beta full-field finite comparisons | **measured only** |70 retained inputs; universal identity unproved. |
| Quiet coherent-copy and original-E0 transparency component | **proved** | Canonical/common-clock/native-flags0 reference; no real1/higher claim. |
| Prepared fifth-stage baseline output mismatch | **proved** | Exact65535-step recurrence plus physical coupling/rest/commit; not intact initialization. |
| Arbitrary-raw dense-head remaining16Q runtime/output obstruction | **proved** | This emitted evaluator and birth time; initial context not intact. |
| Full emitted beta correctness on all raw states | **unproved** | No complete virtual-handler register-invariant proof. |
| Faithful Gray ProgrammeBits/hardwirer/gather/rest/pulse refinement | **unproved** | Immutable64K ROM and zero Workspace are substantial departures. |
| Concrete encoded whole-period self-simulation at these constants | **unproved; current schedule fails** | Prepared evaluator already misses a required output. |
| Continuing real1/higher recovery or positive iid rate | **unproved** | E0-only component equality does not bound higher errors. |
| Corrected Gray/Gács construction or iid-memory counterexample | **unproved** | This checkpoint establishes no such attribution. |

Reproduce without changing the earlier frozen GMW0 receipt:

```sh
python3 Report/proofs/gray_counterexamples/check_gray_moving_word_v2.py
python3 Report/proofs/gray_counterexamples/check_gray_moving_word_v2_audit.py
python3 Report/proofs/gray_counterexamples/validate_gray_counterexamples.py
```
