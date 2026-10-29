# GAWN0: native-padding normalization, with a new own ROM

This is an **explicit isolated proposal**, not a change to G17 or frozen
GAW2R. It retains Q8192/U1048576/lambda24/c104, radius8, Word100, three
gathers, the h1 native correction and the other diagnostic-interface
departures described in GAW2R. Its immutable own ROM is newly emitted.
No Gray-faithfulness, smaller-constant or noisy reliability claim follows.

The new sources are [the total extension](normalized_gawn0.py),
[the changed emitter](build_normalized_gawn0.py),
[the structural/finite supplement](probe_normalized_gawn0.py) and
[the read-only checker](check_normalized_gawn0.py).
The frozen emitted objects are [ROM](../../../../figs/gray_counterexamples/unregistered_gawn0/GAWN0_rom.json),
[listing](../../../../figs/gray_counterexamples/unregistered_gawn0/GAWN0_listing.json)
and [emission metadata](../../../../figs/gray_counterexamples/unregistered_gawn0/GAWN0_emission.json).

## Exact statements

Let A be the GAW2R physical alphabet: native widths13/20/1/1/1/1 and
490 SF words of100 bits, giving49,037 bits per cell. Let D be all
496-word records of100 bits per word, including arbitrary padding in
the six native representation words. Let pi:D->A mask only those six
words, leaving every SF bit unchanged. Apply pi sitewise to configurations.
Let beta_N be the newly emitted fixed ROM. Let F_N on A be the literal
GAW2R physical equations evaluated with **beta_N** in every immutable
lookup. Define their declared extension on D by

    F_N^D(d)=F_N(pi(d)).

This changes the padded-input extension and the own-ROM instance. It
does not reinterpret the old emitter's proved padding obstructions.
On physical legal inputs no new native operation is added; the new
immutable programme still changes the instantiated finite rule.

**Theorem N1 (prepared evaluation).** For every17-record D input tape,
normal entry of the beta_N evaluator halts within141,564 updates,
writing exactly all496 words of F_N^D at the centre. Its early entry
halts within215 updates, writing exactly the four native GF/Age/F1/F2
successor words and zero WF1/WF2. The two executions, on the raw tape
and on its native-projected tape, have identical control histories and
identical outputs. Intermediate registers containing a just-read raw
GF/Age word or GF vector may differ before their normalization macro
finishes. No SF word, memory lane or simulated instruction register is
projected.

**Theorem N2 (complete physical noiseless period).** For any infinite
D configuration d and coherent auxiliary Word100 function B, define
E_D(d,B) by canonical lower GF/common Age0/zero native flags, zero
private work, the beta_N Programme bits, and five coherent Info copies
of d[g]'s496 representation words at gQ+P+i, P3848. At other logical
positions put coherent B. This is a legal physical configuration in A:
upper native padding is carried by lower **SF Info**, not added to the
lower native alphabet. With no physical errors,

    F_N^U(E_D(d,B))=E_D(F_N^D(d),0).

The output represented native words are legal. For d in A this is
exact self-simulation of the same fixed physical rule F_N. For d in D
it is a proved normalization of its represented native padding in one
complete lower period. It does not cover arbitrary damaged lower
geometry, incoherent lower Info holders or arbitrary old lower work.

## 1. Local projection — proved

pi is idempotent and leaves every SF word intact. The declared extension
therefore satisfies F_N^D(pi(d))=F_N^D(d) and takes values in A.
Its Address comparison for SF wiping sees the projected old Address.
The same applies to each computed-primary source, since it is evaluated
on pi(d). These are identities of the stated equations. They are not
claims about the unchanged padded extension or old ROM.

## 2. All input acquisitions — proved by literal emission and word algebra

The new emitter starts with the unchanged GAW2R unresolved instruction
and label sequence. It appends an ALUI AND immediately after each direct
native Mem LDX:16 Address reads get8191;8 Age reads get1048575. The
24 sites include central native fallbacks, every computed-primary
source's fallbacks/old-GF wipe, workspace/main old-GF wipe comparisons,
and the early entry's fallbacks. Removing those24 instructions recovers
every old unresolved instruction/label exactly. All jumps, return
constants and dispatch-data entries are reassembled at their new PCs.

