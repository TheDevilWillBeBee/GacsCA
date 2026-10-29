# GBD2: literal raw-slot packing block and its conditional deadline

Q=8192, U=128Q, lambda24 and c104 remain the target. This is a new,
explicitly changed packing/storage component for the counted GBD0 hybrid
proposal; it is not the frozen GAW2R/GBC6 rule or a complete new rule. It
does not have an own beta, evaluator, supplied native prefix or physical
gathering stage. The errors/noise hypotheses of Gray's theorem are not
asserted. No error witness or shorter U is claimed.

The generic reader's physical-slot correction in GBD1 is used throughout.
All prior frozen sources/receipts remain unchanged. The exact missing
whole-rule/code/runtime obligations are listed at the end.

## Defined fields and total local equations

[packing_kernel.py](packing_kernel.py) implements the complete new block.
It consumes the centre's **already computed** native Address13 and Age20
as declared ports, and reads these actual SF fields at each physical cell:
three17-bit History banks, Word340 packed work, Tag13 and Valid1; each has
five independent backup slots. The slots S=(0,-2,-1,1,2) represent logical
cell x+S[q] at physical x. A logical vote at y reads physical y+S[h], slot
INV[h]=(0,4,3,2,1)[h]. Every input field is voted bitwise, with the ten
triple-AND formula, before any update. History is unchanged by this block.

At output holder x/copy role q, let y=x+S[q]. The service Address is
`(computed_native_GF(x)+S[q]) modQ`, and the time port is the centre's
computed native Age. This is an explicit control convention. It never
reads a neighbouring cell's computed native field. It is coherent under
canonical GF/common clock; its damaged-native composition is unproved.
The entire block reads only physical offsets[-5,+5]. Native ports are not
a hidden host native evaluator and are not silently supplied by a full rule.

The target raw record has K3262 bits at normal residues
P=Q/2-K/2=2465 through P+K−1=5726. There are N=ceil(K/20)=164 chunks.
For chunk h, source and destination are

    source(h) = P+20h+min(20,K−20h)−1
    destination(h) = P+h.

At time S=72Q+3, each represented residue P+i resets its work/tag/valid,
takes the temporal majority of its actual three voted History17 values,
and inserts lane bit lambda at Word340 position20*lambda+(i mod20).
Its tag is floor(i/20), valid1. All other residues reset to0. Thus arbitrary
old packing fields cannot affect the packing seed under this clean clock.

During S+1 through S+19, a cell ORs its old voted payload with the old
voted left payload only when both are valid and their tags agree. It keeps
its own tag/valid. At S+20, only chunk-end residues load carriers, checking
their tag against the local chunk index; all other residues clear. The last
two-bit chunk's unused Word20 positions are masked at this load.

During S+21 through DONE, a carrier with an admitted tag moves left while
its Address is greater than P+tag, then holds at P+tag. Incoming eligibility
reads the old packet at y+1. There is a guard at both frame edges and
on tag<N, so no wrap courier is used. If a held self packet and an eligible
incoming packet collide, output is0. Every other malformed/empty case is
explicit in the code. Outside the stated phase range the voted old packet
is held. These are total local equations on all finite field/control values,
not a correctness claim for corrupted controls or tags.

## Conditional universal packing theorem

Assume the ports are canonical GF/common clock, all lower copies of each
History/packing field coherently represent one logical value, and no error
occurs during this block. The History values may be arbitrary independent
17-bit values at every logical coordinate in each of the three banks.
No equality of the banks, or chosen upper command, is needed. Let T_i be
their bitwise temporal majority at residue P+i. Then at DONE the actual
five-copy packed work at residue P+h contains, for every lane lambda,

    sum_{i=20h}^{min(K−1,20h+19)} bit_lambda(T_i) * 2^(i mod20).

The tag is h and valid1. Packing fields are0 outside P..P+N−1, in every
colony. This theorem is conditional on the declared native ports and
coherent input histories. It does not derive those histories from a complete
autonomous machine or an intact recursive initial configuration.

