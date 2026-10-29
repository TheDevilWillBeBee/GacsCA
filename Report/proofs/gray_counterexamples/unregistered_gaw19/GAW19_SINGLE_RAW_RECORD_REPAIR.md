# GAW19: one arbitrary raw record at the first intact boundary repairs

This is a universal **prepared-boundary theorem for unchanged GAW2R**, with
one separately realized real2 member. It is neither a Gray counterexample
nor a general malformed-input compiler refinement. Q=8192,
U=128Q=1,048,576, lambda=24 and c=104 are unchanged. No transition,
alphabet, schedule, ROM, native mask, or encoding projection is added.

The frozen [GAW18 continuation](../unregistered_gaw18/GAW18_MALFORMED_SECOND_PERIOD.md)
repairs one particular 219-word discrepancy. GAW19 now quantifies every bit
of an entire 496-word replacement. Root's
[padding counterexamples](../unregistered_gaw_padding_quotient/PADDING_QUOTIENT_OBSTRUCTION.md)
remain valid: their no-quorum input is excluded here by four clean native
votes, and their Flag1 wipe input is excluded by the derived zero Flag1.

## Exact theorem and quantifiers

Let R be the frozen GAW2R transition with its emitted immutable ROM. Let H
be GAW4's explicit recursively intact reset initializer, and put C=R(H).
Write P=3848, K_w=496, M=2^100-1, S=(0,-2,-1,1,2). For **every** vector

`w in {0,...,M}^496`,

define W(0)=w and W(g)=words(C(g)) for g!=0. This includes arbitrary native
GF/Age/flag padding and every incoherent packet, Mem, Out, Programme,
Mailbox and History word. Define a raw data array

`D(gQ+P+i)=W(g)[i]` (0<=i<496), and D(y)=0 elsewhere.

Define Z_0 as a **legal lower configuration**: canonical lower GF=x modQ,
common lower Age0, F1/F2/Workspace0, all work/reset fields0, hardwired
Programme copies beta((x+s)modQ), and Info slot s equal to D(x+s). Its
malformed represented native words live in legal lower Word100 Info.
There is no assertion that W(0) belongs to the legal upper alphabet.

Then, without any subsequent errors,

**R^U(Z_0)=E(R(C),0)=E(R²(H),0).**

Every normal record at the final boundary is legal; every unused Info
value is0; native, work, Mail, History and courier fields have their
literal reset values. The equality is of the entire raw lower
configuration on the infinite line, not of a projected decoder alone.
Hence if Z_0 is placed at physical time U of the intact shadow, then its
trajectory equals the shadow at2U and at every later time.

The background is **exactly C=R(H)**. No quantifier over later shadow
phases, arbitrary canonical upper backgrounds, multiple bad records, or
all real1/real2 histories is established. A raw GF/Age word in w may use
every one of its100 bits; no legality or coherence premise restricts w.
Lower execution coherence and reset values are separate hypotheses.

## Sound universal execution certificate

[gaw19_symbolic_executor.py](gaw19_symbolic_executor.py) executes the actual
decoded beta with a bit-cube abstract domain. A cube (v,u), with v&u=0,
contains exactly the100-bit words x satisfying `(x&~u)==v`. A known word
has u=0; TOP=(0,M). Every input access to any word of W(0) returns TOP.
Every other input access returns its exact word of C. Thus this initial
abstraction contains all2^49,600 choices of w. Repeated reads are allowed
to be independent in the abstraction, which only enlarges the family.

The following elementary facts prove the abstract ALU soundness for all
100-bit inputs, independently of the finite audit examples.

- AND and OR use the pointwise minimum/maximum possible bit. XOR marks a
  bit unknown if either operand has that bit unknown. BITNOT complements
  known bits and preserves unknown bits. MOV copies its cube.
- Logical NOT distinguishes an identically0 cube, a cube with a known1,
  and the remaining case. EQ is false if a fixed bit differs; otherwise
  it returns its exact constant result or {0,1}. NE negates that result.
  LT is true if max(a)<min(b), false if min(a)>=max(b), and otherwise is
  {0,1}. These implications use unsigned Word100 order exactly.
- With all **used** operands constant, the operation delegates to the
  frozen generic_alu. The third operand is unused except by WINDOW,
  VADDINDEX and VINSIDE. Arithmetic whose inputs remain unknown returns
  TOP, so modular carries/subtraction cannot cause an unsound guess.
  This also covers MADD5 and unsupported varying shifts.
