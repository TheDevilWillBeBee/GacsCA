# SP31: separate native commands from private service packets

This is an **explicit, isolated rule change**, not a repair applied to G17
or SP30. F31 has Q1024, U475136, radius37 and842 state bits. Its capture
layout, three gathers, five-copy fields, TF278401,2048-update signal
window and primitive NPe272/MP289/NP384 budgets are unchanged from F30.
Its own new ROM is required: candidate
`dc456bac4904647b66ee1f922788cdeb4428df91e21858fd8de0b3ccb4a69421`.

The [proposal](proposed_native_command1024.py) makes four related edits.
Native maintenance receives service_force0. Native Workspace2 becomes
the actual left-special-Info command, guarded by the signal clock,
the computed left-end position and NOT(computed Flag1). Private packet
lifetime retains the former birth/forwarding expression in packet_valid.
Only private service/detector arguments substitute packet_valid for their
old Workspace2 carrier. The private service fields and unconditional
epoch starter remain in the finite alphabet and are simulated by the
new program; they cease forcing native Flag2. No shorter U or smaller
alphabet is claimed here.

This change addresses the extra native service forcing implicated by
J221's F30 history. It is not proved sufficient for reliability, or the
smallest such change. No G17, CURRENT, frozen proposal or active compiler
file changes, and no commit.

## Own rule and program

The [build](../../figs/robustness/SP31_program_build.json) contains91935
gates and130476 scheduled instructions. Actual usage NPe251/MP289/NP374
fits the declared budgets. Its64 random replays have0 mismatches and
are **measured only**.

The [symbolic program certificate](../../figs/robustness/SP31_symbolic_schedule.json)
decodes every instruction, repacks the complete1024-by4096 ROM, and
proves22 Match keys, both early flags and all842 final Hold outputs
equal the new full F31 Boolean functions. Its hypotheses are correct
gathered inputs, the stated abstract front/register/scratch visits,
the correct matched external instruction and no noise in that abstract
execution. It certifies the new program, not a damaged physical period.
Captures finish at input ages4737/14977/25217; early flag stores are
at257973/251472, before courier loads278343/278344. Evaluation finishes
at382336, before commit input475135.

## Conditional local interfaces

Supply the same computed GF, current/new Age and Flag1/Flag2 outputs
to the native-controller interface of F30 and F31. Every SF state
output and ROM control outside the41 private header bits is the same
Boolean function on the same remaining raw inputs. This includes
Info, all three Histories, Mail, all fronts/registers/scratch/pending,
Hold, Workspace1 and23 ROM-control outputs. The private header comprises
Workspace2, packet tag/valid/count, service valid/position/count and
backward pressure. There are824 literal shared-net output identities
(801 state bits plus23 controls).

This is universal in both clock words: the encoding checker leaves
them symbolic. The earlier [interface certificate](../../figs/robustness/SP31_interface_certificate.json)
also checks six particular clocks. The universal identity follows
directly from the four edits: the modified private expressions feed
only the private header once the computed native outputs are supplied.
It is not an equality between complete F30 and F31 trajectories.

The unrestricted native Flag1 function is unchanged. The live input
dependencies of actual F31 GF/Age/Flag1/Flag2 lie entirely in raw
GF/Age/Flag1/Flag2/Workspace1/Workspace2:1922 input keys, with no
private service/header, SF work or external instruction dependence.
This dependency assertion concerns those four outputs. It does not
remove the actual Info and SF provenance obligation for Workspace2.

At commit, if computed GF equals refined raw self-GF and computed
current Age is U-1,807 private bits reset to0 and the five Info outputs
are voted Hold masked by

    A31=([58,901) minus {509,515}) union {901,902,965}.

Equivalently A31=({58,...,900} minus {509,515}) union {901,902,965}.
The842 ordinary upper-bit primaries are A31 minus58/965. Thus phases
3/509/515/1021, including their half-colony aliases, reset to0. These
are conditional local identities, with every old private value and
Flag1/Flag2 free; they do not establish a damaged history's premises.

