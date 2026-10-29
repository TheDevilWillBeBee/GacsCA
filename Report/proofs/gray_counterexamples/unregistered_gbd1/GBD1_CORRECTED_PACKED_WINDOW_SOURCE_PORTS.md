# GBD1: correction of the GBD0 physical backup-slot claim

All GBD0 sources/receipts remain frozen. Its complete listing partition and
state-layout cardinality argument are unaffected. Its abstract function on
one supplied Word340 at each physical coordinate remains a proved function.
**Its asserted refinement to the proposed five-slot raw physical alphabet
was incomplete.** No automaton, beta or error history had been emitted.

The missing distinction is substantive on arbitrary raw states. At physical
cell x, backup slot q stores the logical SF payload at x+S[q], where
S=(0,-2,-1,1,2). To vote a logical container u, holder u+S[h] must therefore
supply its slot INV[h], where

    INV[h] = the index of -S[h] in S = (0,4,3,2,1)[h].

Different logical containers can read different slots at the same physical
cell. A single payload raw_mem[d] cannot represent all those independent
ports. Treating it as the primary slot at each d can change the result.

[packed_window_slots.py](packed_window_slots.py) supplies the corrected
total generic component. The input at each physical offset d=-8..8 is five
independent Word340 payloads, raw_cells[d][q]. A finite control encoding has
q3,c2-signed,lane5,phase5,stride3,count5 bits. All unused control values give0.
The old native fields are not inputs to this component; no future native,
Workspace, tape or Head state is supplied or assumed.

For an enabled output bit i<count, let

    chunk, bit = divmod(phase + stride*i,20)
    u = S[q] + centre - 2 + chunk.

The five actual raw source ports are

    (physical=u+S[h], slot=INV[h], bit=20*lane+bit), h=0..4.

The output is the threshold-three vote of these five bits. q names the
output packet's backup role, centre is its incoming logical shift{-1,0,1},
and the first packed container must be physically aligned at that source
centre−2. This last packing/alignment requirement is a caller premise,
not a synthetic Address or bank hidden inside the primitive.

The following claims are proved:

1. **All-raw port identity.** The physical/slot pair represents u because
   `(u+S[h])+S[INV[h]]=u`. The checker verifies that identity at every
   declared control/output/holder combination. No matching payload or
   coherence is assumed.
2. **All-raw data identity.** For every independent raw payload, extracting
   the five selected bits and threshold-voting equals voting their five
   Word20 values bitwise and extracting the chosen bit. This follows from
   the32-assignment majority truth table, independently for every output
   bit. Selected random full-value comparisons are measured supplements.
3. **Coherent encoding identity.** If raw_cells[d][q]=logical[d+S[q]], all
   five selected payloads are the same arbitrary logical[u] Word340. The
   output equals the stated packed-window extraction from that logical
   array. Coherence is used only for this corollary.
4. **Exact physical radius.** phase+stride*i<=114, so chunk0..5, u=-5..6,
   physical offsets=-7..8. An exact third-vote cofactor at the actual slot
   of d8 attains radius8. Source slots do not enlarge the stencil. Reading
   six containers remains necessary for arbitrary phase.
5. **Explicit finite hardware.** The GBD0 bound185,460 fan-in-two Boolean
   gates still applies after rewiring each of its five vote inputs to the
   matching slot. It precomputes12*17*20 bitwise votes, then the exact
   finite control selectors. There is no immutable data table or new state.
   This is a component bound, not full-rule hardware/programme accounting.

The retained exact slot0-projection witness uses logical u=-2. Its third
vote is supplied by the auxiliary ports at(-4,slot4),(-3,slot3),
(-1,slot2), all bit0, with every primary slot0 and other port0. Correct
output is1; reading only slot0 at each coordinate gives0. This is a finite
raw-port cofactor exposing a reconstruction gap, not a noise history or
counterexample to Gray's construction.

**Remaining gaps.** The component receives decoded controls as arguments.
Binding them to every raw Head branch, actual three-bank preparation,
packing/compaction/expansion, own software, code<=Q, universal movement/
runtime, authentic flag delivery, computed-SimBit/source order and whole
period/noise refinement are unproved. The counted GBD0 proposal K=3262
and531 descriptor bits remain proposed resource arithmetic, not beta-fit
or physical-period certificates. Matching Q8192/U128Q/lambda24/c104 does
not discharge the radius8/word-work/programme/rest departures from Gray.

The parent should retain the GBD0 abstract source-model limitation and cite
GBD1, rather than reinterpret old one-payload code as five-slot code.

Read-only replay:

    python3 Report/proofs/gray_counterexamples/unregistered_gbd1/validate_gbd1.py --output /tmp/GBD1_readonly_validation.json

The new replay recomputes every new slot/Boolean/coordinate claim and pins
the frozen GBD0 proof/source/receipt/manifest and terminal replay. No rule,
CURRENT, main report, or accepted proof is changed.
