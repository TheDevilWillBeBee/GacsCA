# SP30: reserve repair-signal aliases from the ordinary encoded state

SP30 is an **explicit, isolated rule and encoding change** to SP29.
It keeps every primitive parameter: Q1024/U475136, width842, radius37,
64 capture ranks, TF278401, force2048, NPe272/MP289/NP384. It moves
ordinary h2:77 from509 to901 and h2:83 from515 to902. The opposite-phase
repair-signal aliases509/515 are reserved. At commit the Info mask is

    A30=([58,901) minus {509,515}) union {901,902,965}.

The normal842 primaries are A30 minus the early-flag Hold locations58/965.
The native controller, transport recurrence, signal clock, couriers,
reset clock and other storage locations are retained verbatim. The
two input/output representation locations, their sparse history-capture
controls and the literal Info commit mask change. Every compiled macrocell simulates this **same changed
rule**, using its own freshly compiled ROM. G17, CURRENT, SP29 and the
active compiler are unchanged. No globally sufficient or smallest
reliability change is claimed.

The [rule](proposed_sparse_signal_reservation1024.py),
[builder](build_sparse_signal_reservation1024_program.py),
[symbolic checker](check_signal_reservation1024_schedule.py),
[native checker](check_signal_reservation1024_native.py),
[front checker](check_signal_reservation1024_front.py), and
[interface/encoding checker](check_signal_reservation1024_encoded.py)
are separate files. Receipts are stored under SP30 in figs/robustness.
The initial interface checker queried a candidate hash absent from the
native-only receipt. Its checker/log are retained; the dependency check
now uses that receipt's actual full netlist hash. This was a metadata
lookup defect before the interface checks, not a mathematical failure.
The next checker correctly rejected the draft's assertion that all837
non-Info outputs were unchanged: moving represented primaries also
retimes80 h1/h2 outputs through the sparse capture table. Its failed
checker/log are retained. The statement below records those changes;
the already compiled new target and its symbolic programme are unchanged.
A subsequent checker count included23 ROM-control outputs among state
bits. That failed checker/log are also retained; state and control
outputs are now counted separately. All23 controls are unchanged.

## Exact interface theorem

For an arbitrary raw radius37 neighbourhood,757 non-Info output
bits of the new full rule equal the corresponding SP29 Boolean
functions. The80 remaining non-Info outputs are h1/h2 ranks0..7 in
each of five slots. Their capture lookup removes the two old phases
509/515 and adds901/902, retaining offsets(-4,-3,-2,-1,1,2,3,4) and
all capture clocks. The five Info outputs have the new stated commit mask.
This is an equality of **local functions on the same raw input**, not
a claim that complete trajectories of the different rules coincide.
The checker builds both graphs in a shared Net and compares757
non-Info output nodes exactly, with arbitrary instruction words and
all other inputs free. The other80 nodes have exactly the listed keys.
Replacing only the new capture table with the old table, while retaining
the new Info mask, restores all837 non-Info node identities. The842
table rows retain their fields, bits and offsets; all65536 phase/rank
bindings are compared, with exactly32 changes at the four phases and
ranks0..7. Thus the unchanged sparse-control formula gives precisely
the stated retiming. The changed mask is checked at every phase/slot.

If computed GF equals the refined raw self-GF, and computed input
Age is the commit clock U-1, the actual new commit resets807 bits per
cell and forwards voted Hold into all five Info copies exactly at A30;
every other Info output is zero. The cofactor keeps that refined raw
GF word symbolic, permits arbitrary Flag1/Flag2 and all prior work,
and verifies five literal forwarding identities. These are conditional
interface identities; a damaged trajectory must establish the native
and clock premises before using them.

In particular all signal/alias primaries at phases3,509,515,1021 are
zero at such a commit. If the final quiet geometry is canonical or
shifted512, each of their physical copies has virtual phase in that
same four-element set. Thus **both physical signal tracks and their
half-colony aliases reset to zero**, independently of any old ordinary
Hold value or retained H2 computation. Relocating the two represented
bits preserves every842-bit upper state; no upper field is deleted.
This solves the particular ordinary-data/signal-alias collision in
this new rule. It does not prove a pulse endpoint or subsequent signals.

## Complete-start simulation theorem

Let F30 denote the new fixed rule with its own ROM. Let E30(z) place
every bit of each upper F30 cell z(g) in five coherent lower Info
copies at the842 relocated normal primaries of colony g. Store its
auxiliary early native flags at58/965, use lower native GF=x modQ,
Age0, every other non-Info field0, and every other Info primary0.
Let B30(z,b) instead permit arbitrary coherent unused Info values b
at the182 non-normal primaries, including the four signal/alias
positions and auxiliary early flags.

At each tick t let w_t be the computed state, X_t its state after
arbitrary whole-cell overwrites, and w_(t+1)=F30(X_t). Assume the
**entire location set**, including tick0, is an actual globally
isolated E0 set for lambda24, as defined in the pinned repository:
each group is a singleton or an adjacent pair at one tick, with
separation24 from every other group. Starting w0=B30(z,b), for all
upper configurations z, unused values b, and allowed payloads,

    w_(nU)=E30(F30^n(z)) for all n>=1.

