# GAW17: original-c104 large bursts and an illegal U encoding

Five actual intact-start histories in frozen GAW2R exercise four dense
104-site ×104-row bursts and one sparse support of spatial span150.
All five are single original-c104 real1 errors. Four give legal normal
U records, at most an adjacent pair of damaged upper records, and
complete raw recovery at2U. The fifth produces five illegal native
words at U. It excludes literal E(C',A') for every **legal** upper C',
but its second-boundary behavior is unproved here. It is not an observed
failure to recover at2U.

No Gray/Gács counterexample, general real1 repair theorem, iid result or
shorter period follows. The full chronological replacements, source
commands, unmasked U records, withheld theorem and a serialization
failure are retained. No rule is changed.

## Rule, intact row and exact tested property

The rule is the same [GAW2R](../unregistered_gaw2/gray_three_gather_gaw2r.py)
as [GAW16](../unregistered_gaw16/GAW16_WORD_PROGRAMME_BURSTS.md):
Q8192, U128Q=1048576, lambda24 and original separation c104. Its changes
from literal Gray remain h1 erasure, radius8/17 gather lanes/FULLCOL,
WORD100, holder-computed service GF, native-only early pass, bounded
word couriers, immutable dictionary and 102Q late reset. Storage remains
41162 direct beta bits,1049 dictionary entries,270349 immutable bits,
49037 raw-cell bits. Beta<=Q/dictionary512 and Gray bit-layout/refinement
are absent. GAW0–16, registered documents and G17 are unchanged.

Use the actual recursive [GAW4 H](../unregistered_gaw4/GAW4_INTACT_REAL1_MAIL.md),
H=E(H,0) at every level, with its fixed actual Programme choices. The
fault starts at the certified chronological row

    P=3848, S=(0,-2,-1,1,2), T=102Q+1+4096=839681.

The own programme has really executed4096 late ticks. The six-frame
actual Head/Out/Scratch state and each coherent seventeen-input
Mem/History bank are the inherited chronological trace, not prepared
tapes. GF is canonical, Age=T, all native flags0; Info and Programme are
the actual H-derived data. The 3024 last-update and2976 retained-bank
checks and their all-row composition are inherited unchanged.

The challenged boundary extension, **not an accepted real1 theorem**, is:

    For every original real1 history from H, the actual U boundary
    belongs to E(C',A') for some legal upper configuration C'.

Here E is exactly the frozen reset encoding: each496-word normal frame
is the representation of a cell with native widths13/20/1/1/1/1, and
unrepresented Info is arbitrary A'. Native_program104 disproves this
extension. It does not disprove the accepted noiseless or pure-E0
theorems, or an operational relation allowing a damaged untyped colony
before later normalization. No such broader relation or later repair
is silently assumed for that case.

## Original error classes, including sparse span150

Each dense history replaces [b,b+104) at rows T,...,T+103:10816 actual
whole-cell errors. Its extent is(104,104), so any two nonempty subsets
are c104-linked: all coordinate differences are at most103. This is
condition(iii), for candidate level1 subsets as Gray prints it. There
are linked disjoint candidate0 singletons; each candidate0 has another
point within(24,24), so actual E0 is empty. Condition(i) holds inside
Q×U; condition(iv) has empty complement. The exact original classifier
returns level0=0, candidate/actual level1=true,sep104,method window.

The sparse history has the same104×104 core plus (b−23,T) and(b+126,T)
only at the first row:10818 points, extent(150,104). Each endpoint is
24-linked to multiple core points, so is not E0. The two endpoints
cannot by themselves form a candidate1: they are149 sites apart.
Every minimal candidate1 therefore contains a core point; any two are
c104-linked through their core points. Hence(iii) holds, and isolation
is again automatic. The classifier independently returns real1 by
`window and outside pairs`. This is a sparse span150 witness, not an
assumption that a dense150-column burst is real1.

The separately classified **dense150×104** support is rejected. Its
receipt retains separated candidate pairs

    {(0,T),(14,T)}, {(128,T+32),(149,T+19)}.

Each pair is24-linked internally, but every cross spatial separation
is at least114>=104. This is a condition(iii) witness. That rejected
support was not run as a real1 experiment.

Every executed replacement genuinely changes its cell: its five old
Programme words are boolean, while every replacement Programme word
is greater than1. This is checked before each error is installed, not
inferred from a planned support. All54082 chronological old/replacement
496-word records are retained. Each case has one shared history and
no earlier or later errors.

## Replacement recipes and actual commands

