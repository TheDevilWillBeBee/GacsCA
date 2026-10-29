# SP30: zero-GF bank closure, first boundary and next foreign sources

This is the already changed SP30 own rule of J189. No additional
rule, layout, programme or constant changes occur. It adapts the
[SP29 conditional bank proof](SP29_GF_BANK_CLOSURE.md) only after
rechecking the actual **new** listing, ROM and interfaces. In
particular, the true-phase H2 stores have different times. It does
not transfer a damaged private-state trajectory.

[Checker](check_signal_reservation1024_GF_bank_closure.py),
[receipt](../../figs/robustness/SP30_GF_bank_closure_certificate.json),
[new actual first pulse](SP30_NATIVE_PULSE.md),
[new complete-start and reset interfaces](SP30_OWN_RULE.md).

## Conditional theorem

For L<R define T(L,R) by common legal native clock, GF shifted512
exactly on[a,b)=[LQ-512,RQ), Flag1 on[a-512,a) and[b-512,b), and
all other native/header/code/pressure fields zero. Define B(L,R)
to be the five Info copies of every primary jQ+571+k, with
L-1<=j<=R-1 and0<=k<10. Q=1024, U=475136, TF=278401 and
S=TF+6144=284545.

Suppose at a period boundary the native state is T(L,R) at Age0,
all807 non-Info simulation private bits are zero and B(L,R) is zero.
No further errors occur. Retain the frozen own SP30 ROM and actual
arrival/pending equations. Suppose further that through TF..S every
raw/refined/computed GF used for relevant Hold updates is one of
x modQ and(x+512)modQ with common legal clock, and the actual
endpoint at S is T(L',R') with

    L'<R', L'<=L, R'<=R-1.

Then the next computed period boundary has native state T(L',R')
at Age0,807 private bits reset and B(L',R') zero. In the following
period the actual signal has MF509=1 at every hQ+509,
L'<=h<R', by TF. Other Info payloads, pulse-time wipes and
private computed values may be arbitrary; arbitrary pending seeds
or new overwrites are excluded.

This is an implication for pulses meeting the stated premises.
It asserts no general pulse endpoint, full signal mask or eroder.

## Why the old coordinate and physical argument applies

The new rule's73 native/header functions and corrected closed pulse
factor are identical by J192. The quiet T(L,R) native/refinement
cofactors and closed birth/force/WF1 guards therefore apply verbatim.
The four boundaries are512 apart or farther; translating by Q does
not change their residues. The checker repeats shortest-width and
actual endpoint cofactors. Thus the template persists before TF and
after S until the next birth window, with keep1 when it is quiet.

The new GF encoding rows remain exactly59+k and their requested
offsets/capture clocks are unchanged. At a complete foreign-frame
origin hQ-512 every source has primary(h+d-1)Q+571+k. Inside[a,b)
it lies in B(L,R); outside it the actual speed-eight mail route
crosses a512-site Flag1 strip. The voted gate is the indicator of
the unflagged region, even at its four boundaries. A512-site strip
cannot be skipped by eight-site steps. All three actual histories
and direct GF reads are therefore zero, irrespective of outside
data. The full **new** GF0 cofactor gives computed GF0/Flag1one
with every other circuit/instruction input free.

The new own-programme and front certificates, unchanged working
footprint and actual early-courier deadlines supply the physical
prefix induction. The early GF Hold outputs are zero. Moving
h2:77/h2:83 to901/902 changes neither these GF sources nor their
physical paths. This is a bridge through the new programme and
interfaces, not substitution of the old full trajectory.

## Rechecked store and pending windows

The actual new listing/ROM has exactly one Hold store at each of
the twenty phases59..68 and571..580, over all81920 raw phase/selector
keys. The new input issue ranges and materialization ranges are

| Virtual phases | Input issues | Materialization |
| --- | --- | --- |
| 59..68, GF | 276520..278398 | 276522..278400, before TF |
| 571..580, true H2 | 345734..358739 | 345736..358741, after S |

The latter differs from SP29 and is checked afresh. Neither possible
phase has a Hold store during TF..S. The five comb teeth differ by
multiples of5 of magnitude at most20, never512. With the proved
single-arrival equation and common clock, every simultaneously
present pending record for one logical primary therefore has one
destination kind k, possibly removed by its holder's keep mask.
If at least three presences survive, every voted kind bit is k;
otherwise no voted store occurs. The160 presence/k cases check this
argument. Pval can be arbitrary. A scratch destination cannot
manufacture a Hold write, and previous pending stores finish before
TF. This excludes the erroneous inference from listing clocks alone.

For any target jQ+571+k in B(L',R'), either j<L-1, so its initial
true-phase Hold is zero and has no pre-S store, or L-1<=j<=R-2,
so it belongs to a complete old foreign frame with early GF Hold0.
Votes and wipes preserve zero through the pulse. At S each target,
its five holders and refinement footprint lie strictly inside the
new wrong-GF interval: virtual59..68 has at least59 left and444
right clearance. It stays in that quiet foreign phase. Its GF store
has passed, and its later true-phase H2 store cannot address it.
Thus Hold remains zero until commit.

The actual new commit mask contains all phases59..68; the new807
reset/five forwarded-Hold identities put these zeros in Info and
reset the private fields. Repeating the same quiet-bank/source and
new own-programme argument gives all stated next-period complete
foreign Flag1 sources. This proves the conditional theorem. QED.

## Actual first-history instantiation

Use J191/J192's one specified intact-start native error with no later
errors. Initially T(128,144) and B(128,144) are zero: the physical
primaries571..580 encode upper h2:139..148, initially zero. All
private fields are fresh. J192 supplies the binary/common-clock
pulse premises and actual endpoint T(122,136). The inequalities
122<=128 and136<=143 hold. Consequently:

* At computed time U=475136, native state is T(122,136),807 private
  bits per site reset, and all750 Info copies of150 primaries
  jQ+571..580, j121..135, are zero. Sixty targets were initially
  true and ninety belonged to complete old foreign frames.
* At computed time U+TF=753537, MF509=1 at each hQ+509,
  h122..135, from the actual new programme and couriers.

This gives neither the entire MF509/MF1021 mask nor a second pulse
outcome or complete encoded upper data. It proves no claim about
arbitrary phase/width/clock faults, continuing E0 beside an island,
higher-error closure, positive iid epsilon or minimal global repair.

| Step | Status | Limit |
| --- | --- | --- |
| New quiet/native/route/programme bridge and twenty-phase stores | proved | New own ROM and stated quiet-bank start |
| Zero-GF bank implication through a qualifying pulse | proved conditionally | Binary GF/common clock/displacement, no fresh errors |
| Actual first-boundary750 zero copies and14 next complete foreign sources | proved | J191/J192 specified intact-start error |
| Full next mask/pulse, general eroder and iid reliability | unproved | Additional signal/data/fault arguments required |

Finite route/cofactor/ROM checks supplement the written coordinate,
pending and physical inductions. No numerical whole-CA trajectory is
used. G17/CURRENT and all previous sources/programmes remain unchanged;
no commit.
