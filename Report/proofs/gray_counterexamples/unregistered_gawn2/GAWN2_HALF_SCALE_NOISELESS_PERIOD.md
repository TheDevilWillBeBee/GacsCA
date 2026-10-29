# GAWN2: a new Q4096/U524288 rule with a complete noiseless period

This is an **explicit change of rule, constants, schedule, native widths,
instruction encoding and own ROM**, isolated from G17 and every frozen
proposal. It halves both Q and U relative to GAWN1/Gray's numerical
Q8192/U1048576. It retains the original error-class numbers lambda24/c104;
no noisy estimate is transferred by retaining those numbers.

The physical equations are [small_rule_gawn2.py](small_rule_gawn2.py),
derived by [the source-copy generator](derive_small_rule_gawn2.py).
The actual [emitter](build_small_gawn2.py) uses ordinary existing opcodes;
the new fixed [ROM](../../../../figs/gray_counterexamples/unregistered_gawn2/GAWN2_rom.json)
and [listing](../../../../figs/gray_counterexamples/unregistered_gawn2/GAWN2_listing.json)
are not the old rule's programme. The compiler is an offline description
of this finite rule. No physical primitive calls a host native or
whole-cell evaluator.

## Exact statements

Let A_2 consist of six native fields with widths12/19/1/1/1/1 and the
same490 arbitrary Word100 SF words. Its physical bit size is K49035.
Q4096=2^12 and U524288=2^19 make every native Address/Age pattern legal.
Let D be all496-word records with arbitrary100-bit words, and let
pi_2:D->A_2 mask only the six native words to those widths. Every SF
word, including every upper memory/register/packet word, is unchanged.
Write beta_2 for the newly emitted immutable ROM, F_2 for the stated
physical rule with that ROM, and F_2^D(d)=F_2(pi_2(d)).

The frame starts at P1800 and occupies[1800,2296). The five holder
offsets remain S=(0,-2,-1,1,2). Define E_2(d,B) on Z as follows: native
Address x modQ, common Age0, native flags/WF0; all private work0;
Programme at each holder is the beta_2 bit at that holder's logical
Address. Logical Info at gQ+P+i is representation word i of d[g], with
five coherent copies at gQ+P+i-S[h]. At all remaining logical sites Info
is the arbitrary coherent Word100 function B. Upper native padding is
stored in lower SF Info, so E_2(d,B) is a legal configuration of A_2.

**Theorem S1 (prepared evaluation).** For every17-record D input tape,
the new normal-entry evaluator halts within104572 updates and writes
exactly all496 representation words of F_2^D at the centre. Its early
entry halts within221 updates and writes the four new native
Address/Age/F1/F2 words and zero WF1/WF2. Raw and pi_2-projected tapes
give the same control history and final output. Just-read raw native
registers/vectors can differ during their normalization macro.

**Theorem S2 (physical period).** For every infinite D configuration d
and coherent auxiliary B, without physical errors,

    F_2^524288(E_2(d,B)) = E_2(F_2^D(d),0).

For d in A_2 this is exact noiseless self-simulation of the same fixed
finite rule. The lower canonical geometry, common clock, coherent Info
holders and reset work are essential premises. There is no upper
geometry, common upper clock or upper SF coherence premise. Arbitrary
invalid upper packet metadata and upper native padding are covered.

Neither theorem asserts closure of an arbitrary damaged lower encoding,
recovery after a real error, positive iid epsilon, or remembered-bit
reliability. In particular, noiseless equality is not the missing
fault-tolerant simulation theorem.

## 1. The changed finite equations — proved

The generator copies the frozen GAW0 packet/word equations, the h1
native equations and the GAW2R three-gather physical equations into a
new module. It changes the module's Q and U, calls the literal native
scalar with both new parameters explicitly, and uses masks Q-1/U-1.
It does not mutate a frozen imported module's globals. The new native
scalar retains the introduced h1 Flag2 correction; this is still a
departure from the printed Gray rule.

