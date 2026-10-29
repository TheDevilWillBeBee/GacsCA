# SP31: the actual first pulse tolerates both partial-frame Flag2 commands

This concerns frozen F31 of J223, Q1024/U475136/TF278401, with its
actual own ROM. **No rule, constant, ROM or compiler changes here.**
The new C file is an analysis factor. The theorem is a specified
first-period repair statement, not arbitrary higher-error repair or
an iid threshold.

## Statement

Start at input time0 from E31(z), where every upper cell z(j) has
GF=j modQ, Age0 and all fields other than GF/Info0. Its five Info
components may be arbitrary. Let a=128Q-512, b=143Q. Overwrite only
lower GF by(x+512) modQ on[a,b), and lower Flag1 by1 on
[127Q,a) and[b-512,b). Retain all other actual fields; no later errors.
Every site of[127Q,143Q) is actually changed. This is the same dense
16Q-row location set proved originally real2 at lambda24/c16 in J221;
the classification depends on locations and Q/U, not the changed rule.
An initial upper row of the noiseless F31 hierarchy has the required
native/fresh-field form, so such a z is permitted.

**Theorem.** At t=TF+6144=284545 the actual native fields are

    GF=(x+512) modQ on[135Q-512,146Q), x modQ elsewhere;
    Flag1=1 on[134Q,135Q-512) and[146Q-512,146Q), 0 elsewhere;
    Age=the common legal clock t;
    native Flag2/Workspace1/Workspace2=0 everywhere.

Wrong GF shrinks from15872=15.5Q to11776=11.5Q, exactly4Q.
Its left/right endpoints move+7Q/+3Q. These native fields persist
to the current computed boundary U (with the clock advancing to0).
There all807 non-GF/Age/Flag1/Info bits are0, and the four physical
signal/alias tracks at residues3/509/515/1021 are0. Other retained
Info values and the full upper successor are not characterized here.

The theorem covers all initial upper Info payloads and both actual
unknown partial-frame commands. It does not assume either command0,
or reuse F30's damaged-history pulse through the rule change.

## 1. Actual quiet prefix and source enclosure

For this sharp binary-GF template, the four-block joint GF/Age
refinement returns raw self-GF/common Age. The literal quiet native
equations preserve GF and the two Flag1 strips. The checker repeats
162 edge refinement and4258 native cofactors with the common clock
word free, using F31's maintenance and service_force0. The uniform-
region argument and the quiet-template proof in
[SP28_FULL_ADDRESS_ISLAND.md](SP28_FULL_ADDRESS_ISLAND.md) apply to
the unchanged native fragment. Both Workspace guards are closed
on all legal clocks before TF; initially empty private carriers
have no birth before TF. Native Flag2/Workspace flags are0 and keep1.
Thus every Info vote is constant until T_sig=TF-1.

Let M(y,t) be the majority of the five raw Info holders of primary y.
During each gather the exact logical Mail recurrence loads M times
the quiet-Flag1 gate and shifts eight sites with the same gate. Taking
the five-copy vote gives that recurrence even at strip boundaries.
The strips have512 sites, longer than the shift8; the checker tests
the actual arithmetic-progression crossing predicate for every
relevant native GF source. The same three captures agree. The actual
F31 table/ROM/program and its all-output symbolic certificate are used.

Complete foreign frames have origins jQ-512, j128..142. Their working
and copy footprints[origin+1,origin+1023] lie wholly within[a,b).
All virtual GF inputs read true physical upper H2 bits139..148,
initially0. All virtual Age/Flag2/Workspace2 inputs similarly read
initially zero upper H2 bits at their shifted normal primaries.
Mail erasure preserves those zeros. Complete true frames j<=126 or
j>=143 have the ordinary original Age/Flag2/Workspace2 inputs0.
Other captured inputs may be arbitrary.

