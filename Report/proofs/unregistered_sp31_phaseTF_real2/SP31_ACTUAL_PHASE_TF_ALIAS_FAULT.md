# SP31: an intact-start phase-TF alias fault and its encoded lift

This concerns the **unchanged isolated F31 proposal**, not registered
G17: Q1024, U475136, radius37, TF278401 and the frozen own programme.
It proves a particular chronological original-c16 real2 history and
an original-c16 real3 encoded history. Neither is a Gray/G17/iid
counterexample or a failure of the higher-error Address envelope.
No rule, ROM, constants, CURRENT or compiler changes.

## Exact statement

Let R be F31 and E its complete reset encoding from J223. SLOTS is
(-2,-1,0,1,2); an Info component at physical x with slot s holds
logical primary x+s. Ordinary GF primaries are59..68, native F1 is88,
and upper Info components are92..96 in slot order.

Define a binary function A on Z by the terminating recursion

    (g,p)=divmod(y,1024)
    A(y)=bit_(p-59)(g mod1024)             if59<=p<=68;
    A(y)=A(g+p-94)                       if92<=p<=96;
    A(y)=0                              otherwise.

Define H(x).GF=x modQ, H(x).Info[s]=A(x+s), and every other mutable
field0, with the actual immutable F31 programme. Then H=E(H).
In its noiseless trajectory Y_t=R^t(H), GF is canonical, Age is the
common legal age_code(t modU), all four native flag/Workspace fields
are0, and every logical Info alias of phase3/509/515/1021 has all
five copies0, at **every** physical time t>=0. Other SF is the actual
evolving SF, not forced0.

Run H cleanly to input row TF. In the actual Y=Y_TF overwrite only:

- GF by(x+512)modQ on[-14Q-512,0);
- F1 by1 on[-15Q,-14Q-512) and[-512,0);
- the five coherent Info holders of logical primary1021 by1.

Retain every other actual field, including all other Info, work,
private service fields and clock. Call the resulting row C. Every
site of the one-row support

    S=[-15Q,0) union [1019,1024)

is genuinely changed, and no other site is changed. S has15365 sites
and hull[-15360,1024), width16Q. In the original lambda24/c16 error
classification this is exactly one real2, with no E0/E1 points. Apply
no later errors.

For C_s=R^s(C), every right native GF is canonical through s170.
The first wrong right GF is at s171, exactly cell2 with GF514.
Cell0 first changes at s172, to GF512; the right wrong-GF support at
that row is[0,4). The source gives WF1 on[1019,1024) at s1. We assert
no endpoint beyond172 for this shortened-left fault.

There is also an exact lower realization on the **same** intact H
trajectory. At input T0=TF*U=132278337536 the actual noiseless row is
E(Y). Change only those ordinary lower Info holders needed to turn
E(Y) into E(C). This has79385 genuine changed whole-cell locations,
one row and hull[-15728554,1047647), width16776201. It is one original
real3 at lambda24/c16, with no E0/E1/E2 points. With no later errors,

    R^(sU)(E(C))=E(C_s), 0<=s<=172.

Thus the represented upper native GF bit9 has five lower copies1 at
primary2Q+68 at absolute row132359585792=T0+171U, and at primary68
at row132360060928=T0+172U. Those bits were0 at T0. Raw lower GF and
its legal clock stay canonical/common at every row; the lower rule
correctly simulates this particular damaged upper history.

The payload descriptor specifies complete replacements by retaining
the actual Y or E(Y) record and changing only the listed bits. It is
an exact mathematical specification, not a claim that all842-bit
old records at TF or T0 were numerically simulated or printed.

## 1. Explicit self-encoding initializer — proved

The only recursive case has y=gQ+p with92<=p<=96 and parent
g+p-94. For g=0, |parent|<=2<|y|. For g>=1,
|y|>=Qg+92>|g+p-94|. For g<=-1, |y|>=Q|g|-96 and
|parent|<=|g|+2, with(Q-1)|g|>98. Absolute value strictly decreases,
so A is defined uniquely everywhere; no value at an infinite descent
or unspecified origin is chosen.

