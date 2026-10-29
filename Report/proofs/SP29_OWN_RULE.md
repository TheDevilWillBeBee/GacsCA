# SP29: an own programme for the two-Q force window

SP29 is an **explicit change** to the isolated SP28 proposal. Its global
RF force lasts 2048 ticks, starting at T_wf=278401, instead of SP28's
4096 ticks. All other transition equations and parameters are retained.
The proposal has its own compiler family, freshly compiled ROM and
candidate. It changes no active G17 file or earlier proposal.

The purpose is to remove the missing own-programme premise for studying
the short pulse. The conclusion below is restricted to complete encodings
and actual global E0 noise. It is neither a finite-island eroder theorem
nor a reliability theorem under iid noise.

The exact parameters are Q=1024, U=475136, width842, radius37, 64 history
ranks, NPe=272, MP=289 and NP=384. The full Boolean graph is identical,
array for array, to J164/J165's retained D=2Q graph; the comparison includes
all input names, gates and output indices. Layout, capture table and the
generated SF source are also identical. The constructor cache and the
candidate bind to this new family. The complete graph has 91625 gates
and SHA256 `ed9204562cff9335519970fd45998f92aed1881b08b90d3e624ec42e9b7e5851`.
The own candidate SHA256 is
`baa51e7c4dfd73fffc681d687d0533dfb732e975dc533258d7216b425a9516e8`.

Write F29 for the fixed actual rule using that own ROM. Define E29(z)
as E28(z), with z now a configuration of this rule: native GF(x)=x modQ,
Age0, every other non-Info field0, all842 bits of each upper cell in
five coherent Info copies at normal phases59..900, auxiliary upper
Flag2 at58 and Flag1 at965, all remaining logical Info primaries0.
The layout assigns each normal phase its specific state bit.
Define B29(z,b) by allowing arbitrary coherent Info b at all182 phases
outside the normal frame, including the two auxiliary phases and3/1021.

**Theorem (complete-start E0 simulation).** Let w0=B29(z,b), let X_t be
w_t after arbitrary whole-state overwrites at tick t, and set
w_(t+1)=F29(X_t). Suppose the full overwrite location set, including
tick0, is an actual global E0 set for lambda24: groups are singletons
or spatial adjacent pairs at one tick, separated24 from every other
group in the repository's error convention. Then, for every n>=1,

    w_(nU) = E29(F29^n(z)).

The raw five-copy decoder of the normal primaries at every nU, including
n0, is F29^n(z). The computed-state identity is before fresh overwrites.
The theorem quantifies over all upper configurations z, unused bits b
and overwrite payloads satisfying that deterministic location premise.
It makes no assertion that iid errors satisfy this premise.

**Proof.** The native induction of ROBUSTNESS J125 applies with the
present Q/U/clock and actual wiring. For each logical native input,
the four joint GF/Age votes have centers−30,−10,10,30 and radius2.
Every E0 five-cell block has at least three correct joint words.
At least three existing block votes therefore give the correct pair;
the accepted four-block vote gives that pair even at an overwritten
reader. Both native selection modes return canonical GF and the same
legal Age; arbitrary flags, packet/code state and service force choose
between equal values. Changing the force window cannot change this
argument, because the native cofactor leaves service force free.
The literal native output wiring and every legal increment, including
the wrap, are checked for SP29. Induction gives globally correct
computed GF/Age at every tick. The refined raw self-GF and computed GF
agree, so the actual keep mask is1. No assumption about a correct work
programme is needed for this native conclusion.

Before T_wf the WF1 clock guard is closed. With correct native geometry,
there is no diagnostic Flag1 source, and E0 contributes at most two
faults to any five-vote input. The initially zero computed F1/WF1 hence
remain zero until that clock. The only pre-commit special Info writes
are at3/1021, outside the normal frame. All normal primaries and their
copies are restored to their unchanged logical values on each update.
Arbitrary coherent unused Info does not affect this statement.

Use J135's corrected fast-mail recurrence: an offset d capture makes
exactly |d|Q/8 speed-eight shifts and reads (j+d)Q+a at the same normal
phase a. The actual speed/window interfaces are unchanged. All25284
requested gather coordinates are checked, and all requested history
ranks are supplied. Latest captures are4737,14977,25217, before
evaluation25984. The source-reference and five-holder induction in
J135 thus supplies the required upper inputs under E0 for every z.

