# GBD0: whole-code budget and a packing-first design analysis

This is a design analysis and one generic local component, **not an emitted
new cellular automaton**. The target remains Q=8192, U=128Q=1,048,576,
lambda=24 and original error separation c=104. There is no new beta,
interpreter, physical period, shortened U, noisy theorem, or counterexample
to Gray. Frozen GBC6 and every earlier rule/receipt remain unchanged.

The result is concrete in two respects. First, the exact rejected GBC6
listing is partitioned into a complete cost account: eliminating all of its
interpreter control would still leave more than Q bits. Second, a universal
generic packed-window primitive is defined and proved local, and the state
budget of a proposed binary-history/packed-work layout is fully counted.
The primitive's own software and the layout's packing/transport are still
missing. No guessed instruction count is presented as a Q-fit certificate.

## 1. Primary requirement and scope

Gray, printed p.33, text lines1497–1501 in
[the local primary text](../../../../papers_txt/gray_readers_guide.txt),
requires enough primary binary SimBits to encode a K-bit state and assumes
Q>=2K so represented primaries can be placed away from colony boundaries.
The following paragraphs on pp.33–34 require five spatial copies of each
simulation bit and three retained gathering results. Gray pp.30–31, text
lines1347–1406, describes a beta containing the interpreter, bit transport
and native transition, and only gives a sufficiently-large-Q argument with
unspecified additive/multiplicative constants. Neither the displayed lower
bound8192 nor U128Q supplies a numerical software-fit certificate.

Our radius8/17-input-lane completion is already an explicit departure from
Gray's radius5/11-neighbour interface. GBD0 does not attribute its resource
obstruction or its word-window primitive to Gray verbatim. The layout
obstruction below is for a specified **independent raw word-bank
representation**, not a universal lower bound for finite cellular automata.

## 2. Exact cost of the frozen rejection

Source: [GBC6_complete_register_attempt01.json](../../../../figs/gray_counterexamples/unregistered_gbc6/GBC6_complete_register_attempt01.json).
The symbolic labels and instruction bit lengths uniquely determine this
partition. The checker re-sums all 3,140 instruction records across every
listed mode, and all 384 invalid references. The 42,716-bit stream
is the wrapped **diagnostic rejection**; it is never fetched as a Q-bit beta.

| Emitted block | Bits | Instructions |
|---|---:|---:|
| Native/context and raw-GF wipe | 827 | 66 |
| Three gathers, resets, ordinary hold | 3,683 | 221 |
| Head selection/control | 2,863 | 193 |
| IO, stream, span, word-output modes | 7,371 | 576 |
| RUN opcode simulation | 17,442 | 1,304 |
| Head birth/collection | 1,517 | 100 |
| Flag couriers | 3,511 | 236 |
| Final computed source | 1,737 | 120 |
| Generic software helpers | 3,765 | 324 |
| **Total** | **42,716** | **3,140** |

The native prefix is not the dominant code cost. Head control, data modes,
opcode simulation and birth together cost 29,193 bits. Even deleting all four
blocks, an impermissible whole-interpreter oracle shortcut, would leave
13,523 bits. Therefore reducing just virtual opcode dispatch, just serial
field reads, or just the Head return ABI cannot close this exact listing's
Q budget. A successful design must also compact stage/transport/source
software. The required whole reduction is 34,524 bits, about 80.8%.

The instruction classes that dominate the stream are also retained in the
receipt. For example, RUN opcode simulation alone has 5,697 ALUI bits,
3,553 BR bits, 2,718 WGET bits, 918 WSET bits, 716 SWAP bits and 680 PUTWORD
bits. These are actual bit counts, not a lower bound on better compilers.
The proposed change below targets three distinct repetitions:

1. Store bounded word controls/operands in a small fixed packet, avoiding
   the old arbitrary407-bit Work window and its WGET/WSET/PUSH/RETURN
   simulator branches.
2. Pack a completed binary input record once. A generic bounded word
   window can then consume up to20 stride-five bits without serial
   field-access movement through100 raw columns.
3. Keep field reset/hold/copy as bounded loops over an explicit descriptor
   list. The descriptor list and its dispatcher belong in beta; neither
   is an uncounted immutable helper table.

These explain which blocks a future compiler must remove. They do not
prove that the resulting complete programme is small or fast enough.

