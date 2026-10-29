# GMW4: affine physical IO, full emission and prepared deadline obstruction

This is an isolated, explicitly changed evaluator attempt. It retains
Q=8192, U=128Q=1048576, and the original error-location constants
lambda=24, c=104. It does not instantiate Gray's ProgrammeBits evaluator.
The active construction and all previously accepted GMW/GH sources are
unchanged. Neither a Gray theorem counterexample nor iid unreliability is
established here.

## Exact rule and its changes

The total scalar transition is emitted by
[gray_affine_word_machine.py](gray_affine_word_machine.py). Its two complete
generated sources are retained as
[Q-code](../../../figs/gray_counterexamples/GMW4_Q_generated_rule.py.txt)
and [64K-code](../../../figs/gray_counterexamples/GMW4_64K_generated_rule.py.txt).
The generator clones the immutable GMW2 source in a separate namespace,
checks every specified substitution, and never writes the original.

Both machines use the existing five-copy, one-site moving-head geometry.
Native Address/Age/Flag1/Flag2 are the explicit h1-corrected equations;
Workspace flags are always zero. Service/birth Address for an output
holder x, slot s is (computed-GF(x)+s) mod Q. These are explicit departures
from literal Gray. Mem is an eleven-lane bit word. Head, Out, Info,
Scratch and mutable ProgramBit each have five copies. All raw collisions,
malformed heads and invalid IO descriptors use the inherited total
priority/error rules. In particular, an error head is retained with
move=0; no implicit external repair or whole-rule evaluation is invoked.

The Q-code machine has 13-bit instruction PC and an immutable Q-bit
table. It has a 376-bit head, K=1992 represented bits and primaries
[3100,5092). The distinct diagnostic machine has 16-bit PC, immutable
65536-bit table, 379-bit head, K=2007 and primaries [3093,5100).
These tables are fixed parameters of the finite transition. Instruction
fetch reads up to 62 consecutive table bits in one native update; CODE
reads twenty bits from the same finite table, returning zero outside
the table. Thus fetch does not incur serial tape travel. Mutable
ProgramBit at logical service Address a is refreshed from beta[a].
Immutable instruction-table simulation and mutable-programme repair are
different obligations; the former is implemented as finite CODE reads,
not a call to a host evaluator or to the whole rule.

GMW4 removes XORI and uses opcode27 for AFFREAD/AFFWRITE. Its 62-bit
syntax consists of a five-bit opcode, one read/write bit, then

```
(dst/value register:4, base:13,
 scale1:10, index1 register:4, scale2:10, index2 register:4,
 width:5, lane register:4, channel:2).
```

For full twenty-bit raw registers, its physical pointer is the ordinary
integer

```
A = base + scale1 * R[index1] + scale2 * R[index2].
```

Width must be 1..20 and A+width<=8192. AFFREAD additionally requires
R[lane] in 0..10. Its channel selects Mem lane, Out, Scratch or mutable
ProgramBit. AFFWRITE ignores the lane register and selects Out/Scratch
by channel&1. Invalid descriptors retain the old PC and enter ERROR.
There is no modulo reduction that turns an overflowing product into
a valid pointer. Valid descriptors enter the ordinary SEEK/LOAD/WRITE
states: the head travels one physical site each update, reads or writes
one bit at the target, and carries the twenty-bit word in a register.
The added generic scalar operation SATMUL returns min(2^20-1,a*b).
All other old opcodes retain their stated raw-state behavior.

## Locality and physical execution coupling

**Proved for this component.** No spatial lookup was added to GMW2:
affine arithmetic, fetch and scalar ALU use only a decoded voted head
and the finite immutable table. For output slot s, logical data at y=x+s
uses holders y-t for t in {0,-2,-1,1,2}, hence distance at most4.
Incoming heads at y-1,y,y+1 add at most one site, hence distance at most5.
The holder's native controls use radius5. The complete emitted rule
therefore has radius5 on all raw states, even for an invalid pointer or
head collision. Finite ROM access is not a spatial neighbourhood read.

**Proved quiet-copy coupling.** Start with canonical native Address,
common legal Age and all four flags zero, and coherent five-copy values
of each logical service field. Set the interpreted Mem tape once and
prepare a single head at its entry Address, with other logical heads
absent. The h1 native step preserves this geometry, all flags remain
zero and no SF wipe occurs. A logical vote reads exactly its common
word. Each output holder computes the same target Address from its
own GF plus slot. The sole incoming head is selected at its stationary
or one-site destination; every copy executes the same scalar step
with the same local data. An Out/Scratch bit write is consequently
made identically by all five holders. This proves induction of the
coherent physical trajectory from the scalar recurrence. It does not
assert that the programme simulates every upper raw state.

The same one-step copy argument admits up to two arbitrary complete-cell
overwrites in any radius-five input cone, relative to a canonical,
common-clock, native-flags-zero coherent reference: each word vote keeps
three correct copies, and the explicit h1 native step repairs the
controls. This is the existing GMW2 local transparency argument with
different register arithmetic; it is not a full gather/period/noisy
programme theorem or a real1 recovery result.

## Full emitted programme and the space obstruction

[build_gray_affine_word_machine.py](build_gray_affine_word_machine.py)
emits every field of the candidate transition using ordinary finite
instructions and actual operand travel. Constant field and register
addresses now use AFFREAD/AFFWRITE; the shared word-vote loops remain.
The programme includes the virtual opcode27 handler and SATMUL case,
so they are not left as arbitrary external ports. The old five-bit
instruction-length table cannot hold62: a separate opcode27 override
sets62 before virtual PC advance. The virtual affine handler guards
both products before summing them. For a nonnegative product p,
min(2^20-1,p)<=Q iff p<=Q. After these two guards the sum is at most3Q,
strictly below2^20, so ordinary word addition cannot wrap. The common
IO-descriptor check then rejects A+width>Q, invalid width and invalid
read lane. This explains the intended arithmetic implementation;
the complete virtual-head/control equivalence is still unproved.