Every raw Mem input access belongs to one of the following classes.

* Direct native LDX: the read destination alone can differ. The very
  next instruction masks it to the declared native width. The result
  is identical to the projected-input read, for every100-bit word.
  There is no intervening store, use, branch or entry label.
* GF READ5: each physical primitive first extracts the low20 bits of
  five100-bit words. The next three instructions set the signed step,
  set width13 and apply VADDINDEX. Every component becomes
  (v+step*(i+1)) mod8192. Discarding native bits13..99 before this
  operation gives exactly the same value. The temporary raw vector
  is neither stored nor used in a branch before that operation; no
  external label enters the middle of the macro.
* Age READ5: the primitive's20-bit extraction is already exactly pi.
* Native READMASK/FULLCOL: these primitives acquire only bit0, exactly
  pi for each flag; the unchanged shift/window construction chooses
  the required11 neighbour bits. Native padding has no other use.
* The sole remaining raw Mem LDX is the unchanged SF vote helper.
  Its typed call arguments are SF columns>=6, proved by the existing
  whole-emitter helper contracts; it never addresses a native column.
  All those Word100 inputs are unchanged by pi.

The structural receipt checks all24 direct loads, all32 READ5 sites
(16 GF/16 Age), all32 flag-column sites (8 READMASK/24 FULLCOL) and
the sole raw SF-helper load. All other reads use current Out/Scratch
or fixed Programme/ROM, or unchanged SF operands. The generic upper
instruction emulator reads arbitrary SF memory/register words at full
width, including invalid metadata. It acquires no additional raw
native input. This exhausts actual input access opcodes in the emission.

## 3. Relational execution and full semantics — proved using the previous compositional argument

Run the new normal-entry evaluator on d and pi(d), from identical
prepared packet/Out/Scratch states. Induct across the acquisition macros
above and across all other individual updates. The macro outputs agree;
all other operands, immutable lookups, branch predicates and stores
agree. During physical IO travel both executions have identical targets,
movement and pending descriptors. Thus they follow the same branches
and finish each macro with identical packets, Out and Scratch. This
proves the claimed relational equality for all raw words, without a
finite sampling inference. The same induction applies at early entry.

On pi(d), every inserted mask is an identity on its correctly acquired
native value. The complete GAW2R compositional correctness argument in
[GAW2_THREE_GATHER_PERIOD.md §§2–3](../unregistered_gaw2/GAW2_THREE_GATHER_PERIOD.md)
therefore applies to the other instructions. The SF vote, holder offsets,
data/courier/reset/commit equations and generic upper instruction
templates are identical. Its internal control labels and dispatch
constants are relocated together, so every typed return and dispatch
still denotes the same block. The immutable table is **beta_N** in
both the physical upper step and emitted CODE/BITCODE templates; those
templates implement one finite lookup for every raw PC/register value,
including guarded out-of-range values. They do not depend on beta_R's
numerical instruction contents. No old programme value is substituted.
Consequently the whole496-word output is the literal physical
F_N(pi(d)), not merely agreement with another unproved evaluator.

## 4. Total deadlines and resources — proved using the previous cost argument

The old syntax/loop/travel proof bounds every full legal evaluation by
141,557 updates. Added masks are stationary one-update ALU operations;
they change no physical operand destination or travel distance. Native
and workspace control is acyclic before main, with at most six added
masks along any path. Main has one more before the copy loop; none
is in a loop or generic interpreter block. The changed prefix CFG
checks this bound, including all data-dependent branches and typed
SF-vote returns. Thus the whole bound is141,557+7=141,564. Relational
execution extends it to D. The early pass adds exactly two masks to
the previous133-instruction/16-wait bound:135+16*5=215.

Late birth at102Q+1 leaves18Q-1=147,455 active updates. Margin is5891.
Early birth at72Q+4 plus215 is strictly before75Q. As before, sources,
native guard and quietness do not require a shorter work period.
The rebuilt ROM uses3766 tokens/1050 dictionary entries; its used
11-bit token stream is41,426 bits. The allocated finite immutable
resources remain65,536+2048*100+13=270,349 bits. Early PC is3616.
All operands/PCs fit their declared fields. The dictionary is total,
with unused entries zero and out-of-ROM token bits zero.

