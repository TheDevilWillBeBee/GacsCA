# Homogeneous terminal cap: permanent Address defect

2026-09-26. The ordinary cap is valid noiseless termination data, but **one
Address-bit fault in that cap never repairs**. This is now an exact invariant of
the full fixed descriptor, for every faulty Address and every clock phase. An
actual encoded experiment also distinguishes two-copy physical correction from
a three-copy fault that reaches the cap and persists through successive commits.
No physical rule, program, alphabet, boundary kernel or shared source was changed.

## What is proved

Consider an infinite line, or a periodic ring with at least 11 sites. Initially:

- Address is Q-1 everywhere except one site, whose Address is any A in [0,Q).
- Age is uniform and arbitrary; F1=F2=1 everywhere.
- All other raw fields may be arbitrary, including controller, Data, Signal,
  hard-wired metadata before projection, and both primary workspace flags.

One application of the existing rule preserves the entire Address map and both
flags and increments every Age modulo U. Thus the same hypotheses hold again,
regardless of how the other fields evolve. Induction makes the Address defect
permanent. The projected rule has the same geometry property because projection
and metadata regeneration do not change those outputs. In particular, changing
Q-1=32767 to Q-2=32766 is a single mutable Address-bit fault in the existing
ordinary cap, including its prescribed backup head/PC pulses.

The reason is the Address-adjustment vote. For a homogeneous Address background,
the five adjusted Addresses on each side are distinct. Replacing at most one of
them creates at most a pair, never the required triple. Both votes therefore use
the center's own Address as default. The absent right Address vote sets Flag1;
the surrounding Flag2 ones prevent erasure. Uniform Age is preserved. This is a
failure of the cap's geometry to provide a repair reference, not missing Data
redundancy and not a stale-program-bit decoding issue.

`prove_small_holder_cap_defect.py` takes the full 154-output descriptor and
checks its arity/DAG contract before selecting the four geometry outputs. It
then verifies their exact syntactic support: radius five, Address, Age, F1/F2,
and primary Wf only. Every omitted raw field is therefore unrestricted, not
silently assumed zero. A reduced ordered BDD check handles each of the 11
possible local defect positions and the unaffected neighborhood. Each case
quantifies 69 independent bits: 32 clock, 15 faulty Address and 22 primary Wf.
All output bits agree with the invariant. Maximum BDD size is 2698 nodes;
the full proof took 0.503721 s with 36936 KiB host RSS.

This proves geometry persistence, **not** that every damaged raw field follows
the healthy cap orbit. Controller pulses and other dynamics may differ. The
previous full-controller noiseless cap proof remains valid within its domain.

## Executed encoded counterexample and repairing control

Fifteen ordinary cap states at upper Age zero initialize fifteen canonical lower
colonies (491520 physical sites). The raw upper Address is stored at lower
logical site 238922 in colony seven. No upper transition or diagnostic result is
installed into the evolving physical world.

The repairing control flips bit zero in two actual lower holders of that Info
word: positions 238921/s3_data and 238923/s1_data. One literal physical transition
restores both copies. After a complete lower period all 154 decoded raw fields
match the healthy upper cap transition, including Address=32767.

The failure case adds the primary holder, position 238922/s2_data: three physical
one-bit changes total. Local fivefold majority spreads the wrong word to the
other holders. The exact Data rebase retains that wrong state; it does not repair
or replace it. The encoded Address becomes 32766. Initially its Info metadata is
still for Address 32767, and the strict decoder correctly rejects it. The actual
fixed ROM's input regeneration resolves this inconsistency during execution.
It then computes the ordinary upper rule on the wrong Address and regenerates
its output metadata normally.

| Case | After one lower tick | Decoded commit at U | Decoded commit at 2U |
|---|---|---|---|
| Two physical Info-copy bit faults | Correct word restored | Address 32767, every raw field correct | Not run |
| Three physical Info-copy bit faults | Wrong word coherently retained | Address 32766, every raw field matches G | Address 32766, every raw field matches G |

The three-copy world runs continuously through both periods. Its cap defect is
not reinjected. The controller and encoding/decoding relation successfully
simulate this unfavorable upper behavior. The descriptor theorem establishes
persistence for subsequent upper transitions; further physical macrosteps have
not been executed, so infinite lower execution is not claimed.

Total GPU advance across the one-period control and two-period failure case:
55.569326 s; total run 58.649576 s; host peak 180440 KiB; sampled GPU process
442–444 MiB. Extra exception buffers are 18579456 bytes. The general-Signal
backend is required because both computed cap flag Signals are one. The newer
restricted scalar event compiler was not silently substituted.

## Commands and independent audit

