# SP30: an Age-independent zero-GF source contract

This is a local-function theorem for the frozen, explicitly changed SP30
rule F30, Q1024/U475136/radius37. It introduces no rule change. Its
gather corollary is conditional on actual stored words and a persistent
Mailbox-erasing Flag1 strip; it does not establish those premises for
arbitrarily many periods or prove a travelling island/reliability result.

[Checker](check_signal_reservation1024_zero_GF_prefix.py),
[certificate](../../figs/robustness/SP30_zero_GF_prefix_certificate.json),
[own-rule theorem](SP30_OWN_RULE.md),
[actual seventh source proof](SP30_SEVENTH_SIGNAL.md), and
[gather route primitive](check_signal_reservation1024_second_signal.py).

## Unrestricted local identity

Let S=[-37,-23] union[-17,5], a set of38 integer offsets. In an
arbitrary raw input neighbourhood for the actual complete F30 Boolean
local function, assume that each raw GF word at offset d in S is0.
No constraint is placed on any Age, flag, Info, header, programme,
private word or instruction input, or on GF words at other offsets.
Then the literal computed outputs satisfy

    GF_new=0, F1_new=1, Workspace1_new=0.

There is no asserted Age or F2 value. In particular this identity is
valid for every legal or unused Age word and every combination of
the free inputs. It concerns one local transition; it does not require
a common clock, a valid instruction or a fresh work configuration.

**Proof.** For each refined logical offset u in[-5,5], both left
refinement blocks, centred at u-30 and u-10, consist of GF0 words.
Inside either five-cell block the adjusted GF words are the five
distinct residues -(centre+v)modQ, v=-2,...,2. No three whole words
agree, independently of their appended Age words. Both block-quorum
validities are therefore0. At most the two remaining blocks can be
valid, so the joint3/4 quorum fails and retains the raw pair at u.
Its GF is0, with unrestricted raw Age.

Both native five-cell geometry votes have distinct adjusted GF words,
and retain the self GF0. Their selection consequently gives GF0 for
every possible selector. The missing right geometry quorum forces
the native F1 inconsistency term to1. GF0 also makes the actual
Workspace1 right-end guard false. Thus the three displayed output
identities follow, regardless of clock or private controls.

The checker substitutes only these380 raw GF bits in the **complete**
actual SP30 netlist. Every other input remains symbolic. Exact Boolean
constant folding gives all ten output GF bits0, F1one and Workspace1zero.
It checks the precise set of substituted keys, the unchanged candidate
and netlist digests, and the output nodes. This is a universal symbolic
identity, not a sample of Age/payload values. It does not use a shared
GF-selector assumption or constrain unmentioned native fields. QED.

## Conditional gather-prefix corollary

Let R and B be integers with B>=R+5. Consider a true lower colony
receiver j with R<=j<=B-5 in a work period of the frozen SP30 programme.
Assume:

* Its actual GF captures use the already proved own-rule/gather
  protocol and correct normal-phase source and destination geometry.
* At source colonies R,...,B, every GF Info holder used by those
  captures is0 at each corresponding capture time.
* The physical Flag1 strip[(R-1/2)Q,RQ) is present at every time
  when a capture route from the left crosses it. Actual Mailbox
  clearing applies there; no error or competing invalid route
  replaces the certified gather data.
* The receiver's programme control and output-store premises are the
  actual own-rule theorem's, so the computed complete local function
  is evaluated on these captures. Other captured raw fields are free.

Then the receiver's computed GF, F1 and Workspace1 are0,1,0,
respectively, regardless of its captured Age and other raw fields.
Where the actual programme's store/commit bridge is valid, these are
also the resulting stored upper native words. The statement specifies
the bridge as a premise; it does not create a new work seed.

**Proof.** Fix a GF bit, normal phase a in59,...,68, holder slot
s in[-2,2], and d in S. If j+d>=R, then j+d<=j+5<=B, and its
captured GF bit is0 by the source premise. If j+d<R, its source
coordinate is at most(R-1)Q+70<(R-1/2)Q, while its destination is
at least RQ+57. The actual stride8 route crosses the512-site Flag1
strip; a residue class of stride8 cannot skip that strip. Mailbox
clearing gives0, regardless of the source bit. All380 captured raw
GF bits required by the local identity are consequently0.

The checker verifies the exact existing route predicate for all38
offsets, ten phases, five holders and receiver distances0,...,36:
70300 cases. For distances>=37 all sources lie to the right of the
strip, and the same source-bound argument applies directly. Integer
Q translations preserve the route arithmetic, covering every R.
The own programme's universal equality then supplies the local
identity, and its assumed actual store/commit bridge gives the stated
stored words. No Age progression or validity restriction is used. QED.

## Application and limits

J206's sixth-boundary GF source box is0 on98,...,120, including the
recovered98,...,103 words. Its actual strip is[(98-1/2)Q,98Q).
The conditional own-programme/store bridge gives computed
GF0/F1one/Workspace1zero on98,...,115. Its F1 conclusion agrees with
the seventh-period F1 cofactors checked individually in J206; that
certificate's source GF box and recovered holders also agree with
the present premises. The complete local identity explains the
zero-GF prefix structure without depending on an Age value or fixed
Age bits. This application does not supply an entire eighth signal.

This is not an all-period invariant. It needs actual zero source
holders, the time-persistent erasing strip, correct gather geometry,
and programme controls at each invocation. Recovering a six-colony
bank in one pulse does not supply those conditions forever. Even an
indefinitely valid right-prefix contract would leave the left signals,
complete pulse premises, coarse coordinate/clock wrap and higher-level
activity to prove. Full upper data, arbitrary fault repair, continuing
E0 noise, the higher error map and positive iid epsilon remain open.

| Step | Status | Exact limit |
| --- | --- | --- |
| Complete local GF0/F1one/Workspace1zero identity | proved |380 fixed GF input bits, every other raw input free |
| Conditional actual gather-prefix contract | proved | stated source/strip/gather/programme/store premises |
| J206 right-prefix consistency | proved previously; contract applies | one already certified actual period |
| All-period premises/permanent island/general eroder/full data | unproved | local identity does not supply history or left signals |
| Higher map/positive iid epsilon/minimum global change | unproved | all-level noisy induction absent |
| Gray/Gacs verbatim applicability | unproved; not claimed | SP30 is a separately changed rule |

The preliminary one-off cofactor used the equivalent broader interval
[-37,5]; its five missing-lane offsets do not occur in the actual GF
interface. Its [log](../../figs/robustness/SP30_zero_GF_local_cofactor_unregistered.log)
is retained as a prepared probe only. The exact38-offset identity and
route contract are proved above and checked separately. No active
G17/CURRENT, frozen SP30 or accepted-source change and no commit.