The full F31 cofactor with **all raw Age, Flag2 and Workspace2
inputs0**, every GF/Flag1/Workspace1/private/Info/instruction input
free, has output Flag2=0. Indeed common Age0 makes d3 false, old
Flag2/Workspace2 quorums are0, and no private force is supplied.
This is one universal Boolean identity, not a sampled input claim.
The all-GF-zero cofactor also has GF0/Flag1=1, with other inputs free.

The physical quiet-frame program induction is the same as J223:
correct local GF/common clock/keep1, exact three captures, zero initial
work, the new own listing, five-copy/pending/scratch/Match controls
and total own ROM. It executes arbitrary captured circuit inputs,
including each stated constant cofactor. New native Flag1 is the same
unrestricted Boolean function as F30, but its new program is checked
anew. The complete true-frame cofactors give Flag1=1 exactly at
124..126 and143..145; complete foreign frames give Flag1=1 throughout
j128..142. Outside the finite capture neighbourhood, no route meets
either strip and canonical upper-native inputs give Flag1=0.

The actual right courier from virtual965 to1021 delivers those
Flag1 values. The actual left courier from virtual58 to3 delivers
Flag2=0 in every complete frame. The two left-courier paths in the
partial frames can deliver arbitrary bits: true frame127 yields
M(127Q+3,TF), and foreign frame143 yields M(142Q+515,TF).
Their values are left free. No correctness is asserted for the
partial interpreters, Hold, Match or History.

For a non-special physical signal/alias primary, virtual phase is
509 or515 and Info retains its original unused0. The signal holders
are all on a single side of the sharp GF edges: the nearest primaries
are3 sites from an edge and their holders span only±2. Hence there
are no mixed special-write cases omitted at the boundary. The actual
state TF has the exact enclosure

    M(jQ+509)=1 iff j128..142;
    M(jQ+1021)=1 iff j124..126 or j143..145;
    M(jQ+3)=0 except possibly j127;
    M(jQ+515)=0 except possibly j142.

Each exceptional value is a binary voted value. They may be correlated;
enumerating all four assignments is a superset of the actual possibilities.
Both native Workspace fields at TF are0 because their preceding input
clock TF-1 is outside the guard. There is no prescribed future signal.

## 2. Closed actual native/Info factor

After TF and before TF+6144, neither commit nor another special Info
write occurs. F31 native GF/Age/Flag1/Flag2 depend only on raw native
inputs; its Workspace1/Workspace2 read actual old voted Info. Private
headers, execution and external instruction values cannot affect this
projection. This follows from the source equations and the universal
dependency/interface facts in J223, independently of their actual
evolution during the pulse.

The binary adjusted-GF alphabet and common legal clock are closed:
each five-vote has one of the two label majorities; a four-block tie
retains self; both native Age directions have the common clock.
Thus d3 is always false. Write f for new Flag1, A for the count of
old left Flag2 inside the RF colony, B for all five old left Flag2,
and d4 for at least three inside old Workspace2 bits. Then

    on=(A>=4) or(f and B>=4) or d4;
    erase=(not f and A<2) or(f and B=0);
    newF2=(d4 or not erase) if oldSelfF2 else on;
    selectedGF=RF if(not f or newF2) else LF.

Workspace1 reads the old right-special vote at the selected GF's last
five positions. Workspace2 reads the old left-special vote at its first
five positions and additionally requires not f. Both use TF's2048-update
clock guard. These clauses, including nonzero native Flag2/Workspace2,
are implemented in [sp31_two_flag2_sources.c](sp31_two_flag2_sources.c).

For every logical primary y, actual Info voting gives

    M(y,t+1)=M(y,t) * majority(keep(y-slot,t): slot=-2..2),
    keep(x,t)=not(newF1(x,t) and newGF(x,t)!=refinedSelfGF(x,t)).

