# SP28 full-rule two-clock closure and auxiliary quiet intervals

This is a theorem about the existing isolated SP28 full transition, not
a new rule. G17, SP28, its ROM and its constants are unchanged. It partly
connects the externally reduced clock-island operator of J150 to the
autonomous full rule. It does **not** realize that travelling island in
the full rule or prove a finite eroder, confinement or iid reliability.

## Statement and initial conditions

Use Q=1024, U=475136, TF=278401, mixed-clock radix928, epoch window4096,
and packet/code lifetime L=1792. Time t denotes the raw configuration
before update t to t+1. There are no further errors. At every physical
site x initially require raw GF=x modQ. All native Flags, simulation
fields and instruction inputs may be arbitrary.

Then raw and computed GF remain x modQ for all t, even if the initial
raw Ages are arbitrary words. The copy keep predicate is always1.

For the rest of the theorem additionally require initial raw Ages in
the two legal phases {0,TF}. At time t, every raw Age and every computed
current Age belongs to

    {age_code(t modU), age_code((t+TF) modU)}.

No constraint on the spatial arrangement of these labels is imposed.
This alphabet closure holds with arbitrary native flags, workspace,
packet/code headers, backward pressure and instruction inputs.

For the quiet-interval claims additionally require initially
WorkspaceFlag1=WorkspaceFlag2=packet_valid=service_valid=backward_pressure=0.
The tag/position/count fields of invalid records can initially be
arbitrary. Set

    B = {nU, nU+TF : integers n>=0}.

Packet births occur only in input rows b in B. In any interval following
one such b and before the next one:

* Valid packet/code records and raw WorkspaceFlag2 can occur only in
  states b+1,...,b+L. A valid record in state t has count t-b-1.
* All packet/code headers, including their invalid position/count
  payloads, and WorkspaceFlag2 are zero by state b+L+1.
* Computed coded/packet service force can be nonzero only in input rows
  b+1,...,b+L. The last row allows an expired packet cohort, even though
  it cannot produce another valid record.
* Computed backward signal can be nonzero only in rows b,...,b+L.
  Raw backward_pressure is zero by state b+L+2.
* Raw WorkspaceFlag1 can be nonzero only in states b+1,...,b+2Q and
  only in the last five sites of a true colony.

Consequently, on every input row outside

    union over b in B of [b,b+4096),

the full rule's output GF, Age, Flag1 and Flag2 is exactly the output of
the auxiliary-zero native/epoch operator on the same raw native state.
The literal Flag2 commit reset is included on both sides. This agreement
concerns a single update on every quiet row. A long quiet interval may
be advanced by a proved native invariant if its initial native state
satisfies that invariant; the theorem does not assert that pulse dynamics
leave the aligned template of J150.

## Proof of address closure

In each distant five-holder joint GF/Age block, subtracting the physical
displacement from canonical GF produces the same GF word at the reader.
The whole-word majority returns either a word supported by at least
three inputs or the raw self-word. Every such word has that canonical
GF component. This remains true when no Age majority exists.

All four resulting block words therefore have identical canonical GF.
The bitwise three-of-four GF is that word, and both branches of the
joint-quorum mux have that GF. Hence each of the eleven refined GF
words remains canonical, without any assumption on raw Ages.

Both the native right and left adjusted-GF five-votes now exist and
return the reader's canonical word. The native selector can depend on
arbitrary flags/service forces; either selected GF is canonical. The
raw GF output is that selected word. Induction proves the claim for all
t. Because the computed GF equals raw self-GF, the literal wipe
predicate Flag1_new AND (computed_GF != raw_GF) is false, so keep=1.
This is a conclusion about the copy mask, not data correctness.

## Proof of two-clock closure

Assume raw Ages at time t are the two specified legal words. Each
distant five-holder joint vote has a three-of-five majority of one
phase, because all adjusted GF components agree. Thus every block
result is one of the two words and exists. A joint three-of-four quorum
either selects a block word repeated at least three times or keeps the
raw self-word. It cannot create a third word: a successful quorum
explicitly tests equality of at least three existing block words with
the bitwise candidate. The refined Ages still belong to the two phases.

Each native directional five-Age vote likewise has a majority phase.
The special left-Age fallback is inactive because the left GF exists.
The selector therefore chooses one of those two words as Age_now,
whatever native/workspace flags or service force it sees. Legal mixed
increment maps each phase to its phase at time t+1. The phases never
coincide, since their difference TF is nonzero modulo U. Induction
proves closure. Neither programme output nor simulation-field updates
write the native Age directly. The proof allows arbitrary instruction
inputs, and therefore applies in particular to the actual own ROM.
The retained SP28 native certificate already checks the literal mixed
increment on every one of the475136 legal clocks. The packed legal
codes increase with chronological age, so the comparator endpoints
used below have exactly their stated chronological windows.

