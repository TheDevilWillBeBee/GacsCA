# SP31: all4096 third-command assignments shrink the actual native defect

This is a computer-assisted finite pulse theorem for **unchanged isolated
F31**, Q1024/U475136/r37, and the same actual J225 native-only dense16Q
original-c16 real2 error, arbitrary initial upper Info and no later
errors. It proves a third native pulse/quiet boundary. It does not
reconstruct a complete upper successor or prove general repair/iid.

## Exact statement

[J238](SP31_THIRD_SOURCE_ENCLOSURE.md) supplies the actual third commands
at2U+TF=1228673: MF509 ones142..148, MF1021 ones112..140/149..151,
twelve free F2 bits MF3(131..141)/MF515(148), everything else zero.
The native state is T(142,149), common legal clock, F2/Workspace zero.

For every one of4096 binary assignments to the free commands, the
literal native/voted-special-Info recurrence for6144 updates ends

    [148Q,149Q-512)       GFtrue,    F1=1;
    [149Q-512,152Q-512)   GFforeign, F1=0;
    [152Q-512,152Q)       GFforeign, F1=1;
    elsewhere            GFtrue,    F1=0;
    F2=WF1=WF2=0 everywhere.

Here GFforeign means (x+512) mod1024 and GFtrue means x mod1024.
This is T(149,152). Wrong GF has width3584 instead of7680, a reduction
of4096=4Q. The left edge moves7Q and the right edge3Q. The same actual
physical history therefore has this native endpoint at1234817.
The quiet native recurrence carries it to3U=1425408; the existing
807 private reset/masked-Hold/alias-zero identities apply there.
Normal upper Info remains uncharacterized. No mask is asserted
reachable or independent: exhaustiveness covers the actual unknown
assignment without that assumption.

## 1. Unchanged closed factor — previous proved argument applies

Use [J225 section2](SP31_FIRST_PULSE.md). Native maintenance receives
no private SF force. A binary adjusted-GF alphabet/common legal clock
is closed through the pulse. The four distant blocks at centers
-30,-10,10,30 have five entries each; their GF/Age pair vote is exactly
the majority of the binary labels. The three-of-four replacement
returns1 if at least three block labels are1,0 if at most one is1,
and otherwise retains the raw self label.

Both native five-cell GF votes exist. Both Ages are the actual common
clock, hence source3 is false. The literal F1/F2 population/erase
equations and selected right/left GF are the frozen C factor's
`local`. Computed Workspace reads old voted special Info, with the
actual2048-update source guard and F1 suppression of WF2. Other Info
primaries never enter those sources. There is no intervening Info
write or physical error. For each logical special primary y,

    M(y,t+1)=M(y,t) AND majority(keep(y-slot,t), slot=-2..2),
    keep(x,t)=NOT(newF1(x,t) AND newGF(x,t)!=refinedSelfGF(x,t)).

The five physical holders need not stay coherent during the pulse;
this is their exact old-vote/holder-gate/new-vote equation. Arbitrary
other Info, registers and private headers remain unrestricted.
Thus the actual physical history has exactly this factor for each
of its actual commands. J238 derives those commands from actual banks,
captures, own stores and couriers rather than supplying a future tape.

## 2. Dense CUDA transcription — proved equation correspondence

[CUDA evaluator](unregistered_sp31_third_sources/sp31_third_dense.cu)
uses only integer operations. Its byte stores label/F1/WF1/F2/WF2
in bits0..4, just like the frozen C factor. `refine` implements the
four five-label votes and the three-of-four selection above.
`update` first constructs all eleven refined labels, then the right
and left five-votes. Its p=(x+512*RF) mod1024 is the literal inside
guard coordinate. The left mismatch, eight right flags, eleven
Workspace populations, right quiet population, F2 on/erase/retention,
selected GF and source reads are precisely the C equations. It writes
keep using the refined self label. `update_info` multiplies the old
logical vote by the five keep majority. Kernel completion order is
refine, native/keep, Info, capture; it always reads the preceding row.
The modulus is an AND with1023, valid since Q is1024 and x>=0 here.
All sums are tiny bounded integer populations; no floating result
enters the automaton. Metric reductions use exact32-bit counts/maxima,
with no overflow (domain114688 sites).

Initialization constructs exactly T(142,149) and J238's track table.
Mask bits0..10 give MF3(131..141); bit11 gives MF515(148). Every mask
0..4095 occurs once. No native clock, flag, Workspace or special Info
is altered during subsequent evaluation except by these equations.

