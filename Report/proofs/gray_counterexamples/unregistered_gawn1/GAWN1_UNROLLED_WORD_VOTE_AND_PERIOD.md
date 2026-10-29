# GAWN1: unrolled word voting in a new own ROM

This is an **explicitly new isolated own-ROM rule instance**, not an edit
to G17, GAW2R or GAWN0. The physical equations, instruction set, native
padding projection and Q8192/U1048576/lambda24/c104/radius8/Word100
constants are those of GAWN0. A new fixed beta_1 changes the instantiated
physical rule. No new instruction or host whole-rule evaluator is added.

Sources: [rule instance](unrolled_gawn1.py), [emitter](build_unrolled_gawn1.py),
[cost derivative](gawn1_compositional_cost.py), [structural/literal supplement](probe_unrolled_gawn1.py).
Emitted [ROM](../../../../figs/gray_counterexamples/unregistered_gawn1/GAWN1_rom.json)
and [listing](../../../../figs/gray_counterexamples/unregistered_gawn1/GAWN1_listing.json)
remain separate from every previous frozen instance.

## Exact theorem and premises

Let A,D,pi and E_D(d,B) be exactly the physical alphabet, represented
alphabet, six-field projection and canonical/common-clock/coherent/reset
lower encoding in [GAWN0](../unregistered_gawn0/GAWN0_NORMALIZED_NATIVE_EXECUTION_AND_PERIOD.md),
with its [wording corrections](../unregistered_gawn0/GAWN0_CITATION_ERRATA.md).
Use beta_1 wherever that definition used beta_N, and call the resulting
physical rule F_1. Set F_1^D(d)=F_1(pi(d)).

**Theorem.** For every prepared17-record D input tape, the new full
emitted evaluator halts and writes all496 representation words of
F_1^D at the centre within104566 updates. The early pass is unchanged
modulo PC relocation and halts within215 updates. For every infinite D
configuration d and coherent auxiliary Word100 B, with no physical noise,

    F_1^U(E_D(d,B)) = E_D(F_1^D(d),0).

Raw/projection runs have identical control and final output, as in GAWN0.
For d in A this is exact same-rule noiseless self-simulation. The lower
geometry, coherent five-copy Info, reset work and immutable beta_1 in
E_D are essential premises. Represented upper SF may be arbitrary,
including invalid instruction metadata and incoherent upper SF copies.
The theorem covers no arbitrary damaged lower configuration, general
lower error class, positive iid rate or remembered bit under noise.

## 1. Universal helper contract — proved

The old helper votes five words, using the fixed holder order
S=(0,-2,-1,1,2). At entry R11 is a typed SF base field f,
R12 is a centre lane c, R15 is the typed return PC. Its five operands are

    x_i = Mem[P+f+i, c-S_i],       i=0,...,4.

The existing call-site contracts give0<=f<=491 and2<=c<=14, so every
field/lane is in its declared finite range. Actual calls have f>=6.
Neither the unrolled helper nor this statement adds new valid call sites.

The new37-instruction block explicitly computes each lane c-S_i with
MOV or one ADD/SUB, performs the same five actual LDX reads in the same
order, and increments R11 after each read. It writes no Out or Scratch,
uses no payload branch and performs no fixed-table lookup. Travel starts
at the same first field and ends at f+4. Only the final typed JMPR branches.

For an individual bit, let u,v,w denote “at least one”, “at least two”
and “at least three” among the inputs already read. After input x the
standard recurrence is

    w' = w OR (v AND x)
    v' = v OR (u AND x)
    u' = u OR x.

The old helper executes this recurrence five times from zero. The new
helper removes the known-zero initial operations: after the first read
u=x_0; after the second v=x_0 AND x_1 and u=x_0 OR x_1; after the third
w=v AND x_2, v=v OR (u AND x_2), u=u OR x_2. The last two reads use the
original recurrence verbatim. Induction on input count proves w is
exactly the >=3 majority bit. All operations on the data words are
bitwise AND/OR/MOV, so the induction applies independently to all100
bits with no carries or signed interpretation.

At return R0=R5=w, R3=u, R4=v, R1=(x_0 OR ... OR x_3) AND x_4,
R6=0, R7=16, R8=5, R11=f+5. R2,R9,R10,R12,R13,R14,R15 are
preserved. These are exactly all sixteen old helper return registers,
not merely the majority result. The new block sets the old table/loop
debris R6/R7/R8 explicitly. The PC denotes the relocated typed return.

The literal listing has37 executed instructions and five SEEK completions.
The first completion costs at most distance(I,[f,f]); the next four cost
one each because the read fields are adjacent. Thus the helper execution
cost excluding the caller JMP is at most

    37 + distance(I,[f,f]) + 4,

where distance is the prior interval bound max(1,abs(I.low-J.high),
abs(I.high-J.low)). This improves the old86-instruction cost by49
for every call, while preserving its exit-position interval.

