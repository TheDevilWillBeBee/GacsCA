# Factored literal G and two actual noisy macrostep failures

2026-09-28. Full fixed-rule goal remains active. The physical rule, alphabet,
radius, ROM, Q and U are unchanged. This milestone makes damaged evolution about
16times faster and follows two retained failures through an actual commit.

## Exact factorization and its premises

`compact16_holder_canonical_gpu.{py,cu}` accepts full raw projected states only
when Address is canonical and Age is uniform/legal. All other typed fields are
arbitrary: incoherent procedure copies, Data, mail, Signals, flags, Wf and any
number of heads. It retains all154raw fields. The 512workers and temporary arrays
are evaluator storage, not new physical hardware or level-dependent dispatch.

For logical position x and procedure field n, define the bitwise majority
V(x,n) of raw replicas s(2-d,n) at holders x+d, d=-2..2. Every holder computing
the update for x constructs exactly the same virtual core neighborhood when
geometry is canonical/uniform: Address(x+j), common Age, V(x+j,n), and the
fixed ROM metadata at x+j. Consequently compute that core clock output once
per x, then scatter it to the five holders. Each holder still clears every
outgoing mail copy when its own newly computed Flag1 is set. Canonical geometry
prevents the separate Address-change clearing branch. No coherence assumption
is needed for the old procedure inputs; voting runs afresh at every tick.

Separate kernels compute those votes, exact flag updates, the core clock, and
the full raw output. Signal voting retains all five raw bits and the holder-local
capture exception; Wf copies use the updated geometry/Flag1 of their logical
primary and old voted Signals. Metadata is the same fixed pointwise G projection.
There is no skipped physical tick in this executor and no host transition.
The `healthy_domain` core-clock description is valid for these virtual records:
the physical F rule itself constructs them with zero flags/Wf, even when actual
physical holders have nonzero flags. This is not assuming the damaged state is
healthy.

A fresh BDD certificate checks the full F geometry outputs against the simplified
canonical equations: all16384Addresses, all2^30legal Ages and44independent primary
flag/Wf bits (88independent bits total). Unused raw fields are unrestricted by
checked descriptor support. Address stays canonical, Age increments modulo U,
and both flag outputs agree exactly.47811BDDnodes,0.821635s. A wrong Flag1
threshold mutation is rejected. The procedure/Signal/Wf composition above is
an algebraic argument plus backend parity tests, not a universal compiler proof.

Four GPU testsPASS in20.340s: arbitrary complete raw states across reset/vote/
capture/Wf/active/commit clock boundaries; one- and two-colony seams; every saved
case32→128→511→512 compared to prior complete literal-GPU trajectories; and
rejection of bad geometry, metadata, word widths and budgets. Controllers are
actively evolving; host evaluators are patched to fail during GPU calls.
One-colony allocation47,411,200bytes; two-colony test permits128MiB. The bounded
2048tick benchmark took2.013826s, versus approximately16ms/tick for the full-DAG
executor. The physical construction has not become cheaper in mathematical U;
this is an execution optimization.

## All eight retained failures, 16,384 more ticks

The starting point is exactly the preceding saved state after520quiet ticks.
All eight p=.1 local-noise trials are retained. Each runs16384more physical ticks
with no new faults; healthy comparison follows the same clock. Saved complete
checkpoints are1/512/2048/8192/16383/16384. Every raw word is losslessly retained
as a difference against complete saved healthy states.

The run evaluated2,415,919,104site transitions in150.665258s; watchdog151.128685s,
468672KiB sampled peak RSS,47,411,200explicit device bytes, one world at a time.
All eight final Flag1/Flag2/Wf planes are zero. None fully rejoins:

|Case|Differing sites|Raw words|Primary Data differences|Actual heads|
|---|---:|---:|---:|---|
|0|26|125|7|1, PC16785408|
|1|28|40|8|1, same as healthy|
|2|35|125|8|1, PC68420096|
|3|25|90|8|0|
|4|37|150|8|2, PCs72433664 and0|
|5|18|100|3|1, PC132136|
|6|26|80|8|1, PC2473|
|7|39|135|15|0|

Healthy head: position12657, phase1, PC2217. Signals remain different in cases
0/3/5/6/7. Flag clearance therefore does not imply restoration of computation.
Some extra heads seen earlier have also disappeared through actual evolution.

## Guarded idle suffix and actual commit

Cases3/7 satisfy a stronger, complete-state condition: no controller/head/mail
word remains, flags/Wf are zero, and Data/Signals are coherent across holders.
Their Age is508496235, after every reset, vote, capture and Wf event in the
current work period. Until old Age U-1, full G changes only Age in this domain.