This still fails beta<=Q and the512-dictionary requirement. The physical
bit alphabet still has K49,037 and Gray's literal Q>=2K bit-primary
layout would require at least98,074 cells. Word100 primaries and
immutable lookup remain material departures; this is not Gray compiled
with a smaller bit layout or a proof that such a compilation is impossible.

## 5. Full physical period — previous argument applies, with new acquisition/deadline premises proved

Use the literal infinite-line induction of GAW2R §7 with beta_N and d.
Canonical lower GF/common clock make both native candidates agree,
so computed SF wiping is false on every row. Before96Q, native WF
is0. The three reset/load/capture inductions therefore gather every
raw17-record neighbourhood, including its native padding, and retain
three equal History banks by72Q+2. This argument copies Word100 and
does not require legal represented native words. SF copies in d may
be mutually incoherent; the lower five copies are coherent by E_D.

Reset at72Q+3 and birth at72Q+4 produce the actual prepared early
execution. The same physical holder/packet coupling identifies it with
N1 on that raw bank. It finishes before75Q, and the unchanged bounded
couriers deliver its normalized flags before the80Q-1 special writes.
Every true source command is derived from the retained bank.

The96Q..98Q native window can activate lower flags. GF/common clock
stay canonical, so no SF wipe occurs. Erasing Mail cannot change the
already captured History. The existing common-clock quiet argument
clears native flags by99Q. Reset at102Q and birth/reload at102Q+1
derive the actual full prepared input and unique packet. They use the
same raw History bank, not a preprojected or preloaded tape. The
holder/packet induction now applies N1's141,564 bound to this physical
execution, producing all496 words of F_N^D(d[g]) before120Q.

Every Out outside the normal frame remains0, by reset and the proved
typed emission addresses. At U the literal Info commit consumes old
Out before clearing work. Thus normal Info is exactly F_N^D(d),
auxiliary Info is0, all work is reset, Programme is the beta_N bit and
lower native fields have the stated encoded boundary values. This is
E_D(F_N^D(d),0) on every site. Each site proof is local and finite;
no finite simulation boundary is used. This proves N2. Iteration gives
ordinary noiseless self-simulation after the first normalized period.

## Evidence, status and remaining obligations

The [finite receipt](../../../../figs/gray_counterexamples/unregistered_gawn0/normalization_probe01.json)
retains complete raw17-record inputs, projected native inputs and all
496 outputs for four paired full executions plus paired early runs.
They exercise padding with/without GF quorum, Age0 commit and a live
upper instruction step. These are measured transcription supplements.
The universal claims rely on the acquisition/relational/compositional
and physical inductions above. A metadata-only initial build is retained;
its ROM/listing are identical, and its instruction-bit-sum field was
renamed to distinguish it from token-stream length.

| Step | Status | Scope |
|---|---|---|
| Declared D extension/projection identity and output in A | proved | New beta_N instance; old obstruction unchanged |
| Exhaustive native acquisition and raw/projected relational execution | proved | Prepared normal/early entries, arbitrary100-bit record words |
| Whole local semantics and141564/215 deadlines | previous proved compositional argument applies; mask/relocation premises proved | New immutable table used on both sides |
| Complete physical E_D-to-E_D noiseless period | previous physical argument applies; new raw-bank evaluation premises proved | Canonical coherent/reset lower encoding, arbitrary represented D |
| Four paired full/early executions | measured supplements | Not a universal or noisy test |
| Pure E0/general real1/higher repair/coherence under damage | unproved | Padding normalization does not establish these |
| Faithful Gray/smaller Q or U/positive iid rate/memory/minimum fix | unproved | No operational counterexample or reliability theorem |

Read-only command:
`python3 Report/proofs/gray_counterexamples/unregistered_gawn0/check_normalized_gawn0.py`.
No commit; active G17 and every frozen GAW2R source/ROM are unchanged.