The raw five-copy decoder at each boundary nU, including n0, gives
F30^n(z). This theorem makes no assertion that iid errors satisfy
its deterministic location premise. It is not a finite-island
eroder or a noisy higher-level error-map theorem.

**Proof.** The actual native joint GF/Age refinement and two selection
modes are unchanged functions on raw inputs, including arbitrary
flags, packet/code state, pressure and instruction words. Therefore
the native induction in [SP29_OWN_RULE.md](SP29_OWN_RULE.md) applies
verbatim with identical Q/U and legal clock encoding. E0 supplies at
least three correct words to each relevant five-vote joint block;
the joint refined pair and both native selection modes are canonical
GF/common legal Age. The new native checker also repeats4096 actual
mode cofactors, all475136 legal increments and the literal29 output
wiring identities. Computed GF and refined self-GF agree globally,
so keep=1 at every tick.

Before TF the WF1 guard is closed. Zero native Flag1 and correct
geometry persist under E0. The only pre-commit special Info writes
are at3/1021. All relocated normal primaries are disjoint from these
and the two reserved aliases; their five-voted Info values remain
the given upper bits. No arbitrary unused value enters an ordinary
read. The exact opcode audit checks both operands of every new
instruction, including direct Info and field-specific history reads.

The actual three gathers retain the same speed-eight recurrence and
distance37 window. Their requested source coordinates remain
(g+d)Q+a, with a a relocated normal primary. The largest captures
at4737/14977/25217 precede evaluation25984. The new all-coordinate
and operand audit checks all25284 requested routes. Moving two
phases to901/902 changes no distance, transport step or field-specific
rank. Both locations and all their five holders remain strictly
inside the existing working front/courier footprints.

The new own symbolic programme certificate decodes all131238 actual
instructions, repacks the whole ROM, proves all22 Match bits, both
early flags and all842 final Hold outputs equal the full new F30
Boolean outputs. This includes the changed mask in the rule being
simulated, so no old-rule programme is substituted. Its visits,
pending forwarding, scratch/register causality and capture clocks
are certified. The unchanged physical five-copy/pending/source
induction of SP29/J135/J138 now applies to the new listing: same
centres, directions, schema, copy windows, keep1 and total arrivals;
the two new represented locations satisfy those same geometric
bounds. The new front checker verifies unique arrival and total
ROM indices for all raw native words. The literal operand audit
excludes every unused/special/alias Info primary from reads.

The early stores finish before the same courier loads. Those courier
loads replace any old unused Info/mail references with the newly
computed flags and write the special sources at278401, before the
first enabled WF1 input. Subsequent native Flag1 mail gating cannot
alter completed captures or erase the work because keep1. The same
closed-source native contraction makes F1 quiet by281026, before
evaluation382336 and commit475135. The newly proved807 reset/five
masked-forwarding identities give exactly E30(F30(z)) at the first
computed boundary. This supplies the full next-period premise,
proving the all-period identity by induction. Current E0 overwrites
affect at most two copies of each five-copy group, so the raw decoder
is exact too. The initial decoder is exact directly from B30. QED.

Noiselessly F30^U E30=E30 F30. The same compact nested encoding-image
argument used in SP29/J135 supplies an infinite noiseless hierarchy
for this one fixed rule. This does not prove positive-noise memory.

## What remains open

The reservation removes a specific alias/data obligation for a new
construction. It does not transfer SP29's three damaged-history pulse
certificates: that history must be checked again for **F30**. In
particular the old H2:77/H2:83 timing, scratch-cache identities,
MF509/MF1021 masks and damaged-data source enclosures belong to the
old layout/programme and are not inherited.

No arbitrary GF/Age/private seed eroder, repeated noisy real1 repair,
higher-level simulation error bound, intact iid hierarchy, explicit
positive iid epsilon or globally minimal repair is proved here.
The build's64 replay vectors are measured support only; the own
programme and complete-start theorem use symbolic identities and
the physical induction above. No numerical whole-CA trajectory is
used for these claims.

| Step | Status | Limit |
| --- | --- | --- |
| Explicit relocation/reservation and total finite own rule | proved | New842-bit encoding/own ROM, raw GF/selector bounds |
| 757 non-Info local functions unchanged;80 capture outputs retimed; new commit/alias zeros | proved | Same raw inputs; commit requires native GF/clock premises |
| Build and64 replays | measured only | No universal proof supplied by replay count |
| Own symbolic programme and raw front/native interfaces | proved | New full rule/listing/ROM, all outputs and deadlines |
| Complete-start broad-Info/noiseless/all-period E0 simulation | proved | Canonical/common native start, fresh private fields, actual global E0 only |
| Infinite noiseless encoding hierarchy | proved | Compactness and exact commutation; no iid conclusion |
| SP30 damaged-history signal/pulse, general eroder/higher map/iid epsilon | unproved | Old SP29 damaged-history certificates do not apply to the new layout |
| Smallest globally sufficient reliability change | unproved | Reservation is a concrete local proposal, not global sufficiency |
