This result concerns explicitly changed SP28 force durations Q and2Q.
It does not provide their own programmes, a finite-island eroder, an
all-period orbit or an iid theorem. G17 and original SP28 are unchanged.

**Statement.** Let Q1024/U475136/TF278401 be the retained SP28 parameters.
Change only the global RF force-window duration to D=Q or2Q, retaining
the birth at TF and all packet/code/backward/private equations. At common
legal Age TF, set GF=(x+512 L_x) modQ with L the indicator of
[128Q-512,144Q). Set native F1 to1 on[127Q,128Q-512) and
[144Q-512,144Q), and0 elsewhere. Set native F2, both Workspace flags,
packet/code validities and backward pressure to0. Invalid header words,
all private fields and all instruction inputs may be arbitrary. No later
errors occur. Then the following conditional native prefix holds on Z,
independently of these arbitrary inputs:

* For D=Q, at offsets0 through2064, GF=(x+512 L_x(r)) modQ, where
  L(r) is the same interval translated by-3r.
* For D=2Q, the same holds through offset2368.
* Age is the common legal clock TF+r. Native flags lie in the retained
  lower/upper enclosure; packet/code validity, tags/positions and common
  counts, and backward pressure agree with the exact header computation.
* At the next update, the lower/upper **allowed raw-state corners** give
  different GF outputs at one site:461/973 at x124365 for D=Q, or573/61
  at x123453 for D=2Q. Both have output F1=1; output F2 is0/1.
  Actual dynamically reachable flags are not proved to attain both
  corners. Therefore this enclosure does not determine that next GF.

This is a proved finite conditional prefix and an exact local limitation
of the enclosure. It is not proof that either changed rule is an eroder
or admits a persistent defect. The initial native seed is prescribed;
this certificate does not derive its private history from an intact
recursive hierarchy.

**One-step projection.** Here are the identities connecting the C
certificate to the actual full Boolean transition.

1. At fixed reader x, every adjusted GF word is either x modQ or
   (x+512) modQ. Their low nine bits agree and their high bits are
   opposite. Their Age words agree. Each five-word block consequently
   has a whole-word majority. The four-block joint3/4 refinement is
   exactly majority of the four binary block labels if at least three
   agree; with two of each it retains the raw label. This is the C
   `refined` equation. The refined Age remains common. Both RF and LF
   five-word GF/Age votes exist. The native clock selection therefore
   selects the common Age and increments it correctly. No arbitrary
   instruction or private field occurs in this identity.
2. Write v=(x+512 RF) modQ. The actual `inside[j]` is precisely
   0<=v+j<Q. Native inconsistency reduces to at least three left GF-label
   mismatches. Joint-right exists; quiet-joint is at least three matching
   right labels with raw F1=0. Right native F1 counts, its hysteresis,
   the guarded quiet failure and Workspace F1 votes then give exactly
   C's `flags` F1 formula. Native d3 is false. Native d4 is at least
   three valid raw packet/WF2 bits inside this range. The remaining
   Flag2 on/erase clauses and service force give C's F2 formula.
3. Every packet/code descendant is born at the sole common TF birth.
   There is no earlier valid header. At positive offset r, each valid
   packet or code has counter r-1. Birth is only offset0 and output
   RF GF1..5 gives tag GF-1. Invalid initial words are ignored by validity
   and are canonicalized in the first output. By induction every valid
   packet tag lies0..4 and every valid code position lies0..1028.
4. The packet cohort's adjusted tag is(tag_j-j) mod16. Equal-counter
   tests are automatic for live headers. Any three adjusted tags force
   the packet cohort bit, even when the target tag is outside0..4 or
   the counter is1791. A retained packet additionally needs target
   tag<5 and r-1<1791, hence r<=1791. A strict minimum-counter selector
   chooses the first qualified lane on equal counters. The C loop uses
   this exact order; it does not assume a single integer packet origin.
5. For the combined code carrier, a usable packet wins a tied usable
   code at the same physical cell. Its position is tag+6. Otherwise a
   usable code supplies its raw position. Adjusting each by-j mod2048,
   voting at least three equal adjusted positions and retaining the
   first qualified lane with position<1029 reproduces the code selector.
   Both carrier kinds need r<=1791. This handles all simultaneous
   origins and overlapping frames, without the two-origin quotient of
   the separate canonical-GF clock-island proof.
6. The backward detector is the same any-three packet cohort on13
   inputs. Right-pressure propagation needs three of five right bits
   and RF GF!=Q-1. The legal common clock lies in its window exactly for
   offsets0..1792. These are C's backward equation. The force passed
   to native maintenance is exactly global(r<D) OR packet-cohort OR
   valid-new-code OR backward-signal. Raw packet/WF2 d4 is also retained.
   At state1793 packet/code validity is0; backward can remain1 there
   and is0 at state1794. The computation does not omit these forces
   merely because the global window has ended.