At a GF primary gQ+59+b, A equals the b-th bit of H(g).GF. At
an Info primary gQ+94+s, A equals A(g+s), the corresponding bit of
H(g).Info. All other ordinary state fields have0 and primaries
outside the ordinary layout also have0. In particular auxiliary
58/965 and aliases3/509/515/1021 have0. Field-by-field, including
all five holders, this is exactly E(H)=H. The full frozen layout is
checked; the finite513-upper-coordinate check is a supplement to
these identities, not their universal proof.

This uses an unshifted origin. Translating a physical fixed point
without translating the upper coordinate convention is not used.

## 2. All-time intact native/alias quietness — proved using J223

Canonical GF/common legal clock remain correct independently of any
flags or SF: all four refined block pairs agree and both directional
choices return that pair. The legal mixed-clock successor advances
it. Thus computed GF always equals refined self-GF and keep is1.
This also holds if flags are temporarily allowed in a comparison;
no circular zero-flag premise is needed for the geometric induction.

J223's complete-start noiseless theorem quantifies **all** upper raw
states. Starting H=E(H), its composition gives

    R^(qU)(H)=E(R^q(H)) for all q>=0.

These identities hold before proving the proposed all-time zero flags.

Suppose tau is the first time at which some native F1/F2/WF1/WF2 is1.
Such a minimum exists if the set is nonempty, even on Z. Correct
geometry/common clock and zero old flags/Workspace make a first F1
or F2 impossible in the literal native equations: the mismatch source
and clock-inconsistency source are false; no propagation/source quorum
or private service force is present. Hence the first is Workspace,
whose preceding input clock must be in[TF,TF+2Q).

Write that input time as qU+a, TF<=a<TF+2Q. The actual earlier
boundary is E(R^qH), with fresh work and zero unused Info. All earlier
rows have zero native flags, so the ordinary actual gather, own-ROM,
early execution, five-copy and courier equations from J223 apply
through this period's special write. They compute the F1/F2 bits of
R^(q+1)H. But q+1<tau=qU+a+1; minimality makes those bits0 at every
site. Both actual special writes at input TF-1 therefore write0.
No normal capture/program operand uses an alias. Phases509/515 have
no special write, and commit's A31 mask excludes all four aliases.
Between writes each alias is its old five-copy vote (keep1). Thus
every old voted alias source at the proposed first Workspace input
is0, contradicting a new positive Workspace. No tau exists.

With zero sources and zero boundary aliases, that same Info recurrence
proves all five alias holders0 at all times, including their writes
and resets. This establishes the actual TF old-value facts used by
the fault. Other SF may be nonzero and is retained exactly; no empty
work premise is asserted for Y_TF. The80 selected full-R cofactors
leave all other SF/instruction inputs free and supplement the written
all-phase/minimal-first-command argument. They are not an all-time
experiment.

## 3. Genuine chronological support and original classes — proved

Every upper GF overwrite toggles bit9 of the old canonical GF, every
F1 overwrite changes old0 to1, and the five alias holders change0 to1.
Their union is precisely S. The following uses the original recursive
candidate definitions, not an operational damage class.

There is no E0: in each dense left interval or five-site right block,
any singleton/adjacent pair has another point within(24,24). In the
graph joining error points at distance<24Q in space (one common time),
S is connected; its largest gap is1020<24Q. An isolated real1 subset
would therefore contain all S, which cannot fit its Q-wide candidate
box. Thus E1 is empty. S fits a Q²-by-U² box and contains two disjoint
linked candidate1 subsets, e.g. the first two adjacent pairs in its
dense left end. It is a candidate2. Its diameter16Q-1 is<cQ; any two
nonempty subsets are(cQ,cU)-linked. Condition(iii) follows, and
condition(iv) is vacuous because there are no exterior errors. S is
one original real2.

For the encoded lower fault, each changed upper GF bit uses five
lower holders at xQ+68-slot, each changed F1 bit uses xQ+88-slot.
The five changed upper Info components are at upper x=1021-s with
component s+2; their lower primaries are xQ+94+s with holders±2.
There are14848*5+1024*5+5*5=79385 distinct lower sites. Every changed
bit really differs in E(Y), by the old-value results above. The exact
minimum/maximum and distinct count are checked without inventing any
additional lower overwrite.

