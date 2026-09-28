# Packed self-ROM: Q=8192 and U=2^28

2026-09-28. The `packed28_holder_*` candidate is one fixed radius-seven,
finite-state physical rule. Depth changes only the initialized configuration;
the physical schema (154 raw words, 4090 meaningful bits), 15-site local
neighborhood, transition code, packed instruction decoder, and hard-wired
complete self-description stay the same. The fixed ROM occupies 7597 sites
inside each 8192-site colony. A continuous physical run on 15 distinct
encoded upper cells completed two lower work periods and decoded two
successive upper transitions of this candidate's own projected rule.

This is an executable self-simulation milestone on the canonical coherent
domain. It is not a full U-transition upper work period, a noisy repair
experiment, or a proof for all admissible initial configurations.

## Source basis and optimization

Gray, pp. 31–32 of `papers_txt/gray_readers_guide.txt`, explains hard-wiring
the rule program and projecting away `ProgramBit` when its value is determined
by Address; the specialized projected model can self-simulate without being a
general-purpose universal machine. Gács, §§9.2–9.3 of
`papers_txt/gacs_2001.txt`, explicitly allows the simulated self-correcting
rule to be identical or similar and gives `My-rules` as the self-simulation
source. The older `Report/design_selfsim.md` uniformity claims were treated as
proposals. The present packed decoder and its transitions are part of
`My-rules`: adding `PACK3` changed the complete physical F and its compiled
ROM. The reference Q=16384 implementation and its limitations are in
`GATHER29_FULL_PERIOD.md`.

The prior fixed-rule compiler emitted 10249 physical instruction cells after
sharing three gathers. Most of its ALU operations used MEM addresses below
4096. The new fixed kind-10 `PACK3` row stores two or three contiguous virtual
ALU instructions in the existing immutable `a:64`, `b:64`, and `d:32`
fields. Its `index:32` stores the first virtual PC. At each fetch, the moving
head computes `(pc-index) mod 2^32`, extracts that slot, and executes the
ordinary ALU transition; the moving controller PC remains virtual. Remaining
instructions retain their old form. The three-slot decoder is in both the
scalar physical rule and its complete Boolean word description. The ROM
compiler and checker decode actual physical rows and confirm they reconstruct
all 10606 virtual instructions, including the code that evaluates the
packed decoder itself. No extra physical register, alphabet field, local
radius, depth dispatch, or general-purpose interpreter was added.

| Fixed candidate | Q | U | MEM sites | Physical instruction sites | Total core sites | Scheduled controller path |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Shared gather, earlier physically tested | 16384 | 536870912 | 3383 | 10249 | 13633 | 357637146 |
| Packed ROM, original clock | 8192 | 536870912 | 3383 | 4213 | 7597 | 205636692 |
| Packed ROM, retimed clock | 8192 | 268435456 | 3383 | 4213 | 7597 | 205636692 |

The packed core leaves 595 sites, five of which are reserved tail/Signal
sites; the free gap before that tail is 590 sites. Against the shared-gather
candidate, the *allocated* colony length and work period are each halved,
and the scheduled controller path is 42.5% shorter. The virtual program grew
because the packed evaluator describes its own decoder. This is a real
self-description cost, not an instruction-count estimate borrowed from the
old rule.

The retimed ages are fixed constants in the physical rule:
`RESET=(0,20m,40m,80m,82m)`, `ACTIVE_END=(19m,39m,74m,81m,256m)`,
`VOTE=(60m,82m)`, `CAPTURE=76m`, and the forcing window begins at 80m and
lasts `2Q=16384` ticks. Exact symbolic head and packet timing gives minimum
gather margin 6981596 ticks, early capture margin 5310425, early head-stop
margin 3311021, and late evaluation margin 14941622. The full final
evaluation stops at physical age 241058378, before the 256m active cutoff;
the work period ends at 268435456. The prior 2^29 clock is retained as a
separate candidate and receipt. Retiming did not change the packed physical
ROM layout, but it changed the rule's Age logic, self-description, and ROM
values; it was validated independently.

## Verification and physical execution

`python -m unittest -q tests.fixed_rule.test_packed29_holder
tests.fixed_rule.test_packed28_holder` passed 9 tests in 29.656 seconds after adding the full
physical one-period regression to the retimed test. The tests check fixed
width, radius, ROM hash and projected identity across depths 1–3; complete
raw encode/decode including controller state; descriptor versus scalar F on
arbitrary typed raw neighborhoods; exact radius rejection; all three packed
slots as literal local FETCH steps; own-ROM dataflow on 15 upper cells; a
physical-row tamper that must fail; and a full retimed lower period with a
changed decoded upper state. The earlier eight-test run, before adding the
one-period regression, passed in 16.84 seconds.