7. For arbitrary private fields, output Workspace F1 is bounded between
   zero and[computed GF>=Q-5 AND0<=r<2Q]. Native F1 is increasing in raw
   F1 and WF1. The native F2 formula is increasing in new F1 and raw F2
   (the literal assignment check reused from J154 also proves this).
   Packet, code and backward outputs do not depend on these flags.
   Induction thus encloses every actual flag input and output in the
   two computed corners. At a site where RF!=LF, every actual selector
   chooses RF if !F1_hi OR F2_lo; every selector chooses LF if
   F1_lo AND !F2_hi. Otherwise the C certificate stops. Before the
   reported stop, every selector is certified unique. Workspace bounds
   at the next row use that common computed GF.

Commit reset is absent throughout this finite pulse because its clock
stays below U-1. Neither the early special Info update nor private
execution is silently substituted for a header or force equation.

**Finite certificate and infinite line.** The retained C source evolves
all256Q sites with the exact header positions and the two monotone native
corners. At the start of every prefix row it asserts that the entire GF
plane equals the proposed sharp interval translated by-3r. It stops
before choosing an ambiguous output. The checker compares every retained
snapshot and the terminal raw-state frame against the independently
retained exploratory frames. Four full-net symbolic cofactors, with all
private/instruction bits free, verify the differing terminal native
outputs directly in the changed Boolean rules. The finite prefix proof
uses the one-step identities and exhaustive row computation; random
sampling is not its basis.

Periodicity of the numerical array does not supply an unqualified lift.
The initial two boundaries are separated16Q+512. A sharp two-phase GF
step is unchanged by the four symmetric block refinement; its RF/LF
votes only differ within three cells of that step. The prefix assertion
closes this shape hypothesis on every row. Thus the GF support moves
three cells per row. Other native discrepancies propagate at most eight
cells per row: raw F1 reaches eight to the right, other flag inputs five,
and packet/code selection and pressure propagation five (the pressure
seed detector reaches six). Initial birth differences depend on refined
GF within37 cells. Comparing with the Q-periodic canonical far reference
therefore confines all discrepancies through the last row inside the
initial support enlarged by8*(2368+1)+37<48Q. The array's seam is more
than112Q away. Its wrap never enters this interval. The far reference
matches itself under periodic wrapping; induction lifts the finite
prefix and its corner words to Z. This lift does not choose a selector
after the stop or extend the conclusion to another period.

**Other exploratory outcomes.** In separate controlled runs, imposing
WF1=0 throughout the pulse leaves a quiet native template translated-6Q
at6Q, for both short durations. Imposing WF1 equal to its maximum guard
leaves a quiet template translated-8Q. Both retain16896 wrong GF sites.
These retained traces are **measured only** here: the certificate does
not derive either imposed private signal history from an intact hierarchy,
prove all-period composition, or use them as a universal eroder/orbit
theorem. Their differing displacements also prohibit identifying the
two extreme traces with the arbitrary-input trajectory.

**A useful conditional private invariant.** If, at clock TF, all five
Info holders of every logical primary at residues509 or1021 modQ are0,
then they stay0 throughout this pulse, provided the common legal clock
and two-GF-phase hypotheses continue. On these clocks neither commit
nor special Info update fires. Every output Info copy is its current
five-holder majority multiplied by the wipe keep bit. It cannot create1
from five zero holders, independently of private execution or I. For
either computed GF phase, the Workspace F1 source's logical primary
has canonical spatial residue Q-3-512*phase, namely1021 or509. Its vote
is therefore0 and actual WF1 remains0. This invariant is **proved under
the stated initial Info premise**, but this document does not assert
that a full all-period damaged hierarchy supplies that premise. In the
current layout residue509 encodes upper h2 bit77, whereas1021 is the
special upper Flag1 source. Their future values need a genuine data-map
argument; native geometry alone does not prescribe them.

| Step | Status | Scope |
| --- | --- | --- |
| Full duration-only Boolean transitions | proved defined | Explicit unincorporated revisions; free instruction inputs |
| Actual header/native one-step projection and monotone enclosure | proved | Two GF phases, common legal clock, simultaneous birth ancestry |
| Unique arbitrary-private native prefix through2064/2368 | proved | Prescribed initial native seed; finite pulse lifted to Z |
| Two terminal allowed corners give different full-rule native outputs | proved | Four all-private cofactors; reachability of both corners unproved |
| Zero Info residues imply zero WF1 during this pulse | proved conditionally | Initial five-holder zero premise and continued common/binary geometry |
| Fixed-zero/fixed-maximum WF1 quiet-template outcomes | measured only | Controlled traces; full private reachability/all-period lift unproved |
| Post-stop native trajectory, own programmes, higher map, eroder and iid ε | unproved | Short durations remain undecided |
