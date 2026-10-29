# GMW6: a token-coded whole transition, with explicitly extra immutable ROM

This isolated candidate keeps Q=8192, U=128Q=1048576, lambda=24 and c=104.
It is **an explicitly changed rule**, not a faithful implementation of Gray.
Its five-stage/whole-period refinement, noisy execution and reliability are
unproved. The theorem here starts with a **preloaded coherent input tape**;
it does not assert that the earlier physical stages produce that tape.

Sources: [total kernel](gray_token_word_v6.py),
[full emitter](build_gray_token_word_v6.py),
[finite comparison/static checker](check_gray_token_word_v6.py),
[universal execution bound](check_gray_token_word_v6_bound.py),
[read-only validator](validate_gray_token_word_v6.py),
[receipt](../../../figs/gray_counterexamples/GMW6_token_word_certificate.json),
[beta](../../../figs/gray_counterexamples/GMW6_token_beta.bin),
[dictionary](../../../figs/gray_counterexamples/GMW6_dictionary.json),
[listing](../../../figs/gray_counterexamples/GMW6_token_listing.json),
[retained prepared comparisons](../../../figs/gray_counterexamples/GMW6_full_replays.json).
The initial [8280-bit overflow](../../../figs/gray_counterexamples/GMW6_first_token_overflow.json),
[temporary/destination alias](../../../figs/gray_counterexamples/GMW6_slot_alias_failure.json)
and [wrong shift direction](../../../figs/gray_counterexamples/GMW6_slot_shift_failure.json)
are retained with their exact source snapshots. They are failures in this
changed implementation. No claim about Gray follows from them.

## Storage and explicit changes

The programme contains884 instruction words and15 data words. Each word is
represented by a nine-bit token, giving899*9=8091 beta bits; its physical
bit store is padded to8192. A **separate immutable dictionary** contains512
100-bit words, of which406 entries are used. Thus the total immutable
capacity is8192+51200=59392 bits. Even the unpadded used stores take
8091+40600=48691 bits. Calling beta an8091-bit token programme does **not**
make this a Gray-faithful Q-bit self-evaluator: much instruction information
is in the dictionary. Both stores are part of the fixed transition rule.

Relative to GMW5, PCs count whole instruction words; PC increment is1modQ.
CODE decodes one nine-bit token and performs a dictionary lookup. BITCODE
reads one beta bit. SIGNEXT and unsigned RSHIFT are new generic word ALU
operations. Working scratch uses physical coordinates primary+128..135,
instead of primary-64..-57. These changes require the fresh emitted beta
and dictionary. They are not applied to any earlier candidate or G17.

Other inherited departures remain: h1 Flag2 erasure,100-bit mutable
Info/Out/Scratch/Programme words, an11-word Mem bank, a22-word moving head,
holder-computed native Address for service controls, and fixed-zero native
Workspace.Flag1/2 outputs. In particular this omits the Workspace pulses
driven by simulated Flag1/Flag2, which Gray uses in higher-error repair;
completing physical gathers alone would not restore that mechanism or its
proof. Programme is mutable and voted when an instruction
reads it, but **instruction execution uses the immutable stores**. No Gray
ProgrammeBits hardwirer/gathering/refinement theorem is being asserted.

The physical alphabet has

    37 + 5*(22*100) + 5*(11*100) + 4*(5*100) = 18537 bits.

The raw cell representation occupies191 words of100 bits, including the
zero padding of the six native fields. Its primaries are4001..4191. This
word encoding is a departure from Gray's single-SimBit layout.

## Exact prepared fifth-stage theorem

Fix the emitted beta and dictionary in the linked receipt and call the
resulting total finite local rule F6. Let C_i be arbitrary **legal raw F6
cells**, for all integer i; neither their geometry nor their private fields
need be coherent. In lower colony i, preload logical Mem at primary4001+w
with the11 words `word_w(C_(i+j))`, j=-5..5, little-endian. Its five holders
are coherent. All lower native Addresses are xmodQ, their common Age is112Q,
and all four lower native flags are0. Lower Out and Scratch are0. The reset
at112Q has removed lower heads. No physical errors occur through the next
Age0. Other unused lower SF values are arbitrary coherent logical values.

