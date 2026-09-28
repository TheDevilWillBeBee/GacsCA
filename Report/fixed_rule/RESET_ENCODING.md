# Complete reset encoding and physical period handoff

2026-09-26. A clean physical period boundary now has an explicit full-state
encoding, including every controller field and retained Signal. The final local
reset identity is proved for all 154 raw outputs. Two actual reset-to-reset GPU
periods match the encoding at every physical coherent row. This is a prerequisite
for a justified nested execution shortcut, not yet such a shortcut or a complete
all-input macrostep theorem.

## Encoding and the missing-state trap

For a finite projected parent ring x, write C(x; L,R) for this ordinary physical
initial configuration:

- Canonical physical Address, common physical Age 1, and zero flags/Wf/mail.
- Info contains all 154 raw words of the lifted parent, including its complete
  evaluator/controller state and all metadata. Other physical Data is zero.
- Each colony has its actual reset head at Address zero, FETCH phase, PC equal
  to the fixed first entry; all other controller fields are zero.
- The five left Signal holders contain L times [16,8,4,2,1], and the five right
  holders contain R times that same sequence. These are actual stored Signals.

All procedure/Wf fields have the existing fivefold coherent physical lift.
No extra physical field, level tag, register pair or transition is introduced.
C(x) denotes the special case L=x.f2 and R=x.f1, per colony. Initial L,R can be
other bits. The initializer/diagnostic module is `small_holder_reset_encoding.py`;
its complete verifier reads bounded chunks and never writes an evolving world.
The represented alphabet remains 105 words/2704 bits, with 154-word raw lift.

A decoded Info tuple alone is insufficient to specify a clean physical boundary.
The physical head and old Signals must also be represented. In particular,
resetting Signals to zero during a purported macrostep acceleration would change
the physical state. Tests deliberately omit a head or Signals and require the
complete verifier to fail.

The desired future clean relation is

    G^U C(x; L,R) = C(G x),

where G on the left is the same physical local rule over the encoded ring and
G on the right is its projected action on the parent ring. This turn verifies
that relation for two successive active fixture steps and proves its final reset
component. It does not establish the displayed identity for every x,L,R.

## Exact local reset theorem

At old Age zero, assume canonical geometry, coherent Data, zero flags/Wf,
zero heads/controllers/mail, and a stationary five-holder Signal pattern.
The seven center static records are arbitrary. For each logical procedure copy,
let first, kind and a be its local static fields. One full raw local transition:

- Preserves Address, Signals and all static records, and sets Age to one.
- Clears Data exactly when first is true or kind is MEM with bit zero of a set;
  otherwise retains that logical Data word.
- Sets head=first and PC=first times the low 32 bits of a.
- Leaves every other controller, mail and Wf field zero.

The BDD certificate evaluates the unchanged complete descriptor against this
identity. It quantifies **1983 independent bits**: all physical Addresses, six
neighboring colony Signal bits, nine independent coherent 64-bit Data words,
and every static field of all seven center records. All 154 output words are
checked. Maximum BDD size is 128995 nodes; proof time 1.158850 s; host peak
115820 KiB. The independent audit also checks that exterior static inputs and
Data outside the quantified logical support cannot enter these outputs.

The audit enumerates every one of the 32768 actual ROM/fallback Addresses.
Exactly the 154 Info locations survive reset among MEM Data. Only Address zero
has first set, with the correct fixed entry. Non-MEM Data must already be zero;
this is an explicit pre-reset trajectory check, not an assumed erasure effect.
Scratch MEM Data may be arbitrary before reset. Thus the local theorem applies
to the checked boundary and yields the complete C(x) state afterward.

An earlier narrower metadata proof is retained as
`small_holder_reset_encoding_proof_v1.json` with its exact source archived in
`small_holder_reset_encoding_restricted_metadata_v1.py.txt`. The final v2 proof
quantifies every static word. The v1 live-source hash refers to that archived
source version; it is not presented as provenance for the strengthened proof.

## Executed active handoff

The 15-colony fixture starts directly in C(x; L,R), with alternating old Signal
bits deliberately different from x's flags. Its upper state has an active WRITE,
all upper F2 set, and an Address fault 30000 at the center. Initialization happens
once. There is no re-encoding, Signal clearing or healthy-state installation
between periods. Host transition/evaluator functions are forbidden during
physical advancement.

Starting at physical Age one, each cycle advances U-1 ticks to commit at Age zero,
checks every boundary hypothesis, and takes the actual next physical reset tick.
Every one of the 491520 coherent rows is checked at initialization, both commits
and both resets. At commit only scratch MEM Data is unconstrained; all Info,
controllers, Signals, geometry, flags, mail and non-MEM Data are checked. After
reset no field is ignored. The complete physical raw state follows from the
existing coherent five-holder representation; no physical-exception claim is
made outside that representation.

