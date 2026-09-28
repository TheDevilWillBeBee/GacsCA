# Conditional complete-state two-tick repair theorem

2026-09-27. Exact Boolean and structural certificates now establish a repair
lemma for the unchanged fixed G rule. It covers arbitrary mutable physical-state
replacements, including active controllers and transport fields, under explicit
geometry/coherence hypotheses. The local proof also permits spatially distributed
faults. It does not establish general Gacs amplification or a stochastic threshold;
the full project goal remains active.

## Statement

Let x be a configuration of G=pi F iota on the infinite line, or a periodic ring
whose size is divisible by Q=32768. Assume:

1. Address is canonical, and all sites have the same legal Age in [0,U), with
   U=2147483648.
2. Healthy Flag1, Flag2 and all Wf copies are zero.
3. The five physical procedure copies are coherent: for every logical site,
   all copies of each Data/head/controller/mail field carry the same typed word.
   These logical words are otherwise arbitrary; **no one-head, inactive-controller,
   valid-PC, quiet-workspace or initialization-only premise is imposed**.
4. Signals are coherent fivefold bit copies. Equivalently, some Boolean sequence
   s gives physical Signal_i = sum over d=-2..2 of s_(i+d) times 2^(d+2).

Let D be any set of sites such that **every interval of eleven consecutive sites
contains at most two sites of D**. Replace the entire G state at each site of D
arbitrarily, producing y. With no further faults during the next two ticks:

**G²(y) = G²(x), as complete physical configurations.**

There is no bound on the total number of sites in D. At most two arbitrary sites
anywhere is an immediate special case. The physical alphabet is the existing
105-word projected G state; its 49 hard-wired metadata words are regenerated from
Address, not independently faulty hardware. Complete raw reconstruction includes
all 154 F words. Faults in encoded metadata stored as lower-layer Data remain
ordinary mutable physical Data faults; this statement does not silently omit them.

## Proof and machine-checked premises

**Geometry, one tick.** Prune the complete descriptor to its four geometry
outputs. The checker verifies that their entire syntactic support is radius five
and uses only Address, Age, Flag1/Flag2 and primary Wf. Every other raw field is
therefore unrestricted. For all 55 pairs of distinct positions in that support,
an exact reduced ordered BDD evaluates the actual descriptor with:

- every healthy Address and all U legal healthy clocks;
- both faulty Addresses across all 32768 values;
- both faulty Ages across the full 32-bit physical field, including illegal
  colony-clock values;
- both faulty primary flags/Wf independently arbitrary.

Each case has 148 independent Boolean inputs. Every output is exactly canonical
Address, the healthy Age plus one modulo U, and zero Flag1/Flag2. Zero/one defects
are included by assigning an unused defective record its healthy value. Local
faults outside the checked support cannot affect these outputs. The largest BDD
has 34309 nodes. The full 55-case check passes in **6.574527 s**, peak **57976 KiB**.
This proof makes no sampled-Age or sampled-Address approximation.

**Protected input words.** Three equal copies outvote any two arbitrary copies.
The existing exhaustive Boolean/bit-local majority certificate is replayed.
The new checker locates exact expression subgraphs in the full descriptor:
20 geometry groups, 119 used procedure-majority groups and ten used Signal-vote
groups. These are matched by expression structure, not by names or an opcode list.
Each procedure/Signal vote spans five sites, so the eleven-site sparsity hypothesis
ensures its corrected value equals the healthy value.

**First-step outputs.** Substitute the certified repaired geometry and corrected
procedure/Signal words at those checked graph cuts. All 15 mutable nonprocedure
outputs are independent of the old damaged center and agree with the healthy
outputs. These include geometry, Signal and all ten Wf fields. Remaining procedure
outputs depend only on corrected logical words and the center's old Address/Age/
metadata; thus they agree at every originally uncorrupted holder. G projection
restores metadata everywhere from the already equal Address. After one tick,
discrepancies can remain only in procedure fields at sites of D.

The same symbolic graph evaluation compares all five output copies for each of
the 18 logical procedure fields. They are identical for arbitrary typed logical
inputs, including arbitrary head/controller/mail values. Metadata is spatially
consistent as required by the fixed ROM, but is otherwise allowed to be symbolic.
No routing/head-count assumption is inserted. Healthy first-step procedures are
therefore coherent.

**Second tick.** Every five-copy vote now has at most two wrong holders, all
confined to D, and at least three equal healthy words. Nonprocedure inputs already
agree everywhere. The replayed complete-descriptor procedure cut proves that
**every F output** agrees once these corrected words and nonprocedure inputs
agree. Projection gives identical G outputs too. This proves complete recovery.
First-step healthy Signals need not remain coherent for this argument: they
already agree between the two trajectories, so no second correction premise on
them is needed.

