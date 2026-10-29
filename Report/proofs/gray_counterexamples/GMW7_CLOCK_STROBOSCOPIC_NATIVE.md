# Sixteen actual gathered native steps on the intact GMW7 clock island

This is a theorem about the **explicitly changed, fixed-Workspace-zero GMW7
rule**, at Q=8192, U=128Q=1048576, lambda=24 and c=104. It does not reconstruct
Gray's three gathers, Mailbox erasure or simulated-flag repair. It introduces
no new rule, programme, schedule or error. In particular its displaced-word
phenomenon must not be attributed to Gray's actual gathering protocol.

Sources: [frozen rule](gray_token_gather_v7.py),
[frozen own-programme emitter](build_gray_token_gather_v7.py),
[accepted period contracts](GMW7_SINGLE_GATHER_PERIOD.md),
[actual first-bank proof](GMW7_CLOCK_GATHER_BANK.md),
[root intact initializer](../GMW7_INTACT_HIERARCHY.md),
[native stationary orbit](GMW7_WF0_CLOCK_ISLAND.md),
[new checker](check_gray_clock_stroboscopic_native.py),
[new read-only validator](validate_gray_clock_stroboscopic_native.py).
The [receipt](../../../figs/gray_counterexamples/GMW7_clock_stroboscopic_native_certificate.json)
contains exact native rows, finite coupling boundaries, full-word signatures
and supplementary actual emitted-programme comparisons.

## Statement and shared history

Let X be the pinned, infinite, recursively intact initializer in the root
proof. At physical input row0 overwrite only Age, setting it to1 on
[0,17Q), and make no subsequent errors. All other fields are those of X.
This is the same one actual original real2 history certified in the
stationary-clock proof; no separate upper history or prepared bank is chosen.
Let Z_t be the subsequent noiseless F7 trajectory and let e(x) indicate
[0,17Q). Its native projection is already proved to be

    GF(x,t)=x modQ, Age(x,t)=(t+e(x)) modU,
    Flag1(x,t)=1 on [-h_t,0) union [17Q-h_t,17Q), h_t=min(3t,Q),
    Flag2=Workspace.Flag1=Workspace.Flag2=0.

For each n=0..16, the actual five-holder voted Info words at the191 normal
primaries of lower colony g, in physical row nU, form a legal upper cell
C_n(g). They satisfy the explicit distorted-bank recurrence below, with
C_0(g)=X(g). There is no preloaded input hypothesis.

All C_n have canonical GF, and for n>=1 their Ages are between1 and n.
Their Head, Mem, Out and Scratch fields are zero; their Info remains legal
but need not equal X's Info. Their Programme fields are the printed beta
bits at the corresponding service Addresses. The first departure from a
common upper Age n is at **n=5, g=2**, where the actual represented Age is2.
For all n=1..16 and all g=0..16, C_n(g).Flag2=0. These are finite-time
facts about the actual decoded GMW7 trajectory, not a claim that an authentic
Gray repair command can never be generated.

## The exact distorted-bank map

Write e_g=1 for0<=g<17, and let W_n(g)=cell_words(C_n(g)), indexed0..190.
Extend this word list by W_n(g)[-1]=W_n(g)[191]=0. For the input with colony
offset j=-5..5 put

    sigma(g,j)=sign(j)*(e_(g+j)-e_g),
    T_(n,g,j)[w]=W_n(g+j)[w+sigma(g,j)], 0<=w<=190.

Thus a crossed input is the real source word list shifted by exactly one
physical primary, in either direction. Normalize only the raw native flag
words2..5 to their low bits. The raw GF and Age words have legal widths on
this trajectory. Call the resulting legal cell R_(n,g,j). Then

    C_(n+1)(g)=F7(R_(n,g,-5),...,R_(n,g,5)).                 (1)

F7 on the right is the actual pinned scalar local rule, with its actual
immutable beta/dictionary. It is not an intrinsic added to that rule.
The checker evaluates (1) as a finite coupling certificate; the following
arguments lift it to the physical trajectory.

## Every SF field follows its logical centre clock