**Theorem.** The birth update produces exactly one coherent head per colony
at4001, p=1, PC=0, all other packet words0. In at most47913 execution
updates after birth, every colony's head halts. Its191 represented Out
words are exactly `cell_words(F6(C_(i-5),...,C_(i+5)))`. The head, input
tape and outputs stay in that colony. These words persist through rest;
the update producing Age0 copies each into all five corresponding lower
Info holders, before Out is reset. Native geometry stays canonical and
the four lower native flags stay0 throughout.

The birth row is112Q+1; available execution rows are112Q+2..120Q, hence
65535 updates. The47913 bound leaves17622 execution updates. Total U is
unchanged. This is a **noiseless prepared physical self-evaluation theorem**,
not a complete encoded-period theorem, an intact recursive-history witness,
an E0 execution theorem or an iid theorem.

## Total primitive and all-raw locality (proved)

A head has six100-bit metadata words and sixteen100-bit registers. Presence
means p!=0. Missing heads produce ZERO. Candidate order is stationary self,
then a right-moving left source, then a left-moving right source. Collisions
produce `fail(first)`. Movement>=3, mode>=4, invalid opcode14/15, invalid
IO target/lane and invalid branch-register target have specified ERROR
outcomes, preserving old PC, target, args and registers while setting p=1,
move=0, mode=ERROR. HALT/ERROR stay stationary. SEEK arrives in one tick if
already at its target, or after the exact number of one-site moves otherwise.

For a word address a, CODE returns dictionary[token(a)], where token(a) is
the nine bits of beta beginning at9a; absent trailing bits are0. Addresses
outside[0,Q) return0. Dictionary[0]=0 (literal HLT). BITCODE returns beta[a]
for0<=a<Q and0 otherwise. Both are fully specified finite table lookups.
Neither calls F6, a host evaluator or a packet-step function. Their constant
tables, including dictionary padding, are emitted and pinned independently.

The ALU operations are the listed finite integer/bit equations. SIGNEXT
returns0 for width0, a high-bit sentinel for width>100, and the100-bit
signed extension otherwise. RSHIFT returns a>>b for b<100, else0. Invalid
ALU functions return2^99. Opcode parameters are masked to their syntax
widths; raw PCs and register values retain their full100-bit width.

Let S=(0,-2,-1,1,2). A holder x's slot s represents y=x+s. A voted incoming
head at y+d, d=-1,0,1, reads holders x+s+d-t, t in S: the maximum distance
is5. Destination Mem/Out/Scratch/Info/Programme votes read x+s-t, at most4.
Service Address is (computedGF(x)+s)modQ, not another site's computed field.
Native calculation/wipe use radius5, and both ROM lookups are constants.
Consequently F6 has radius at most5 on **every raw physical state**.

## Own-programme correctness (proved by register and field contracts)

This proof concerns the actual emitted programme, including its interpreter
and mutable fields. The finite retained comparisons are additional checks;
they are not the universal argument.

**Field access.** Encode native fields in rows0..5; for SF field number f
and copy q, row is6+5f+q. The five raw sources of logical field y are C_(y-t)
at copy t. `vote` visits those five rows in order q=0..4 and reads lane
y-t+5 from their preloaded11-word Mem. All normal and incoming accesses
have -3<=y<=3, hence0<=lane<=10. For every output slot, these are the
actual raw holder coordinates, rather than a substitution of head centres.
The register helper obtains row36+5r+copy, exactly the requested selected
packet register, for0<=r<16. Each output field is written to its distinct
row6+5f+copy. No other copy's output is read as a source input.

**Bitwise vote.** `vote` starts R3=R4=R5=0. For each word v it updates
R5|=R4&v, R4|=R3&v, R3|=v, in that order. Induction makes these three
words the at-least-three, at-least-two and at-least-one predicates after
each input word, at every bit. After five words R5 is their bitwise3/5
vote. This commutes with concatenating the22 head words and the11 Mem
words. R11 advances by5, and R9/R10/R12/R13/R14/R15 are preserved.
The helper's logical source R12 and caller's saved control variables are
therefore unchanged. Its scratch R7 is distinct from each actual slot
destination (0,6,12); this is the corrected alias. Right-shifting the
packed slot word by4q, then SIGNEXT4, returns exactly S[q].