Every lower group contains five adjacent sites, so E0 is empty.
The<24Q graph has two components: the left groups and the five right
groups. Each component has internal consecutive gaps<=1020 and
width>Q (the right width is4097). An isolated real1 would have to
include a whole component, impossible in a Q-wide box. E1 is empty.
The whole lower support has diameter16776200<24Q², so is connected
for real2 isolation. A real2 subset would have to be the whole support,
whose width16776201>Q² prevents candidate2. E2 is empty.

The support fits Q³-by-U³. Two distinct neighboring five-site groups
at the left end supply disjoint four-point candidate2 subsets (each
contains two linked adjacent-pair candidate1s); those candidate2s
are(24Q²,24U²)-linked. Thus it is a candidate3. Its diameter is
16776200<16Q²=16777216, making condition(iii) automatic. There is no
exterior error for condition(iv), so it is one original real3.

## 4. Actual native pulse through172 — previous projection applies

Use only the closed native/alias projection from J223/J225/J259, not
the full private configuration. Its fields are binary GF label,
F1/WF1, common clock, F2/WF2zero and the four alias votes. The two
GF labels and legal common clock are closed. On inputs TF..TF+171
there is neither a special Info write nor old-Out commit. Alias copies
obey the old-vote/refined-self-keep recurrence proved in J225; other
Info and SF cannot create a new native source. F2/WF2 stay0 since
their two source alias families remain0 and there is no private force.

This projection has radius at most39 in native fields and logical
alias votes: the native factor's radius is37 and each Info vote's
next holder keep uses an additional±2. End-guarded alias reads lie
within±3. The actual raw holder copies need not be assumed coherent
after the overwrite; their shared old vote and individual keep give
exactly that recurrence.

C's initial projection agrees with J259's prepared C on every
x>=-14Q-512=-14848. The only projected difference is the shortened
far-left stripe; actual other SF/ordinary Info are irrelevant to this
projection. Since172*39=6708<14848, their projections agree for
every x>=0 and all0<=s<=172 by finite propagation. J259's retained
513-state exact interval trajectory therefore proves the stated
first right GF change171, first cell0 change172 and right support
[0,4) at172. Its s512 endpoint is **not** transferred: that cone
reaches the changed far-left geometry.

## 5. Lower chronological realization — previous encoding applies

At T0 the actual clean H row is E(Y) by J223's iterated full encoding
identity. The listed lower Info-only overwrite makes it exactly E(C),
including every other actual field, rather than merely a decoded
match. J223 applies again to arbitrary C_s and gives the full stated
composition. In E(C_s), ordinary GF bit9 is at primary68 (translated
by xQ). The two absolute event times follow by exact arithmetic.
Canonical/common lower native geometry survives at every row as in
J223, regardless of the represented upper damage.

## Status and limitations

| Step | Status | Scope |
|---|---|---|
| Terminating A, complete H=E(H) | proved | All integers and actual842-bit layout |
| Intact all-time canonical native/zero flags/zero aliases | proved using previous proved J223 arguments | Minimal-first-command proof; actual SF evolves |
| Genuine TF fault/original real2 and lower original real3 | proved | Specified finite supports; no later errors |
| Binary/common-clock/alias projection and172-step transfer | previous proved argument applies, with proved finite-propagation comparison | J223/J225/J259; not the s512 endpoint |
| Full chronological lower encoding lift/bit9 events | previous proved argument applies | Exact E(C), every sU boundary through172 |
| Finite initializer,80 cofactors/support arithmetic/replay | measured supplements | Not numerical TF/T0 full trajectories |
| Original J225 TF state, arbitrary higher repair, iid rate/memory, globally sufficient minimum | unproved | This is a different actual phase-TF fault family |

The real2 and real3 native excursions fit much larger higher-error
allowances; a finite excursion does not violate those propositions.
No all-time repair failure, persistent loss of a bit, faithful Gray
counterexample, shortened U or global reliability theorem follows.
J259's *prepared-family* limitation remains correct historically;
this different chronological fault does not identify its prepared
host with J225's actual continuation.

Read-only replay:
`python3 Report/proofs/unregistered_sp31_phaseTF_real2/check_actual_phaseTF.py`.
The retained startup log records a missing output directory before
Python ran. Its subsequent successful discovery changes no rule or
mathematical input; there was no failed CA run.