For any raw physical SF row define B_f(y) to be the vote of field f in
holders y-s, slot s, for s in S=(0,-2,-1,1,2). Raw copies need not agree.
With the native orbit above the mandatory SF wipe is false: calculated GF
equals raw holder GF at every site. Holder x producing its slot s for
logical y=x+s uses service Address `(calculatedGF(x)+s)modQ=y modQ`.
Every old logical source used in that slot is the same B_f(z), independently
of the holder. Its only remaining holder-dependent input is calculated Age
`(t+1+e(x))modU`.

Consequently, for each field, the five new slot values take at most two
values, the outputs of the same logical operation at these two Ages. At
least three of the five holders y-s have e(y-s)=e(y), because the binary
label is a single interval of width17Q and the holders lie within two sites.
Their identical output has the Age of logical centre y. Its bitwise vote
is exactly that output. This proves the centre-clock factor simultaneously
for packed Head, all eleven Mem lanes, Out, Info, Scratch and Programme,
including every reset, birth, execution, transport and commit branch.
It does not assume coherent raw copies at the two clock interfaces.
The checker uses actual five-holder F7 transitions with independently
chosen raw SF words at all phase boundaries as supplementary cofactors.

## Actual inputs, head execution and asynchronous commits

Suppose the normal primaries at row nU hold W_n, and the two adjacent
padding primaries4000 and4192 hold0. Logical Info is held until the next
Age0 commit. Inside colonies that commit is at row(n+1)U-1; outside it is
at row(n+1)U. Thus Info is stable throughout the next32Q..37Q gather,
even where raw copies span a clock interface.

The accepted first-bank backwards-path proof depends only on this stable
Info and the static e labels, not on its initial values. Its load and
transport recurrence therefore applies at every following period. For
normal primary p=4001+w it captures

    Info((g+j)Q+p+sign(j)*(e_(g+j)-e_g)),

which is T_(n,g,j)[w]. Each normal primary and its five holders lies strictly
inside its lower colony. Those holders have the same clock, so their input
Mem bank is coherent by capture, and remains held through execution.
All lanes are ready before37Q in their own colony clock.

The universal prepared interpreter contracts then apply in each colony:
reset at112Q clears Head/Out/Scratch; birth at112Q+1 makes one actual head
at4001; every instruction, operand and Out store stays within4001..4191;
the complete execution takes at most49068 updates, less than65535.
All these controls use that colony's own calculated clock. Different
colony clocks shift this entire execution by one physical tick and do not
mix head executions: the distance between frames is8001 sites and heads
never leave their frame. Previous halted heads are removed by that same
local reset. No exterior head exists initially or can be born except at
the true frame entry.

The previous all-raw own-beta theorem concerns legal upper cells. A
displaced native flag word may instead contain an old Age or GF word.
The following input-normalization observation supplies the missing step.
The emitted native prefix reads raw words0/1 with LDX/READ5 and raw words2..5
only through READMASK, which extracts the low bit in each lane. The main
wipe test reads *computed Out* words0/2 and raw GF word0; every SF vote
reads raw rows6 or later. The simulated packet's Mem reads likewise vote
the raw rows for its Mem fields, rather than accessing raw native rows.
The printed programme and instruction-ROM lookup read no input flag word.
Thus replacing raw flag words2..5 by their low bits leaves every instruction
result, branch, store and execution time unchanged. Raw GF/age words remain
legal here. The accepted legal-cell own-beta equivalence therefore gives
the full F7 output of R, also for the actual displaced tape. The bound used
arbitrary readonly words and still applies. This is a source/register
argument about this emitter, supplemented by paired raw/normalized physical
instruction executions; it is not a new field-width convention in F7.

At commit each colony consumes old Out before reset. By row(n+1)U all
normal primaries have committed C_(n+1), in both clock phases. Reset made
Out0 everywhere outside the frame, and the emitted programme writes Out
only at frame primaries. Therefore both padding primaries4000/4192 commit0
and remain0. They are also0 in X. This proves the padding induction and
closes the actual bank/execute/commit recurrence (1).

## Quiet upper-private family and exact infinite-line coupling