**Native prefix.** R12/R13 retain central GF/Age. READ5 packs the five
right or left20-bit input components. VADDINDEX adjusts GF modulo2^13;
using the20-bit residue of-1 gives the same adjustment, since8192 divides
2^20. VMAJ/VEXISTS implement whole-word3/5 votes with central defaults.
R6/R7 are right adjusted GF/existence, R8 its Age vote, R10/R11 the left
votes. The WINDOW/mismatch recipe makes R14 exactly h1 Flag1, using the
right GF existence and in-colony interval even if a different vote fails.
R4 and R9 are the two Flag2 sources; R15 is the off-to-on predicate. The
new healthy erase clause is left-inside Flag2 count<=1 when !Flag1; the
unhealthy clause is no left Flag2 when Flag1. The central old Flag2 branch
chooses the corresponding keep/on value. Right votes are selected iff
R7 && (!R14 || R15); Age is incremented modulo2^20. Six stores write the
four native outputs and two zeros. These are exactly `scalar_native`'s
six outputs for every legal native input. The h1 correction is explicit.

**Top-level SF equations.** The wipe gate is newF1 && newGF!=old raw selfGF.
If true, all185 SF words are set0; native words are already written. If
false, the37 SF fields of each output copy are first assigned their old
logical votes. At computed Age0, old voted Out is copied to Info before
resetting Head/Out/Scratch. At112Q, those three fields reset without the
Info copy. At112Q+1, only service Address4001 births p=1; all other head
words are0. Fresh Programme is BITCODE(serviceAddress). Rest retains the
old voted head. These are exactly the kernel's phase partition and order.

**Incoming heads.** During an active update the three candidate P/movement
pairs are tested in the kernel's centre/left/right order. R9 counts accepted
candidates; R10 saves the first source. No candidate zeros the22 head words.
Otherwise `incoming_loop` copies that selected source's22 voted words.
Before any failure the original PC is saved in Scratch2. More than one
candidate, movement>=3 or mode>=4 reaches the common error block; HALT and
ERROR simply clear movement. Thus arbitrary nonbinary P, malformed movement
and full-width mode/PC values have the specified raw-state outcomes.

**RUN.** The full-width PC guard precedes CODE. Its low four opcode bits are
guarded<14. The immutable dispatch data maps all14 valid opcodes to their
actual emitted labels; these labels are independently decoded. Default PC
is (oldPC+1)modQ. The following exhausts the syntax, including CODE words
that are data or padding rather than aligned emitted instructions:

| Opcode | Actual emitted effect, equal to the kernel |
| --- | --- |
| HLT | Restore old PC; set HALT/move0. |
| JMP | Set the13-bit literal target and move0. |
| JMPR | Read the selected100-bit register; guard<Q; set PC/move0. |
| BNZ | Test the selected full word; keep default PC or use literal target; move0. |
| MOVI | Write the selected20-bit literal to the selected register; move0. |
| CODE/BITCODE | Read the selected full index register, invoke the same finite ROM primitive, write selected destination, move0. |
| ALU/ALUX/ALUI | Extract the stated operand indices/functions/immediate; invoke the same generic ALU; write only selected register; move0. |
| LDX | Guard index<Q, base+index<Q, lane<=10; form kind0/dst/lane/source descriptor. |
| STX | Guard index/base sum; form kind1/value-register/default lane5/destination descriptor. |
| READ5 | Guard target<Q; form kind2/default lane5/side descriptor. |
| READMASK | Guard target<Q; form kind3/dst/default lane5 descriptor. |

All IO cases use their common `new_io`: store target/args, set SEEK, and
choose movement by comparing target with the current service Address.
All bit fields and descriptor defaults, including the otherwise-unused
lane5 bits, agree with `descriptor`. Guard failures restore old PC in the
shared error block; no invalid request advances PC.

**SEEK.** An invalid full-width target errors. A nonarrival only adjusts
movement towards target. Arrival preserves PC/target/args and handles all
four possible kind bits. Kind0 first guards lane<=10, even for non-Mem
sources. It selects old Mem lane, old Out, old Scratch, or a fresh `vote`
of **old Programme** from the readonly input tape. This last path deliberately
does not read the freshly printed Programme in Out. Kind1 writes the selected
register to Out or Scratch. Kind2 packs the low20 bits of the five selected
left/right Mem lanes into R0. Kind3 packs the11 lane LSBs into the selected
register. Accumulation uses scratch only; every other packet word is unchanged.
The common exit sets RUN/move0. This covers arbitrary raw args, unused high
bits, both sides, all register choices and all100-bit source words.