Ordinary byte compression also does not solve this rejection. The checker
packs its exact 42,716 diagnostic bits and measures zlib9/xz9/bz2 sizes.
All are greater than Q even before adding a decoder or changing raw-PC
semantics. This is measured encoder evidence only; different control-flow
or program representations remain open.

## 3. A strict state-layout obstruction

Suppose each site stores three retained History banks, each bank contains
2r+1 independent W-bit words, and each such word has five independent
backup copies in the raw state. Retain the37 binary native bits used by
the Q8192 instance. Then its raw binary alphabet necessarily has

    K >= 37 + 3 * 5 * (2r+1) * W.

Proof: the specified field values have2 raised to this many distinguishable
assignments. An injective raw-state encoding needs at least this many bits.
No transition or noise claim is used. A compression exploiting equality of
the three banks or equality of five holders changes the admitted alphabet
or represents it by a new coding relation: arbitrary raw field patterns
cannot all be compressed injectively to fewer bits.

At r8/W20 the History banks alone require K>=5,137, hence2K>=10,274>Q.
Adding a separate five-copy voted17-word bank requires K>=6,837 and
2K>=13,674. The arithmetic is independent of CPU design. At r5/W20 the
History banks alone fit the numerical premise, but adding the voted bank
already yields K>=4,437 and2K>=8,874>Q.

For the explicitly specified parallel-word layout with98 logical words
(51 History,17 voted input,22 Head,4 Info/Out/Scratch/Programme,
2 Mailbox,2 couriers), all five-copy backed, K=37+490W. With W20,
K=9,837 and2K=19,674; the smallest *power of two meeting this layout
inequality alone* is32,768. At Q8192 its word width must be<=8, before
any omitted state is added. A width8 architecture is not impossible:
native13/20-bit values could be represented by multiple words, with a new
arithmetic/runtime proof. No minimum colony size for other layouts is proved.

The smallest resource-only choices actually justified here are:

- Keep this exact W20/98-word layout and increase power-of-two Q to at
  least32768; code and runtime still need proof.
- Keep Q8192 and represent the parallel words by at most8 bits; multiword
  arithmetic, native/source semantics and time remain unproved.
- Retain **binary** histories and pack only their temporal majority after
  the last capture, using the counted layout in §4. This avoids the
  particular cardinality obstruction without asserting beta fit.
- Use word-valued SimBit instead of binary SimBit, as in previous word
  prototypes. This changes the encoding and alphabet; it does not satisfy
  Gray's binary Q>=2K premise by relabelling Word20/Word100 as a bit.

These are specific representation changes, not sufficient reliability fixes.

## 4. Counted hybrid proposal, not an issued rule

The following **proposed** binary-state layout preserves three binary
retained histories. The17 Word20 work lanes are introduced only as packed
working storage, not multiplied across all three history banks. Each row
below denotes a logical SF field with five raw backup copies.

| Logical field | Bits before five backups |
|---|---:|
| Info | 1 |
| Two Mailbox valid/payload pairs | 4 |
| Three binary17-lane History banks | 51 |
| Packed voted work,17 Word20 lanes | 340 |
| Input packing tag and valid | 14 |
| Word output | 20 |
| Output packing tag and valid | 14 |
| Scratch word | 20 |
| Two flag couriers | 2 |
| Fixed Head described below | 179 |
| **Logical SF total** | **645** |

With 37 native bits, K=37+5*645=3,262; 2K=6,524, leaving 1,668 bits in the
numerical Q>=2K inequality. The179-bit packet consists of presence1,
movement2, mode2, PC13, return13, target13, remaining5, lane5, kind3,
index5, destination-register2, four Word20 registers80, and native-result35.
There is no407-bit Work or allocated mutable stack. Return calls would
need one fixed nonnested13-bit link or a separately counted software tape.

This is a complete count of the *proposed listed fields*, not a proof these
fields suffice. If the actual implementation needs another validity field,
head bank, working register, hardwirer ProgrammeBit or nested return stack,
it must be added. For example, a five-copy mutable ProgrammeBit would add5
to K and10 to2K. No ProgrammeBits protocol is silently supplied here.

