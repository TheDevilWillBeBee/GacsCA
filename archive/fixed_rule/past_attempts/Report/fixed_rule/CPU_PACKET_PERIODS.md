# Retimed physical packets and successive work periods

2026-09-26. The retimed fixed-rule CPU reference now executes complete work
periods from Info-only initialization. The one-colony pilot completed two periods
without reinitialization in 47.700667 s, at 63164 KiB peak RSS. All 154 represented
raw words match independent scalar and descriptor references at both commits.
The initial represented controller is active; two of its raw controller words
change in the first simulated transition. A nonzero captured physical right
Signal is retained through the second period. The 15-colony run also passed both
periods in 696.240266 s, at 86012 KiB peak RSS; its independent audit passed.

This advances the [previous evaluation-phase result](CPU_EVENT_EVALUATION.md):
histories are now gathered by actual emitted packets, and reset, vote, capture,
forcing, clearing, commit and the next physical period are included. These are
successive **one-link** periods. Two lower work periods mean two upper ticks;
they do not constitute a complete upper work period at depth two.

## Fixed identity and source interpretation

The physical rule, descriptor, ROM and alphabet were not edited. Q=32768,
U=2147483648, radius seven, raw 154 words/4090 bits and projected 105 words/2704
bits remain as in [RETIMED_HOLDER.md](RETIMED_HOLDER.md). The descriptor digest is
`6e2f29f61bf281ec5d346cd58e717cf7e5b0afea263d2c17a18a58de295d8d23`;
the ROM digest is
`4dc026b976c541001421dd214df9c9e33f6f851053d4ba5f53dbbec925ba5645`.
Neither execution nor representation selects a rule by depth. The CPU colony
capacity bounds host resources, not the physical alphabet or permitted depth.

The source interpretation remains Gray pp. 31–32's hard-wired ProgramBit
projection and Gacs §§9.2–9.3's identical or suitably modified rule. The
represented rule is G=pi F iota; the actual evaluator describes its own raw
controller transition. The [retimed period argument](RETIMED_NOISELESS_MACROSTEP.md)
supplies the descriptor-semantics relation F^U(E(y)) subset E(G(y)). The new
execution result tests a restricted physical backend and does not expand that
theorem into a general backend-equivalence or noisy-amplification claim.
U<=128Q is not imposed. Compactness and practical depth-two execution remain
optimization objectives, subject to correctness.

## Actual packets and guarded acceleration

`retimed_holder_cpu_gather.py/.cpp` extends the frozen event reference with live
packets `(position, track, target, payload, remaining)`. Actual SEND payloads come
from complete native F evaluations. The backend counts colony-boundary crossings,
including repeated laps of a one-colony ring. It reconstructs all raw mail
replicas from live packets. Left/right delivery at the same site and time uses
the physical rule's right-track priority.

Packet delivery can be deferred within a call only because every target is a
guarded MEM history/Signal-buffer cell and controller data access there rejects.
Actual history targets exclude the local-neighbor history and the vote slot.
Same-track births are checked for overlapping space-time trajectories. The
backend stages all writes and rejects unsupported interactions or exhausted
budgets atomically. It does not replace the represented transition by a host
calculation. Actual packets retain their emitted data until delivery or drop.

The packet-flight BDD induction is replayed for all 15-bit source/target
coordinates, 19-bit elapsed values and hop counts 0..7; the leftward case is
coordinate reflection. The retimed and reference core receive functions are
source-identical. A separate compiled check extracts the actual CPU helpers and
checks both tracks, every source coordinate, all hops, seven target classes,
one-/15-colony rings, and six endpoint/time probes: 44040192 cases in total.
The replay and compiled audit took 2.895568 s at 59172 KiB peak RSS. Premature zero-distance hit
and early left-edge drop mutations both fail. This bridge does not prove every
C++ execution path; ordering, noninterference and local-factorization obligations
remain explicit and have their runtime guards and literal tests.

## Full boundaries and physical context

`retimed_holder_cpu_boundary.py/.cpp` first introduced literal synchronous full-F
steps at all physical sites for zero-context states. It rejected nonzero context
instead of discarding it. The retained failed first pilot executed all three
gathers and first evaluation, then rejected Signal capture: its computed upper
Flag1 was one. This was a real representation limitation, not a rule failure.

`retimed_holder_cpu_profile.py/.cpp` extends the representation to mixed right
Signals and zero left Signals. One bit per colony compresses the existing five
coherent right Signal fields; it is not an added physical register. Actual
capture is computed by literal full F and validated for coherence. Physical
Flag1 and Wf1 are reconstructed from the exact age-dependent forcing/clearing
profile. The new BDD check verifies this profile at all addresses and front
positions with three independent neighboring right Signal bits. Nonzero left
Signals, incoherent tail Signals and unsupported mail at boundaries reject.

Controller event calls use context erasure through the proved canonical
factorization. Thus event calls with erased context are not claimed to be
literal calls on each full nonzero physical neighborhood. Boundary calls use
actual full context. Reconstructed physical cells contain actual Signals, flags
and Wf; quiet advancement includes their profile evolution. Packets and new
emission during forcing/clearing reject. This makes the supported domain precise
and leaves arbitrary noisy raw states unsupported.

## Executed trajectory and independent audit

`run_retimed_holder_cpu_periods.py` starts with Info containing iota(y), zero
histories/scratch/controllers/mail/context and canonical Age zero. The fixture
has varied Data and an active represented READ_B controller. Every period runs:

1. Three reset/gather phases with actual transport and comparisons of all
   completed raw histories.
2. First vote and complete self-evaluation, including ten Signal SENDs.
3. Literal capture, precommit reset/HALT, forcing and clearing.
4. Final reset/vote, complete self-evaluation and literal commit/Age wrap.
5. Decode and full streaming validation of every physical cell against E.