These contracts prove by induction on the programme's instruction sequence
and bounded loops that every final represented word equals F6 on the supplied
raw upper cells. They do not rely on any upper hierarchy coherence. The
static certificate identifies every numeric field/slot/dispatch address and
the exact immutable code. There is no assumed whole-rule/packet/native syscall.

## Universal prepared execution deadline (proved)

The linked bound checker uses intervals plus finite sets as an abstract
domain. Each domain includes all concrete values it represents. Constant
sets are evaluated exactly when small; other arithmetic operations use
inclusive integer bounds or the full100-bit domain. Addition/subtraction
crossing a modular wrap use the full domain. Bit AND is bounded by the
smaller upper bound; OR/XOR by their maximum bit length. Comparisons give
0/1 unless forced. Signed shift is evaluated exactly for a constant distance,
otherwise widened. Unhandled generic operations widen to the full domain.
CODE evaluates all possible finite table indices, retaining the exact
dispatch-label set. Thus every transfer over-approximates the concrete opcode.

Mutable input reads widen to all100-bit words. Computed native outputs are
bounded by their legal widths, and Workspace outputs0; the native contract
above establishes these premises. Exact working-scratch stores/reads are
retained. A write with several possible addresses invalidates all potentially
affected known words. No readonly input is changed. Both outcomes of an
unknown branch are followed, with sound LT/EQ/NE and zero/nonzero narrowing.
Every source-register write invalidates earlier comparison facts about that
register, even if its new interval equals the old interval. The pre-hardening
checker and its bound are retained in the
[comparison-fact audit](../../../figs/gray_counterexamples/GMW6_bound_predicate_hardening.json);
the hardened checker produces the same bound. No concrete kernel/beta change
or data witness follows from this abstract-checker hardening.
The exact own loop counters and return/dispatch PCs prevent artificial
unbounded loops. All physical IO target/lane ranges are asserted legal.

At an IO opcode the cost is1 for initiation plus max(1, travel distance).
The distance bound uses both endpoint domains; it includes every one-site
SEEK update and the arrival update. Other instructions cost1. State
memoization only discards a smaller-cost visit to the same abstract machine
state; its future maximal cost is identical. All paths terminate at the
copy block's exit, without fetching a data word as a lower instruction.

Each copy begins with arbitrary100-bit SF words and a cursor anywhere in
the191-word frame, a deliberate enlargement of all actual entry states.
Its possible complete costs are bounded by

    9759, 9638, 9517, 9396, 9334 ticks.

The native prefix has133 instructions and16 IO commands of distance<=5:
213 ticks. The main gate is bounded by40; five copy-loop tails plus final
HLT cost16. Summing yields47913. The separate wipe path is bounded by1364.
All loops have fixed lengths37,22,5 or11; no loop bound depends on a raw
simulated data word. This is an exhaustive conservative **execution proof**,
not a maximum observed runtime or a random-input estimate.

## Physical lifting and status

Canonical GF/common legal Age/zero native flags stay canonical under h1:
both native votes agree, sources and inconsistency vanish, and Age increments.
The raw-GF wipe is therefore absent. A coherent logical SF word has five
equal voted holders. One coherent head moving at speed at most1 has exactly
one incoming candidate at its next site; all five holders compute the same
packet, data and write using their corrected service Address. These facts
inductively lift the instruction-level machine and travel count to F6.
Every accessed location is in4001..4191. Separate colonies cannot interfere.
When a head halts, active updates preserve it; rest preserves it and its
Out words. At Age0, old voted Out is committed to all five Info holders
before Head/Out/Scratch reset. This proves the stated prepared theorem.

| Step | Status |
| --- | --- |
| Finite total local equations, raw invalid-state semantics, radius5 | **proved changed rule** |
|8091 beta bits plus separately counted51200-bit dictionary | **proved static emission** |
| Native, holder/word votes and all14 opcode/IO cases | **proved register/field contracts** |
| Universal47913 prepared execution bound | **proved interval over-approximation** |
| Noiseless prepared physical evaluation and boundary Info commit | **proved conditional theorem above** |
| Retained finite prepared comparisons | **measured additional checks** |
| Earlier gathers/hardwirer/flags produce its inputs; complete period | **unproved** |
| Gray-faithful Q-bit evaluator/ProgrammeBits protocol | **unproved; explicit dictionary/word departures** |
| Continuing E0/higher errors, intact-history counterexample, iid memory | **unproved** |

No shorter U, change to G17, faithful-Gray counterexample or reliability
theorem is claimed by this checkpoint.
