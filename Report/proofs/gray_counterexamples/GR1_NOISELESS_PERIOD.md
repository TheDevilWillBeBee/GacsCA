This proves a deterministic encoded-period theorem for the explicitly
changed diagnostic rule GR1. It does not prove a theorem for Gray's
printed simulation protocol, nor any reliability theorem.

Let A be GR1's 386-bit alphabet, Π its pinned 8192×1024 table of 24-bit
instructions, M its pinned radius-5 Boolean netlist, and F the local rule
obtained by supplying M with I=Π[laddr,psel]. The lookup outputs depend
on the raw local input, not on I. F denotes the same fixed rule at both
physical and simulated scales. Q=8192 and U=128Q=1,048,576.

Enumerate the bits of A in schema order and let ℓ(b) be the pinned layout
cell of bit b. These 386 cells are distinct and are disjoint from
{3,Q−3,3850,4341}. The layout and the exact instruction listing are
reconstructed by the universal own-programme checker.

For s∈A^Z define E(s) as the following family of physical configurations.
Every physical cell y has Address y mod Q, Age 0 and all four native and
Workspace Flags 0. Every simulation field except Info is 0. There is a
logical Info bit D(y) at each integer y; its five physical copies are
coherent, with copy slot t∈{−2,…,2} in holder y equal to D(y+t).
Require D(iQ+ℓ(b))=s_i[b]. Logical Info values at unrepresented cells are
arbitrary. Define Δ at a period boundary by reading the primary Info bit
at iQ+ℓ(b). Then Δ(c)=s for every c∈E(s).

**Theorem (noiseless GR1 encoding).** For every doubly infinite s and
every c∈E(s), the noiseless physical evolution satisfies

    F^U(c) ∈ E(F(s)).

Consequently Δ(F^{nU}(c))=F^n(s) for every integer n≥0. This is a
deterministic self-simulation assertion for this fixed, explicitly changed
prototype. No noise set is permitted in the theorem. No finite boundary
or statistical hypothesis is used.

**Proof.** The native canonical-geometry invariant proves that, for every
physical phase and every common 20-bit clock, the new Address stays
canonical and the common clock increments modulo U, even with arbitrary
native and Workspace Flags. Thus throughout this evolution computed
Address is canonical and computed Age is the actual next clock. The
all-simulation-field wipe is always false: computed Address equals the
current Address. This step uses the exact native invariant certificate,
not a bounded-clock numerical recovery observation.

Workspace flags are 0 outside computed Ages [96Q,98Q). Starting with native
Flags 0, the h1 native equations keep Flag1=Flag2=0 before the pulse can
enter the next native update. In particular all first-three-stage mail
transport is unblocked. When the fourth stage begins at 96Q, the two mail
tracks are reset to 0. No later stage moves mail or loads a courier, so
they stay 0 thereafter, even with nonzero computed Flag1. The primitive
therefore retains coherent copies throughout: before the pulse its
holder-local Flag1 masks are 0, and afterwards the only fields with such
masks are already 0. All other simulation outputs have the zero native
wipe mask throughout.

The complete clock/Address routing partition and the full-GR1 forwarding
coupling prove the tracked-field transitions. In a gather stage beginning
at S∈{0,32Q,64Q}, mail is reset at S and snapshots Info at S+1. A Mailbox.R
bit moves one logical site to the right each active tick; a Mailbox.L bit
moves one site to the left. For nonlocal offset o, the destination is
ℓ(b)+skew(o). The capture tick is S+2+d, where

    d=|o|Q+skew(o) for o<0,
    d=|o|Q−skew(o) for o>0.

The current mail read at that tick has propagated d steps from the
snapshot. Its origin is exactly ℓ(b)+oQ. For o=0 the separate own-input
lane reads Info at S+1. All 33 coordinate identities are checked and every
capture is before S+16Q. No represented Info cell changes during the
period: the only intermediate Info writes are at 3 and Q−3, which the
layout excludes. Thus all three histories supply the same s_{i+o}[b] at
every compiler input location. Their selective resets preserve completed
earlier histories. The stored temporal-vote bank at 112Q+1 supplies those
same inputs.

The physical front has five distinct compact register cohorts per colony,
with centers five sites apart. Its five holders never overlap another
cohort's holders. The nonmatch control-class certificate covers every
instruction visit and proves that each holder reads the same corrected
register and data operands, computes the specified interpreter operation,
and produces coherent new registers and pending stores. Nonarriving slots
produce 0. At the first tick of each evaluator window, the front's register
source is reset to 0, independent of older contents. The pending-store
coupling proves that the next tick forwards the same value into Hold or
scratch. The abstract schedule only reads scratch at least one tick after
its write, so its scratch reads have exactly their proved abstract values.
The stage resets occur outside both evaluator windows. No intervening
reset can cancel a required pending store.