| Emission | Exact bits | Instructions | Invalid instruction references | Code labels outside capacity |
|---|---:|---:|---:|---:|
| Q-bit table, 13-bit PC | 39544 | 1413 | 165 | 120 |
| Separate 64K table, 16-bit PC | 40188 | 1410 | 0 | 0 |

**Proved specified-emitter failure.** The Q-target exceeds8192 bits by
31352. The full attempted
[bitstream](../../../figs/gray_counterexamples/GMW4_Q_full_attempt_beta.bin)
and [listing](../../../figs/gray_counterexamples/GMW4_Q_full_attempt_listing.json)
retain the165 invalid references and their masked encodings. This is
not an admissible Q-sized own programme. No repair is made by silently
truncating the programme or its labels. The separate
[64K bitstream](../../../figs/gray_counterexamples/GMW4_64K_full_attempt_beta.bin)
and [listing](../../../figs/gray_counterexamples/GMW4_64K_full_attempt_listing.json)
do fit that changed table and have no invalid references. Decoding every
listed instruction proves emission/ROM identity. It does not prove
the beta's universal semantic identity with this rule. Neither count
is a lower bound for another compiler, ISA, layout or Gray's evaluator.

## Finite checks and the actual deadline failure

The [receipt](../../../figs/gray_counterexamples/GMW4_affine_full_attempt_certificate.json)
pins kernel/compiler/checker/proof sources, emitted code, listings,
dependency sources and both retained input/output assets.

**Measured only as evidence for universal semantic equivalence.**
Fifty-one preloaded eleven-cell upper neighbourhoods are retained in
[full-field replays](../../../figs/gray_counterexamples/GMW4_64K_full_attempt_replays.npz).
They include canonical-zero SF, native birth/commit clocks, one RUN
case for each used opcode, affine arithmetic with five uniform full-word
register values, and five LOAD kinds. All complete output comparisons
match the scalar physical rule. Runtime is76614..115920 head updates;
canonical101902, native birth76614, native commit115920. The comparable
GMW2 canonical count was102026, a saving of only124 updates, despite
the reduction from1863 to1410 emitted instructions. Physical helper
and operand-travel costs remain; no saving equal to the programme-bit
reduction may be inferred.

**Proved finite prepared-context deadline failure.** Use the canonical
upper neighbourhood C[j].GF=j mod Q, Age0, flags0, all SF0 for j=-5..5.
Populate the lower logical Mem tape with its exact eleven-lane frame
via input_tape(C), initialize every lower Out/Scratch bit to0, and use
coherent copies of this tape and beta. Lower native GF is canonical,
Age112Q+1, flags0, with a sole born head at3093. All other lower logical
heads are absent. This is an explicit prepared completion, not an
intact recursively encoded hierarchy or a proved faithful gathering.
There are no errors; the physical error support is the empty set.

The birth row is112Q+1 and execution rows run112Q+2..120Q, so there are
8Q-1=65535 actual execution updates. The
[deadline asset](../../../figs/gray_counterexamples/GMW4_64K_prepared_deadline.npz)
retains every packed head before/after, actual Address, Out/Scratch
write, input neighbourhood, expected output and truncated output.
Replaying each exact step and the quiet-copy induction gives the
physical trajectory. At Age120Q the head is RUN, PC38105, Address5079.
The only differing output frame bit is2006: expected1, actual0.
This is mutable ProgramBit copy4 at represented primary5099, and its
expected value is beta[2]=1. Thus unfinished head status is accompanied
by a wrong represented output, not merely late HALT.

During the subsequent rest every head and Out bit is preserved by
the literal component equation. On wrap to Age0 the output Info takes
OLD voted Out before reset. Actual local transitions at all five
holders5099,5101,5100,5098,5097 store this wrong0 in their corresponding
Info slots and clear Out. Therefore the prepared fifth-stage map for
this diagnostic programme fails at unchangedU128Q, even without noise.
The uninterrupted canonical programme eventually produces all expected
bits and halts at101902 updates, but it cannot use those extra updates
under the stated schedule. No larger or shorter schedule has been
certified, and finite runtimes do not give a universal deadline.

## Status and what remains

| Obligation | Status | Exact scope |
|---|---|---|
| Total affine arithmetic/IO and radius5 | proved | Explicit changed finite component, including invalid raw cases |
| Canonical coherent physical-head coupling | proved | Prepared tape, quiet native controls, one-site head |
| Q-sized attempted code/ref/reference failure | proved | This emitted programme only |
| Separate64K emitted-code/ROM identity | proved | Static identity, not universal beta semantics |
| Full-field comparison campaign/runtime | measured only |51 retained prepared inputs |
| Wrong represented output at actual65535-update deadline and commit | proved | Exact no-error prepared canonical context |
| Universal beta equivalence/runtime | unproved | All raw head/field cases not certified |
| Own beta<=Q or a sufficient actual five-stage schedule | unproved | This Q emission fails |
| Gray-faithful evaluator, physical input gathering, early flags and special write | unproved | GMW4 interface/storage departures remain |
| Intact-context counterexample, corrected Gray refutation or iid memory failure | unproved | No such claim follows |

Reproduce the generation/finite campaign with
`python3 Report/proofs/gray_counterexamples/check_gray_affine_word_machine.py`.
Read-only validation is
`python3 Report/proofs/gray_counterexamples/validate_gray_affine_word_machine.py`;
it reassembles and decodes both attempts, replays the retained comparisons
and all65535 deadline steps, then checks actual rest/commit equations.