- Known shifts move the known/unknown bit masks and truncate to100 bits;
  signed SHIFT uses the frozen20/100-bit convention. BIT extracts a known
  position, returns0 when every position is>=100, or {0,1}. RSHIFT has its
  literal unsigned convention. SIGNEXT masks to the stated width and
  extends the known/unknown sign bit. Other unresolved width cases are
  TOP. All out-of-range constants use the literal total ALU semantics.
- POPCOUNT lies between popcount(v) and popcount(v|u). WINDOW sums the
  selected11 bits with its actual in-colony/enable guards. The smallest
  cube containing the resulting integer interval fixes its common high
  prefix and leaves lower bits unknown; it contains every such count.
- VMAJ/VEXISTS inspect five20-bit components. If three components are
  the same known value, they force the unique quorum whatever the other
  two components do. If all components are known, the literal fallback
  is used. Otherwise TOP/{0,1} is safe. In every native quorum reached
  here, at least four components are known and agree.
- VADDINDEX masks each component **after** adding its stated multiple of
  the constant step. A known component is evaluated exactly; an unknown
  one returns all possibilities in the masked width. The higher packed
  components do not affect these low<=20 bits. VNE uses sound component
  EQ results. VINSIDE is exact whenever its used operands are known and
  otherwise TOP. Invalid operation numbers return TOP or their exact
  literal sentinel, as applicable.

For each instruction, the machine follows the frozen step_packet
equation: immutable fetch/decode, register write, pending SEEK travel,
LDX/STX, READ5's low20-bit packing, READMASK/FULLCOL's bit0 extraction,
CODE/BITCODE and JMPR all have their literal meaning. No whole-rule or
host evaluator is an instruction. Every instruction, dynamic ALU number,
PC, travel target and lane used as a control is proved constant by the
checker; unresolved control fails the proof instead of choosing a value.

At BNZ, an identically0 or definitely nonzero condition chooses its exact
edge; an unresolved condition forks **both** edges without narrowing its
cube. This preserves every concrete trajectory. Each branch has its own
registers, Out and Scratch. Identical abstract machines can be merged
because their represented state sets are identical. Out/Scratch reads
use the current branch's last abstract store, with initial0. Movement is
at most one site per update and every address/target is proved in
[3848,4343]. HALT branches retain their state while other branches run.

Induction on actual instruction/travel ticks now proves that each
concrete emitted execution belongs to some retained abstract machine at
every tick. At termination every retained machine HALTs; every one of
its496 Out words is a known constant; all branches have the same result.
The checker compares that entire result against words(R²(H)(g)). This is
a universal emitted identity/deadline certificate, not a sample over w.

The result for **every** affected receiver -8<=g<=8 is:

| Pass | Universal maximum updates after birth | Available updates | Proven result |
| --- | ---: | ---: | --- |
| Early native-only | 150 | 24571 | HALT; F1/F2 courier seeds0/0 |
| Late full | 65062 | 147455 | HALT; all496 words equal R²(H)(g) |

For g=0 alone, the possible old F2 bit forks the early pc3702 and late
pc108 branch. There are at most two abstract machines, which merge back
to one; both branches take the same final deadline. Every other control
is resolved. Lower Programme and packet controls are initialized from
the fixed own code; arbitrary *simulated* Programme/head words are data
in the bank and are never substituted for those physical controls.

The [symbolic receipt](../../../../figs/gray_counterexamples/unregistered_gaw19/GAW19_symbolic_execution_certificate.json)
pins every instruction-family count, abstract trace digest, output word,
address bound and unresolved branch. Exact small-cube, full-width quorum
and adjusted-GF tests in the physical checker supplement the mathematical
soundness proof; those tests alone do not establish the100-bit quantifier.

## Why a single malformed native record is absorbed

This also explains why the prepared family differs from J246's witness.
In the simulated native neighborhood, each adjusted five-word GF side
and each five-word Age side has at least four clean canonical/common
words. READ5's existing low20-bit packing and VADDINDEX's existing low13
mask act on their literal raw inputs; a corrupted100-bit word contributes
at most one arbitrary component. The correct GF and old Age1 quorum
therefore wins on both sides, giving computed GF=g modQ and Age2.

