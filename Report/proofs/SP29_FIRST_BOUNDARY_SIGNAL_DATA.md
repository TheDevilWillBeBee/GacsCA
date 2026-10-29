# SP29: retained signal data at the first boundary

This theorem concerns the unchanged isolated SP29 own-ROM rule and the
exact first-error history of SP29_FIRST_SIGNAL.md, corrected by
SP29_REFINED_WIPE_FACTOR.md. It changes no rule, programme or constant.
It does not prove a complete second signal, second shrinking pulse,
general eroder, upper error map or positive iid rate.

Use Q1024/U475136/TF278401. The first pulse ends at t*=284545 with the
quiet native template on [a,b)=[122Q-512,136Q). The complete foreign
frames have origins hQ-512, h122..135; the complete true frames are
jQ, j<=120 or j>=136. The two remaining partial frames are left true
frame121 and right foreign frame136. An Info primary means its logical
five-holder group, irrespective of the physical holders' native phase.

**Theorem.** At computed state U:

1. All five Info copies at jQ+509 are0 for every j<=120 and j>=136.
2. All five Info copies at jQ+1021 are0 for j121..134.

Combining with the actual next foreign signals proved in
SP29_NEXT_GHOST_SIGNAL.md, at computed state U+TF:

    MF509(j)=1 for j122..135, 0 for j<=120 and j>=136;
    MF1021(j)=0 for j121..134.

MF509(121), MF1021(135), and the true-frame MF1021 track are unspecified.
The original upper Info payload remains arbitrary. No new correct upper
encoding is assumed at U.

## An exact programme suffix, independent of the earlier work

The own programme has exactly one Hold issue at virtual phase509,
for upper raw h2 bit77: sequence129986, page357, tick456, input age
357736. Its Hold materializes at state357738. Virtual phase1021 has
no Hold issue. The phase509 result is inside the normal commit frame.

Start an abstract execution at age E0+280PL=285824, after the first
pulse has settled. Give all front registers and every scratch location
arbitrary Boolean seeds; permit an arbitrary fetched I word at Match.
All readonly inputs except the following fourteen raw field-bit families
are free:

    every mr and ml input (five bits each);
    h2 inputs at bits13,77,205,269.

Set every required direct/lane readonly value in those families to0.
Executing the actual remaining41477 ROM/listing instructions gives
Hold(509)=0 as a Boolean identity. Sound AND/OR/XOR/ANDN term reduction
proves this equality; no sampled assignment establishes it. The
instruction words are independently decoded from the pinned own ROM.
All earlier Hold values are arbitrary; the unique later issue replaces
the target. This is stronger than a full fresh-programme argument: it
does not require the earlier register/scratch computation to be correct.

The checker also retains an exploratory suffix probe. Setting only raw
h2 bit77 to0 is insufficient in that larger abstract fibre: an explicit
Boolean seed assignment gives1. That assignment has no proved physical
reachability. In particular it is not a counterexample to this theorem
or SP29. Setting all readonly data to0 is an unnecessarily strong
successful premise; the fourteen-family identity supplies the physical
argument below. Late Age outputs are not forced correct by these data
premises, and no such conclusion is inferred.

## The physical first history supplies the zero readonly inputs

The normal layout has mr at phases102..106, ml107..111, and the four
selected h2 bits at445,509,637,701. All of these represented upper
fields are initially0 in E29(z), independently of upper Info.

In a true frame these are their physical phases. In a foreign frame
the same virtual phases correspond respectively to614..623 and
957,1021,125,189. Those physical positions initially represent zero
upper h2/h1 fields or unused zero primaries. None represents upper GF
or arbitrary upper Info. The omitted fifth h2-copy bit141 would be
physical61 in a foreign frame, where it reads upper GF bit2; the
suffix identity deliberately leaves that input free.

Before TF all gather loads/captures precede the special courier writes.
For a fixed physical phase with initial logical Info0 everywhere, mail
transport and per-holder gates preserve0, irrespective of gate values
or the dependency rank selected at that phase. All captured history
values at that phase are therefore0. Initial histories are0; later
history five-votes, resets and wipes preserve0. Capture windows are
closed after E0, before the native pulse. Consequently every required
lane/history readonly value in the fourteen families remains0 through
the suffix. This does not require a correct full gathered upper state.

