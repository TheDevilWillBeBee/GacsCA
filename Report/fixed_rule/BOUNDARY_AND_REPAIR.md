# Ordinary boundary data and a physical repair counterexample

The verified candidate-B self-description admits an ordinary flagged boundary
orbit. This meets the **no special top kernel** part of finite-depth termination:
the cap is initial data processed by the same G. It is not an organized colony,
and dynamical consistency alone does not establish a noise-robust boundary.

## Exact descriptor identities

For a homogeneous cap with Address=Q-1, Flag1=Flag2=1, zero payload/controller/mail/
Signal/Wf, and synchronized Age, the next raw state changes only Age, to
(Age+1) mod U. The new diagnostic `word_bdd.py` checks exact word-expression
identities using reduced ordered binary decision diagrams. It is never used by a
physical transition or executor. The complete 2,648-operation descriptor reduces
to the claimed outputs for **all 2^30 clock values**, not sampled clock phases.
The proof uses 3,113 BDD nodes and takes 0.31179165840148926 s; see
`cap_orbit_proof_v1.json`. The existing separate scalar/native/descriptor tests
remain necessary evidence for implementation fidelity; this symbolic identity
alone is a theorem about the specified word descriptor.

A stronger payload-family conjecture initially failed: nonzero Data can set the
low Signal bit at computed capture Age, even in the flagged cap. The failed
source is preserved in `failed_cap_payload_v1.txt`, with the v1 logs. The corrected
invariant family allows Signal in {0,1}, independent Data words at all eleven
neighbors, and a shared arbitrary Age. Its exact next-state identities are:

- Data is zero at the five old reset Ages, and otherwise retains its own value.
- Signal is the old own Data low bit at computed capture Age, and zero otherwise.
- Address/flags remain the cap values, Wf/controller/mail remain zero, and Age
  advances modulo U. A low Signal bit alone cannot win any five-copy vote.

`cap_payload_proof_v2.json` covers **745 independent Boolean input bits** using
21,748 BDD nodes in 0.3321866411715746 s. In this family a nonzero payload resets
within at most 32Q=268,435,456 **upper** transitions. This is not a full damaged-
state recovery theorem: faults in geometry, higher Signal bits, heads and mail
are outside the family. Two BDD arithmetic tests exhaust all pairs of four-bit
operands; four cap tests include descriptor mutations for a frozen clock and a
missing raw controller output. Corrected cap tests pass in 0.857 s. A later
strict front-end validates exact input/output arity and DAG references before
running the proof. Three further mutation/contract tests pass in 0.662 s, and
`cap_proof_contract_v1.json` verifies both complete construction descriptors.
The known descriptors had complete outputs already; the stricter interface also
rejects a descriptor with a deleted or extra output.

## Single physical Info-bit fault

`cap_fault_execution_v1` starts two ordinary cap cells at upper Age 1, encoded
as two physical colonies. It flips exactly bit zero of the physical Data word at
address **8,390,034**, which encodes the second upper cell's Data. No transition
kernel, program, or other field is changed. Both full work periods use the actual
preceding physical state. Host `Program.evaluate` and scalar upper transitions
are disabled while physical executors run.

After **2,147,483,648 physical ticks**, the clean upper Data is still zero and the
damaged upper Data is still one. Every one of the three temporal gathers in
both periods contains that same damaged input. Their temporal majority therefore
cannot repair it. The complete run took 99.17036919947714 s. This demonstrates
that current temporal redundancy and candidate-B Flag2 repair do **not** provide
Gray's fivefold spatial protection for Info or arbitrary workspace/controller
bits. The eventual cap reset above does not turn this into one-period repair.

`cap_fault_audit_v1.json` independently checks 251 frozen/live source files,
the exact single changed bit, all raw gathered words, scalar/native/descriptor
agreement for both decoded transitions, exact physical handoff, raw Info commit,
and complete native reset transitions at stored positions. It passes in
1.1393326567485929 s. It does not rerun the entire long trajectory. The two-cell
ring aliases simulated neighbors; this is a fault witness, and does not replace
the separate 23-cell active-controller/nonaliased two-period evidence.

## Source and construction consequence

Gray pp.33–34 explicitly require fivefold storage, moving mail, workspace and
procedures in addition to temporal redundancy. See
[the supplied text](../../papers_txt/gray_readers_guide.txt). Current Info words
are single physical copies. The next construction must include its redundant
controller, correction operations and their resource cost in its self-description;
adding a wrapper without updating that description would lose closure.

The radius obstruction and first implementation step are recorded in
[SERIAL_VOTE.md](SERIAL_VOTE.md). Full spatial protection remains unimplemented.

## Commands

All runs used `OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1`.

```sh
python -m unittest tests.fixed_rule.test_word_bdd -v
python -m experiments.fixed_rule.prove_cap_orbit --output figs/fixed_rule/cap_orbit_proof_v1.json
python -m unittest tests.fixed_rule.test_cap_proof -v
python -m experiments.fixed_rule.prove_cap_payload --output figs/fixed_rule/cap_payload_proof_v2.json
python -m experiments.fixed_rule.cap_fault_execution --output figs/fixed_rule/cap_fault_execution_v1
python -m experiments.fixed_rule.audit_cap_fault --input figs/fixed_rule/cap_fault_execution_v1 --output figs/fixed_rule/cap_fault_audit_v1.json
```
