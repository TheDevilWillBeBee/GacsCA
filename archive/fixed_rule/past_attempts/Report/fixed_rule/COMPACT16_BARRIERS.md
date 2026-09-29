# Compact16 phase interfaces and entry relation

2026-09-27. These checks extend [the paths/mail milestone](COMPACT16_PATHS_AND_MAIL.md).
The candidate remains Q=16384, U=1073741824, radius seven, 154 raw words/4090
bits and 105 projected words/2704 bits. No rule, ROM, alphabet, or timing constant
changed. This is not yet a compact16 whole-period self-simulation theorem or run.

## Direct descriptor checks

`certify_compact16_holder_barriers` passes against descriptor
`53f7adbf7c34df6b17897b20a0d0654108f23a9c064defb89bb3c6d1a7fb846b`
and ROM `4d055889959a880f189539dc213801780f8e2efa3daa7cb31e72cb3003f48b32`.

* Nine mail cases (quiet plus eight controller phases) check 11242 complete raw
  output identities across all 2^30 normalized physical Ages. Canonical geometry,
  coherent old procedure/static records, and zero or one head are premises.
  Physical flags, Signals and Wf are arbitrary. Mail may become incoherent when
  holders have different computed flags; this proof does not erase that behavior.
* Quiet reset/vote/commit identities check all 90 procedure words, 49 static words
  and two geometry words. Votes use old Data and override simultaneous reset;
  commit copies adjacent Hold into Info. Age wraps at 2^30, retaining a 32-bit
  physical field. The general boundary formulas supply the remaining 13 fields.
* A separate full-raw Age-zero reset BDD proves all 154 outputs with 1982
  independent bits: canonical Address, nine arbitrary Data words, all seven
  complete static records and six colony Signal bits. It assumes stationary
  five-holder Signals and zero flags/Wf/controllers/mail. Its stronger Signal
  premise is explicit; arbitrary entry Signals are handled by the boundary
  formulas, not silently covered by this stationary identity.
* Fifteen geometry/flag/Signal/Wf output formulas hold for all canonical
  Addresses and normalized Ages, with every other raw field arbitrary. Capture
  reads each holder's old corrected Data. Equal five-buffer low bits are required
  to produce a coherent captured Signal.

The modules were adapted from the prior proofs but rerun on the new descriptor.
Address geometry uses 14 bits and clock arithmetic 30 bits; physical widths stay
15 and 32. The all-clock mail proof inherits the new compact regular-mail terms.
No old-Q local identity or old clock-wrap result is substituted.

## Actual schedule interfaces

The checker verifies recorded source hashes and replays the complete compact
packet schedule, including all 1786 SEND occurrences. Five left buffers receive
Hold.Flag2 and five right buffers receive Hold.Flag1. Their last deliveries are
454947563 and 455121353. Capture reads old Age 495999999, leaving respectively
41052436 and 40878646 ticks. Destination accesses, unchanged common sources,
the intervening halt, and absence of reset/vote overrides are checked.

No scheduled packet survives into forcing. With Wf zero after Age 500032768,
the directed clearing implications give 8192 ticks per flag, hence both zero by
500049152. Final evaluation starts at 502000000, leaving 1950848 ticks.
The clearing statement uses candidate-B Flag2, not a resolution of the printed
Flag2 issue. Voted-old-Signal remains the explicitly modified D10 choice.

This join assumes that the checked instruction/packet trajectory is produced
from the encoded entry. It establishes timing compatibility, not that missing
semantic induction. It also does not establish noisy correction/amplification.

## Executable entry relation and tests

`compact16_holder_period_relation` defines Age-zero encoding, diagnostic
decoding, local validation and streaming ring validation. Every simulated raw
field, including controller and regenerated own-ROM metadata, occupies Info;
physical metadata is the fixed ROM. Scratch and initial Signals may be arbitrary.
Layout checks find 154 Info words and 3298 MEM scratch words; first reset clears
all scratch and retains Info, and every Info has its Hold immediately to the right.
No relation function evolves a simulated state.

Six tests pass. A streaming full 16384-site ring encodes/validates/decodes a seeded
arbitrary complete projected parent, arbitrary scratch and physical Signals with
a 64-cell cache. Missing represented PC and wrong represented metadata are
rejected. Thirteen literal native local steps match independent scalar F and
explicit expectations: five resets, extra vote entry, two votes (including
simultaneous reset), commit/wrap, two captures and two forcing sites. Other
mutations reject a missing raw PC output/reset bootstrap and a missing Signal
buffer in the schedule.

The first test run failed one fixture: projected lift had replaced intentionally
custom raw metadata by fixed ROM, yielding PC=0 instead of 17. The corrected
fixture explicitly supplies coherent raw static records for raw-F tests.
`COMPACT16_BARRIER_TEST_FIXTURE_FAILED_V1.txt` and the v1 log/watch preserve the
failure. No transition-rule fix was needed; fixed-ROM entry tests stay separate.

## Reproduction and limits

Commands (all CPU, existing private native binary, no GPU/build):

```sh
OPENBLAS_NUM_THREADS=1 python -m experiments.fixed_rule.bounded_cuda_probe --output figs/fixed_rule/compact16_holder_barriers_v1_watch.json --seconds 180 --rss-mib 768 -- python -m experiments.fixed_rule.certify_compact16_holder_barriers --output figs/fixed_rule/compact16_holder_barriers_v1.json > figs/fixed_rule/compact16_holder_barriers_v1.log 2>&1
OPENBLAS_NUM_THREADS=1 python -m experiments.fixed_rule.bounded_cuda_probe --output figs/fixed_rule/compact16_holder_barrier_tests_v2_watch.json --seconds 180 --rss-mib 768 -- python -m unittest tests.fixed_rule.test_compact16_holder_barriers -v > figs/fixed_rule/compact16_holder_barrier_tests_v2.log 2>&1
OPENBLAS_NUM_THREADS=1 python -m experiments.fixed_rule.seal_compact16_holder_barriers
```

Proof: 8.477696 s, self-reported peak 128620 KiB; watcher 9.355803 s,
sampled child peak 123096 KiB, exit 0. Corrected tests: six PASS in 10.539 s;
watcher 10.861744 s/120864 KiB, exit 0. Failed fixture run: six tests/one failure
in 10.335 s; watcher 10.715378 s/120920 KiB, exit 1. Watchdog parents are not
included in child figures; jobs ran sequentially. RAM is far below the 40 GB
task allowance. All jobs are terminal; no shared source, dataset or job changed.

Next: connect entry, semantic ROM dataflow, physical paths and these barriers
into the compact rule's complete period relation and its iteration. Then validate
the private execution backend and run physical periods/depth two/cross-level
faults. The frozen retimed execution baseline is not replaced. General noise
amplification, boundary reliability and depth-three execution remain open.