**Raw coherence closure.** Each output slot q invokes the same logical
operator at y=x+S[q]. The exact physical inverse-slot vote returns the
logical field there, for arbitrary coherent values. Under the port premise,
the service Address is y modQ and the time is common. Therefore the literal
raw block is the five-copy encoding of the logical block at every row.
No primary-slot substitution or noise-free host field fetch is used in that
raw identity. The checker verifies the source slot identity and supplements
it with actual local updates for every copy role at phase/frame boundaries.

**Merge.** By induction, after j merge ticks the payload at i is the OR of
seed bits at indices max(20floor(i/20),i−j)..i. Tags prohibit cross-chunk
mixing. At each chunk end, j19 collects the complete chunk. Every seed
occupies a distinct Word20 bit position, independently in17 lanes, so this
OR identity holds for all temporal input values. The checker uses symbolic
source sets; its proof does not depend on a selected numerical input tape.

**Transport.** After t transport ticks, carrier h is exactly at

    position_h(t) = max(destination(h), source(h)−t).

Both source(h) and destination(h) strictly increase with h, so these
positions are distinct. An incoming moving packet cannot collide with a
held predecessor: if positions become adjacent at P+h and P+h+1, the
right packet's own destination is already P+h+1 and it stops. Thus the
collision branch is never entered in this admitted coherent trajectory.
The controller simply copies arbitrary payload values, making this formula
and the data identity universal for the stated family. The checker follows
every transport row/site for one arbitrary full-value payload assignment;
the universal data conclusion follows from the copy-only transition and
the data-independent position formula, not from that one run.

Maximum travel is3098; loading is at S+20. Consequently

    DONE = 72Q+3+20+3098 = 592945 < 73Q = 598016.

The block takes3118 updates after its seed, plus the seed update itself.
This is a universal **component** deadline, not an interpreter or period
deadline. It lies in the third active interval64Q..80Q; no stage endpoint
or U has been changed. Whether the actual early computation/flag couriers
fit the remaining interval is unproved.

If a future verified three-gather prefix supplies the actual encoded raw
record bits of C[j+lambda] at the17 lanes of each residue P+i, this theorem
places those raw bits in the compact input words. Coupled with the corrected
GBD1 window reader, this gives an exact route to the actual raw input bits
for an own evaluator. Supplying that prefix, controller/Head alignment and
every software branch is still required; the implication is not a supplied
full period.

## Resource and proof status

This block uses51 History bits,340 packed data bits,13 tag bits and1 valid
bit:405 logical SF bits, or2025 bits with five backups. These fields are
already included in GBD0's proposed K3262, so it adds no new state to that
counted proposal. There is no immutable dictionary, controller data ROM,
host transition opcode or extra packet list in the local equations. The
global packet map in the checker is a proof/trace instrument; the literal
local block reads only its fixed radius5 neighbourhood. Full hardware gates
and own software bytes for this block have not been emitted or counted.

| Step | Status |
|---|---|
| Total finite raw-slot packing/reset/transport equations | proved component |
| Literal raw-to-logical coherence closure | proved under canonical/common ports |
| Arbitrary temporal-data merge and transport | proved under stated coherent premise |
| Maximum3098 travel and DONE<73Q | proved component deadline |
| Corrected inverse-slot data accesses | proved |
| Autonomous native port prefix/gather/History derivation | unproved |
| All-raw own software and full beta<=8192 | unproved |
| Head/controller binding, full evaluator and late deadline | unproved |
| Authentic Flag1/Flag2/source/rest/commit integration | unproved |
| Encoded period, E0, higher-error or iid theorem | unproved |
| Faithful Gray refinement, counterexample or shorter U | unproved |

Read-only replay:

    python3 Report/proofs/gray_counterexamples/unregistered_gbd2/validate_gbd2.py --output /tmp/GBD2_readonly_validation.json

The standalone replay pins every frozen GBD0/GBD1 dependency and recomputes
all new kernel/packing/transport claims. No active rule or main document
is edited.
