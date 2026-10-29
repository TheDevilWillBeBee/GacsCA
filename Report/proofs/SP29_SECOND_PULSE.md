# SP29: the actual second shrinking native/Info pulse

This is a theorem about the unchanged isolated SP29 rule and the exact
original error of SP29_FIRST_SIGNAL.md. The upper Info payload is
arbitrary, and there are no errors after the native GF/Flag1 overwrite
at clock0. It uses the corrected refined-self-GF factor of
SP29_REFINED_WIPE_FACTOR.md, the actual first boundary of
SP29_NEXT_GHOST_SIGNAL.md, and the complete second-signal enclosure of
SP29_SECOND_SIGNAL_ENCLOSURE.md. No rule, ROM or constant is changed.

**Theorem.** At computed time

    t2 = U + TF + 6144 = 759681,

native GF is canonical outside [118272,131072) and shifted by512 inside
that interval. Its width is12800, compared with14848 at the beginning
of the second pulse: a further decrease of2048=2Q. The left and right
edges move respectively -6Q and -8Q. Native Flag1 is exactly1 on the
512-site strips preceding these two edges. Native Flag2, WF1, packet
and code validities, backward pressure and code positions are0. The
remaining signal Info majorities are the ones specified by the common
final arrays in the eight-case certificate. All eight final projected
native/code/Info states are identical.

The conclusion is on Z and applies to the actual preceding physical
history. It is not a theorem of complete upper-data restoration,
general finite-error erosion, a third signal, or iid reliability.

## Initial state supplied by the physical history

At t0=U+TF=753537 the preceding native theorem gives the common legal
TF clock, binary GF template [124416,139264), quiet Flag1 strips
[121Q,121Q+512) and [135Q+512,136Q), and zero native/header auxiliaries.
The physical signal-enclosure theorem gives precisely these tracks:

    MF509: ones122..135, possible extra one121;
    MF1021: ones118..120 and136..146, possible extras117 and135;
             zero elsewhere.

The three optional bits may be correlated. Any actual history chooses
one of the eight masks; enumerating all eight requires no independence
or extra preparation premise. No correct upper encoding is assumed
at U, and no scalar/native substitute is used for the cofactor proof
of the signals. Other simulation/private state and matched I words
remain arbitrary.

## Exact closed transition and eight finite certificates

The corrected factor theorem applies verbatim to this pulse. With L
the raw binary GF label and J its joint-refined old label, it uses

    K(x,t)=NOT(F1_new(x,t) AND (L_new(x,t)!=J(x,t))),
    M(y,t+1)=M(y,t) AND [sum_{s=-2}^2 K(y-s,t)>=3].

WF1 reads the old M at the computed-GF signal primary. All native,
header and code equations are the actual restricted rule equations.
There is no special Info write or commit within these6144 updates.
The common legal clock, two-GF alphabet, initially zero valid headers
and actual sole birth close the factor independently of other private
data. The duration is SP29's actual2Q guard, not an imposed signal.

The generated C wrapper includes the corrected factor source. For each
of the eight masks it checks every site of N=256Q=262144 at every one
of6145 rows, including the initial row. Each run certifies1610874880
GF-support site checks and1113215910 exterior/background equalities.
The total over eight masks is12886999040 and8905727280 respectively.
Every run finishes with the stated contiguous wrong-GF interval and
quiet native/header/code template; the saved full final arrays compare
equal between masks for native, code and both retained Info tracks.
Two intermediate rows have two holes in the GF support, so the proof
does not infer an always-contiguous intermediate interval or a uniform
inward velocity.

These are exhaustive finite integer-recurrence certificates, combined
with the exact factor and the lift below. The driver retains every row,
source and endpoint. Its independent receipt deliberately calls the
patterns conditional; the separate physical enclosure is what makes
their conclusion apply to the actual history. No finite noisy sample
is used to establish a universal error-recovery statement.

## Infinite-line lift

Take the initial projected defect seed I=[117Q,148Q), which contains
the entire GF/Flag1 defect and every possible signal one. Outside I
the projected state is the actual Q-periodic canonical background.
The native/header background evolves during the pulse, including its
epoch-born components; it is not replaced by a permanently quiet row.

The binary-GF hull lemma of SP28_INFO_NATIVE_SHRINKING_PULSE.md applies
to the same native update: arbitrary flags/signals cannot create label1
more than3 sites beyond its previous finite hull. Joint refinement
reads within32 of a holder; a flag's nearby refined-GF reads are covered
by the37-site reserve. Native flags, valid headers and codes propagate
at most8 per update once that GF reserve is included. The corrected
Info equation can only erase existing ones. Induction therefore confines
all projected differences at row r to

    [117Q-(8(r+1)+37), 148Q+(8(r+1)+37)).

This is a projected support bound; it says nothing about spatial
confinement of the arbitrary unobserved simulation/private fields.
The wrapper verifies exterior equality with the evolving periodic
background at every site of every row. At r6144 the protected interval
is [70611,200749), strictly inside the quotient. The radius of each
actual projected read is covered by the stated margin, and Q divides N.
Consequently the quotient seam always has the same periodic input
neighborhood as the background on Z. Induction on rows identifies the
quotient recurrence with the infinite-line projected recurrence inside
the protected interval and with background outside it. This supplies
the stated endpoint on Z for every mask, hence for the actual history.

## Scope

| Step | Status | Exact limit |
| --- | --- | --- |
| Actual second tracks lie in the three-bit enclosure | proved | Same specified initial error, arbitrary initial upper Info, no later errors |
| Corrected native/header/Info factor during the second pulse | proved | Restricted binary GF/common-clock/sole-birth premises, arbitrary other private/I |
| All eight finite recurrences, common final arrays and exterior certificates | proved | All sites and6145 rows; intermediate holes retained |
| Actual second shrinking native/Info pulse on Z | proved | Physical enclosure plus exact factor, finite certificates and explicit support lift |
| Third signal, all upper data, arbitrary width/phase/errors, higher map and positive iid rate | unproved | Two particular shrinking pulses do not provide this induction |

Reproduce the conditional finite certificates with
probe_short_force1024_second_pulse_cases.py and the actual-history bridge
with check_short_force1024_second_signal_enclosure.py. Sources, eight
logs and final arrays are retained in figs/robustness. Active G17 and
all frozen proposals remain unchanged; no commit is made.
