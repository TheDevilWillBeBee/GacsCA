# Canonical global structural invariant

2026-09-26. The complete fixed physical descriptor now has a checked head-routing
and inactive-controller lemma at every clock value. Joined with the previous
[replica output-image result](ALL_CLOCK_MAIL.md), it establishes an invariant
structural domain for arbitrary numbers of physical ticks. This closes a
premise of the instruction-refinement work; it is not yet the work-period
simulation relation.

## Domain and conclusion

Consider the infinite lattice, or a periodic ring containing a positive integer
number of Q-cell colonies, with:

- canonical Address `i mod Q` and uniform Age;
- actual fixed-ROM metadata, coherently represented in the physical holders;
- coherent Data, head and controller replicas, with every controller field zero
  at each logical site without a head;
- at most one logical head in each computation core, at Addresses 0 through
  30723, and no heads outside those cores;
- arbitrary raw mail copies, Flag1/Flag2, Signals and Wf, without coherence or
  zero-value assumptions on those fields.

Every literal synchronous physical transition preserves this domain. Therefore
it persists for every finite number of physical ticks, starting in the domain.
This allows different colonies to have different Data, controller values, head
positions and head phases. Age remains synchronized as part of the premise.
It excludes damaged Address geometry and corrupted controller/Data replicas.

No new physical field, transition, ROM, parameter, neighborhood, projection step
or hierarchy-dependent dispatch is involved. The head and controller values are
the complete raw fields of the existing 154-word, radius-seven rule.

## Local routing and spatial composition

At an ordinary active tick a nonhalted left-moving head moves left unless it is
at the first cell, where it reflects. A right-moving head moves right unless it
is at the last cell or executes WAIT, in which case it stays. The three possible
destinations are disjoint. HALT, and IF_THIRD outside its third-stage window,
remove a matching right-moving FETCH head. During rest the head stays in place.
Reset and the first vote replace this behavior: only the first cell receives
the fresh head. These priority statements are checked against the *complete*
physical descriptor, with arbitrary old raw mail and flags.

The symbolic checker covers no head and each of the eight head phases, every
Address, every one of 2^32 Ages, arbitrary metadata and arbitrary stale
controller values at the head. It checks 365 head identities and 95,995
bit implications of the form `next_head=0 => next_controller_bit=0`.
The complete output-image proof supplies coherent next Data/head/controller
copies; canonical Address and Age preservation are checked in both paths.

The fixed ROM has exactly one first marker (Address 0) and one last marker
(Address 30723). All 61,448 directed source positions in the core have an
in-core successor. Waiting and halting also preserve confinement. There are
2044 intervening noncore cells before the next colony core, so the local
nine-primary halo cannot contain two legal heads.

The composition checker traces the descriptor's raw dependencies. Every
Data/head/controller/Wf output depends on old head/controller words only at
logical offsets -1, 0, 1 relative to its primary, or on none of them. Thus the
output-image cases at primaries -1, 0, 1 cover every primary affected by a head;
the no-head case supplies the exterior. It also verifies that all 49 static
metadata outputs are the exact unchanged center input wires. Canonical Address
preservation consequently preserves their actual-ROM interpretation.

These facts complete the induction for this structural domain: spacing permits
the local cases; routing preserves head count and confinement; the output-image
and zero-inactive-controller lemmas restore the procedure premises. Mail,
Signals and Wf remain unrestricted. No host correction or simulated transition
is inserted between ticks.

## Boolean abstraction and failed pilots

The new checker translates bitwise gates and Boolean selector masks into exact
BDDs. Other arithmetic bits and word predicates are independent opaque atoms.
Proving an identity for all assignments to those atoms is conservative: it does
not rely on an unproved correlation between a comparison and an operand.
Modular truncation, bit zero of constant addition, Boolean comparisons and the
two's-complement Boolean mask are handled explicitly. Budgets cap the checker
at 100,000 atoms and 200,000 BDD nodes; the largest successful case used 140,310
BDD nodes. These are proof objects, not physical workspace.

The first pilot could not relate normalized mask additions to their Boolean
selectors. The second passed the no-head case but could not prove an inactive
PC bit in FETCH because a De Morgan-normalized selector was still opaque.
Adding the corresponding sound mask/Boolean recognitions resolved these
abstraction limitations. No physical-rule change was made, and neither failure
was a concrete transition counterexample. Preserve the v1/v2 pilot logs and
`small_holder_head_invariant_failed_pilot_v{1,2}_source.py.txt`. The successful
pilot is v3; the full certificate is v1.