```sh
OPENBLAS_NUM_THREADS=1 python -m experiments.fixed_rule.prove_small_holder_cap_defect --output figs/fixed_rule/small_holder_cap_defect_proof_v1.json
OPENBLAS_NUM_THREADS=1 python -m unittest discover -s tests/fixed_rule -p test_small_holder_cap_defect.py -v
# Four tests, 1.155 s, OK.
OPENBLAS_NUM_THREADS=1 python -m experiments.fixed_rule.small_holder_encoded_cap_defect --output figs/fixed_rule/small_holder_encoded_cap_defect_v2
OPENBLAS_NUM_THREADS=1 python -m experiments.fixed_rule.audit_small_holder_encoded_cap_defect --input figs/fixed_rule/small_holder_encoded_cap_defect_v2 --proof figs/fixed_rule/small_holder_cap_defect_proof_v1.json --output figs/fixed_rule/small_holder_encoded_cap_defect_audit_v1.json
# Audit passed, 1.519051 s, 62396 KiB host RSS.
```

The v1 execution attempt had a syntax error before any world was allocated. Its
log is preserved; the corrected experiment uses a fresh v2 artifact name.

Tests include all proof cases, incomplete-output and frozen-clock mutations,
and a constant-Address mutation that passes an undamaged cap geometry check but
invalidates the defect theorem. They also compare independent scalar/native
full transitions with arbitrary other fields and evolve the one-bit fault across
reset/vote/wrap controller phases. The audit re-proves the all-clock invariant,
checks exactly five physical changed bits across the two separate cases, and
compares 30 complete physical local outputs and 45 complete decoded upper
outputs against scalar, native and full-descriptor calculations. It verifies
that stale initial metadata was not hidden. Saved outputs and source/artifact
hashes are independently checked; the full lower trajectory is not replayed by
the audit. Host physical/upper transition calls are forbidden during the hashed
driver's physical advancement.

## Consequences and alternatives

This finding does not invalidate noiseless finite-depth termination through
ordinary initial data. Recursive encoding can still terminate at this cap;
there is no special top kernel. It also does not invalidate correction of one
or two physical procedure-copy faults or the previously demonstrated active
upper WRITE repair. It rules out a stronger proposed use of this particular cap:
a boundary that erases all isolated finite perturbations, even single Address
bits. Merely waiting longer, enlarging U, or repeating temporal votes cannot
repair this invariant geometry defect.

Three alternatives must be kept distinct:

1. Use the current ordinary cap as a noiseless terminal specification and measure
   finite-horizon failure at the highest represented layer explicitly. This is
   consistent with the fixed-rule requirement but provides no cap repair theorem.
2. Design organized terminal data with an Address gradient that supplies the
   missing agreement. Canonical colony geometry can repair isolated Addresses,
   as earlier geometry-closure experiments show. A complete terminal orbit,
   controller dynamics, and boundary interaction still need construction/proof;
   simply renaming a normal active colony a cap is insufficient.
3. Change the local rule to recognize and repair a terminal family. Any such
   change must be fixed independently of depth and included in the complete
   self-description, program regeneration, timing and noise analysis. A top-only
   callback or externally forced Address restoration would violate the goal.

None of these alternatives is silently installed by this experiment. The next
boundary-design work should choose and test an explicit admissible terminal
family; the next execution work must still resolve full nested-period cost.

The distinction between noiseless termination, finite-horizon reliability and
indefinite immunity matters in the source too. In the supplied Gacs text,
Definition 2.2 specifies periodic finite spaces (lines 631–635), and the start
of section 3 discusses eventual forgetting versus increasing finite-space
relaxation times (lines 990–995). Sections 9.2–9.3 permit suitably modified
self-correcting self-simulation; they do not supply a repair theorem for this
implementation's homogeneous cap. These source statements should not be read
as requiring an eternally immune finite cap or as excusing an unmeasured failure.
See [the local source](../../papers_txt/gacs_2001.txt) and
[the existing closure audit](SMALL_HOLDER_CLOSURE.md).

## Provenance, ownership and remaining goal

`figs/fixed_rule/small_holder_cap_defect_proof_v1.json` SHA256: `166ecb71f4eb6e6246b71cb55807b99b849d5a677488ae6bdafae5926b86e4b2`.

`figs/fixed_rule/small_holder_encoded_cap_defect_v2.json` SHA256: `186230d517902eab4f7e5222c9ec5344d56bba574e6546779ef8b5efea0bb45b`.

`figs/fixed_rule/small_holder_encoded_cap_defect_v2.npz` SHA256: `177c886891e4cef61532ff92f4c10448788adb3b56c8729097d95b09d14f12ce`.

`figs/fixed_rule/small_holder_encoded_cap_defect_audit_v1.json` SHA256: `c977d1971d5b2668ae281a5e49e0779bf51343d1ef47aa9ab0c9a31c25004153`.

The physical descriptor remains
`af2de0673ac685bb83e8a319751b7f10e22c05037809ff0479bdf292a789fbb6`.
No construction or existing CUDA source was modified. Owned additions are the
proof, test, encoded experiment, independent audit, this report and namespaced
evidence. STATUS.md carries this handoff. All jobs are terminal. The separate
8 GiB allocation request remains unanswered; no large job was launched.
MAIN_AGENT_NOTES.md remains absent. The historical third-link job was not
observed, which is not evidence of successful completion.

The full goal remains active. Full nested upper periods, a suitable boundary
reliability relation, and measured general cross-level noise suppression remain
unfinished. This turn provides a verified construction limit and a distinguishing
physical experiment, not a claim that the final objective has been met.