During the early window, physical computed Age 70Q onward, the gathered
inputs are stable. The universal prefix certificate puts the correct new
upper Flag1/Flag2 in coherent Hold at 4341/3850. These outputs are
I-independent native outputs, so the prefix does not need the final lookup.
All prefix writes, including their one-tick pending application, precede
the two courier loads. The load coordinates and propagation times prove
that the unrepresented Info cells Q−3 and 3 receive these flags at 80Q−1.
The couriers have completed before mail resets at 96Q.

During the fresh final window beginning at 112Q+2, the universal abstract
programme computes its lookup key before Match. The physical Match
certificate proves all 512 ticks, five fronts and five copy holders with
arbitrary registers/instructions. Front0 visits each work-row key exactly
once. Before that hit its selector is unchanged; at the hit it loads all
24 instruction bits from Π[key,selector]. The Address key is not overwritten
and never revisited. The overlapping selector/instruction buffer therefore
cannot cause a second hit. The next forward page starts at the same final
center and carries the loaded instruction. The other fronts' post-Match
registers are immaterial: the abstract checker discards them and verifies
that every later required register/scratch value is defined.

There is one special case. If the upper key is outside the work rows,
front0 does not load an instruction. Every such ROM row is 0. The actual
upper netlist gates every instruction and match write by an arriving
logical Address being inside the work rows; otherwise its front merely
carries, or all front outputs are 0. Every other upper output is
I-independent. Thus in this case the computed upper output is independent
of all 24 I-buffer bits, and equals the output for the correct zero
instruction. The abstract programme is universally correct for arbitrary
I, including this possibly correlated stale buffer. This establishes the
same result in both key cases without assuming a correct nonexistent fetch.

The universal own-programme identity now gives exactly F(s)_i[b] in Hold
at every ℓ(b). The full replay assumes no early register/scratch residue.
All listed writes and their pending applications end before 120Q. Later
zero instructions perform no Hold/scratch writes. Hold is preserved through
the final rest interval. Registers/pending fields are 0 after their declared
window closes, before 120Q, so they are 0 at the next period boundary.

It remains to verify native Flags at that boundary. Both Workspace flags
are 0 in the state with Age 98Q and remain 0 until the next pulse. The
healthy-geometry flag certificate proves the following exact h1 implications.
A cell with at most one possibly flagged positive in-colony neighbour
computes Flag1=0. A zero Flag1 suffix therefore grows from the right colony
edge by at least two cells per clean tick, and clears the whole colony in
ceil(Q/2) ticks. Once Flag1 is everywhere 0, a cell with at most one possibly
flagged negative in-colony neighbour computes Flag2=0. A zero Flag2 prefix
grows from the left edge by at least two cells per tick, clearing the colony
in a further ceil(Q/2) ticks. These facts hold for arbitrary remaining Flags
and arbitrary common clocks. Thus all native Flags are 0 by Age 99Q,
well before the next boundary. They stay 0 with Workspace flags 0.

At computed Age 0, Info takes the coherent previous Hold values while
Hold, mail, all histories, voted data and scratch reset to 0. All private
front fields and both Workspace flags are also 0; the native state is
canonical Address, Age 0 and Flags 0. At represented cells Info contains
F(s)_i[b]. Unrepresented Info values, including the two unused courier
source cells, are allowed by E. Five-copy coherence is preserved. The new
configuration therefore belongs to E(F(s)), completing the proof. ∎

All implications above are exact local/coordinate identities plus the
explicit composition argument. The proof is not a million-tick sampled
simulation or a formally verified proof-assistant development. Source and
receipt hashes are pinned by the checkpoint validator.

**Departures and remaining tasks.** GR1 corrects healthy Flag2 erasure to
h=1 and reads corrected current SimBit for Workspace, whereas the printed
text specifies computed SimBit. It uses an instruction table indexed by
both Address and selector, not Gray's one-ProgramBit-per-Address interpreter.
The table has 201,326,592 logical bits and 27,571 nonzero 24-bit words;
their 661,704 payload bits have not been compressed into Gray's Q=8192
ProgramBit positions. Its multiple fronts and their clearing outside the
evaluator windows are an explicit microcode choice. The theorem proves
closure of E under clean periods; it does not prove the printed rest rule
on arbitrary damaged raw states. Native-control/copy premises after errors,
continuing E0, real1 simulation recovery, localization at higher levels,
the literal computed-SimBit refinement and all iid claims remain unproved.