One raw flag/Workspace bit cannot reach a source or propagation quorum.
Each left mismatch count is<=1. New F1 is0. The h1 erasure removes a
possible isolated old F2; hence new F2 is0. Workspace guards at computed
Age2 are closed. **These are derived native outputs**, not assumptions
about the malformed record. The raw-self-GF wipe is multiplied by new
F1=0, so it is false even if the raw GF word has arbitrary padding.

C's five SF holders are coherent: H begins coherent and its first update
votes them, performs its Age1 LOAD and hardwirer with a common native
clock, and returns the same value to all holders. One arbitrary record
can replace at most one holder in any group. Its four other clean
holders fix the majority to the shadow word, including every Mem/Head
bit. The symbolic execution verifies the actual emitted handling of
this geometry, rather than assuming a universal raw native quotient.
The proof does not need to define R on an illegal upper record.

## Physical period: no preloaded bank or prescribed command history

All following identities apply to every D defined in the theorem.
They are derived from the frozen local_transition equations; the
[physical receipt](../../../../figs/gray_counterexamples/unregistered_gaw19/GAW19_prepared_period_certificate.json)
also checks the full transition on an all-M member, including the
nonboolean Programme, Head, Mail and all three History representations.

Canonical **lower** raw GF and common legal Age force both native
GF/Age quorums independently of all SF words. Thus lower computed
GF/Age remain canonical/common and every raw-self-GF wipe is false.
Initially lower flags/Workspace are0. Before96Q the Workspace guards
are closed, and the literal native equations preserve zero flags by
induction. This establishes the clean-control premise for all gathers
and the early evaluator without assuming its future flags.

For s_j=(j-1)32Q, Mail is reset at s_j, LOAD at s_j+1 votes exactly D(y),
and each subsequent active update shifts one site. There is no Flag1
erasure because F1=0 has just been proved. The resulting logical values
are `ML(y)=D(y+a-s_j-1)` and `MR(y)=D(y-a+s_j+1)` until the16Q cutoff,
then hold until the next reset. For holder x=y-s, its actual service
Address `(computed GF(x)+s)modQ` is ymodQ; the routing reads the actual
five holders of y or y±1.

Lane d+8 captures at s_j+1 if d=0, and at s_j+2+|d|Q otherwise, reading
old Mail after exactly |d|Q shifts. Thus the three derived banks are

`B(y)=sum_(d=-8..8) D(y+dQ) * 2^(100(d+8))`.

The literal staged resets clear each bank before its captures and keep
the earlier ones. Every bank finishes by72Q+2. Their temporal bitwise
majority at72Q+3 and102Q+1 is the same B(y), for all100 input bits.
No upper word is projected. Histories have no further captures and no
native wipe, so remain B. Mail/Mem reset at96Q as specified; late birth
reloads the retained majority, not the reset Mail.

Early reset clears Out/Scratch/Head, and early birth at72Q+4 creates one
coherent five-copy head per colony with the actual early_pc. For -8..8
its B is exactly the symbolic input bank just proved. For every exterior
colony, B excludes W(0), and the frozen legal-input theorem applies only
to that unaffected shadow bank. All early seeds are consequently0.

The actual75Q seed equations, route-gated couriers and80Q-1 special Info
write now give0 at sites3 andQ-3 globally. The initial unused special
Info was0. During96Q<=Age<98Q, final computed-primary Info there is0;
hence actual WF1/WF2 are0. At98Q the half-open source window closes.
This closes the simultaneous zero-native/zero-command induction through
the whole period: closed guards derived the early execution premise,
and actual derived early outputs derived the later source premise.
No independently chosen future Workspace history appears.

At102Q the literal reset again clears Head/Out/Scratch; at102Q+1 the
actual birth creates PC0 with the actual temporal-majority Mem. For
every coherent logical group, all five lower holder votes return its
one packet/data word. incoming routes the unique head using its old
one-site pending move, and step_packet sees the same logical Address,
Mem, Out, Scratch, Programme and clock at all five holders. Therefore
its computed packet/store is copied identically to them. A group not
reached by the head keeps its coherent word. This is a direct one-step
identity in local_R for arbitrary coherent word values, independent of
represented upper-native legality. Induction gives the complete physical
execution from the abstract certificate. All addresses and targets are
inside [3848,4343], and their holders are strictly inside their colony;
heads from neighboring colonies cannot interact with this execution.

