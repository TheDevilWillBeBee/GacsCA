# Physical continuation repairs the decoded upper controller

2026-09-27. The actual damaged endpoint from
[CONTEXTUAL_MACROSTEP.md](CONTEXTUAL_MACROSTEP.md) now continues through three
more lower work periods. **The decoded upper state rejoins its unfaulted
17-cell window after two periods.** A third period refreshes the remaining
lower histories: every bank word and Signal then matches the unfaulted terminal
reference. Three explicitly retained nonMEM Data words persist.

This executes the path from a physical lower noise burst, through a wrong upper
controller state, to repair by the self-simulated rule. It is a result for the
matched periodic **17-colony context**, not a full-Q lower-ring noise run,
complete physical erasure, a threshold or a general amplification theorem.
The full project goal remains active.

## Results and cost

The starting decoded error is the actual zero Info record committed by colony 9,
with 12 wrong mutable fields including the upper WRITE controller. No error
symbol is inserted into a fresh upper fixture. Each subsequent decoded state
matches G applied to the preceding actual decoded state, including every raw
controller field.

| Subsequent lower periods | Different upper cells | Bank words differing from the unfaulted terminal reference | Retained nonMEM words |
|---:|---|---:|---:|
| 1 | Colony 9 | Not measured separately | 3 |
| 2 | None | 660, in colonies 2–16 | 3 |
| 3 | None | 0; Signals also equal | 3 |

The two-period GPU run takes **51.693753 s**; the three-period run takes
**75.496703 s**, including restoration and a separate normalization twin.
The explicit device bound is **44344850 bytes**. Process peak RSS for the longer
run is **876452 KiB**; its watchdog samples 875004 KiB. No substantial GPU
reservation was used. CPU/device allocations remain below the user limits.

The three persistent values remain at colony-8 addresses 30960–30962. They
occupy 15 raw Data-copy fields at seven physical sites. They are retained in
the executable representation and are not counted as repaired or erased.

## Exact retained-Data relation

The new descriptor certificate substitutes shared arbitrary 64-bit variables
into the five copies of each of those three Data words. It checks all **3234
complete raw outputs** in their radius-seven causal support. The 15 Data copies
remain exactly their input variables; the other 3219 outputs are independent of
those variables. Canonical Address and uniform legal Age are preserved.

This covers **every legal clock value**, including reset, vote, commit, forcing
and Signal capture. Other raw controller, mail, flag, Signal and Wf fields are
arbitrary; no head-count or controller-phase assumption is made. Fixed ROM,
canonical Address, common legal Age and unanimity of the selected Data copies
are required. The proof is a symbolic Python descriptor check, not a proof
assistant result. It does not justify holding these words constant through
future faults that break those hypotheses.

Thus the existing encoding may be extended by these independently retained
words along the checked canonical trajectory. `retimed_holder_inert_storage.py`
uses the same GPU rule for the remaining state and preserves their exact values.
Initialization uploads the actual bank, including malformed encoded metadata,
and verifies **85786624 raw words** at the unchanged time. There is no new
physical field, rule, ROM, depth selector or evolving host interpreter.

The certificate passes in **2.292499 s**. Four proof tests reject a real MEM
word, a Signal-capture source and a mutated Data-to-packet dependency. Four more
storage tests reject omitted/unsupported state and compare native G at the clock
boundaries with arbitrary raw context. They pass in **3.210 s /2.069 s**.
Two earlier checker versions are preserved with their failure logs: one confused
primary Data with packet `lp_data/rp_data`; the next parsed `signal` incorrectly.
These were harness defects, not physical counterexamples.

## Physical normalization closes the entry-domain gap

The damaged Info is not initially a normalized encoding. The actual stage-zero
program executes 49 LOAD/META pairs and six address calculations before gathering.
A separate comparison world starts with just the Info metadata normalized; the
two initial banks differ in **16 words**. The actual world receives no copy from
that comparison world.

By physical Age **10487886**, both worlds agree in every raw field, including
the retained Data. The mutable Info is unchanged and all metadata has been
rebuilt by the physical evaluator. The prefix is independently replayed with
the full native global event executor and with guarded scalar procedures:
**2266 trace intervals**, **75582 scalar candidate outputs**, and **48781
distinct complete scalar neighborhoods**. All saved raw fields agree.