Three no-error gathering stages keep the old baseline endpoints. Retained
radius8 banks become complete by72Q+2. A future implementation could pack
their majority in groups of20 raw bit columns, compact those chunks to a
164-word input interval (ceil3262/20), run a small Word20 packet there,
and expand Word outputs back into the binary normal primaries before
commit. A mutable scratch interval would be disjoint from the input pool.
The proposed tags account for transporting input/output words. Actual
packet collision rules, every reset, malformed tag handling, gap-closing,
logical/source Address identities, courier lineage and rest-stage
behaviour are **not defined**. This checkpoint claims no physical packing
trajectory or period theorem.

The intrinsic instruction family being considered is fixed-size ALU,
bounded literal, branch, generic local packed-window read/write, immutable
code-bit read and movement. Native arithmetic/quorums would be software
using ordinary window reads, ALU and loops; **there is no proposed NATIVE
or whole-rule evaluation instruction**. The native physical equations would
still need a full finite-circuit implementation and software refinement.
The old native gate count is not a programme-size certificate. No code-word
dictionary, opcode-control ROM, descriptor table or omitted register file
is allocated outside beta. **No beta has been emitted for this proposal.**

For clarity, the contemplated eight-opcode format has the following exact
operand counts. This is only a syntax/resource proposal, not a proved
interpreter: opcode3 bits; register selectors2 bits; direct PC targets13
bits; ALU function4 bits; a bounded literal stores n zero bits, one delimiter
and n payload bits for value+1, with n<=20. READ/WRITE refer to actual local
packed work/input/output ports and retain movement as a separate action.

| Proposed opcode | Counted format bits |
|---|---:|
| HALT | 3 |
| LIT(destination, literal) | 6+2n, maximum46 |
| ALU(destination, source1, source2, function) | 13 |
| BR(condition2, source, target13) | 20 |
| READ(destination, target-register, lane-register, phase-register, count-register, stride1) | 14 |
| WRITE(source, target-register, lane-register, phase-register, count-register, stride1, port2) | 16 |
| CODE(destination, index-register) | 7 |
| MOVE(target-register) | 5 |

The proposed normal-field descriptor table needs10 records of23 bits
(offset12,width9,kind2); Head metadata13 records of17 bits
(offset8,width7,kind2); two4-bit loop counts; native fields6 records of12
bits (offset6,width5,kind1): **531 stored beta bits**, not free control data.
Any interpretation that needs a different descriptor is a changed budget.
With no other data, a complete software listing with opcode-class counts
H,L,A,B,R,W,C,M would have to satisfy

    531 + 3H + sum_over_literals(6+2n)
        + 13A + 20B + 14R + 16W + 7C + 5M <= 8192.

Even166 worst-case46-bit rows would fit this *syntax budget*. This is not
a claim the entire transition can be written in166 rows, or that literals
are the only extra data. All class counts and actual labels are **unset**.
It gives a falsifiable whole-code target before another ISA implementation,
instead of assuming a5x saving from a few folded instructions. In
particular, the earlier42,716-bit programme cannot be reclassified as
fitting by merely changing this proposed format.

## 5. Proved generic packed-window component

[packed_window.py](packed_window.py) defines an all-raw generic read, with
no host evaluator, transition callback, immutable data ROM or state addition.
Its input is actual raw Mem340 at offsets[-8,+8]. For copy index q in0..4,
incoming source centre c in{-1,0,1}, bank lane lambda in0..16, bit phase
b in0..19, stride p in{1,5}, count n in0..20, output bit i<n reads the
five physical raw bits

    u_i = S[q] + c - 2 + floor((b+p*i)/20)
    physical holder d = u_i + S[h],   h=0..4
    payload bit = (b+p*i) mod20,     selected lane lambda,

where S=(0,-2,-1,1,2). It outputs their bitwise3/5 vote. Every malformed
control gives0. Controls may be encoded by q3,c2-signed,lambda5,b5,p3,n5
bits; all their unused patterns are covered. The caller must physically
place the first packed container at source-centre−2. Correct logical
Address/packing is a caller premise, not substituted into the local function.

**Universal all-raw correctness of the component (proved).** For every
input Word340 pattern, vote-first-then-extract equals extract-five-bits-
then-vote. For a chosen output bit this is the identity between the ten
triple-AND majority formula and a threshold of three among five independent
bits. The checker exhausts its32 assignments; different output bits simply
apply that identity to the exact indexing above. Other payload bits and
lanes are irrelevant. The checker also proves the quotient/remainder identity
20*chunk+bit=b+p*i for all800 phase/stride/output cases.

