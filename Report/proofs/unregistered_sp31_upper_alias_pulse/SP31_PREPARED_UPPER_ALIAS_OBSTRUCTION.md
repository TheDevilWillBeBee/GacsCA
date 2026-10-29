# SP31: arbitrary right Info defeats an all-time right native-bank barrier

This concerns unchanged isolated F31, Q1024/U475136/r37/TF278401.
It is a **prepared-state obstruction**, not J225's original fault
history, an intact-hierarchy noise witness, or an iid failure theorem.
No physical rule, ROM, constant or G17 changes. The analysis C has
the same native/Info function core as J225's frozen sp31_native_events.c.

## Exact prepared configuration and statement

Let R denote the full F31 rule and E its complete reset encoding.
Define an upper raw configuration C on the integers as follows:

- Age is age_code(TF) everywhere; logical TF278401 is raw word307201.
- GF(x)=(x+512)modQ on [-16Q-512,0), and xmodQ elsewhere.
- F1 is1 on [-17Q,-16Q-512) and [-512,0), and0 elsewhere.
- F2/WF1/WF2 and every private SF field are0.
- The single logical upper Info primary Q-3=1021 has its five
  coherent copies1: at holders1021-slot, slot=-2..2, the corresponding
  Info component is1. Every other Info component is0.
- The immutable programme is the actual F31 programme.

Thus upper native GF/Age and all old native flags are canonical/common/
zero for x>=0, but the left native geometry and right Info need not
belong to an intact hierarchy. E(C) satisfies J257's A(TF,0), without
its outgoing bound n<TF. The one positive **upper** alias is encoded
as ordinary lower Info bits, not preloaded into any lower signal group.

Write C_s=R^s(C). For0<=s<=512 the common upper logical clock is TF+s,
native F2/WF2 are0, and the actual native/Info factor is the exact
retained finite execution certificate. In particular:

1. C_1 has upper WF1=1 on [1019,1024). This is the real right-end
   Info vote under the open upper clock guard.
2. The first wrong upper GF on x>=0 occurs at s171, exactly at x2;
   C_171(2).GF=514. Every right native GF was canonical at all s<171.
3. C_s(0).GF=0 for all0<=s<172, and C_172(0).GF=512.
   At s172 the right wrong-GF support is [0,4).
4. At s512 every x in [0,1024) has GF=(x+512)modQ and all x>=1024
   have canonical GF. The source Info vote first becomes0 at s512.
   No persistence or repair after this stated horizon is asserted.

The complete-start theorem J223 gives, for this same actual noiseless
prepared history,

    R^(sU)(E(C))=E(C_s),  0<=s<=512.

Consequently the five lower ordinary Info holders of the upper native
GF bit9 at normal primary2Q+68 are1 at physical171U=81,248,256,
and those at primary68 are1 at172U=81,723,392. Both were0 in E(C).
These are represented native-GF changes, not raw lower GF damage.
Raw lower GF and its legal clock remain canonical/common throughout
this noiseless complete-encoding execution.

Therefore a canonical right **represented native-GF** bank cannot be
preserved for all upper clock values under A's other premises with
arbitrary other Info, even if its zero-WF conclusion is omitted.
Translation by any upper R that is a multiple of Q gives the same
prepared obstruction at that edge. This does not show that J225's
actual TF*U row supplies these Info values or left native banks.

## 1. Actual closed projection — previous proved argument applies

The full native dependency/interface facts of J223 and the closed
factor in J225 apply verbatim. Binary adjusted GF and a common legal
clock stay closed under joint refinement and both directional votes.
Each right GF vote has a binary-label majority; its existence is true.
With native F2/WF2zero and no service force, the d3/d4/on/retention
clauses keep F2zero. WF2 reads an old Info vote only from physical
aliases3/515, both of which are0 here. Thus WF2zero remains closed.

On the present interval current upper Ages are TF..TF+511, strictly
after the only special Info write at TF-1 and strictly before U-1.
There is no further special write or old-Out commit. All actual Info
components evolve solely by their old five-copy vote and the holder's
keep. In particular, if M(y,s) is a voted Info group,

    M(y,s+1)=M(y,s) * majority_slot keep(y-slot,s),
    keep(x,s)=NOT(newF1(x,s) AND newGF(x,s)!=refinedSelfGF(x,s)).

Zero groups remain0; other SF, work and actual instruction histories
cannot create a new alias or force the native projection. This does
not assume that the private SF stops evolving. The present positive
group is an initial raw state, not a supplied future command stream.

The C core through its exported cofactor function is byte-identical
(excluding the trailing blank separator before the report function)
to sp31_native_events.c. Its state bits are the GF offset label,
F1 and WF1; the other three native fields are supplied by the proved
common-clock/F2-WF2 invariant. Its GF refinement, clipped Flag1,
direction, old-voted right Info read and refined-self keep are exactly
the foregoing J225 projection. No old raw-self wipe model is used.