Tests compare the abstraction with concrete word-bit evaluation, including
Boolean masks, word predicates, arithmetic, shifts and truncation. Mutation
tests reject spontaneous heads, stale inactive PC, altered ROM endpoints,
metadata changes, distant logical head dependencies and omitted phase coverage.

## Independent checks and resources

| Check | Result | Seconds | Peak host RSS (KiB) |
|---|---|---:|---:|
| Full head certificate | 9 cases, 365 routing identities, 95,995 controller-bit implications | 6.986220 | 119,420 |
| Scalar/native audit | 917 cases, 8,253 complete 154-word outputs | 48.228473 | 60,008 |
| Spatial composition join | All source hashes, endpoints, dependency and static-wire obligations passed | 0.655216 | 62,272 |

The scalar/native audit covers 41 clock boundary/neighbor Ages, both directions
at actual first/last and HALT/IF_THIRD locations, arbitrary raw flags/mail, and
eight additional WAIT metadata cases. It checks 300,920 inactive controller
words and 55,020 coherent five-copy groups. It samples full semantics
independently of the BDD abstraction; it is not itself the unbounded induction.
Five head-checker tests passed in 0.954 s. Three composition mutation tests also
passed; exact unittest output is saved alongside the manifests.

The full proof's peak host RSS was about 117 MiB. No GPU execution, shared CUDA
rebuild, historical dataset change or shared-source edit occurred. The separate
8 GiB GPU scheduling request remains pending and unused.

Commands used `OPENBLAS_NUM_THREADS=1`, with stdout/stderr saved as matching
`.log` files. Use new output names when repeating an experiment.

```sh
python -m experiments.fixed_rule.certify_small_holder_head_invariant --output figs/fixed_rule/small_holder_head_invariant_v1.json
python -m experiments.fixed_rule.audit_small_holder_head_invariant --certificate figs/fixed_rule/small_holder_head_invariant_v1.json --output figs/fixed_rule/small_holder_head_invariant_audit_v1.json
python -m experiments.fixed_rule.join_small_holder_structural_invariant --head figs/fixed_rule/small_holder_head_invariant_v1.json --image figs/fixed_rule/small_holder_procedure_image_v1.json --output figs/fixed_rule/small_holder_structural_invariant_v1.json
python -m unittest discover -s tests/fixed_rule -p test_small_holder_head_invariant.py -v
python -m unittest discover -s tests/fixed_rule -p test_small_holder_structural_invariant.py -v
```

JSON hashes (prefix `figs/fixed_rule/small_holder_`):

| Suffix | SHA-256 |
|---|---|
| head_invariant_v1.json | `c5fd27e87fb806fe7c29138ccd5a6fa7dbf0712fc623d17eac8716943f78b1c4` |
| head_invariant_audit_v1.json | `98d34076242c01b8d7c0c52ae58ca8635191f1e73e1e1ed21d01ae4519e80af5` |
| structural_invariant_v1.json | `c922c3cbb78fe6f0bf77a2e2e929b94f890f606fa26d8d947be000f7f7705ee3` |

The descriptor and ROM hashes remain respectively
`af2de0673ac685bb83e8a319751b7f10e22c05037809ff0479bdf292a789fbb6` and
`c59c72abe15729e4848ce549b31f1faec63465f16da2c717f0eb233fb1e7cbe4`.

## What this does not establish

A confined unique head can still execute an incorrect computation or wait too
long. This structural invariant establishes no correct Data value, instruction
schedule, Signal capture relation, flag profile, macrostep timing or decoded
upper transition. Arbitrary admitted flags can erase mail and cause a
computation to fail while every structural property remains true.

The next obligation is to combine actual entry states, the instruction/packet
schedule and Data dependencies with the Signal-buffer and flag evolution across
successive work periods. A complete physical-to-simulated macrostep relation
still needs that semantic induction. Then demonstrate complete upper work
periods at depth two with measured practical GPU costs and cross-level repair.
Q/U optimization remains subject to correctness, without requiring U<=128Q.

The source rationale remains Gray's specialized ProgramBit-eliminated simulator
(pp. 31–32) and Gács's identical or suitably modified self-correcting rule
(§§9.2–9.3). This is a lemma about the current candidate, not a proof that its
Flag2/SimBit choices resolve the source ambiguities or satisfy all correction
and amplification machinery. Finite-cap Address-defect persistence and general
noise suppression remain open.
