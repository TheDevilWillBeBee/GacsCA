# GAW18: the actual unmasked GAW17 record repairs in the second period

This is a selected continuation of the **unchanged, explicitly modified
GAW2R rule**, not a Gray counterexample and not a universal malformed-record
theorem. Q=8192, U=128Q=1,048,576, lambda=24 and the original error-class
separation c=104 remain unchanged. No new errors, alphabet projection,
commit mask, programme, schedule, or CA transition are introduced.

The starting history is exactly GAW17's `native_program104`: the recursively
intact H, its actual chronological late-execution row, and 104 genuinely
changed cells at each of 104 consecutive rows. Its original-c104 real1
classification, complete 10,816 whole-cell payloads, actual delayed writes
and first-boundary commit are frozen in
[GAW17's proof](../unregistered_gaw17/GAW17_LARGE_REAL1_BURSTS.md) and
[complete receipt](../../../../figs/gray_counterexamples/unregistered_gaw17/native_program104_complete.json).
The last fault is at physical time 839,784. Subsequent events below all come
from that same history, without another replacement or selected future tape.

The frozen GAW17 result deliberately left this case's 2U outcome unproved.
GAW18 supplies a new proof; it does not rewrite the historical null outcome.

## Exact statement

Let R be the frozen GAW2R physical transition with its exact emitted immutable
ROM, and let X_t=R^t(H) be the infinite-line error-free shadow. Let Z be the
actual noisy trajectory of the GAW17 history, with no errors after its last
replacement. Then

**Z_(2U)=X_(2U)=E(R^2(H),0), and Z_t=X_t for every physical time t>=2U.**

Here E is GAW2R's established legal-record encoding relation, used only at
the clean shadow and at the proved final boundary. The actual Z_U is a
legal *lower* CA configuration but is outside E(C,A) for every legal upper
C. We describe it by the raw-word array W below. We never call W a legal
upper configuration or apply the legal-input evaluator theorem to its
malformed neighborhoods.

This theorem is proved by the infinite-line composition below and exact
finite computations of the 17 affected programme executions. Those
computations are certificates of these fixed input words and deadlines;
they are not statistical evidence for a universal quantifier.

## Actual U state, with every word retained

Write P=3848, frame length K_w=496, and S=(0,-2,-1,1,2). The frozen complete
receipt records W(g), all 496 unmasked normal words of each affected upper
receiver. W(g)=words(R(H)(g)) for every g!=0, by the prior actual-boundary and
exterior proof. W(0) differs from that shadow at **every index 1..219**.
Only indices 1..5 violate native field widths; the other 214 differences
are simulation-field words and are also retained. In particular

`W(0)[0..5] = (0, M, M, M, M, M),   M=2^100-1`.

The actual unused Info array is identically zero. Define

`D(gQ+P+i)=W(g)[i]` for 0<=i<496, and D(y)=0 elsewhere.

Z_U has canonical GF=x mod Q, common lower Age=0, native flags and Workspace
flags zero, the actual hardwired Programme copies, all work/reset fields
zero, and Info holder slot s equal to D(x+s). Thus its lower cells are legal:
the illegal native *representation words* live in 100-bit Info, not in the
13/20/1/1/1/1-bit native fields of those lower cells.

The checker confirms `cell_words(cell_from_words(W(g)))==W(g)` before its
diagnostic raw-helper comparisons, including all native padding. This is
a roundtrip of a Python diagnostic record, not an assertion that W(g) is
an element of the legal upper alphabet.

## Lower native and source closure

For canonical raw GF and a common legal lower clock, both adjusted GF
quorums give x mod Q and both Age quorums give the common old clock. This
holds independently of all native flags, old Workspace and SF words.
Consequently computed GF/Age remain canonical/common, and every raw-self
GF wipe is false. The upper representation's M values do not enter these
lower native votes.

Initially all lower F1/F2/WF1/WF2 are zero. Before computed Age 96Q,
Workspace guards are closed. With canonical GF, common Age and zero old
flags/Workspace, the literal native source/propagation/erasure equations
return zero flags. This proves zero native flags inductively throughout
the three gathers and early evaluation.

The early programmes in all 17 affected colonies halt with both flag
courier seed bits zero. Their exact executions are established below.
In every unaffected colony, the input bank is the legal shadow bank; the
accepted legal-input native-prefix equivalence gives the shadow's zero
flag outputs. These uses of the legal theorem exclude every bank
containing W(0).

At 75Q the actual left/right courier equations seed only the corresponding
low bits, hence seed zero globally. They start/reset at zero, and their
route-gated shift/hold equations preserve zero. At computed Age 80Q-1 the
actual old couriers therefore write zero into special Info 3 and Q-3.
Those unused Info values were zero already. During the actual half-open
96Q<=Age<98Q window, final computed-primary Info at those special sites
is zero. Thus actual computed WF1 and WF2 are zero. At and after 98Q the
guards close. Zero native flags now continue through the entire period.

This is a simultaneous induction, not a supplied future WF history:
closed guards prove the pre-96Q premise needed to derive the early zero
outputs; those derived outputs prove the subsequent actual source zeros.
The certified control checks include reset, seed, special write, source
opening and the half-open 98Q closure with all fields compared.

## Actual three gathers and temporal majority

Put s_j=(j-1)32Q. At computed Age s_j the actual Mail reset is zero. At
s_j+1 the literal LOAD votes the five coherent Info holders, returning
D(y) for logical position y, including all 100 bits. While the stage is
active, one actual update shifts left/right Mail by one cell. There is
no Flag1 erasure because the native/source induction gives F1=0.
Hence at current Age a with s_j+1<=a<s_j+16Q, the logical Mail values are

`ML(y)=D(y+a-s_j-1),  MR(y)=D(y-a+s_j+1)`.

They then hold the value reached after 16Q-2 shifts until the next reset.
Every holder follows the same source identity: for x=y-s, computed service
Address `(GF(x)+s) mod Q` is y mod Q. The vote source in `local_R` is the
same logical group y or y±1; it is never a head-center substitute.

Lane d+8 captures at s_j+1 for d=0, and at s_j+2+|d|Q otherwise. The latter
reads *old* Mail after |d|Q shifts. Thus each actual History bank becomes

`B(y) = sum_(d=-8..8) D(y+dQ) * 2^(100(d+8))`.

All three captures finish by 72Q+2. Their resets are the literal staged
History resets, with each new bank initially zero and earlier banks
retained. At 72Q+3 and again at the actual late birth 102Q+1, the bitwise
temporal majority of three equal actual banks is B(y), without truncating
native representation words. Histories remain unchanged thereafter: no
later captures exist, and GF wipes are false.

This algebra proves the gather and majority identities for every y on
the infinite line. The checker additionally evaluates the full literal
local transition for every one of the 3*17*5*5=1,275 malformed native-word
capture/holder cases and all stated reset/source/birth controls. It hashes
each affected 496-word bank. No bank is independently preloaded.

## Actual early and late executions

Only receiver g with -8<=g<=8 has W(0) in its bank. For each such g, start
the head at the *actual* early birth 72Q+4, PC `ROM.early_pc`, or actual late
birth 102Q+1, PC 0. The reset clears Head/Out/Scratch; Mem is the actual
derived B. The lower Programme is the actual hardwirer output. Every
instruction fetch, mutable data read, operand journey, pending move and
store uses the frozen `step_packet` and fixed ROM; no host whole-rule
oracle is an interpreter instruction.

The complete finite executions, for these exact 17 banks, give:

| Pass | Updates after birth | Last computed Age | Available updates | Result |
| --- | ---: | ---: | ---: | --- |
| Early | 150 | 589978 | 24571 | HALT; left/right seeds 0/0 |
| Late | 65062 | 900647 | 147455 | HALT; all 496 output words equal the legal shadow |

Early availability is `75Q-1-(72Q+4)`; late availability is
`120Q-(102Q+1)`. Birth itself consumes a row. Both passes keep the actual
head address in [3848,4343]. All actual writes likewise lie in the normal
frame. The checker iterates every instruction/travel tick and records the
execution digest, final packet, Scratch, full Out and exact typed address
range. It does **not** use the universal malformed-input cost or identity
which J246 disproves.

The physical five-copy lift follows directly from the actual equation.
At a coherent logical group, voting returns its one word for every
holder. `incoming` routes the single head according to its old move, and
`step_packet` gets the identical logical Address, Mem, Out, Scratch,
Programme and clock. A pending move is at most one site. Thus all five
new copies equal the computed logical packet/store; groups not reached
by it retain their coherent values. The entire frame including its five
holders is strictly inside its colony, so another colony's head is never
in a source vote. This conditional one-step identity is independent of
upper native word legality. The selected execution's every-tick address
checks discharge the frame premise, and the native/source proof
discharges the common-clock/no-wipe premise. Therefore induction lifts
the complete finite execution to the physical history. Full `local_R`
cofactors check all five holders at every actual Out store and every
mode/movement combination seen, in addition to birth/control checks.

For |g|>8, its derived bank does not contain W(0). The accepted legal
GAW2R evaluator and deadline apply to that unchanged shadow bank and its
own in-frame head, proving the exterior outputs. This is local programme
input independence, not a finite-ring boundary condition: Mail can carry
differences farther, but the bank's 17 actual capture routes have exactly
the stated sources, and neither the later head nor source couriers read
uncaptured Mail.

For completeness, selected diagnostic raw-helper evaluation also agrees
with the emitted outputs. In the raw extension, the single changed
upper cell still has its correct GF; each Age side has at least four
clean votes, and a single flag/Workspace bit cannot reach any source or
propagation quorum. The h1 Flag2 erasure clears the possible isolated old
F2. Thus computed GF/Age are canonical/2 and all computed flags zero.
R(H)'s SF groups are coherent, as follows from the initial LOAD equation;
one arbitrary holder is absorbed by the other four. All SF votes needed
for this step therefore equal shadow votes, and the selected raw-helper
successor equals R²(H). The checker compares all 496 outputs and checks
the actual raw SF votes. This comparison is specific to W and does not
assert a native-padding quotient or any all-malformed compiler theorem.

## Full raw second boundary and future equality

After HALT, Out is unchanged through the active cutoff 120Q and rest.
At computed Age 0 (physical time 2U), the actual transition takes *old*
Out into Info before clearing work. All affected Out words have been
checked against words(R²(H)(g)). Every outside-frame Out is zero: it was
reset, and no actual or exterior typed programme target writes there.
Thus unused Info is zero too. The same boundary resets every History,
Mem, Head, Out, Scratch, Mail and courier, restores Programme bits and
keeps canonical native GF/Age/flags. This proves literal raw equality
with E(R²(H),0), not merely a majority decoder or native projection.
Full `local_R` boundary checks cover all normal frame holders and the
special/colony-edge cones of each affected colony. The algebra above
covers the infinite exterior. The shadow's legal period theorem gives
X_(2U)=E(R²(H),0). Determinism and the absence of later errors then give
Z_t=X_t for every t>=2U, without another legal-period inference on W.

## Status and limits

- **Proved for this exact history:** actual unmasked U starting state;
  three gathers/temporal vote; actual early resets/execution/zero couriers;
  native and Workspace zero closure; actual late reset/birth/execution;
  complete legal 2U encoding and full raw shadow equality thereafter.
- **Exact finite computations:** all 17 affected early/late executions,
  raw-helper/shadow comparison, physical copy/control/commit cofactors.
  The accompanying induction supplies their infinite-line scope.
- **Unproved here:** arbitrary malformed records, all real1 bursts,
  general higher-error confinement, a positive iid rate or remembered bit.
- **Gray faithfulness remains unproved.** This rule changes radius to 8,
  uses 17 lanes, WORD100/FULLCOL, h1 Flag2 erasure, holder-computed control,
  immutable instruction dictionary, native-only early pass, route-gated
  couriers and a 102Q late reset/birth. Its direct emitted beta is 41,162
  bits with 1,049 distinct dictionary words; counted immutable storage is
  270,349 bits and raw cell size 49,037 bits. It is not a Q-bit Gray
  programme/layout. No shorter U or new candidate is supplied.

Root's [padding obstruction](../unregistered_gaw_padding_quotient/PADDING_QUOTIENT_OBSTRUCTION.md)
remains valid. GAW18 neither projects W nor generalizes these particular
65062-tick executions to its no-quorum fallback counterexample.

The final read-only command is
`python3 Report/proofs/gray_counterexamples/unregistered_gaw18/validate_gaw18_malformed_period.py`.
The manifest pins all 472 accepted ancestor assets and every new proof,
checker and receipt. Initial discovery/preliminary physical receipts are
retained separately; the final `02` receipts add bank hashes and the exact
219-word raw comparison without changing any execution or rule.
