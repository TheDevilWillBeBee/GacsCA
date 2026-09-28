# All-clock mail factorization and physical replica output shape

2026-09-26. The fixed physical rule now has a checked local mail reduction over
every clock value, including resets, votes, capture, workspace transfer, rest and
commit. It permits independent raw mail replicas and arbitrary physical flags,
Signals and Wf. This removes the mail-coherence premise from the earlier
[factorization](MAIL_FACTORIZATION.md). It does not establish a complete work
period or a second hierarchy level.

## Exact scope

The physical rule F, radius 7, 154-word alphabet, Q=32768, U=4294967296 and ROM are
unchanged. The descriptor hash remains
`af2de0673ac685bb83e8a319751b7f10e22c05037809ff0479bdf292a789fbb6`.
All nine cases (no head and each of eight head phases) quantify every Address
and all 2^32 clock values. Old Address geometry is canonical, Age is uniform,
and static records, Data, head and controller replicas are coherent. There is
zero or one old head in the checked local domain; inactive controller fields
are zero. Those premises have not yet been established as a global invariant.

Let E erase only old mail. The checker compares complete F(x) against F(E(x)),
replacing the latter's Data and mail with explicit clocked local formulas. It
reuses F(E(x)); this is a reduction lemma, not an independent proof of the
mail-free controller or a new evolution backend. The extension substitutes the
actual bitwise majority of five independently variable raw copies into every
old logical mail term. It retains every raw output word, including controller
fields and mail words whose valid bit is zero.

The extra simplifier identity is the word identity
`NAND(NAND(m,x), NAND(~m,x)) = x`. Tests cover arbitrary words and reject a
noncomplementary mask. Independent scalar/native audits do not use the
symbolic simplifier.

Canonical Address and the incremented uniform Age survive arbitrary old
physical flags in this domain. Computed holder Flag1 clears that holder's mail;
it can make the five copies of a logical packet unequal. Data and controller
clearing would additionally require an Address change, which does not occur
here. Thus treating all procedure replicas as coherent after every tick would
be incorrect.

The output-image checker establishes that all five copies of each logical Data,
head, controller and Wf word agree, while each mail copy has the form

```
next_mail_copy_at_holder_h = 0 if next_Flag1[h] else common_mail_word
majority5(next_mail_copies) = common_mail_word if at least 3 holders survive else 0
```

The common word is an algebraic proof term, not an extra hardware register.
The second equality is checked by a six-variable BDD over all 64 assignments,
and applies bitwise to every mail word. **Metadata wording correction:** the
saved v1 certificate describes this as equality with the common bit “iff” three
holders survive. That sentence is imprecise when the common bit is zero. The
code actually proves `common_bit AND majority5(survival_bits)`, exactly the
formula above. Frozen sources and manifests are preserved; the symbolic and
native checks implement the correct formula.

## Boundary behavior and literal trajectories

The tests distinguish priorities that a whole-period composition must retain:
reset may keep same-tick delivery to unmarked Data; rest retains stale invalid
packet words; vote and commit override incoming Data; computed Flag1 clears
mail after delivery; Signal capture reads old Data before that tick's delivery.
These are properties of the current candidate, including its documented
voted-old-Signal D10 choice, not resolutions of all source ambiguities.

Five saved two-tick causal cones compare the scalar rule and compiled complete
descriptor on all 154 raw words. Clean delivery produces Data=55; two corrupted
mail copies are corrected and still deliver 55; three corrupted copies or a
Flag1 gradient leave Data=7. A rest case repairs replicas without transporting
the packet. The two- and three-copy corruptions change 200 and 300 bits in these
fixtures, respectively; they are not two- and three-bit noise experiments.

A separate replay installs actual fixed-ROM metadata in each *initial* fixture
and verifies the same dynamic effects. Every subsequent state is a literal F
output. Diagnostic projection checks never replace intermediate states. These
are two physical ticks, not two hierarchy levels, and show no stochastic noise
threshold or cross-level suppression.

## Checks and measured cost

| Check | Verified result | Seconds | Peak host RSS (KiB) |
|---|---|---:|---:|
| Coherent-mail all-clock reduction | 9 cases, 11,242 raw word identities | 6.761247 | 78,852 |
| Independent raw-mail extension | 9 cases, 11,242 raw word identities | 7.167483 | 88,168 |
| Boundary scalar/native audit | 8,979 full + 8,979 mail-erased outputs, 41 Ages | 64.637906 | 75,248 |
| Saved two-tick witnesses | 80 complete outputs | 0.281886 | 36,800 |
| Saved replay and actual-ROM variants | 80 replayed + 80 new complete outputs | 0.963873 | 60,348 |
| Output-image symbolic check | 324 coherent groups, 1,080 masked copies | 3.095835 | 83,684 |
| Output-image scalar/native audit | 1,890 complete outputs; 9,720 coherent groups; 32,400 masked copies; 6,480 decoded majorities | 7.328811 | 58,016 |