The new stage resets are0,32Q,64Q,96Q,100Q, with the additional early
reset72Q+3. Late birth/reload is100Q+1; the late head remains active
through computed Age127Q. U is128Q. Head packet widths remain Word100;
generic ALU/window/inside and all physical target guards use the new Q.
Generic READ5 still acquires five20-bit components. Native Age no
longer uses that full component width without further projection.

JMP and BNZ encoded target operands narrow to12 bits. This matters:
the inherited virtual templates do not separately guard an encoded
immediate target after decoding it. With12-bit operands every encoded
target is below the new4096-word capacity, as required by the physical
equation. Arbitrary register JMPR targets and raw PCs still pass the
explicit new-capacity guards. Keeping13-bit immediate targets while
merely changing Q would not justify reusing that template. LDX/STX
base operands remain13 bits, with their unchanged explicit new-Q
guards; all larger base values are handled by the ERROR equation.

The declared D extension projects before the old-Address wipe test and
before computed-primary source reads. Thus F_2^D(pi_2(d))=F_2^D(d)
and its native output is legal. This is a changed padded-input
extension, not a claim about an earlier unnormalized emitter.

## 2. Exhaustive native acquisition and compiler — proved using prior contracts

The emitter starts with the complete GAW2R unresolved programme built
with the **new engine**. Physical frame bases, Q-dependent guards,
capture clocks, dictionary addressing and PC-width decoding therefore
already use its new parameters. The following remaining literals and
acquisitions are changed explicitly:

*16 GF-vector widths13->12; eight native Age-successor masks20->19;
 five service-Address masks8191->4095. Service Address is computed
 Address plus holder offset modulo the new Q, not modulo the old Q.
* Four remaining late-schedule literals: two births102Q+1->100Q+1,
 active start102Q+2->100Q+2, and cutoff120Q+1->127Q+1.
*24 direct raw-native LDX masks,16 GF12 and8 Age19.
*16 native Age READ5 sites each followed by MOVI R1,0;
 MOVI R15,19; VADDINDEX R0,R0,R1,R15.
* The previously proved37-instruction SF vote helper, with identical
 full-word reads and all sixteen return registers, is reassembled.

For any100-bit native word v, a direct mask equals pi_2(v). A GF-vector
component becomes (v+step*(i+1)) mod4096, independently of bits12..99.
MOVI(-1) encodes unsigned1048575; it is congruent to-1 modulo4096,
which is sufficient for this GF calculation. Age's new zero-step
VADDINDEX strips each20-bit component to19 bits before its majority,
existence test, mismatch test or fallback is used. All source and early
instances receive that macro. Flags are acquired only at bit0.

No branch or external label enters a partial acquisition macro. The Age
macro's additional R1/R15 values are dead after its VADDINDEX: on every
native body both registers are overwritten before their next use.
The literal register-read check verifies this at all16 sites. All seven
central/computed-primary native bodies have identical normalized
arithmetic; the early body is the central prefix with relocated targets
and HLT in place of the final jump.

There are exactly24 direct native raw Mem reads,32 native READ5 sites
(16 GF/16 Age),32 low-bit flag-column sites, and the five SF-helper
raw Mem reads. The latter have the previously proved typed SF-field
contracts, so no native input escapes projection through that path.
Other reads use unchanged SF words, current Out/Scratch or fixed ROM.
No upper SF memory or register word is masked to the native Age width.
In particular the generic upper READ5 template retains its20-bit mask.

Induct on simultaneous executions from the raw and projected prepared
tapes, grouping each native acquisition macro as one block. Their
outputs agree, their targets and waiting descriptors agree, and all
other operands/branches/stores agree. This proves identical control
and output for all raw words, including travel updates.

On legal inputs the compiler proof in
[GAW2 §2](../unregistered_gaw2/GAW2_THREE_GATHER_PERIOD.md)
and the generic instruction equations in
[GAW1](../unregistered_gaw1/GAW1_UNIVERSAL_PREPARED_EVALUATOR.md)
apply as parameterized word contracts. The premises that changed have
just been supplied: GF12/Age19 modular arithmetic, new-Q windows and
targets, new12-bit jump decoding, actual relocated returns/dispatch,
new service moduli, new schedule, and the
[GAWN1 helper contract](../unregistered_gawn1/GAWN1_UNROLLED_WORD_VOTE_AND_PERIOD.md).
The arithmetic/interpreter templates otherwise compute the same
explicit equation schemas. Invalid raw upper packet values take their
literal guarded failure branches. CODE/BITCODE use beta_2 on both sides,
including their total zero-padding behavior; no old instruction table
is substituted. Every interpreted opcode case therefore implements
the new physical step, and their compositional output is F_2(pi_2(d)).