An independent observer of the frozen C event evaluator retains its
complete native segments and special Info at every row for masks
0/2047/2048/4095. Their original event traces are byte-identical to
the earlier four pilots. Sorting the CUDA transition records and Info
coordinates gives exactly those whole states for all24580 rows.
Counts alone are not the state-comparison claim. These selected
transcription checks supplement the universal clause correspondence;
they do not establish a general rule identity by sampling.

## 3. Finite domain extends to Z — proved checked invariant

CUDA evaluates [80Q,192Q). The native factor radius is37; a Workspace
source read under its end guard is at displacement[-2,3]. Every row
checks the first and last64 sites have native byte0 and special Info0,
including row0 and row6144. All25,169,920 case/row records have zero
border violations. The selected transition records also include the
last transition to0; neither endpoint is cut off by the domain.

Native byte0 denotes true GF/common Age/zero flags. With every special
Info source0, the infinite exterior maps to itself. Every exterior
site whose radius37 cone could meet the represented domain sees only
the checked zero strip. Logical special Info cannot be created where
its old vote is0. Thus induction on rows proves equality of the finite
representation with the infinite-line factor: the exterior is exact,
not a forced repair wall. Ordinary Info outside the four native source
tracks may be arbitrary; it is irrelevant to this projection.

## 4. Exhaustive finite certificate — proved, computer assisted

The complete execution retains all4096*6145=25,169,920 row records,
covering2,886,218,022,912 represented native cell updates. Each final
native byte is compared directly with the specified three-segment
template; the per-case mismatch count is0 for every mask. This is
stronger than matching the wrong-GF width. Every final F2/Workspace
count is0. Every case has the same all-row GF hull[144896,155648),
not an assumed solid-interval invariant. Info erasures and all four
native flags are computed normally at intermediate rows.

The receipt contains all binary arrays, their dimensions/hashes, the
source/executable/build provenance and selected complete state records.
The checker rebuilds both evaluators, verifies all retained hashes,
independently reruns all4096 GPU assignments and four C state traces,
checks every row metric and compares sorted full selected states.
This finite computation is a proof dependency; it is not a noisy
simulation extrapolated to unlisted masks or unbounded time.
For CUDA executable comparison only nvcc's PID in one nonallocated
`.strtab` STT_FILE filename is normalized, with exact ELF section/type/
allocation checks and fixed-length replacement. Every other byte,
including host instructions/device fatbin, must match. The initial
overstrict raw executable hash check failed on precisely this compiler
temporary filename before any replay; its source/log and diagnostic
rebuilds are retained. This is not a CA or trajectory failure.
The C rebuild's identical warning text also contains its temporary
source path. Only that exact path is substituted for log comparison;
the whole C executable is byte-identical. The intermediate raw-log
path assertion failure is retained and occurred before CA replay.

The actual J238 assignment is included, so the closed-factor induction
transfers this endpoint to the same original physical history for all
initial upper Info. It does not introduce independent later errors.

## 5. Quiet3U boundary and remaining obligations

The endpoint has512-site strips and separated edges, common legal
clock and F2/Workspace0. Its shortest homogeneous bulk is far larger
than twice radius37. Both Workspace guards are closed after TF+6144.
The unchanged literal quiet lemma in J225 section4 therefore applies
until commit. Native/private force is still0 regardless of actual SF.
At input U-1 the computed GF equals refined self-GF. J223's807 reset,
five masked-Hold forwarding identities and reserved alias store
exclusion give the stated native/reset/alias-zero boundary at3U.
These statements concern the same physical history, not prepared SF.

Actual fourth-period native banks/sources/pulse remain unproved.
The third pulse enters new true frames and no correct execution of
their prior full SF is asserted merely from the native endpoint.
No full upper successor/repeated invariant, arbitrary real2 eroder,
surrounding E0/higher repair, positive iid rate or minimal sufficient
change is supplied. G17 and Gray are not refuted. No rule was changed.

| Step | Status | Scope |
|---|---|---|
| Actual third commands/fresh native boundary | previously proved argument applies | J238, same original fault/all upper Info |
| Closed binary native/voted-Info factor | previously proved argument applies | J225, actual erasures/flags retained |
| Integer CUDA equations/checked infinite exterior | proved | Direct correspondence and every-row border invariant |
|4096 final native templates | proved by exhaustive finite certificate | Every mask, no reachability/independence premise |
| Four C/GPU whole-state comparisons | measured supplements | All6145 rows for each selected mask |
| Actual third pulse/quiet3U native/reset boundary | proved by composition | Actual command enclosure and literal quiet/reset identities |
| Fourth banks/pulse/full successor/general repair/higher/iid/minimum | unproved | No global reliability theorem |