| Completed cycle | Center upper Address | Center upper Data |
|---|---:|---:|
| First | 107 | 0 |
| Second | 107 | 0x123456789ABCDEF0 |

All decoded raw fields match the intended G at both commits. Actual GPU advance
for 2U=8589934592 ticks took 40.158518 s. Complete-row verification took 33.928519 s;
whole run 75.883395 s; host peak 174996 KiB; GPU process 424 MiB. Verification
retains chunks of at most 256 coherent rows. The general-Signal backend is used
unchanged because both flag Signals are supported; this is not a timing comparison
against the newer restricted event compiler.

## Tests, audit and exact commands

```sh
OPENBLAS_NUM_THREADS=1 python -m experiments.fixed_rule.prove_small_holder_reset_encoding --output figs/fixed_rule/small_holder_reset_encoding_proof_v2.json
OPENBLAS_NUM_THREADS=1 python -m unittest discover -s tests/fixed_rule -p test_small_holder_reset_encoding.py -v
# Four tests, 1.744 s, OK.
OPENBLAS_NUM_THREADS=1 python -m experiments.fixed_rule.small_holder_reset_handoff --output figs/fixed_rule/small_holder_reset_handoff_v1
OPENBLAS_NUM_THREADS=1 python -m experiments.fixed_rule.audit_small_holder_reset_handoff --input figs/fixed_rule/small_holder_reset_handoff_v1 --proof figs/fixed_rule/small_holder_reset_encoding_proof_v2.json --output figs/fixed_rule/small_holder_reset_handoff_audit_v1.json
# Audit passed, 2.184582 s, 115872 KiB host RSS.
```

Tests retain all parent raw fields, exercise ROM/tail/colony boundaries with
nonzero scratch Data against full native transitions, and reject omitted
controller/Signal state. The independent audit re-proves the local theorem,
checks all ROM/fallback reset markers, compares 30 complete decoded outputs using
scalar/native/descriptor evaluation, checks 210 saved full-raw reset probes, and
rebuilds all three complete clean-state hashes with a separate dense-per-colony
construction. At most about 6.25 MiB is needed for that construction's row array.
The audit verifies saved outputs/provenance; it does not independently replay
the entire lower trajectory. The pre-reset whole-state checks are runtime
assertions in the hashed driver.

## What is still required before nested compression

Gray's specialized ProgramBit projection and Gacs's modified self-simulation
remain the source justification described in [SMALL_HOLDER_CLOSURE.md](SMALL_HOLDER_CLOSURE.md).
They do not authorize replacing physical execution with a decoded callback.
This encoding is currently used only for initial data and read-only diagnostics.

A certified macrostep shortcut still needs a full admissible-input argument for
retrieval, temporal votes, fixed-ROM evaluation including its own controller,
metadata regeneration, Signal delivery/capture, and timing/halt/clearing before
the proved reset. The exact endpoint relation must include all of those fields.
It must also address how intermediate physical times are reconstructed and what
happens when faults invalidate the clean relation. Applying the upper rule and
then installing C of its output is not justified by the current finite tests.

Next concrete proof work is the fixed-ROM instruction/communication trace and
its timing for arbitrary encoded words, to close the whole-period relation.
Only after that may composition of encoded trajectories support a nested
acceleration claim. Full nested upper periods, fault-aware composition, cap
reliability and general cross-level error suppression remain open. Q and U are
unchanged; no U/Q=128 constraint has been reintroduced.

## Provenance and ownership

`figs/fixed_rule/small_holder_reset_encoding_proof_v2.json` SHA256: `b4b66944fd6e926e9cdf5532f0970ba5b40d24577b0ff22f4a8fd0f26d2b9ee4`.

`figs/fixed_rule/small_holder_reset_handoff_v1.json` SHA256: `65fcd6ff604e8b69079f5ce6ad0ef08dad6e434badc980ed21e4607dd8d57f9a`.

`figs/fixed_rule/small_holder_reset_handoff_v1.npz` SHA256: `ea03d30c9cf07c28d34f9c03ddc0e77281188528888d5c35c90ddc4c0186eab4`.

`figs/fixed_rule/small_holder_reset_handoff_audit_v1.json` SHA256: `c106b1ae6961419adcfd8453ec64764c1632050d4b48004397487a5e29e3ffb9`.

Physical descriptor remains
`af2de0673ac685bb83e8a319751b7f10e22c05037809ff0479bdf292a789fbb6`.
Owned additions: reset encoding, proof, test, handoff driver/audit, this report,
and namespaced evidence. No frozen/shared module or CUDA artifact was modified.
All own handles are terminal. MAIN_AGENT_NOTES.md remains absent and the separate
8 GiB allocation reservation is pending; no large GPU job was launched. Full goal
active, not complete.