Only receivers -8..8 have the malformed record in B. This is the exact
17-source bank identity, not a finite ring boundary condition. Uncaptured
Mail differences may travel farther, but the later heads/couriers read
the banks and their own in-frame outputs. Exterior banks use the legal
shadow evaluator. Thus every physical colony's late output is its clean
R²(H) record and no outside-frame Out target was written.

HALT precedes120Q; Out then holds until the boundary. The actual Age0
transition commits **old** Out into Info before resetting all work.
Every normal primary gets the proved clean word, every unused primary
gets0, and all five Info copies agree. The same transition resets Mail,
History, Mem, Head, Out, Scratch and couriers; it preserves canonical
native/reset values and restores Programme. This proves the stated full
raw equality with E(R²(H),0), including infinite exterior. Determinism
then supplies all later equality without evaluating an illegal upper
configuration.

## One actual intact-start member and original classification

The all-M member w=(M,...,M) is physically realized as follows. Start in
the same recursively intact H, run the actual clean prefix toU, and
at rowU replace each whole lower cell x in [P-2,P+498) by the same actual
cell with Info slot s set to D(x+s). All other fields are retained.
There are **500 genuinely changed replacements**; their complete496-word
payloads are recorded in the physical receipt. This creates precisely
the theorem's Z_0. No further errors occur, so complete2U and all-later
shadow equality follows.

The shared error support E is a dense500-site row. It has no actual E0
points, and no proper subset can be an isolated actual real1: a spatial
edge of any nonempty proper subset links it to E\S at distance1. The
whole E fails real1 condition(iii), since it contains two candidate1
adjacent pairs separated by at least104. These pairs are **candidate1
subsets relative to the shared E**, not actual isolated real1 errors.
Their original24Q/24U linkage gives candidate2 condition(ii). E fits a
Q² byU² box, and its entire diameter (499,0) is smaller than the original
(104Q,104U), ruling out separated candidate2 subsets. Isolation from
other errors is vacuous. Thus E is one actual original-c104 **real2**.

This example neither makes every arbitrary w realizable by one real1,
nor proves a general real2 error-map theorem. The prepared theorem is
independent of error classification. Its exact first-boundary scope is
material; later common clock phases and arbitrary clean backgrounds
would require a new emitted identity/deadline proof.

## Status, retained failures and limitations

- **Proved:** universal emitted early/late outputs and deadlines for all
  49,600 bits; actual global three gathers, temporal majority, zero
  commands/native closure, copy lift, complete boundary and later
  equality for the prepared family at E(R(H),0).
- **Proved separate actual instance:** the all-M500-site row is one
  original-c104 real2 from intact H and repairs fully at2U.
- **Finite replay checks:** abstract execution, small cube/quorum tests,
  concrete all-M copy/control/source/commit ports and full payloads.
  The written abstraction/factor proofs establish their universal and
  infinite-line interpretation.
- **Unproved:** arbitrary other shadow phases/backgrounds, general
  original-real1/real2/higher repair, positive iid rate and bit memory.
  No failed operational relation or faithful Gray refutation is found.

Initial proof-checker failure01 treated an unused third ALU operand as
unknown control data, losing precision at an LDX lane. Failure02 called
the candidate1 pairs actual errors relative to themselves rather than
candidates relative to the shared500-site history. Both source versions
and failed logs are retained. The corrections change only proof-checker
contracts/classification wording, not the frozen CA or emitted ROM.

Gray faithfulness remains unproved. GAW2R changes radius to8, uses17 lanes,
WORD100/FULLCOL, h1 Flag2 erasure, holder-computed controls, an immutable
dictionary, native-only early pass, route-gated couriers and102Q late
reset/birth. Its direct beta is41,162 bits with1,049 dictionary entries;
total counted immutable storage is270,349 bits and cell size49,037 bits.
It is not Gray's Q-bit ProgrammeBits layout. No shorter U is inferred.

The standalone read-only command is
`python3 Report/proofs/gray_counterexamples/unregistered_gaw19/validate_gaw19_single_record.py`.
The new manifest pins the entire frozen GAW18 ancestry, frozen main
document hashes, new sources/receipts and retained failures.