Let t=0,...,103 and y=x+S[h]. Except as stated, fields are retained from
the **actual current row**. Set Scratch=M=2^100−1 in every case. Native
GF is modulo Q and raw Age remains in the legal20-bit range.

| case | b | GF shift | raw Age | raw flag word | Programme / Info / Out |
|---|---:|---|---|---|---|
| native_program104 | P−2 |0 |T+t |0 | M / retained /0 |
| cycle_control104 | P−52 |+1 if x+t even,−1 otherwise |cycles U−1,72Q+1,72Q+2,102Q+1 |(x+t)&15 |2^99+1 / M / M |
| source_flags104 | Q−52 |+1 first52,−1 last52 |96Q+t |15 |M / M / M |
| interacting104 | Q−52 |+1 first52,Q/2−1 last52 |T+t first52,T+t+4Q last52 |0 |2^99+0x15555 / retained /1 |
| sparse_span150 | Q−52, plus stated endpoints |same wide fork |96Q+t left,102Q+t+1 right |0 |M / M / M |

Flag word bits are native F1,F2,WF1,WF2. Current-row raw WF overwrite
is part of that listed physical error, not a future controller. The
native batch subsequently consumes it and recomputes commands from
actual computed-primary Info on its actual guards.

Native_program104 retains all bank fields. Its forged packet is p1,
SEEK,pc3566,target y modQ, descriptor reading mutable Programme into
register0, register11=(y modQ−P) mod496, other registers0. Instruction3566
is actual immutable STX(register0,P,register11,Out), followed by the
compiled increment/bound/branch loop. No opcode, instruction or host
evaluation is supplied after the burst.

The other cases use p1/RUN packets with pc0 on even y, actual early_pc3594
on odd y, register0=1, other registers0, move1 for y<Q and move2 for
y>=Q. The error reinstalls them only on its104 rows. All collisions,
pending moves, instruction reads, writes and later packet states are
the same frozen total transition.

Independent banks have literal alternating1700-bit word A (lanes M/3
odd and2M/3 even), Mem=A,H1=all1700ones,H2=0,H3=A. The cycling recipe
preserves actual current banks at the six native normal words P..P+5;
it replaces the other bank coordinates. Source/interacting/sparse
replace those banks throughout the core and endpoints. Every holder
edge and alias is resolved in the full chronological payload.

## Exact factor and finite continuation

The [new executor](search_gaw17_large_bursts.py) generalizes only support
size and recipes. It inherits GAW16's full Word100 Programme mapping
and unchanged GAW15 native/SF equations, including each computed clock,
raw-GF wipe, separate History banks, actual Mail erasure, resets,
captures, births, courier and old-Out commit order. The C library and
own ROM are byte-identical to the accepted ones.

The factor has no16-site hypothesis: holder-local native and SF clauses
and target enumeration are unchanged. The larger core is included
before the first step, and all updated groups/incoming targets/births
are enumerated. Full Programme operands are voted from their actual
raw100-bit holders; new Programme is universally boolean by the
hardwirer/wipe equation. Its refresh does not truncate consumed Head
registers. Actual whole-local_R probes at listed rows and every source
and changed-Head holder check this substitution; they supplement the
local equations and finite-cut proof rather than assert a proof by
sampling arbitrary error payloads.

At native/copy closure the actual GF/common clock/flags and Programme
are correct, every remaining SF group is coherent, and the subsequent
logical packet factor starts from **those** Mem/History/Out/Scratch/
Head states. It never restarts or prepares a clean interpreter. All
five selected executions are terminal by901770<120Q. Rest holds their
actual Out. The real U update consumes old Out and then resets all
work. The same[-2Q−32,4Q+32) finite representation,24-site margin and
unaffected exterior-frame proof give an infinite-line lift; neither
native nor SF disturbances reach the cut.

| case | native/copy closure | first GF-or-Age quiet after last fault | max GF-or-Age sites | actual WF outputs/rows | bad U normal records | unused nonzero Info |
|---|---:|---:|---:|---|---|---:|
| native_program104 |104 |104 |0 |0/0 |{0}, illegal |0 |
| cycle_control104 |2324 |131 |105 |0/0 |{0}, legal |0 |
| source_flags104 |4227 |130 |104 |312/104 |empty, legal |9 |
| interacting104 |6946 |2851 |413 |0/0 |{0,1}, legal |0 |
| sparse_span150 |6946 |2851 |413 |593/119 |{1}, legal |0 |

Times are elapsed updates since T. Site counts are GF **or** Age,
not a claim about only clock disagreement. The complete receipts retain
20547 rows,9239 selected whole-local_R checks,15166 raw U commit/reset
checks and52 actual next-upper cones. Every nonzero WF source is
derived from actual SF and guards; none is independently selected.