The new checker reruns formal-word Mail/History/Mem equations on all720
clock/Flag1/copy instances and courier/Info equations on all2880
clock/Address-class/copy instances. The helper is abstracted only by
its proved five-word contract, with explicit register clobbers. All
old words are formal atoms, not selected data. Actual loop increments,
typed holder lanes, scratch initialization, ROM decode, dispatch and
the changed early prefix are checked against the new listing. This
verifies the new finite premises of the compositional proof.

## 3. Universal deadlines and resources — proved

The [new cost graph](small_compositional_cost.py) is the frozen GAWN1
graph with only imports, output names and the available-window expression
changed. Its actual newly assembled rows include every new acquisition
instruction. No branch, loop-counter, typed-address or travel edge has
been removed to improve the bound.

Each prepared real trace follows a path in the bounded contract graph.
Each non-helper instruction costs one execution update plus its actual
IO travel bound; helper calls use the same37+first-distance+4 contract.
The graph retains all payload branches, exact loop/copy counters,
possible head-position intervals and generic mask mode. Every IO target
is in[0,496) relative to P, hence inside the new colony; all typed native
and SF lanes remain in[0,17). Finite loop syntax and definite Scratch
initialization checks use the actual new listing. The maximum cost of
the finite acyclic contract graph dominates each real execution by
reverse induction.

All72 exact computed-Age classes partition[0,U); new birth/cutoff
thresholds are included. Recalculation gives maximum104572 updates,
at computed Age294915. This is an all-payload contract bound, not a
maximum among sample executions. Late birth409601 and active end520192
give110591=27Q-1 updates, leaving6019. The early prefix has141 executed
instructions and16 IO completions whose distance is at most5 each:
141+16*5=221. This is less than the available gap3Q-4=12284 to75Q.

The emitted ROM uses3829 tokens and1055 dictionary entries; all PCs
and typed return/dispatch targets are below4096. Used11-bit token
stream length is42119 bits. Allocated immutable resources are
65536+2048*100+12=270348 bits. These are finite constants, but fail
Gray's beta<=Q and512-entry dictionary budgets. Gray's literal
bit-primary condition Q>=2K would require98070 at K49035. The496
Word100-position representation is an explicit different interface.
There is no proof here of optimal compression, minimum Q or minimum U.

## 4. Actual infinite-line physical period — proved

Start at E_2(d,B). Native adjusted-GF candidates all equal canonical
Address and both Age candidates equal the common successor clock.
This remains true for arbitrary evolving native flags/WF/SF. Thus
geometry remains canonical and the computed SF wipe is always false.
Five coherent copies of every logical word remain coherent by the
literal holder equations; lower packet movement represents one logical
head, not five unrelated executions.

Before96Q, WF sources are0 and initially zero native flags stay0.
The actual resets, loads and moving Mail therefore implement three
gathers at0,32Q,64Q. At each holder of frame word i, lane j captures
the old logical Info at (g+j)Q+P+i; capture is S+1 for lane0 and
S+2+abs(j)Q otherwise. This is the same source-coordinate induction
as GAW2 §4 with the new Q/P. The furthest third capture is72Q+2.
All three History banks then contain the same full17-record D bank.
No auxiliary Info lies on a represented-frame source coordinate.

Reset72Q+3 and birth72Q+4 derive, rather than assume, a prepared early
execution with readonly Mem, zero Out/Scratch and one pc=early logical
packet. S1 and the holder/packet induction complete its outputs within
221 updates, strictly before75Q. Its F2/F1 bits seed the actual bounded
left/right couriers at P+3/P+2. Distances to3/Q-3 are1800/2291;
both routes are wholly inside their own colony and their absorbing
endpoints hold the correct source through80Q-1. They arrive before
the required old-source read at80Q-2. The literal special Info writes
therefore install those same early commands. No future command is
provided externally.