The diagnostic upper step supplies expected outputs only. It does not write
the evolving physical world. The second period starts from the first period's
actual retained state, including scratch and right Signal. No host cleanup or
reinitialization occurs.

The pilot traverses 4294967296 physical ticks, with 345250 colony event ticks,
1415628 complete raw F calls (including boundary sites), and 12956 emitted and
delivered packets. Every boundary relation validates all 32768 physical sites.
Both stored right Signal bits are one. The second upper transition changes Age
but no controller word; active-controller change is exercised in the first.

`audit_retimed_holder_cpu_periods.py` reads saved snapshots, checks source and
snapshot hashes, evaluates scalar F and its word descriptor independently for
each upper step, and compares all 154 normalized raw Info words. It also checks
non-MEM physical Data, retained right Signal bits and final raw controller/mail
emptiness. The pilot audit passed in 0.648992 s, 58244 KiB peak RSS. It is a saved
state audit, not a second independent physical execution.

## Nonaliasing 15-colony result

All 15 distinct positions of the represented radius-seven neighborhood are
present. Both periods passed full E validation at all 491520 physical sites.
Execution covered 4294967296 physical ticks, 5180388 colony event ticks,
21239796 complete raw F calls and 194340 emitted/delivered packets. No packet
was dropped or left live. Total wall time including validation/snapshot work was
696.240266 s; peak RSS was 86012 KiB (84.0 MiB), under the 512 MiB limit.

The independent audit passed in 0.885250 s, 66064 KiB peak RSS. It compared 2310
complete raw Info words per commit to both scalar F and descriptor evaluation.
Seventy represented controller words changed in the first upper tick and 65 in
the second, demonstrating active controller dynamics across successive periods.
The physical retained right Signal bits were one in colonies 12–14 after the
first period and 9–14 after the second, with all other right bits zero. This
exercises mixed adjacent Signal profiles rather than only uniform forcing.
There was no between-period reset by the host.

All runs are terminal. The evidence index
`figs/fixed_rule/retimed_holder_cpu_packet_periods_evidence_v1.json` binds six
new passing manifests, two snapshots, four passing test logs (18 tests), failed
attempt artifacts, and the reused local-transfer/period proofs. Source hashes
were verified before writing the index; successful implementation sources remain
frozen.

## Commands and checks

All CPU commands used `ulimit -v 524288` and `OPENBLAS_NUM_THREADS=1`. Builds are
private under `figs/fixed_rule/build/`. No CUDA artifact or shared GPU job was
changed. The pending separate 8 GiB GPU reservation was not used.

```
python -m unittest discover -s tests/fixed_rule -p test_retimed_holder_cpu_gather.py -v
python -m unittest discover -s tests/fixed_rule -p test_retimed_holder_cpu_boundary.py -v
python -m unittest discover -s tests/fixed_rule -p test_retimed_holder_cpu_profile.py -v
python -m unittest discover -s tests/fixed_rule -p test_retimed_holder_cpu_period_audit.py -v
python -m experiments.fixed_rule.prove_retimed_holder_mixed_profile --output figs/fixed_rule/retimed_holder_mixed_profile_v1.json
python -m experiments.fixed_rule.certify_retimed_holder_cpu_transport --output figs/fixed_rule/retimed_holder_cpu_transport_v1.json
python -m experiments.fixed_rule.run_retimed_holder_cpu_periods --colonies 1 --periods 2 --output figs/fixed_rule/retimed_holder_cpu_periods_pilot_v2.json
python -m experiments.fixed_rule.audit_retimed_holder_cpu_periods --execution figs/fixed_rule/retimed_holder_cpu_periods_pilot_v2.json --output figs/fixed_rule/retimed_holder_cpu_periods_pilot_audit_v1.json
python -m experiments.fixed_rule.run_retimed_holder_cpu_periods --colonies 15 --periods 2 --output figs/fixed_rule/retimed_holder_cpu_periods_15_v1.json
python -m experiments.fixed_rule.audit_retimed_holder_cpu_periods --execution figs/fixed_rule/retimed_holder_cpu_periods_15_v1.json --output figs/fixed_rule/retimed_holder_cpu_periods_15_audit_v1.json
```

Seven packet tests passed in 3.123 s; three boundary tests in 2.433 s; four
profile tests in 1.933 s; four audit tests in 0.639 s. These cover full raw cones,
all hop counts, repeated laps, simultaneous priority, real SEND payloads,
segmented live mail, atomic domain rejection, actual capture, mixed flag fronts,
active controllers under nonzero flags, and detection of omitted raw controller
or metadata words. The mixed-profile BDD proof passed in 1.374982 s.

The initial compile failed only on a misleading-indentation warning under
`-Werror`; source/logs were retained before the formatting correction. The failed
zero-context capture pilot and exact driver source are also preserved:
`retimed_holder_cpu_gather_failed_build_v1.cpp.txt`,
`retimed_holder_cpu_periods_pilot_v1.log` and
`retimed_holder_cpu_periods_failed_capture_v1.py.txt` in `figs/fixed_rule/`.
The successful pilot uses the same represented fixture, with the extended
physical context representation. Successful execution sources are frozen.

## Remaining scope

Practical complete depth two, retimed GPU equivalence, general physical noise,
cross-level repair/amplification and robust finite-cap behavior remain open.
Candidate-B Flag2, voted-old-Signal D10, printed Flag2 persistence, SimBit timing
ambiguity and malformed Info repair retain their prior caveats. Future backend
work must support more raw context without silently changing the state relation.
The next implementation step is measured retimed GPU adaptation against these
saved CPU states when scheduling is available. Generalizing raw context and
noise support requires further explicit state representation and local tests.