Eight clock tests passed in 7.073 s; four raw-mail tests passed in 7.309 s.
All successful manifests report `passed: true`; all recorded source hashes
were rechecked. No GPU run or physical-rule modification was needed.

The first boundary audit failed because its dense fixture initializer cleared
`physical_age` along with names beginning `physical_`. The failure happened at
the Age assertion. The corrected harness excludes Age and explicitly checks
assigned Age/Address before auditing. Preserve
`small_holder_clock_mail_factorization_audit_v1.log` and
`small_holder_clock_mail_audit_failed_v1_source.py.txt`; the successful audit is
v2. No rule or proof formula changed to resolve that harness failure.

Commands below used `OPENBLAS_NUM_THREADS=1`, with stdout/stderr saved beside
each output as `.log`. Existing evidence must not be overwritten when rerunning.

```sh
python -m experiments.fixed_rule.certify_small_holder_clock_mail_factorization --output figs/fixed_rule/small_holder_clock_mail_factorization_v1.json
python -m experiments.fixed_rule.certify_small_holder_raw_mail_factorization --output figs/fixed_rule/small_holder_raw_mail_factorization_v1.json
python -m experiments.fixed_rule.audit_small_holder_clock_mail_factorization --certificate figs/fixed_rule/small_holder_raw_mail_factorization_v1.json --output figs/fixed_rule/small_holder_clock_mail_factorization_audit_v2.json
python -m unittest discover -s tests/fixed_rule -p test_small_holder_clock_mail_factorization.py -v
python -m unittest discover -s tests/fixed_rule -p test_small_holder_raw_mail_factorization.py -v
python -m experiments.fixed_rule.small_holder_flag_masked_mail_witnesses --output figs/fixed_rule/small_holder_flag_masked_mail_witnesses_v1
python -m experiments.fixed_rule.audit_small_holder_flag_masked_mail_witnesses --execution figs/fixed_rule/small_holder_flag_masked_mail_witnesses_v1 --output figs/fixed_rule/small_holder_flag_masked_mail_rom_audit_v1
python -m experiments.fixed_rule.certify_small_holder_procedure_image --output figs/fixed_rule/small_holder_procedure_image_v1.json
python -m experiments.fixed_rule.audit_small_holder_procedure_image --certificate figs/fixed_rule/small_holder_procedure_image_v1.json --output figs/fixed_rule/small_holder_procedure_image_audit_v1.json
```

JSON evidence SHA-256 values (prefix `figs/fixed_rule/small_holder_`):

| Suffix | SHA-256 |
|---|---|
| clock_mail_factorization_v1.json | `4021cb76937f06392cfe606151eead8ba37d18287f3c15f9c1bdae7276c43e38` |
| raw_mail_factorization_v1.json | `b0ba96366800fa811e1e7124041ecbd4acefd9d6713a0a7abab104f9c79f5a70` |
| clock_mail_factorization_audit_v2.json | `3894d959b218a8a815954cb0025be72d512eb8638b9f88829afa1cef50293b3d` |
| flag_masked_mail_witnesses_v1.json | `171918c2f0cd34b18e95eb7a0202a06f301ef1d7da0644cea67f86793ae1f04a` |
| flag_masked_mail_rom_audit_v1.json | `ac213e14de3c8f453e810a2e6899c0f9533800ed0d5d0a594c52278ef517f551` |
| procedure_image_v1.json | `e7be6fdf152af724bca3759d1d98c0dfcd40bde2754309c6dcc696f3b2dc8a0d` |
| procedure_image_audit_v1.json | `aed0f5343ee38d6c8884fd4730b168e48941dec1e76a0e05be288c9f42a01dc2` |

## Construction relevance and remaining obligations

Gray pp. 31–32 motivates eliminating ProgramBit by specialized hard-wiring;
Gács §§9.2–9.3 allows an identical or appropriately modified self-correcting rule.
This work checks the existing specialized complete-controller candidate. It adds
no general-purpose programming requirement, depth-specific state or kernel.
See [MAIL_FACTORIZATION.md](MAIL_FACTORIZATION.md) and the linked architecture
and source audits for the construction and its unresolved Flag2/SimBit choices.

The next induction can accept arbitrary raw mail after each tick, so holder
masking no longer invalidates its mail premise. Still required: global head
count and core confinement, entry production and controller/Data occupancy
invariants, the actual Signal-buffer/capture relation and flag profiles across
successive periods. Signal-copy coherence is not established here. Local
identities alone do not authorize skipping an entire physical work period.

After those obligations, demonstrate complete decoded upper work periods at
depth two, measure GPU space/time, and test repair across levels. Current Q/U
are experimental costs, not optimized values or a justification for U<=128Q.
The latter is not an acceptance constraint. The cap Address-defect persistence
also remains open; none of these mail results supplies robust termination.