Initially upper Head, Mem, Out and Scratch are0. In any shifted input,
the three middle copy slots of every such field still read a word of
the same zero field. Boundary slots may spill from a neighbouring field:
Out can receive Info and Scratch can receive Info or Programme. There
are at least three zero copies, so every voted Head/Mem/Out/Scratch value
remains0. The first Head word can additionally receive native Workspace2
at its left boundary, which is0. No computed upper Age in the finite
certificate reaches a gather, reset, birth, execution or commit stage;
they lie between1 and16. The output GF is canonical, matching the unshifted
self raw GF, so the upper wipe is also false. Consequently the quiet
private family closes while Info may evolve by its actual votes and
Programme is printed. This justifies the zero Head word at the upper end
of the shifted native record and the continuing full-word legal map.

The checker retains16 exact applications of the **full actual F7** map (1)
on g=-128..144. Outside a shifted-source or previous-disagreement cone,
the map is the clean F7 map of X at upper time n: canonical GF, Age n,
zero native flags, zero private fields, held initial Info, and printed
Programme after the first step. The shift differs from0 only within five
colonies of the two lower clock boundaries. Each application has radius5
in g. Therefore all disagreement through16 steps is strictly inside
[-85,102], whose complete five-neighbour inputs lie inside the retained
frame. Clean exterior checks and explicit dependency margins certify the
infinite-line extension. No periodic ring, independently chosen boundary
payload, or finite-truncation hypothesis is used.

Every retained word and each raw/normalized input is pinned by signatures;
the receipt also records all native rows. Together with the algebraic
factor, physical gather and own-beta contracts above, these exact finite
full-rule identities prove the stated physical stroboscopic facts. They
are not an empirical claim about an unbounded future native map.

## Why the common-Age premise fails

At the fifth evaluation, receiver g=2 has the following native inputs.
Its offsets j=-5,-4,-3 cross the left clock interface. Their source words
are shifted forward, so their Age input is the previous Flag1, namely1.
The other left offsets -2,-1 and self have Age4. Its right Flag1 inputs
at offsets3,4,5 are1, so the computed native Flag1 is1. Computed Flag2 is0
and the native left majority Age is1. The native equations therefore take
that left Age and produce **2**, instead of the clean fifth Age5. GF stays2.
The receipt contains the exact raw source records and actual local output.

The four-null first Address bank in the accepted command contract is real,
but it does not provide sixteen successive common upper Age increments in
this single-gather history. Right-edge Ages at g13,14,15,16 are common n
through n=9; at n=10 they are(6,6,10,10), and from n=11..16 they are
(6,6,7,7). In all sixteen evaluations the Flag2 columns inside0..16 are
empty. This disproves that proposed *common-Age continuation premise* for
the actual changed GMW7 trajectory; it is not a contradiction to a
published Gray lemma or a proof that an authentic repair architecture fails.

## Status

| Step | Status |
| --- | --- |
| Intact recursive start and one shared original real2 history | **previously proved; reused unchanged** |
| Native stationary orbit | **previously proved; reused unchanged** |
| All-SF logical centre-clock factor | **proved by identical-candidate majority** |
| Repeated actual capture, padding and asynchronous commit induction | **proved for this history and F7** |
| Raw native-flag low-bit invariance of emitted programme | **proved source/register contract; comparisons supplementary** |
| Sixteen full actual upper maps and infinite-line coupling | **proved exact finite certificate plus dependency margins** |
| Fifth evaluation Age2 at g2 and sixteen inside Flag2-zero rows | **proved changed-rule finite decoded facts** |
| General all-time distorted-map recovery or absence of future flags | **unproved** |
| Authentic Gray gathering/early-command/repair refinement | **unproved; material departures remain** |
| iid unreliability, bit-memory failure or G17 failure | **unproved; not claimed** |

The separate dictionary still has51200 immutable bits in addition to the
8192-bit token beta. No faster U or global sufficient repair is inferred.

The first supplementary instrumentation run treated a physical STX store
at a native flag output primary as though it were a raw flag input read,
and failed that extra trace assertion. The exact initial checker and log
are retained and pinned by the receipt. Distinguishing descriptor kind1
stores from kind0/3 reads corrects the instrumentation; no rule, map,
source-read contract or physical lift premise changed.