**All-raw physical locality (proved).** Since b+p*i<=19+5*19=114,
chunk ranges0..5, so u ranges−5..6 and physical holders range−7..8.
The radius is at most8 even with arbitrary raw GF/Age/Head controls:
no data-dependent physical lookup occurs. It is exactly8 for this declared
family, as the retained endpoint cofactor changes a third vote at d8.
Six containers are necessary for unrestricted phase. The tempting assertion
that20 stride-five bits always occupy five containers is false when b>=5.
The component uses the fixed incoming centre c and raw-holder offsets,
not a selected head-centre replacement for all five holders.

**Explicit finite implementation (proved).** The word vote is the OR of
ten triple ANDs, independently for each bit. Precompute it at12 logical
container centres for17 lanes and20 payload bits:118,320 fan-in-two
AND/OR gates. One-hot selectors choose q,c,lane and phase/stride/count;
the declared loose bound is185,460 total AND/OR/NOT gates, with no stored
truth table. The checker derives the terms of this bound. Fixed source
ports are circuit wiring counted by the selector gates. This bound is
neither optimal nor the full rule's hardware cost.

This component replaces serial consuming of up to20 input bits in one
**proposed** native update after physical alignment. It does not remove
travel, guarantee packed input, or implement its own software branch.
In particular, software self-simulation still must reconstruct every
selected upper raw word and execute these votes/window calculations with
counted registers and beta. No speedup or Q-fit follows just from hardware.

## 6. Whole-resource and deadline ledger

| Obligation | Status in this checkpoint |
|---|---|
| Exact frozen full-listing cost partition | proved |
| Parallel-word raw-alphabet/cardinality obstruction | proved for stipulated layout |
| Count of proposed hybrid fields | proved arithmetic; sufficiency unproved |
| Generic raw packed-window data identity and radius8 | proved |
| Generic finite hardware gate upper bound | proved for this component |
| Packing/compaction/expansion with actual binary histories | unproved |
| ProgrammeBits or explicit immutable-Q-code choice/refinement | unproved |
| Total local equations for proposed Head/tags/reset/store | unproved |
| Emitted own branch for packed-window and all CPU modes | unproved |
| Whole beta<=8192, including descriptor/controller data | unproved; none emitted |
| Universal movement/branch/packing cost and late deadline | unproved |
| Stage3 authentic computed-flag/courier delivery | unproved in this proposal |
| Full encoded clean/E0/damaged period | unproved |
| Literal Gray refinement/positive-rate theorem/refutation | unproved |

At baseline, a112Q+1 birth leaves execution rows112Q+2..120Q, namely
65,535 updates. The third bank ready time leaves an earlier stage3 budget
of8Q minus its capture/birth delays for native flag calculation and delivery.
Those are exact schedule constraints, not established prepared execution
bounds for this proposal. No schedule change, no lower U and no assertion
that a theoretical constant a or b is small enough is made.

The next runnable target is an actual packing/reset kernel and an emitted
loop interpreter for this representation. It must count every raw malformed
Head/tag/code case, not just a prepared normal path. If it needs immutable
dictionary data or wider PC/code, that is a different proposal with an
explicit budget. A successful component does not yet test Gray's full
construction. The earlier literal printed predicate contradiction and
conditional stage-envelope obstruction remain separate accepted results.

## 7. Receipts

Run the new checker:

    python3 Report/proofs/gray_counterexamples/unregistered_gbd0/check_design.py --output /tmp/GBD0_certificate.json

The checker only reads frozen GBC6 and the primary paper, recomputes all
new arithmetic/locality/Boolean claims, and separately marks selected
random full-word comparisons as measured. The standalone read-only
validator pins new proof/source/receipt and the exact inherited listing,
frozen manifest/terminal replay receipts, and primary text. It does not
recompute or upgrade inherited whole-rule claims. All prior rule/main
documents remain unchanged.

The first provisional layout checker failed because the listed fields were
incorrectly summed as 745 rather than 645. The old proof/checker are retained
with the failure record; correcting this arithmetic changes no automaton.

Standalone read-only replay:

    python3 Report/proofs/gray_counterexamples/unregistered_gbd0/validate_gbd0.py --output /tmp/GBD0_readonly_validation.json