The old five Info holders need not be coherent: each new copy reads
the same old vote before its holder gate. Thus arbitrary other Info
primaries do not influence this native factor, and a zero special vote
stays zero. The two exceptional votes evolve by this same actual
erasure recurrence. They are not set independently at future ticks.

The checker compares4096 selected complete F31 raw-state cofactors to
the C factor, with arbitrary four flags/Info and private/instruction
bits. These finite transcription checks are measured support; the
source/algebra correspondence above supplies the universal reduction.

## 3. Four exact pulses on Z

Encode GF label and the four native flags in five bits. Outside the
finite nonzero native/special-Info support, the factor maps0 to0.
Its native input radius is37, while the special source reads lie
within[-2,3] of the reader under their end guards. The event partition
splits every native endpoint shifted by-37..37 and both GF phases'
colony/inside boundaries shifted by-8..8. On each interval all raw
native tuples and guard predicates are constant; each special source
is a fixed primary of its selected colony. Endpoint tuple/guard/output
checks certify this constant-interval execution. All cut writes are
capacity-checked before insertion; native segments are sorted and
coalesced, and zero exterior is represented exactly on Z.

Starting from the actual enclosure, replay all four assignments for
the two TF votes, retaining their subsequent erasures and native
Flag2/Workspace2. Each6144-update run finishes at the stated same
T(135,146), with Flag2/Workspace1/Workspace2 zero. The four traces have
40,166,464 event intervals in total and maximum61 native segments.
Flag2 and Workspace2 do fire in the nonzero-source cases: respective
peak supports are1024/5 for either single source and2048/10 for both.
They do not invalidate this endpoint. Every case has one intermediate
row with3 wrong-GF holes; no solid-interval invariant is assumed.
The retained two exceptional Info votes survive when initially1.

The actual TF state corresponds to one of these four assignments.
The closed-factor induction therefore transfers the exact finite
endpoint to the **same actual physical fault history**, for every
initial upper Info payload. No independent later tape or Workspace
input is introduced. QED for the pulse.

## 4. Current boundary and remaining obligations

The new endpoint is again a sharp quiet template with both edges
separated by much more than74, partial strips512 long, a common legal
clock and empty native Flag2/Workspace fields. Both Workspace clock
guards are closed after the pulse. The unchanged literal quiet lemma
therefore advances it through the rest of the current period; actual
private carriers are immaterial because their force into maintenance
was removed in F31. At input U-1 computed GF equals refined self-GF.
J223's807 reset and five masked-Hold forwarding identities apply.
The mask reserves all four signal/alias phases for either binary GF
phase, so those physical tracks are0 at U. This proves the stated
boundary conclusion, not a complete upper-state reconstruction.

What remains unproved is a **second-period bank/source invariant**.
The pulse moves the right edge three colonies into previously true
frames. Their actual GF/H2 and early Hold records, the initially partial
foreign frame, and intervening stored data must be tracked under F31's
own new listing. F30's left-moving bank closure is inapplicable. No
second shrinking pulse, finite arbitrary-island eroder, continuous-E0
repair around this class2 error, full upper error map, iid epsilon or
smallest globally sufficient change is claimed.

| Step | Status | Scope |
| --- | --- | --- |
| Quiet native prefix/common clock/keep1 | proved; existing native-fragment argument applies | Specific one-row template/no later errors; guards and actual wiring checked |
| Complete-frame gathers/new own program/two-free-bit source enclosure | proved by written physical composition and full-function identities | All initial upper Info; partial commands explicitly free |
| Closed native/voted-Info factor | proved | Binary GF/common clock; actual signal erasures and no intervening Info writes |
|4096 selected full-net transcription checks | measured only | Supplement the written reduction |
| Four6144-update endpoints/current native boundary and807 reset | proved by exact finite certificate and composition | Same actual history; one dense16Q real2 at c16 |
| Later regeneration/general higher repair/positive iid theorem | unproved | No transfer of old F30 banks; no globally sufficient/minimum change |