For each candidate,
`experiments/fixed_rule/certify_packed{29,28}_holder_rom.py` checked
structural equality of all 154 optimized raw outputs, conditional own-ROM
execution of 188865 virtual instructions on 15 colonies, 62010 gathered
histories, 2205 metadata queries, 26790 packets, the Flag-only early pass,
the complete late raw Hold, and full Info commit/reset. It reports positive
timing margins. This symbolic checker is conditional on the head/packet
path contract; it is complemented, not replaced, by physical runs.

`experiments/fixed_rule/validate_packed{29,28}_holder_physical_events.py`
reached the three packed slots in one actually evolved lower state. For each
slot it compared the accelerated event with one literal full-ring physical
step (8192 sites), then checked nine local output sites against independent
scalar complete F. All 154 raw fields agreed. Complete physical periods use
the candidate's native F compiled from its own full descriptor at
reset/vote/capture/commit steps. Between these points a guarded CPU backend
skips regular head travel and quiet intervals, while applying literal F to
controller events and preserving the emitted packet payloads. The host
computes upper steps only for diagnostic comparison; host upper local-step
functions are patched to raise inside physical `step` and `advance`.

The following evidence is under `figs/fixed_rule/` (data, not Git source):

| Two-period physical run on 15 upper cells | Packed U=2^29 | Retimed U=2^28 |
| --- | ---: | ---: |
| Lower ticks elapsed | 1073741824 | 536870912 |
| Complete physical sites checked at each boundary | 122880 | 122880 |
| Complete raw upper Info words checked per boundary | 2310 | 2310 |
| Changed projected upper words, periods 1 / 2 | 108 / 97 | 108 / 97 |
| Changed represented controller words, periods 1 / 2 | 70 / 47 | 70 / 47 |
| Emitted / delivered / dropped packets | 53580 / 53580 / 0 | 53580 / 53580 / 0 |
| Wall time / peak process RSS | 225.18 s / 52912 KiB | 222.58 s / 50368 KiB |

Both Signal sides and both physical flags were active. No state was
reinitialized between periods. The independent saved-state audits recompute
all 30 represented upper transitions with scalar F and the hard-wired
descriptor, and check complete raw Info, flags, Signals, non-MEM Data,
controller emptiness, and mail emptiness. Both audits passed. The two seals
record execution/snapshot/audit, source, and six compiled binary hashes.
The final retimed physical F digest is
`26487a8bd653e025ed8f570d39734a8cc2d802532df9616bff3fe54dc6c1a95a`;
its ROM SHA-256 is
`663323a11ae6efae5328759daec2be5283f56ca421b33d018d343532c78b5252`.

Reproduction from the repository root:

```
python -m unittest -v tests.fixed_rule.test_packed28_holder
python -m experiments.fixed_rule.certify_packed28_holder_rom
python -m experiments.fixed_rule.validate_packed28_holder_physical_events
python -m experiments.fixed_rule.run_packed28_holder_cpu_general_periods --colonies 15 --periods 2 --output figs/fixed_rule/packed28_holder_cpu_periods_15_NEW.json
python -m experiments.fixed_rule.audit_packed28_holder_cpu_general_periods --execution figs/fixed_rule/packed28_holder_cpu_periods_15_NEW.json --output figs/fixed_rule/packed28_holder_cpu_periods_15_NEW_audit.json
python -m experiments.fixed_rule.seal_packed28_holder_periods --execution figs/fixed_rule/packed28_holder_cpu_periods_15_NEW.json --audit figs/fixed_rule/packed28_holder_cpu_periods_15_NEW_audit.json --output figs/fixed_rule/packed28_holder_cpu_periods_15_NEW_seal.json
```

## Limits and next optimization boundary

One lower work period represents **one upper transition**. These runs check
two such transitions on a 15-cell upper ring. They do not execute U upper
transitions, an entire Q-cell upper colony, or a full depth-two work period.
The physical backend requires canonical coherent geometry and Signals and
rejects certain faulty packet/flag overlaps. Three selected PACK3 events
were matched to literal full-ring steps; all intervening accelerated ticks
were not literally replayed. Noise amplification, upper-layer repair and
the printed Flag2 persistence/source timing qualifications remain open.

Gray's `U=128Q` is an asymptotic existence choice tied to his short looped
program, not a constraint satisfied by this concrete serial-head evaluator.
Here `U/Q=32768`, still 256 times Gray's ratio. A simple second retiming
cannot reach `U=2^27`: the late full evaluation alone needs 159058378 ticks,
already greater than 134217728. Nor does the present 7597-site core fit
Q=4096. A diagnostic four-op packing calculation on the *unchanged* virtual
program would reduce the core to 6800 and late traversal to 142371589 ticks,
still above 2^27 and Q4096 **before** including the larger self-decoder.
That estimate is a packing bound, not a built or verified rule. The next
substantial gains require reducing evaluator traversal and/or live workspace.
A full depth-two
Q-colony would have Q²=67108864 bottom sites, making a dense 154-word raw
state larger than the 80 GB A100 before buffers. Sparse/compressed evolving
state and radically shorter U are needed for practical whole-level GPU
experiments. Any new evaluator must again describe and execute its own
decoder and retain the two-period regression.