## Complete-start simulation under pure E0

Let E31(z) be the F30 relocated five-copy encoding with **F31's** upper
state and own program: GF=x modQ, Age0, all lower non-Info fields0,
the842 ordinary Info primaries encoding z and all unused primaries0.
Let B31(z,b) permit arbitrary coherent unused Info votes b at the182
remaining primaries, including signal/alias and auxiliary early-flag
locations. Every842-bit upper state is represented.

Write w_t for the computed lower state, X_t for that state after
arbitrary whole-cell overwrites, and w_(t+1)=F31(X_t). Suppose the
entire error-location set, including tick0, consists solely of actual
globally isolated E0 groups for lambda24: each group is one singleton
or one adjacent pair at one tick, separated24 from every other group.
For every z,b and every such payload history, starting w0=B31(z,b),

    w_(nU)=E31(F31^n(z)) for every n>=1.

The raw five-copy decoder of X_(nU) equals F31^n(z), including n0.
No claim is made that positive iid errors meet this deterministic
location premise.

**Proof.** At each input tick an E0 group corrupts at most two words
of any five-cell native voting block. The joint GF/Age refiner hence
returns the canonical GF/common legal clock. All four adjusted block
outputs agree; both subsequent native directional choices have the
same canonical pair. Removing service forcing, or changing native
Workspace2/Flag2, cannot distinguish these identical choices. The
increment is the legal mixed-clock successor. Induction gives correct
computed GF/Age for all t, refined self-GF equal to computed GF, and
keep1. The new native checker certifies the actual29 output wiring,
both directional mode cofactors and every475136 legal increment.
No general damaged-GF induction is used.

Before TF the Workspace1 guard is closed. The unchanged Flag1
equations and canonical geometry preserve computed Flag1 zero under
E0. All ordinary Info sources are disjoint from special3/1021 and
reserved509/515, so their voted values remain the given upper bits.
The literal new-program operand audit excludes all unused primaries.
The actual speed-eight gather recurrence extends to distance37;
all25284 requested coordinates and fixed captures remain the same
as F30 and finish before25984.

With keep1 and correct native clock/position, the actual SF outputs
have the same local equations as the physical five-copy induction
in [SP30_OWN_RULE.md](SP30_OWN_RULE.md), ultimately J135/J138. A
current E0 group punctures at most two holders of any five-copy vote.
The source, pending forwarding, register, scratch, capture, Match,
store and courier inductions therefore apply to the **new** listing:
same copy geometry and controls, persistent voted references, total
ROM lookup and unique arrival. The symbolic certificate supplies
F31's new output terms and verifies the actual scratch delays and
visits. No old F30 output/program is substituted. The new all-raw
front checker verifies the retained raw address/selector bounds and
one-arrival limit, and the encoding checker verifies every operand's
ordinary source binding.

Both newly computed early flags reach the unchanged courier loads
and replace any initial unused values before the first enabled
Workspace1 input. Flag1 thereafter may alter late Mail, but cannot
alter completed captures or erase the work because keep1. Workspace2
can change native Flag2, but still cannot change the identical
canonical LF/RF pair or any SF core equation. The unchanged closed-
Workspace1/Flag1 contraction applies verbatim: computed Workspace1
is zero from280450, and computed Flag1 zero by281026, before382336
and475135. The actual commit identities then give precisely
E31(F31(z)). This is the complete next-period premise, proving the
all-period identity by induction. Fresh E0 overwrites at a boundary
affect at most two copies of each decoder vote; its value remains
exact, including the initial B31 boundary. QED.

In particular F31^U E31=E31 F31 noiselessly. The unchanged encoding
geometry and this exact commutation give the same compact nested-
image construction of an infinite noiseless hierarchy used for F30.
This establishes a noiseless hierarchy, not all-time noisy memory.

## Prepared native pulse and its missing bridge