`compact16_holder_late_idle_gpu.{py,cu}` checks every one of these premises on
GPU before changing any word. It rejects invalid states without mutation. The
host checks the fixed event interval; a matching GPU clock check prevents a
stale host clock from authorizing a jump. The kernel advances only Age, stops
at U-1, and leaves the actual commit to the ordinary canonical literal kernel.
No simulated upper transition is supplied by the host.

The idle core identity is checked by BDD for every old Age502000001..1073741822,
all Addresses, arbitrary typed virtual ROM metadata and neighboring Data.
All18procedure fields are covered;958independent bits,148358BDDnodes,
189operations after exact constant propagation,0.994165s. Combined with the
geometry certificate, coherent majority/Signal identity, and the absence of a
future Wf/capture event, this gives the full-holder idle composition. Removing
the commit boundary has a concrete differing-bit witness. Three GPU testsPASS
in23.893s: native literal parity, active/inactive and commit boundaries, a long
skip, and complete-state/interval rejection without mutation.

Two earlier proof attempts exhausted their200000node cap while forming an
unnecessary union of64mutation-counterexample bits, **after** the actual idle
output equalities had been checked. V2's exact constant propagation alone did
not fix that union. V3 stops at the first concrete differing bit, which suffices
to reject the mutation. Both failed sources/logs/watchdogs are preserved. No
physical source or simulation result changed to make the certificate pass.

For each retained case, the GPU advances565245588idle ticks to U-1, then executes
one actual commit. All154Info words are decoded, including every raw controller
copy, and compared with the intended scalar self-simulated G transition of the
original top state. The independently completed healthy fixture agrees with
that scalar target. Both noisy commits disagree in49raw fields; after removing
metadata they still disagree in33of105projected fields. All five physical Info
copies agree on those wrong values. Decoded Age is0, expected502000101; affected
procedure fields include Data, head, phase, PC, value and ALU, plus Flag1/Flag2.
This establishes actual decoded macrostep failures for these two noise histories,
not merely incomplete raw recovery by a deadline. Both outputs are word-width
valid; that does not establish membership in the correct projected code image.

The two-case run took3.203463s/watch3.651636s,372156KiB sampled RSS and47,411,204
explicit GPU bytes. It does not establish the other six macrostep outcomes or
a noise threshold. The histories were drawn in the earlier unfiltered pilot;
this suffix selected the two states satisfying a proved execution domain, not
a sample from which to estimate a failure probability.

## Independent checks and reproduction

The audit checks the final literal transition of all8longer trajectories; every
saved field count; all final flag planes; all idle premises; complete precommit
states; both actual commits; all five Info replicas; and projected decoding.
30,277,632raw words checked plus340complete scalar outputs (32seam outputs and
all154physical Info sites in both commits). Audit9.352809s/watch9.737111s,
228032KiB peak RSS. Long factored trajectories are not wholly replayed with a
second backend; finite parity and the stated factorization support them.

```sh
FIXED_RULE_GPU_TESTS=1 python -m unittest tests.fixed_rule.test_compact16_holder_canonical_gpu -v
python -m experiments.fixed_rule.prove_compact16_holder_canonical_geometry
python -m experiments.fixed_rule.compact16_holder_canonical_noise
FIXED_RULE_GPU_TESTS=1 python -m unittest tests.fixed_rule.test_compact16_holder_late_idle_gpu -v
python -m experiments.fixed_rule.prove_compact16_holder_late_idle_v3
python -m experiments.fixed_rule.compact16_holder_headless_macrostep
python -m experiments.fixed_rule.audit_compact16_holder_canonical_noise
```

All above commands exit0. Each has a matching receipt/log/watch under
`figs/fixed_rule/compact16_holder_*_v1`, except successful idle proof `_v3`.
Evidence manifest: `compact16_holder_canonical_noise_evidence_v1.json`. It binds
new sources, private binaries/generated headers, successes and bounded proof
failures, while preserving all935prior files and nine external banks.

## Remaining work

Continue the other six actual states through commit using a justified accelerator
that retains arbitrary Signals and damaged controller motion; then test what the
next work period repairs. Use multiple simulated colonies to distinguish repair
by healthy simulated neighbors from the one-periodic-top fixture here. Broaden
stochastic sampling and cross-level experiments without discarding failures.

These counterexamples do not contradict the conditional sparse two-tick lemma:
their dense continuing-fault histories violate its premises. They expose a real
limit of the implemented protection. General Gács amplification, malformed code/
geometry recovery, reliable finite caps, sustained depth-two top arithmetic and
depth3 remain open. Gray31–32 specialized hard-wiring and Gács9.2–9.3 modified
self-correcting simulation remain the architectural basis; Flag2/SimBit source
qualifications remain. No physical alphabet, rule, ROM or hierarchy-depth case
was added. User40GB host limit respected; shared sources/jobs/builds unchanged.
