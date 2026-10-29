# SP30: a literal c104 Proposition5 box transplant fails

This is a consequence of [J216's finite actual history](SP30_FINITE_REGENERATION.md)
for unchanged frozen F30, Q1024/U475136. It changes no rule, programme,
constants or accepted receipt. The error-class constant here is a
classification parameter; the actual physical trajectory is the same.
It is not Gray's rule and no conclusion about Gray/Gacs reliability or
positive iid noise follows.

[Checker](check_sp30_error_envelope_comparison.py),
[certificate](../../../figs/robustness/unregistered_envelope_comparison/certificate.json)
and [run](../../../figs/robustness/SP30_envelope_comparison_run.log).
The primary statement is Gray's Proposition5, printed p43 in the
[supplied text](../../../papers_txt/gray_readers_guide.txt): one level-k
error is associated with a box of spatial width2Q^k and temporal
heightU^k/16; outside the boxes every level's Address is preserved.
We test that exact statement only as a proposed transplant to F30.

## Exact scope of the failed statement

Take J191's one dense error row S=[127Q,144Q) at time0, from its
pristine hierarchy, with the exact GF512/F1 payload and no later errors.
Such a hierarchy exists by J189's nested encoding construction and is
included in J216's quantifiers. The error-free shadow has native
GF(x)=xmodQ at every time by J189's native/noiseless theorem.

At c104 this is one original real2 and no lower errors. Suppose there
were a box [jQ^2,(j+2)Q^2) times[t,t+U^2/16), for some integer j
and some t, outside which the actual native Address equals that shadow.
The two calculations below independently contradict that supposition.
They also rule out an arbitrarily placed spatial interval of width2Q^2
or temporal interval of heightU^2/16, so alignment conventions cannot
repair the contradiction.

## The original recursive class, not a size label

In fact S is real2 for every integer c>=17 and real3 for1<=c<=16.
Use Gray's four original definitions with lambda24, as in ROBUSTNESS§3.
No proper candidate1 or candidate2 subset can be real: some member
of its complement lies within the corresponding isolation scale,
since the entire row has span17Q<24Q. Real0 groups fail their
24-site isolation against their nearby remaining dense-row points.
Thus E0/E1 are empty; when S is not real2, E2 is empty too.

S fits a Q^2 by U^2 box and contains two linked candidate1 pairs,
so it is candidate2. If c>=17, its total spatial span17407 is less
than cQ, excluding two (cQ,cU)-separated candidate2 subsets. The
whole history has no exterior, so condition(iv) holds. Hence S is real2.

For1<=c<=16, its first four and last four points are disjoint
candidate2 subsets. Their minimum spatial distance is17Q-7=17401,
at least cQ, so they violate real2 condition(iii). They are nevertheless
linked at the next scale24Q^2, and S fits a Q^3 by U^3 box. Its
whole span is less than Q^2<=cQ^2, so real3 condition(iii) holds;
condition(iv) is again vacuous. Hence S is real3.
This agrees with the frozen c16/c104 classifier receipts of J156/J191.
Translation of their error time from U to0 changes no distances.

## Spatial contradiction at two proved endpoints

J216 gives the wrong-GF interval at input period p as

    I_p=[(122-6p)Q-512,(128-6p)Q),
    t_p=pU+284545, 6<=p<278401.

At p6, I_6=[87552,94208), so x=94207 has wrong computed native GF.
At p347, I_347=[-2007552,-2000896), so x=-2007552 also has wrong GF.
An interval containing both integer sites must have lattice width at
least94207-(-2007552)+1=2101760. This exceeds2Q^2=2097152 by4608.
Consequently no single Proposition5 spatial box can contain all damage
from this one real2 history. Both endpoints precede upper WF activity.

## Temporal contradiction at two proved endpoints

At p6, t_6=3135361 and the wrong interval is nonempty.
At p29703, t_29703=14113249153 and the wrong interval is nonempty.
Their time difference is

    29697U=14110113792 > U^2/16=14109638656.

Thus no time interval of the asserted height can contain both damage
rows, independently of its origin or whether endpoints are included.
The second row is still far before the J216 horizon p278400.
No permanent defect or extrapolation beyond that horizon is used.

Therefore the literal Proposition5 Address-box statement is false for
this changed F30 under c104, and also under every integer c>=17.
Both the spatial and temporal parts fail for this same original error
history. This is a deterministic counterexample to that transplant,
not a proof that the variant lacks every possible noisy repair bound.

## Why c16 and iid conclusions do not follow

At c16 the same row is real3. Its asserted Proposition5 box would
have width2Q^3=2147483648 and heightU^3/16=6703997272457216.
The hull of **all J216 endpoint** wrong intervals has width1710459392
and their first-to-last temporal difference132275011584. Both are
smaller than those class3 allowances. This comparison does not prove
containment in an aligned box, does not bound intermediate/higher-level
damage and does not establish actual later recovery. It establishes
only that the preceding class2 size contradictions do not carry over
to class3. The R envelope used in ROBUSTNESS§11 is also a separate
statement with different constants and requires its own comparison.

The largest integer c that promotes this particular row to real3 is16.
That is an exact classification boundary for this witness, not a
minimum sufficient modification or a proof of reliability at c16.
Every positive iid noise history has additional faults excluded from
J216; neither the finite defect nor this box comparison proves an
iid memory failure. G17 and Gray's actual construction remain unaudited
by this specific counterexample. No commit.

| Step | Status | Limit |
| --- | --- | --- |
| Original recursive class for all integer c>=1 | proved above | One dense17Q row; no exterior noise |
| Actual damaged endpoints and correct native shadow | proved previously; applies | J216 and J189, unchanged F30 |
| Literal real2 Proposition5 spatial and temporal boxes | refuted for F30 at c>=17 | Same actual history and finite endpoints |
| c16 class3 envelope or general alternate repair envelope | unproved | Class2 contradictions do not imply either claim |
| Gray/Gacs contradiction, iid failure or sufficient minimum change | unproved; not claimed | F30 has explicit mechanism/compiler departures |