The separate [C factor](sp31_native_events.c) treats a common legal
clock TF+s, two raw GF phases0/+512, arbitrary Flag1/Workspace1,
native Flag2/Workspace2 zero, no errors or Info writes, and voted
Info zero at all physical phases3/515. These are **prepared premises**.
For this restricted factor, adjusted GF differs only in its high bit.
For each reader take five-majority labels in the four blocks centred
at-30,-10,10,30; select a label present in at least three blocks,
otherwise retain the raw self-label. Next take left/right five-label
majorities. Common Age makes age mismatch and absent-Age diagnostics
false, and binary labels ensure the right majority exists, so d3 is
false. With Flag2/Workspace2 zero and service_force0, Flag2 remains0.
The new Workspace2 source stays0 by the assumed Info3/515 zeros.
GF therefore selects LF when computed Flag1 is1, and RF otherwise.

Flag1 has exactly the unchanged inconsistency, right-eight flag,
self-retention, inside Workspace1 and quiet-right clauses. Workspace1
has the actual held right-special-Info source and TF's2048-update
guard. For a logical primary y, its next voted Info is its old vote
times the majority of the five keep predicates at holders y-slot;
each keep is NOT(newFlag1 AND(newGF != refined self-GF)). No unused
private value participates in these restricted equations.

The interface checker compares2048 selected full-net raw cofactors
to the C transcription. These are **measured checks**, supplementing
the algebra above; they are not exhaustive raw-state verification.
The event engine partitions at all native endpoints shifted by
-37..37 and both colony-phase guard boundaries shifted by-8..8.
On each interval the native input tuple and inside/birth predicates
are constant; special Info's address is a fixed primary of that
phase's colony. It checks both endpoint tuples/guards and outputs,
then merges equal outputs. The zero exterior remains zero and voted
Info only erases, giving an exact finite representation of Z for
this prepared pulse. This engine has not been asserted for arbitrary
mixed clocks, GF words or signal positions.

Initially T(128,143) has wrong GF on[128Q-512,143Q), left Flag1 on
[127Q,128Q-512), right Flag1 on[143Q-512,143Q), and Workspace1 zero.
Voted Info509 is1 in colonies128..142; Info1021 is1 in124..126 and
143..145; all other primaries are0. The retained6144-update run gives
T(135,146): wrong GF[135Q-512,146Q), left Flag1[134Q,135Q-512),
right Flag1[146Q-512,146Q), Workspace1 zero. The wrong-GF width
shrinks from15.5Q to11.5Q, exactly4Q, while the two edges advance
7Q and3Q. The trace has9,894,718 event intervals and11 retained
Info-one primaries. This is a conditional finite pulse, not the
first pulse of a proved intact-start fault history.

The missing bridge is substantive. Partial true/foreign frames may
supply unknown actual Flag2 commands at3/515. Initial Flag1 can
temporarily suppress them, but the strip changes during the pulse.
We have not proved those commands zero, bounded their causal effects,
or derived a complete repeated-period bank/source invariant for F31.
J221's F30 damaged-history certificates cannot be imported across
the changed native branch. Arbitrary higher-error erasure, the full
upper error map and explicit positive iid epsilon remain unproved.

| Step | Status | Limit |
| --- | --- | --- |
| Explicit total own rule/new program | proved | New finite1024-by4096 ROM; all raw keys in range |
| Build64 random replays | measured only | Finite compiler checks |
| Universal abstract own-program execution | proved | Gather/front/Match/no-noise hypotheses stated above |
| Conditional SF interfaces and native dependency/Flag1 identities | proved | Equal supplied native outputs; complete clock words free |
| Complete-start pure-E0 simulation/noiseless hierarchy | proved | Canonical common native start, fresh work, globally isolated E0 only |
| Restricted factor algebra/prepared finite pulse | proved conditionally;2048 transcription checks measured | Prepared common clock/two phases/zero native Flag2 and special commands |
| Actual damaged-history special commands and repeated repair | unproved | Partial-frame provenance and next bank not established |
| Gray/G17 refutation, iid theorem or minimum sufficient change | unproved | No such inference from this changed-rule pulse |