## 2. Exact finite trajectory on Z — proved by interval induction

Native tuples and the single nonzero Info primary have finite support.
Outside that support enlarged by37, the projection maps the zero
offset/flag/Info tuple to itself. Its representation is the infinite
zero exterior, without a periodic boundary or external repair.

At every step, split the integers at every native interval endpoint
shifted by -37..37 and at both GF labels' colony boundaries shifted
by -8..8. Include the source support in the enclosing interval.
For a fixed such interval all raw native tuples at each required
offset are equal. The inside-colony, end and quiet predicates are
constant; a selected special Info address is one fixed primary of
its selected colony. Hence the projected output tuple is constant
throughout the interval. The code checks both endpoint outputs,
every shifted raw tuple and every phase predicate before appending
the resulting interval. These checks establish the exact next state
from the exact preceding state by induction. All integer values and
cut/segment capacities in this run are within their declared bounds.

There are508646 checked constant intervals across512 updates. The
full513 states, voted Info sets and endpoint are retained in
native_trace02.jsonl and reproduced byte for byte by the read-only
checker. The original profile-only discovery remains in trace01;
the retained initial source differs only in trace output. Its every
profile agrees with trace02 after the added full states are removed.

At s171 the right segments are [2,3) with offset/F1 bits3,
[3,1019) with F1bit2, and [1019,1024) with F1/WF1 bits6.
At s172 they are [0,4) with bits3, [4,1019) with bits2,
and [1019,1024) with bits6. All earlier retained states have no
right GF offset, and all s<172 have offset0 at cell0. At s512 the
full endpoint is

    [-17408,-16896):2; [-16896,-512):1;
    [-512,173):3; [173,512):1; [512,1024):3,

with zero elsewhere and an empty nonzero Info set. The displayed
claims follow directly from these exact interval states. A first
right hole is allowed; no unproved solid-front invariant is used.

The190 selected full-F31 cofactors are measured supplements. They
leave all other SF and instruction inputs symbolic. Actual raw Info
holder bits are reconstructed from the previous vote, the next native
state and refined-self keep, so partial holder erasures are included.
They confirm the actual six native outputs at10 selected times and
19 receivers. The universal projection and interval proof supply the
scope beyond those chosen inputs.

## 3. Physical encoding lift and meaning — previous proved argument applies

J223's complete-start/noiseless theorem quantifies all raw upper
configurations, including C_s; no native health premise is needed for
the represented upper state. Repeated application therefore gives
the stated full raw encoding identity at every sU boundary. In that
encoding, GF bit9 is the ordinary native primary68; translating to
upper cell2 gives2Q+68. The encoded five holder bits are exactly that
upper native bit. Lower work and alias groups are fresh at boundaries.
The common canonical physical lower pair always survives refinement
and both directional selections, irrespective of the represented
upper flags; the raw lower GF/clock assertion follows as in J223.

This is not a defective self-simulation or memory claim: the lower
system correctly simulates C_s, whose upper Address changes as just
proved. Initial C is deliberately a partially damaged native host
with arbitrary right SF/Info. It is not identified with an intact
recursive hierarchy plus the original J225 error. No uniform original
error class, minimal fault or positive iid failure probability is
claimed for this prepared family.

An actual continuation past J257's horizon must constrain or derive
the higher-level native/alias provenance. Allowing arbitrary right
Info and checking only right native bank geometry cannot close the
induction. A reset of that upper alias would remove this particular
prepared pulse, but is an explicit potential rule/interface change
with no own programme or reliability proof here; no such edit is made.
General repair, a globally sufficient smallest change and iid ε remain
unproved.

| Step | Status | Scope |
|---|---|---|
| Binary-GF/common-clock/old-voted Info/refined-self keep projection | previous proved argument applies | J223/J225; no Info write or commit on TF..TF+511 |
| Prepared C, exact infinite-line512-step interval trajectory | proved | This finite prepared history only; all513 states retained |
| Complete encoding composition/represented GF bit changes | previous proved argument applies | Arbitrary raw upper C_s, same frozen F31 programme |
|190 full-native/raw-Info-holder cofactors | measured supplements | Chosen times/receivers; other SF/instruction bits free |
| All-time arbitrary-right-Info native-bank barrier | disproved for the prepared A family | GF changes at171/172; raw lower geometry remains correct |
| Actual J225 after TF*U, intact-noise failure, general higher/iid/minimum | unproved | No identification with the prepared state |

Read-only replay:
`python3 Report/proofs/unregistered_sp31_upper_alias_pulse/check_prepared_alias.py`.
The initial checker source and failure log are retained. Its source-core
comparison included one added blank report separator; excluding that
separator fixes provenance comparison without changing any function,
mathematical receipt or trace.