SP29's own symbolic programme certificate checks every130871 actual
instruction, independently repacks its entire ROM, proves the22 Match
key bits, both early flags and all842 final Hold bits equal their
corresponding F29(z) outputs. It checks causal register/scratch reads,
every front visit, and every capture deadline. Its abstract premise
is discharged by the same physical register/pending/scratch copy
induction used in J135/J138: the centers, directions, storage schema,
copy windows and source families are unchanged, and keep remains1.
The own front checker establishes unique arrival for all raw native
words and total ROM bounds for every raw address/selector. Shortening
the force only changes which already equal native modes are selected.

The separate read audit checks all261742 operands. Its1354 direct
Info reads and17684 history reads all use normal primaries; remaining
reads are registers, scratch or constants. No unused Info, previous
auxiliary flag or unspecified initial Hold enters the programme.
This proves that B29(z,b) and E29(z) have the same required programme
inputs, without an initial auxiliary/ordinary flag equality assumption.

Both early stores, at276528 and260747, precede their courier loads
278343/278344. Those loads replace the mail references with the newly
computed upper flags. The protected paths write special Info at signal
clock278400, producing computed state278401, before the first enabled
WF1 read. Thus the pulse uses the new flag values independently of b.
Later flags can gate mail but cannot erase the completed histories or
work, since keep1. WF1 closes at computed clock280450. The same native
source-free Flag1 contraction used in J138 needs575 updates and gives
all F1 quiet by281026, before evaluation ends382336 and commit475135.
The contraction depends on correct native fields and the closed WF1
source, not on the length of an arbitrary service-force selection.

The actual commit interfaces give807 literal zero outputs, all five
forwarded-Hold/Info-mask identities, canonical GF/Age0 and zero F1.
Exactly844 allowed primaries have4220 allowed copies; the other900
copy slots are zero. Hence the computed commit is precisely E29(F29(z)),
including the two newly established auxiliary aliases. This is the
complete initial premise for the next period, proving the identity
for every n. At any boundary an E0 overwrite changes at most two of
each five-copy group, so the raw decoder also has the stated value.
The n0 decoder is exact directly from B29. QED.

Noiselessly F29^U E29=E29 F29. The same nested compact encoding-image
argument as J135 yields an infinite noiseless initial hierarchy for
this one fixed rule. This is a deterministic consequence of the proved
commutation, not a positive iid threshold.

J164's exact native/Info factor and J165's conditional shrinking pulse
now apply to this own rule, because their native proof allows arbitrary
I and private fields and the complete graph has been compared directly.
They still require the prescribed TF native island and asymmetric
logical Info values. The new own programme does **not** prove that an
intact damaged hierarchy supplies those values, that they replenish
in later periods, or that every damaged island shrinks.

| Step | Status | Limit |
| --- | --- | --- |
| Explicit constructor graph/layout/capture identity | proved | Direct complete arrays, not checksum comparison alone |
| Build and64 replay vectors | measured only | A successful compilation is not the theorem |
| Own symbolic programme, deadlines and local front/ROM bounds | proved | Abstract execution and literal local interfaces |
| Global native GF/Age induction | proved | Canonical/common initial native fields; actual E0, also J125's real1-only native extension |
| Physical complete-start simulation and broad-family contraction | proved | Actual global E0 only; all upper configurations and coherent unused Info |
| J165 prescribed asymmetric shrinking pulse | proved conditional statement applies | Graph identical, arbitrary I/private; source values still premises |
| Actual damaged-history supply, any-phase/width repair, higher map and iid rate | unproved | Neither build nor E0 simulation discharges these |
| A sufficient or smallest globally reliable change | unproved | SP29 is a research proposal, not a reliable replacement |

All checks use python3. Receipts are in figs/robustness under SP29:
interface_identity, program_build, symbolic_schedule, front_certificate,
native_certificate, encoded_certificate and encoding_family_certificate.
No C/CUDA trajectories are used for this complete-start theorem. The
64 build replays are explicitly separate experimental evidence.
