# GMW5: full word-tape emission and a prepared deadline failure

This is an explicitly changed component at Q=8192, U=128Q=1048576,
lambda=24 and c=104. It does not instantiate Gray's ProgrammeBits protocol.
Its native rule uses the explicit h1 Flag2 correction, holder-computed
Address for service controls, and zero Workspace.Flag1/2 outputs. Info,
Out, Scratch and Programme are100-bit mutable words; Mem contains eleven
100-bit words. A head has six100-bit metadata words and sixteen100-bit
registers. All these fields have five actual physical copies.

Sources: [total kernel](gray_word_tape_v5.py),
[full emitter](build_gray_word_tape_v5.py),
[emission/execution checker](check_gray_word_tape_v5.py),
[read-only validator](validate_gray_word_tape_v5.py),
[receipt](../../../figs/gray_counterexamples/GMW5_word_tape_execution_certificate.json),
[exact deadline trace](../../../figs/gray_counterexamples/GMW5_64K_dense_mask_deadline.npz).
Earlier accepted candidates and G17 are unchanged.

## Total component and specified emission

The alphabet has37 native bits, five2200-bit head packets, five1100-bit
Mem words, and four groups of five100-bit words:18537 bits. An upper cell
occupies191100-bit rows, with zero native padding. Primaries4001..4191
hold its represented words. The five slots are S=(0,-2,-1,1,2): slot s at
x represents logical y=x+s. Incoming-head votes use holders x+s+d-t,
d=-1,0,1 and t in S, giving radius at most5. Destination data votes have
radius at most4. Service Address is (computedGF(x)+s)modQ. The native
calculation/wipe has radius5. Immutable instruction lookup has no physical
source. Thus all raw-state equations have radius at most5.

The thirteen instruction types are HLT, JMPR, MOVI, ALU, LDX, STX,
READ5, READMASK, CODE, BNZ, JMP, ALUI and ALUX. CODE returns one100-bit
window from the immutable beta bit-ROM in one update; instruction fetch
also occurs in one update. Neither invokes the complete rule, native
calculation or a packet-step oracle. LDX/STX and the two native read
instructions initiate SEEK with real one-site operand travel. Every raw
packet has a total outcome: missing, colliding, invalid movement/mode,
out-of-range target/lane/PC and invalid opcode semantics are specified.
The physical Programme words are voted data; they are not the instruction
fetch store. This is an explicit departure.

The specified Q-bit emission has26137 bits,891 instructions,105 invalid
13-bit code references and70 out-of-range labels. It cannot instantiate
its own fixed Q-bit ROM. The distinct64K diagnostic changes the immutable
store capacity to65536 and reference widths to16; its emitted26542 bits
and891 instructions have no invalid references. Static decode establishes
the emitted-listing/ROM identity, not universal semantic equivalence.

The initial26024-bit887-instruction attempt is separately retained in its
[first failure](../../../figs/gray_counterexamples/GMW5_first_Q_full_attempt.json).
The generator assertion and three implementation errors are retained in
[generator failure](../../../figs/gray_counterexamples/GMW5_initial_generator_assertion_failure.json),
[execution failure1](../../../figs/gray_counterexamples/GMW5_execution_failure_01.json),
[execution failure2](../../../figs/gray_counterexamples/GMW5_execution_failure_02.json),
and [execution failure3](../../../figs/gray_counterexamples/GMW5_execution_failure_03.json).
They include exact source snapshots. The substantive fixes are signed
slot subtraction, restoring old PC on HLT, and matching otherwise-unused
descriptor lane5 bits. These are our changed emitter's bugs; they do not
contradict Gray.

## Exact prepared failure at the execution deadline

The lower geometry is canonical with a common clock, all native flags0,
and coherent physical SF copies. Its readonly eleven-lane input tape is
preloaded with the exact upper cells in the linked trace. These cells are
legal raw states: upper GF is j modQ and common upper Age112Q+1. Every
logical source has a stationary SEEK head, its target equals its own
Address, and its kind3 operation reads the eleven Mem low bits. The other
word values are the retained seed71 fixture. This is a prepared upper
context, not an intact recursive initialization. The error history is empty.

The birth output row is112Q+1. Actual execution outputs run112Q+2..120Q,
so the active execution interval contains65535 updates. At that deadline,
the exact emitted64K recurrence has a SEEK head, PC23773, at4113. Its
represented output differs from the actual local transition at two words:

| Word | Field | Primary | Actual | Required |
| --- | --- | --- | --- | --- |
|20|mode copy4|4021|1|0|
|75|register7 copy4|4076|0xb657f818b715a6e0aa8ce3b47|0x3f9|

The validator checks each of65535 packet updates against the pinned trace,
including every instruction fetch, operand move, Out write and Scratch
write. Quiet canonical geometry makes the raw-GF wipe false. A unique
one-site head and coherent data lift that recurrence to all five physical
holders: each voter sees the same logical source, controller and data.
The source/destination footprints stay within the colony. No-error native
geometry remains canonical and all native flags remain0.

Rest retains these wrong Out values and the pending head. The rest formula
is independent of time throughout120Q..U-2; the endpoints and one interior
clock are also checked at all five head holders. The update producing Age0
copies old voted Out to Info before resetting Out. Hence all five actual
holders at primary-minus-slot commit each wrong word. This proves an
actual decoded-field failure for this prepared no-error component. It is
stronger than an unfinished-head observation, and weaker than a complete
period or intact-hierarchy counterexample.

The62 retained full comparisons are additional measured checks. They all
match the actual kernel after uninterrupted execution; runtimes range
23358..68254. Canonical, birth and commit fixtures take23358,26547 and
27458 updates.128 native-only comparisons match in150..152 updates. These
measurements do not establish a universal own-beta semantic or deadline
theorem. The dense-mask finite failure establishes that the unchanged
120Q execution endpoint is insufficient for this specified diagnostic.

| Step | Status |
| --- | --- |
| Total raw-state component, real IO and radius5 | **proved changed rule** |
| Q-bit emission/reference obstruction | **proved for this emitter** |
| Separate64K listing/ROM identity | **proved static identity** |
|128 native and62 full finite comparisons | **measured only** |
| Prepared65,535-update decoded-field/rest/commit failure | **proved finite witness** |
| Universal own beta/deadline, physical input preparation and whole period | **unproved** |
| Gray-faithful Q-bit evaluator or intact/noisy/iid counterexample | **unproved** |

No smaller U, change to G17, universal evaluator lower bound or result
against Gray's corrected construction follows from this checkpoint.