## Proof of record lifetime and temporal separation

The literal right-epoch helper uses a right five-Age vote. Under closure,
its age is one of the two current phases and its existence bit is true.
The equation for packet_birth requires its age exactly TF, so possible
birth rows are exactly the two congruence classes B. The shortest
distance between consecutive possible batches is

    min(TF,U-TF)=196735 > 4096 > L+2.

There are no initially valid records. Invalid initial payloads cannot
become an ancestor: packet eligibility includes packet_valid and wf2;
code eligibility includes service_valid. Full outputs wf2 and
packet_valid are identical, so their equality is preserved.

At a birth update, the packet count is0. Any valid nonbirth packet output
comes from a qualified packet cohort. Its selected input counter c must
obey c<L-1, and its output count is c+1. Every valid code output similarly
comes from a qualified combined-record cohort. Its chosen combined
record is either an eligible packet or an eligible code, with count
c<L-1; again its output count is c+1. Within a physical cell the
minimum-counter choice changes the ancestor, not the selected count.
Between cohorts the same is true. An output may be erased by commit,
but commit cannot generate a valid record or reset a surviving count.

Inductively, between births every surviving valid record in state
b+1+s has count s. An output from a record with count L-1 is not
qualified. Therefore the last possibly valid state is b+L and the
next state b+L+1 contains no valid record. The helper also returns zero
tag/position/count when no qualified output exists. After that state
all packet/code headers stay zero until a new batch.

The service force is computed flag_valid OR packet_any_cohort.
The latter deliberately does not test the lifetime guard, so at input
b+L an expired raw packet cohort may force one final row. At the next
input no valid record exists and both terms are zero. Hence the claimed
input-row bound includes that last row. The spatial arrangement and
minimum-counter competitions do not affect the ancestry argument.

No later birth overlaps the lifetime just proved. In the gap all
validities are zero, which reestablishes the induction base for the
next batch. This proves the statements on the infinite time axis,
without a finite-horizon measurement or an externally cleared field.

## Proof of backward/workspace supports and native agreement

The backward helper's RF clock window is [TF,TF+1792] inclusive.
Its packet and right-pressure inputs can be arbitrary, but that window
multiplies the entire computed signal. Clock closure confines the signal
to rows b,...,b+L. The raw backward bit at t+1 is that signal, possibly
cleared by commit, so it is zero from state b+L+2 onward. This computed
signal is the force used in native maintenance; raw pressure outside
the window cannot force a native update.

WorkspaceFlag1 output is guarded by computed current GF in [Q-5,Q)
and computed Age_now in [TF,TF+2Q). Address and clock closure give the
stated last-five-site and row bounds, irrespective of the corrected
Info signal. An output in row b+s, 0<=s<2Q, becomes raw workspace at
b+s+1. Thus the final possible raw nonzero row is b+2Q. It is zero
from state b+2Q+1 until the next possible pulse.

All these native inputs/forces are zero outside [b,b+4096):
WorkspaceFlag1/2 are zero, coded/packet service force is zero, and the
computed backward signal is zero. The right-epoch force is already the
force retained in the reduced operator, and it is zero on these rows
as well. Native Flag1/2/GF/Age use no other auxiliary fields or
instruction bits. The full output Flag2 has the same final commit reset
as the reduced operator. Substituting these zeros proves literal native
one-step equality on every quiet row. This completes the theorem.

## Status and remaining bridge

| Step | Status | Limit |
| --- | --- | --- |
| Canonical GF/keep=1 closure with arbitrary raw Ages and auxiliary fields | proved | No further GF errors; no data-correctness conclusion |
| Two legal clock phases closed under the full rule | proved | Canonical GF and stated initial alphabet; no later Age errors |
| Packet/code lifetime, backward/window and workspace supports | proved | Initially zero validities/workspace/backward; no further errors |
| Full native update equals auxiliary-zero update on all quiet rows | proved | Outside the two4096-row slabs per period; same actual native input |
| Full pulse dynamics preserve or destroy J150's travelling island | unproved | Workspace signals and generated service records act during pulse slabs |
| Full finite-island eroder, data confinement, higher-error lift, positive iid ε | unproved | No conclusion from alphabet closure or auxiliary expiration alone |

The checker pins the actual full wiring, checks all1024 GF phases with
free Age/flag inputs, exhausts the two-label vote primitives and legal
clock/window arithmetic, and checks restricted service cofactors at
lifetime endpoints. The universal lifetime proof is the counter-ancestry
argument above, not an extrapolation from those local cofactors. No C,
CUDA or noisy full-state experiment is used here.

The first checker invocation failed at import, before any mathematical
check: maj5 is defined in gacsca.rule_g rather than gacsca.netlist.
The original checker and failure receipt are retained in figs/robustness.
Correcting the import changes no rule or mathematical statement.
