# GT0's actual Flag1 Mailbox barriers and two retained native banks

This closes a **conditional physical-prefix component** obligation for the
frozen GT0 bit transducer. It uses Gray's printed Mailbox-on-Flag1 erasure
and three separate gathering stages, rather than GMW7's single word gather.
It does not provide a complete Gray own-programme, final alphabet/layout,
late Workspace equations, early flag evaluator or noisy theorem.
Q=8192, U=128Q=1048576, lambda=24 and c=104 remain unchanged.

Sources: Gray pp20–22,33–35,41, in the pinned primary paper/text;
[frozen component](gray_raw_gather.py),
[its emitted-transition/route proof](GT0_RAW_GATHER.md),
[literal native transcription](literal_maintenance.py),
[conditional command contract](GRAY_FLAG_COMMAND_CONTRACT.md),
[new checker](check_gray_clock_erasure_bank.py),
[new read-only replay](validate_gray_clock_erasure_bank.py).
The [receipt](../../../figs/gray_counterexamples/GT0_clock_erasure_bank_certificate.json)
pins the native/input/control checks, prefix assumptions and exact bank words.

## Exact completion premises and history

Consider a putative completion of GT0 with the following prefix premises.
These are requirements, not a claim that a faithful full automaton exists.

1. It retains the frozen GT0 SimBit/Mailbox/History output equations.
2. Its native fields use the printed Gray transition, or the separately
   flagged h1 Flag2 correction. Workspace flags obey the published condition
   that they can be nonzero only at computed Ages96Q..98Q. There is no
   earlier private-to-native forcing. Initially the lower native row has
   GF(x)=x modQ, common Age0 and all native/Workspace flags0.
3. Its represented native bits use any fixed injective interior layout
   ell, with5<=ell(b)<=Q-5. Initially their logical primary SimBits encode
   the canonical upper native row: GF(g)=g modQ and Age/Flags/Workspace0.
   All five SimBit holders agree. These native bits and the other initial
   SimBits are part of an intact recursive initial data encoding for the
   completed layout, if such a completion is supplied. No all-zero programme
   is assumed. The preliminary277-bit GT0 frame gives one concrete data
   example, not an own-beta or final-layout certificate.

At input physical row0 overwrite Age only on[0,17Q), setting it from0 to1;
all other native and data fields retain those initial values. No later
errors occur. This is one actual original real2 set, as in the accepted
clock-island certificate. There is no independent upper fault or selected
preloaded bank.

For each normal native-bit primary in lower colonies15 and16, the actual
History2 and History3 banks at physical row70Q have the native words below.
They are equal to each other, so their bitwise majority with **any** first
History bank is the same bank.

* Receiver15: its self and five left records are the original correct native
  words of upper cells15,14,...,10. All five right native records are zero.
* Receiver16: its self native word is the original correct upper cell16.
  Every nonself native record, left or right, is zero.

Both banks compute native GF equal to the receiver, Age1, Flag1=1 and
Flag2=0 under the actual printed and h1 equations. Receiver15 has the
correct-left/common-Age/five-null-right bank of the conditional command
lemma, while its lower native Flag1 is0. Receiver16's lower Flag1 is1
throughout the complete colony. This establishes actual first-prefix
bank premises for the component; it does **not** establish sixteen later
common Ages, an early source store or eventual recovery.

## Native prefix from the printed window

Write e(x)=1 on[0,17Q), and h_t=min(3t,Q). Up to row70Q+2 the Workspace
window is still closed, so both Workspace flags are0 regardless of future
flag-result and programme ports. The actual native induction gives

    GF(x,t)=x modQ, Age(x,t)=(t+e(x)) modU,
    Flag1(x,t)=1 on[-h_t,0) union[17Q-h_t,17Q), Flag2=0.

The existing stationary-orbit proof supplies the GF/Age/Flag1 induction.
It also applies to the printed Flag2 clause on this prefix: old Flag2=0,
the apparent colony exists because GF is canonical, and Workspace2=0.
Thus no Flag2 source is present and no1-to0 predicate is used. The h1
correction has the same trajectory. This is independent of evolving
Mailbox, History and all other SF fields.

By row2731 the whole predecessor colonies[-Q,0) and[16Q,17Q) have Flag1=1.
Let F be their union. Each subsequent computed native Flag1 is exactly its
indicator. Computed GF always equals raw GF, so the all-SF wipe is false.
This persists through both later gathers. Every native-bit SimBit is held:
no clock wraps occur, and the only other SimBit writes before row80Q are
at the two unused special primaries3/Q-3, outside ell's interior layout.

## Logical Mailbox factor, including boundary copies

Let B_f(y,t) be the five-holder vote of GT0 field f at logical coordinate y.
Every old data source used by a slot for y is such a logical vote, even
when the five raw output copies do not agree. Calculated service Address
is y modQ. After saturation, a flagged logical centre y has at least three
flagged holders. The GT0 printed erasure makes all their Mailbox output
bits0, so both new logical Mailbox votes are0 independently of their
phase-dependent pre-erasure operations and all raw data.