Direct Info at the physical phases other than509/1021 is initially0
and is never a special-write primary in either possible GF phase.
The possible physical special residues are3,515,509,1021; the selected
other phases avoid them. Thus these direct values remain0 before commit.
The selected exceptions are supplied by the corrected first-pulse
certificate: at t*, MF509 is1 only for j128..135 and MF1021 only at
144,145,146. In every complete new true frame, selected phase509 is
therefore0. In every complete new foreign frame, selected physical
phase1021 has j121..134 and is0. No further special write occurs before
commit. A zero logical majority gives five zero copies on the next
update; age285824 is1279 ticks after settling, so these copies are
already coherent0 at the suffix start.

## Lift the suffix to the actual full frames

The corrected endpoint and quiet-native proof keep GF/Age stationary
relative to each full frame after t*. The actual keep is1. All front
centres38..985, including their radius37 footprints1..1022, lie inside
each complete quiet true or foreign frame. Native Flag1 is0 there.
The own all-raw arrival/lookup theorem gives the actual ROM visit and
instruction for each front. Match supplies some actual bounded word;
the suffix certificate permits every I word, so no damaged-key
correctness assumption is needed.

The same five-holder register, scratch and pending source-reference
argument used in the physical programme proof applies from arbitrary
work values. On the first clean output in a fixed full frame, every
front's five physical register holders write the same voted old word
and instruction result. Scratch/history carries vote their logical
groups; forward pending writes have the unique actual destination kind
supplied by the now-fixed visits. An older pending record is consumed
within two ticks. No store reads a current simultaneous scratch write,
as certified by the own schedule's causal-read check. Hence at the
page280 start, well after settling, there is an abstract snapshot of
arbitrary register/scratch values (including any already forwarded
previous-tick scratch store) whose subsequent instruction execution
is exactly the actual physical one. The suffix proof allows this
entire snapshot to be arbitrary. It never assumes that a newly emerged
full frame executed the earlier programme correctly.

The other readonly inputs also have fixed logical majorities during
this suffix: all captures and special Info writes have finished, no
commit occurs until U-1, and each full frame has keep1. Their carry
votes have already restored coherent groups after settling. They may
therefore be the arbitrary fixed input variables used by the suffix
identity; no assumption of a correct upper state is hidden in their
constancy.

The unique phase509 issue therefore writes five Hold copies0 at357738.
No later Hold issue occurs at either possible phase for the primary.
Subsequent votes/keep1 preserve0; actual commit forwards those copies
through the allowed phase509 mask. The existing807 reset/5 forwarding
identities apply. For true frame j this primary is jQ+509; for foreign
frame h it is (h-1)Q+1021. This proves conclusions1 and2 at U, including
the infinite families of true frames.

## Until the second special signal

J169 keeps the same native template from U to U+TF. The above zero
primaries all have computed logical phase509, so the special signal
does not overwrite them. No commit occurs in that interval; votes
and keep1 preserve their zeros. J169 supplies MF5091 in every complete
foreign frame h122..135. The combined second-track conclusions follow.

The two partial frames have insufficient full-front source geometry
for this lift. They are left unspecified even though some of their
individual cells have the desired native phase. The true-frame second
Flag1 computations also depend on upper GF/Age/Workspace data not
restored by this theorem. No second pulse or induction is claimed.

| Step | Status | Exact limit |
| --- | --- | --- |
| Late41477-instruction zero h2:77 identity | proved | Four copy/mail readonly zeros; arbitrary earlier register/scratch seeds and fetched I |
| Fourteen-family source zero premises in the first actual history | proved | Original first-error preparation; corrected pulse tracks; no later errors |
| Physical suffix and first-boundary retained zero tracks | proved | Complete quiet true/foreign frames; partial frames excluded |
| MF509 next track except one partial bit; interior MF1021 zeros | proved | Same original history, native quiet continuation and J169 signals |
| Complete second signal/pulse, arbitrary-error eroder and iid rate | unproved | Partial bits and true-frame upper control data remain open |

Reproduce with check_short_force1024_first_boundary_signal_data.py;
the exact certificate and exploratory/failure receipts are in
figs/robustness. No active rule/compiler/backend is modified.