For the four legal cases, unmasked496-word normal records round-trip
to legal upper C'. Their actual unused A' is retained separately.
The accepted broad-E period theorem applies to those legal records
with arbitrary A', not merely coherent/canonical upper states. Each
next-upper cone meeting the listed normal damage is checked against
F²(H); the remaining cones are identical. Thus F(C')=F²(H) and the
actual full boundary at2U is E(F²(H),0), with all-later equality by
determinism. Source_flags104 has no normal upper damage but nine
nonzero unused words at U; full raw U equality is not claimed there.

## The actual illegal encoding and delayed write

Native_program104 gives normal receiver0's first six U words

    (0,M,M,M,M,M), M=2^100−1.

The five illegal words are Age(index1,limit2^20), F1(index2,limit2),
F2(index3,limit2), WF1(index4,limit2), WF2(index5,limit2). All five Info
copies of each logical primary agree on these exact words. The other
normal records are correct. No legal upper cell can have those normal
words, so no legal C' and unused A' can satisfy Z_U=E(C',A'): A' can
change only unrepresented primaries. This is a concrete obstruction to
the stated narrow-E boundary extension.

The [lineage checker](check_gaw17_padding_lineage.py) starts from the same
actual T row and executes the whole10816-point burst. After its last
error at839784, all five Head copies at native Age primary y=P+1=3849
hold register0=M/pc3566 at839785. Programme has already refreshed to
boolean. At839786 the real STX prepares SEEK(target3849,r0=M); at839787
the actual store writes Out=M in all five holders. Its224 following
whole-kernel checks retain the raw states. The separate complete
execution/commit trace proves the final illegal Age/flag/WF words at U;
no assertion that every native Out stays M throughout execution is
needed (the final GF word is0).

The continuation explicitly sets `actual_U_legal_E_encoding=false`,
`legal_record_period_theorem_applied=false` and
`untyped_record_not_decoded_or_given_legal_period_theorem=true`. Its
`complete2U_shadow=false` means **withheld**, not a measured2U
disagreement. The aggregate gives second-boundary equality=null and
an explicit unproved outcome for this case. It does not call a masked
word projection the actual upper input. A broader encoding/decoder
completion or actual second-period derivation would require a new
proof; eventual repair and memory failure remain open here.

The extra100-bit native padding and a Programme word M are legal in
this changed WORD100 physical rule, but they are not Gray's bit
Programme/Info alphabet. Immutable STX fetch and the moving-word
evaluator are also reconstruction departures. Thus even the local
dependency is not sufficient to attribute this boundary obstruction
to literal Gray. It is neither a G17 nor an iid counterexample.

## Status, preserved failure and replay

| step | status |
|---|---|
| Frozen rule/ROM and recursively intact chronological start | inherited proved identities, all dependency hashes checked |
| Four dense and one sparse original-real1 classification | proved explicit sets; original classifier replay |
| All replacements genuinely changed and all later fields derived | checked chronological whole-cell payloads plus actual local factor |
| Five native/copy closure times and raw U records | exact finite calculations with infinite-line/coherent-factor composition, selected cases |
| Four legal-record U/2U recovery instances | proved selected actual maps plus accepted broad-E period theorem |
| One literal narrow-E U encoding obstruction | proved five exact illegal represented words; actual delayed write and U trace |
| Illegal case's decoder,2U/eventual repair or memory failure | unproved, not inferred from false/withheld receipt flag |
| Arbitrary104×104 repair, Gray fidelity or iid theorem/failure | unproved |
| Shorter U,new rule or globally smallest repair | none asserted |

The first support audit passed its mathematical assertions but failed
when JSON encoded the rejected dense150 witness's NumPy `int64`. Its
source snapshot, exact TypeError log and failure-provenance receipt are
retained. The corrected new diagnostic converts exact NumPy scalar
values with `.item()`; the original classifier and rule are unchanged.
No trajectory ran before that serialization failure. The validator
replays the old failure and proves the same classification after exact
JSON conversion. No operational failure or unsupported history is
discarded.

Run from the repository root:

    python3 Report/proofs/gray_counterexamples/unregistered_gaw17/validate_gaw17_large_bursts.py

The read-only validator checks every inherited GAW16 asset, rebuilds
the identical native binary, replays all five32-row discoveries and
all five complete histories, checks the actual padding lineage,
replays the preserved serialization failure and verifies unmasked
aggregate outcomes. It does not write receipts or registered files.