A separate reset-entry check constructs a valid encoded Age-zero state, with
arbitrary admissible scratch and the certified retained Data, and executes one
full global G step. All **85786624 raw words** match the normalized twin at
Age one. This gives a concrete reset preimage; admissibility is not assumed from
the malformed noisy endpoint. The check passes in **10.539936 s**.

Combining this reset preimage, the physical prefix coupling, the retained-Data
commutation relation, and the existing conditional noiseless macrostep identity
justifies using the terminal relation for this particular continuation. It does
not establish entry recovery from arbitrary corruption.

## Endpoint audit and reproducibility

For each actual GPU period, the auditor checks all **168572 bank words**, every
controller/mail field, Signal, flag and raw copy against the diagnostic terminal
identity. This formula is never installed into an evolving world. The two-period
audit passes in **32.423913 s**, checking 257359872 raw words including the
normalization endpoint. The three-period audit passes in **33.349412 s**.
The common entry, normalization and first two endpoint snapshots of both runs
are identical. The history-refresh comparison has a separate reproducible
auditor. All accepted runs terminate with return code zero.

The core commands below write matching private `.log` files; use new artifact
names for reruns. Tests use `python -m unittest` with
`tests.fixed_rule.test_retimed_holder_inert_data` and
`tests.fixed_rule.test_retimed_holder_inert_storage`.

```sh
python -m experiments.fixed_rule.bounded_cuda_probe --output figs/fixed_rule/retimed_holder_inert_data_v3_watch.json --seconds 180 --rss-mib 2048 -- python -m experiments.fixed_rule.certify_retimed_holder_inert_data --output figs/fixed_rule/retimed_holder_inert_data_v3.json
python -m experiments.fixed_rule.bounded_cuda_probe --output figs/fixed_rule/retimed_holder_contextual_next_periods_3_v1_watch.json --seconds 240 --rss-mib 3072 -- python -m experiments.fixed_rule.retimed_holder_contextual_next_periods --periods 3 --output figs/fixed_rule/retimed_holder_contextual_next_periods_3_v1.json
python -m experiments.fixed_rule.bounded_cuda_probe --output figs/fixed_rule/retimed_holder_contextual_next_periods_3_audit_v1_watch.json --seconds 240 --rss-mib 3072 -- python -m experiments.fixed_rule.audit_retimed_holder_contextual_next_periods --input figs/fixed_rule/retimed_holder_contextual_next_periods_3_v1.json --output figs/fixed_rule/retimed_holder_contextual_next_periods_3_audit_v1.json
python -m experiments.fixed_rule.bounded_cuda_probe --output figs/fixed_rule/retimed_holder_contextual_reset_entry_v1_watch.json --seconds 120 --rss-mib 3072 -- python -m experiments.fixed_rule.certify_retimed_holder_contextual_reset_entry --input figs/fixed_rule/retimed_holder_contextual_next_periods_2_v1.json --output figs/fixed_rule/retimed_holder_contextual_reset_entry_v1.json
python -m experiments.fixed_rule.bounded_cuda_probe --output figs/fixed_rule/retimed_holder_contextual_history_refresh_audit_v1_watch.json --seconds 60 --rss-mib 1024 -- python -m experiments.fixed_rule.audit_retimed_holder_contextual_history_refresh --input figs/fixed_rule/retimed_holder_contextual_history_refresh_v1.json
```

The normalization-only and two-period runs use the same driver with `--periods
0` and `--periods 2`; exact commands and limits are retained in their watchdog
receipts. Evidence index:
`figs/fixed_rule/retimed_holder_contextual_upper_repair_evidence_v1.json`.
All new sources and artifacts are confined to the owned fixed_rule namespaces.
No shared source, historical dataset or other agent's job was changed.

## Remaining work

Extend this contextual result to a complete upper colony, with an explicit
embedding/boundary argument or a larger physical run. Continue optimizing Q/U
and execution cost while keeping one fixed rule independent of hierarchy depth.
Further noise experiments must account for the retained Data if new faults
break canonical geometry; the quiet invariant cannot silently replace those
transitions. General amplification, stochastic robustness, robust finite-depth
caps, depth three and the existing Flag2/SimBit fidelity issues remain open.

STATUS.md is the handoff. Please use MAIN_AGENT_NOTES.md for replies; this agent
does not edit that file.