The structural check compares all outputs with 37559 symbolic terms and passes
in **1.854099 s**, peak **62752 KiB**. The sparse corollary uses only local premises:
each radius-five geometry neighborhood sees at most two defects, and each
five-copy voting neighborhood is contained in an eleven-site interval. It does
not replace local hypotheses with a global fault-count bound.

These are inspectable Python BDD, DAG-support, algebraic-term and composition
certificates. They are not a proof-assistant derivation or an independent proof
of the entire source-to-descriptor compiler. The unchanged rule/descriptor,
proof-tool source hashes, and prior scalar/native trajectory audits remain part
of the trusted/evidential chain.

## Distinguishing tests

Seven certificate tests pass in **2.602 s**. They exercise another quantified
geometry pair and reject deliberately modified descriptors that retain a bad
Flag1, add an unreviewed controller input to geometry, bypass the rb/Signal votes,
or route one head backup inconsistently. Invalid defect-position domains reject.

Four further tests pass in **1.388 s**. The cyclic local-sparsity predicate agrees
with brute force for all 8192 subsets of a 13-site ring. Six physical experiments
place **16 arbitrary complete-state replacements** in eight separated pairs and
run the full local rule at clock contexts 0, 1, capture-minus-one,
forcing-start-minus-one, forcing-end-minus-one and U-1. All rejoin within two ticks.
A three-copy Data corruption violating the local condition survives, so the
negative control distinguishes the theorem's spatial hypothesis.

The first structural-check attempt expected eleven Signal-vote groups. Descriptor
pruning removes the unused vote at logical offset -5; actual used votes are -4..5.
The check correctly rejected that inaccurate inventory. Exact v1 source/log are
preserved. Accepted v2 checks the actual ten groups and separately rejects every
uncut raw dependency; it does not weaken the complete-output claim.

## Scope within the construction

This supplies a base repair lemma for the actual fixed self-simulator, rather
than only a favorable finite pulse demonstration. It applies to the canonical
complete lower checkpoints used in the executed hierarchical experiments when
the stated flag/Wf and coherence hypotheses hold. Q/U, physical alphabet,
neighborhood, evaluator, ROM and transition implementation are unchanged.

The nonzero-front cases in [PHYSICAL_FAULT_SWEEPS.md](PHYSICAL_FAULT_SWEEPS.md)
explain why the zero-flags/Wf hypothesis cannot be discarded: four measured
forcing disturbances need more than two ticks. General recovery through such
contexts, continuing space-time faults, amplification across colonies, robust
finite-depth caps and depth three remain open. The homogeneous-cap Address
persistence counterexample is not covered by these canonical/zero-flag hypotheses
and remains unresolved. Printed Flag2/computed-SimBit ambiguities remain explicit.

Gray pp. 31–32 specialized hard-wiring and Gacs 9.2–9.3's suitably modified
self-correcting simulation remain the construction basis. This lemma alone is
not the papers' full correction or amplification theorem. It introduces no
U<=128Q requirement.

## Reproduction and handoff

All commands run from the repository root with `OPENBLAS_NUM_THREADS=1`:

```sh
python -m experiments.fixed_rule.bounded_cuda_probe --output figs/fixed_rule/retimed_holder_two_site_geometry_v1_watch.json --seconds 45 --rss-mib 512 -- python -m experiments.fixed_rule.prove_retimed_holder_two_site_geometry --output figs/fixed_rule/retimed_holder_two_site_geometry_v1.json
python -m experiments.fixed_rule.bounded_cuda_probe --output figs/fixed_rule/retimed_holder_two_tick_repair_v2_watch.json --seconds 45 --rss-mib 512 -- python -m experiments.fixed_rule.certify_retimed_holder_two_tick_repair --output figs/fixed_rule/retimed_holder_two_tick_repair_v2.json
python -m experiments.fixed_rule.bounded_cuda_probe --output figs/fixed_rule/retimed_holder_two_tick_certificate_tests_v1_watch.json --seconds 45 --rss-mib 512 -- python -m unittest tests.fixed_rule.test_retimed_holder_two_tick_certificate -v
python -m experiments.fixed_rule.bounded_cuda_probe --output figs/fixed_rule/retimed_holder_sparse_pulse_tests_v1_watch.json --seconds 30 --rss-mib 512 -- python -m unittest tests.fixed_rule.test_retimed_holder_sparse_pulse -v
python -m experiments.fixed_rule.compose_retimed_holder_sparse_repair --output figs/fixed_rule/retimed_holder_sparse_repair_theorem_v1.json
```

All accepted commands exit 0. Outputs refuse overwriting. Evidence index:
`figs/fixed_rule/retimed_holder_two_tick_repair_evidence_v1.json`. Only owned new
files and STATUS changed; no GPU job, shared source, physical rule or historical
data changed. No GPU allocation/build was needed.

Next use the lemma to classify recoverable spatial pulses in a reproducible
space-time noise experiment, while evolving unsupported clusters/forcing defects
literally and preserving failures. A longer-term proof still needs to connect
those exceptional clusters to simulated-layer correction and amplification.