The96Q..98Q window may activate lower native flags, but cannot wipe
History under canonical geometry. By current Age98Q all WF fields
are0 thereafter. With old WF0 the Flag1 recurrence is

    (at least3 right-in-colony ones) OR
    (old self1 AND at least2 right-in-colony ones).

Starting at the last two colony cells, a zero strip advances left by
at least two cells each tick; arbitrary Flag1 clears withinQ/2=2048
ticks. Once F1 and WF are0, the h1 Flag2 recurrence is

    (at least4 left-in-colony ones) OR
    (old self1 AND at least2 left-in-colony ones).

Its zero strip advances right by at least two cells each tick. Thus
F2 clears in another2048 ticks and all native flags are0 by99Q.
This argument uses canonical/common-clock geometry and Q even. It is
not a damaged-clock or Gray real-error recovery lemma.

At100Q the actual late reset clears Out/Scratch/Mem/heads, and100Q+1
reloads the retained unanimous History bank while birthing one pc0
packet. Hence the actual bank and execution preparation required by
S1 are derived from the physical history for every d. Late execution
never leaves the new496-word frame. By the holder/opcode induction,
all496 normal Out words are F_2^D(d[g]), complete within104572 updates
and before127Q. Halting/holding preserves them through the boundary.
All logical Out outside that frame remains0 after the global reset;
the proved typed emission addresses store nowhere else.

At U the literal commit consumes **old voted Out before reset**.
Normal Info becomes F_2^D(d), all auxiliary Info becomes0, and all
Mail/History/Mem/Out/Scratch/couriers/heads reset to0. Programme is the
new immutable beta_2 bit; native Age/flags have the encoded boundary
values. This is exactly E_2(F_2^D(d),0) at every site of Z. Each step
uses finite local equations, so no finite-ring or boundary assumption
is involved. This proves S2. Iteration yields ordinary noiseless
self-simulation, with normalization after the first period if d was
initially in D rather than A_2.

## Receipts and remaining proof obligations

[The finite supplement](../../../../figs/gray_counterexamples/unregistered_gawn2/small_probe01.json)
retains416 helper runs and nine paired full496-output/early own-ROM
executions on raw/projected tapes. Besides native padding/quorum/commit,
the latter exercise invalid raw PC4096, JMPR targets4095/4096/8191 and
generic READ5 bit19 retention. These executions are measured
transcription supplements. Universal conclusions come from the
word/contract/physical inductions above.

The initial builder assertion expected three old service masks; literal
inspection found five. Its pre-fix source and failed log are retained.
Only that assertion count changed before emission; no emitted artefact
was replaced. This is a build-check correction, not a CA counterexample.
The first certificate issue also rejected a Python-tuple versus JSON-list
comparison. Its checker source and log are retained; canonical JSON
comparison fixes serialization only, before any certificate was issued.

| Step | Status | Scope |
|---|---|---|
| New finite equations/native widths/12-bit targets/explicit D extension | proved | Isolated new rule, all raw physical SF allowed |
| Native normalization, dead clobbers, helper and relocated compiler premises | proved | All prepared D tapes; prior repository compositional contracts apply |
|104572 full/221 early all-payload deadlines | proved | Fresh72-class contract DAG and actual new listing |
| Complete E_2-to-E_2 infinite-line noiseless period | proved | Canonical, common-clock, coherent, reset lower encoding |
|416 helper/nine paired whole-ROM executions | measured supplements | No universal quantifier inferred from samples |
| Gray/Gács noisy simulation/repair arguments at these constants | unproved | Rest, radius, alphabet, ROM and native departures remain |
| Arbitrary damaged lower encoding, E0/real1/higher closure, positive iid epsilon, memory, minimum fix | unproved | No reliability theorem established |

Read-only reproduction:
`python3 Report/proofs/gray_counterexamples/unregistered_gawn2/check_small_gawn2.py`.
No G17 or earlier frozen rule/ROM is modified; no commit.