## 2. Full semantics and padding — previous argument applies

The emitter starts with the normalized GAWN0 unresolved instruction and
label sequence and replaces only the vote..slots helper block. Every
other unresolved row is identical, including all24 native masks and
the early entry. Assembly recomputes all labels, typed returns, dispatch
data and slots-table addresses. No branch enters an interior helper PC;
all helper calls enter vote. The ROM used by generic upper CODE/BITCODE
emulation is beta_1 on both sides of the physical local-step equation.

The universal helper contract replaces the old contract at every typed
call. Induction over the unchanged compositional blocks therefore proves
the complete local evaluator, using the compiler argument in
[GAW2 §2](../unregistered_gaw2/GAW2_THREE_GATHER_PERIOD.md). The unchanged
GAWN0 acquisition/relational induction proves projection equality on D:
no raw native value is used before its normalization macro completes,
and no SF data word or register is projected. This is a reuse of the
universal contracts, not a comparison of sample outputs.

## 3. Full cost — proved by the same finite contract DAG

The new cost source is an exact derivative of the frozen GAW2R cost
source, except imports, output name/guard and the proved helper cost
86->37. No loop, branch, typed-address, position-interval or phase rule
changes. All new native masks are ordinary one-update ALU instructions
in the actual newly assembled listing. Raw payload branches still fork;
the entire finite state tracks PC, copy index, exact loop counters,
vector mode and head-position interval.

Every real prepared trace follows one path in this graph. Its non-helper
instructions and travel are charged individually, helper paths obey §1,
and literal counter increments bound every loop. Reverse induction in
the finite DAG bounds all such paths. Recomputing every one of the72
exact computed-Age classes gives maximum104566 (at class589827).
The [cost receipt](../../../../figs/gray_counterexamples/unregistered_gawn1/GAWN1_compositional_cost.json)
records the graph results; the proof is that domination/induction, not a
maximum among executions on sampled payloads. Early syntax and targets
are unchanged modulo relocation, so its215-update bound is unchanged.

There are147455 active updates after late birth at102Q+1 before120Q;
the margin is42889. The whole bound also fits13Q-1=106495, with1929
updates to spare. **This does not prove a shorter-U rule:** changing the
clock modulus, native equations, schedule, emitter constants and period
requires a separately defined instance and proof. Current U remains128Q.

## 4. Complete physical period — previous argument applies

Use [GAWN0 §5](../unregistered_gawn0/GAWN0_NORMALIZED_NATIVE_EXECUTION_AND_PERIOD.md)
with the corrected [GAW2 §6](../unregistered_gaw2/GAW2_THREE_GATHER_PERIOD.md)
period reference and beta_1. The native lower equations and physical
three-gather, capture, Mailbox wipe, History retention, early birth,
bounded courier, quietness, late birth and commit schedules are unchanged.
Prepared packet/holder coupling uses §2's new universal evaluator.
Section3 supplies a strictly sufficient late deadline. Every normal
output word, auxiliary zero, Programme bit and reset work component
therefore has the same E_D-to-E_D induction. At U, Info consumes old
Out before reset. This proves the stated equality on every site of Z.
No finite domain or common represented upper clock is assumed.

## Receipts and unresolved work

The [literal supplement](../../../../figs/gray_counterexamples/unregistered_gawn1/unrolled_probe01.json)
checks416 helper executions: all32 input-bit patterns,13 safe lane
centres and both edges of the496-word frame, including every return
register. The universal word claim comes from §1's independent-bit
induction. Four complete496-output own-ROM executions with raw native
padding, including commit and a live upper head, are measured
transcription supplements. The new/old cost-source derivative and all72
contract classes are checked without selecting mutable payloads.

New ROM:3781 tokens,1053 dictionary entries,41591 token-stream bits,
270349 allocated immutable bits. K49037 and every Word100/radius8/
immutable-ROM departure remain. Gray beta<=Q,512-entry dictionary and
literal bit-primary Q>=2K=98074 budgets still fail. No old actual fault
history is transferred to the changed ROM. These facts supply no
Gray/Gács disproof, smaller-Q/U construction or iid reliability theorem.

| Step | Status | Scope |
|---|---|---|
| Actual five reads/bitwise majority/all return registers/37-update instruction cost | proved | Existing typed SF helper calls |
| Whole prepared local semantics and native padding projection | previous compositional/relational arguments apply; new helper and relocation premises proved | Arbitrary represented raw SF/native padding |
|104566 full and215 early deadlines | proved by prior contract DAG with new helper cost | All payload branches retained |
| Full infinite-line noiseless E_D period | previous physical argument applies | Canonical coherent reset lower encoding |
|416 helper/four whole-ROM executions | measured supplements | No universal inference from samples |
| Damaged lower/noisy higher repair/smaller Q-U/faithful Gray/iid-memory/minimum change | unproved | No active rule change or commit |