If y is unflagged, at least three holders are both unflagged and have the
clock label e(y). At the two internal boundaries -Q/16Q the clock does
not change. At0/17Q the clock changes, but the holders with the centre's
clock label are precisely on the centre's side of that boundary. Since
the two flagged strips and two clock jumps are separated by at least Q,
there is no conflicting second boundary within a five-holder group.
Those three or more holders produce the identical unmasked operation at
the centre's Age. Its bitwise majority gives the exact logical Mailbox
rule, using the centre clock and then the mask `y notin F`.

For History fields, the erasure mask is absent. At least three holders
have the centre's clock label, so their identical phase operation gives
the exact logical History output. These statements cover arbitrary raw
Mailbox/History copies; no coherence at a barrier boundary is assumed.
The checker reduces the actual frozen Boolean outputs against independently
named raw bits for every saturated-boundary/clock-event class. It also
checks the actual literal native control words used in those reductions.

## Stage2/3 routing and erasure, not a clean-snapshot assumption

Let S be32Q or64Q. At each logical centre y the Mailboxes reset at physical
output row S-e(y). They snapshot the held SimBit at row S+1-e(y), subject
to the barrier mask, and then move one logical site per update during
the active stage. A History offset d=0 captures the held own SimBit at
that same row. For d!=0 its capture row is

    S+2+|d|Q-e(y),

and it reads the old Mailbox at y on the preceding row. These are GT0's
actual old/new row conventions; the extra tick is not dropped.

At receiver16 every normal primary lies in F. Its old logical Mailbox
is0 throughout either active stage, so all nonself captures are0. The
own record is the held correct SimBit and is not Mailbox-erased.

At receiver15, every left source path stays strictly between colonies10
and15. These have the same clock e=1 and no Flag1 barrier; the accepted
clean routing induction gives exactly the bit at the same within-colony
primary of the source upper cell. The self snapshot is also exact.
Each right source path, whatever its d=1..5, hits F at colony16. If p is
the receiver primary residue, the backward path reaches16Q after Q-p
moves. Its remaining physical row there is

    S+1+dQ-1-(Q-p)=S+(d-1)Q+p,

which is at least S+5 and hence after saturation. The old logical
Mailbox value at that flagged coordinate is0. This supplies a real
erasure origin in the recursion rather than an assumed null source.
All subsequent moves to the receiver preserve0, so the capture is0.
The path never needs a host source filter or a preloaded zero record.

The largest capture is69Q+2-e(y), before physical row70Q. History2 resets
only at stage1/2 starts, and History3 only at stage1/2/3 starts, all earlier
than their captures. Their actual remaining operations through70Q are
same-field votes, so the captured records persist. Neither the special
flag delivery near80Q nor any fifth-stage write port is active. Therefore
History2=History3 for every represented native bit at this time, and a
temporal majority with arbitrary History1 returns their values.
This is a mathematically available three-bank native input at70Q; an
actual early evaluator that forms it and finishes/delivers flags is still
missing. Late retention past repair commands is also not proved here.

## Initialization, layout and scope

Only the represented native bits are used to derive the bank words. For
the preliminary frozen frame, their values come from its accepted
terminating data recursion, with arbitrary correct programme bits at the
unrepresented programme auxiliary. The same argument is valid for any
completed interior native-bit layout satisfying the stated initialization.
It does not show that an own beta fits Q, that final K<=Q/2, or that a
complete evaluator remains compatible with this layout. The component's
printed-computed-SimBit/radius5 late integration obstruction remains open
as an obligation of any such completion; this prefix does not remove it.

The argument is conditional on the exact three prefix interfaces listed
above, including existence of an intact completion for any promoted
whole-rule witness. It closes the native early-prefix controls and
actual blocked native-bank calculation, not every final construction
premise. It reports no theorem refutation: the resulting erased banks
are the intended type of symptom discussed by Gray on pp39–41.

| Step | Status |
| --- | --- |
| Original constants and exact shared dense clock real2 | **previously proved; reused** |
| Printed native and h1 prefix through the third captures | **proved conditional on printed Workspace window** |
| All-raw logical Mailbox barrier and History centre-clock factors | **proved actual GT0 component equations** |
| Stage2/3 native input banks and pre80Q temporal-majority availability | **proved conditional physical prefix** |
| Preliminary recursive native-bit initial data | **previously proved component data frame** |
| Full final layout/own beta/programme, genuine Gray completion | **unproved** |
| Early flag production/delivery and later retained repair history | **unproved** |
| Contradiction to Gray/Gács, global recovery or iid memory failure | **unproved; not claimed** |

The proof changes neither GT0, its schedule, the accepted conditional
pointwise-envelope witnesses nor active G17. It supplies no shorter U.
