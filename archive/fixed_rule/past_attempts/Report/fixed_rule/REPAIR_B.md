# Explicit candidate-B fixed self-simulator

This is a separately named construction revision, not a runtime variant or a
hierarchy-dependent kernel. The printed-rule `delivery_*` implementation and
all its datasets remain unchanged. The new `repair_b_*` rule fixes the healthy
Flag2 erasure condition to **at most one in-colony left Flag2 bit equal to one**.
It makes no claim that this is Gray's intended printed formula.

## Why this modification is being investigated

Gray p.21 prints erasure when no in-colony left site has Flag2 zero. The supplied
text at `papers_txt/gray_readers_guide.txt:943` records this condition. It leaves
an isolated interior Flag2 error unchanged indefinitely, contrary to the nearby
repair discussion (pp.22–26). The shared [D8 audit](../../../../legacy_tower/Report/flag2_recovery_gap.md)
documents that invariant and compares candidates A and B. Candidate A clears one
isolated error but does not clear two adjacent errors in one step. Candidate B
has the stronger local two-fault repair contract already investigated by the
main agent. Neither alternative is source-authorized as an erratum.

The selection criterion here is this repair contract, not merely faster
execution. A rule retaining the demonstrated invariant cannot support the desired
local recovery claim. Gray pp.31–32's specialized projection and Gács §§9.2–9.3's
identical/suitably modified self-correcting rule support investigating a complete
self-description of an explicit modified family member. They do not prove this
particular modification sound for the full amplification construction. The D10
voted-old-Signal choice and other construction gaps remain separately qualified.

The bounded-memory literal-rule experiments continue to provide a reference.
They do not silently change erasure semantics. Candidate-B tests that use a
literal-rule checkpoint label it **arbitrary initial data under a different
rule**, not continuation of the literal trajectory. The actual candidate-B
hierarchy experiment starts afresh with its own ROM and full physical evolution.

## Fixed alphabet and complete description

The physical neighborhood remains radius five. Raw F has **788 bits / 32 words**;
projected G has **590 bits / 25 words**. Q=8,388,608 and U=128Q are fixed constants.
There is no erasure-policy argument or depth argument to the transition,
self-description or program compiler. All depths use the same candidate-B G.

The complete pruned self-description has **2,648 operations**, SHA-256
`36ee9cab67e3520b94ec2f3a4265a7cdbbcd93a09d77e51331f2bbb71666549f`.
The projected ROM SHA-256 is
`4fb696289cc8820236ba63ccf8e3278cc189636ba5ed6d8650201a24942e035c`.
The transcript occupies **7,913 physical core cells**. Measured schedule bounds:

| Quantity | Physical ticks |
|---|---:|
| Complete raw evaluator | 56,601,678 |
| Evaluation budget | 67,108,864 |
| Evaluation margin | 10,507,186 |
| Last third-stage computed-flag delivery, relative to 70Q | 65,140,645 |
| Delivery margin before computed-Age 79Q capture | 10,356,827 |

The scalar maintenance change and expression description change are both
implemented. The evaluator's raw state, active instruction transitions,
communications, metadata fallback, clocks, majority/capture and Wf remain in the
complete description. The program regenerates output program words using the
computed Address. The same all-field initializer and decoder follow real encoded
Info/Data paths at depths 1–3. Those tests establish encoding and identity,
**not deeper dynamic execution**.

## Two separate repair statements

**Two local-field faults.** Start with canonical Address, uniform Age and zero
flags/Workspace flags. Change the local structure and four flag inputs at at
most two physical sites arbitrarily. A five-voter majority still has at least
three correct voters. Neither an inconsistency threshold nor a Workspace
threshold of three can be met. Computed Flag1 is zero, including at an erroneous
Flag1 site, since at most one other right Flag1 can be one. Flag2 cannot be born
(threshold four); an old erroneous Flag2 sees at most one other left one and is
erased. Address/Age then recover from the correct right majority.

This proves one-step recovery of Address/Age/Flag1/Flag2 only. It does not recover
arbitrary Data, computation, mail, or persistent external Workspace forcing.
The tests exhaust the eight flag bits on two adjacent faulty sites, sample
Address/Age faults, and compare 512 healthy self/left neighborhoods plus 300
random damaged neighborhoods with the independent shared scalar specification.

**Unforced canonical flags.** Suppose Age is at least 98Q, the geometry is
canonical, Wf1=Wf2=0, and no new forcing/noise occurs. Arbitrary Flag1 clears from
the right boundary by at least two cells per tick: immediately to the left of a
zero suffix, each of the next two sites has at most one flagged right neighbor.
It cannot be born or persist. Thus all Flag1 is zero within Q/2 ticks.

Once Flag1 is zero, Flag2 at a site with at most one in-colony left one must be
zero after one transition, irrespective of its old value. A zero prefix therefore
grows from the left boundary by at least two cells per tick. Cross-colony Flag2
birth is disabled when computed Flag1 is zero. After at most another Q/2 ticks,
all Flag2 is zero. Canonical geometry is invariant because both directional votes
agree. The all-zero flag state then remains zero until the next forcing window.
The bound from a zero-Wf state at 98Q is therefore **99Q**, not a guessed wave
profile or a host replacement of physical evolution.

`repair_b_flag_bound_v1` executes this on the nontrivial 23-colony literal-cutoff
flag data, explicitly reinterpreted as candidate-B initial data. F1 is zero by
Q/2; both flags are zero by Q; exact fixed-point detection then skips to U.
The 251,658,240-tick probe takes **21.712381306104362 s**: 8,388,609 literal ticks,
243,269,631 verified fixed-point ticks and 1,055,652,541 packed-word evaluations.
This probe is not a hierarchical macrostep or evidence of noise robustness.

## Current tests and physical execution

```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python -m unittest discover -s tests/fixed_rule -p 'test_repair_b_*.py' -v
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python -m unittest discover -s tests/fixed_rule -p test_repair_b_recurrent.py -v
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python -m experiments.fixed_rule.repair_b_flag_bound --input figs/fixed_rule/flag_cutoff_checkpoint_v1.npz --output figs/fixed_rule/repair_b_flag_bound_v1
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python -m experiments.fixed_rule.repair_b_execution --output figs/fixed_rule/repair_b_execution_v1
```

The first suite passed **28 tests / 8.575 s** before the recurrent-prefix tests
were added. The latter passed **3 tests / 1.597 s**. They preserve every input
word, admit coherent carried Signal without zeroing it, compare a complete reset
tick against the local rule, check local capture overwrites old Signal, and reject
unsupported Signal patterns. No previously frozen execution dependency was edited.

The actual 23-cell candidate-B prefix completed 805,306,367 physical ticks in
510.10821578931063 s. Its independent audit checked 224 frozen/live source files,
three full-raw gathers, active simulated WRITE, full self-description evaluation,
computed-flag delivery and capture. The suffix then completed the first full
U=1,073,741,824-tick physical period in 63.699842274188995 s. Every Info word
committed to the complete G(top) result, including controller state. Actual
physical flags were zero by 99Q and at commit; the unrepresented padding was
checked against canonical empty state at representative structural addresses.

`repair_b_macrostep_audit_v2.json` passed in 8.099663030356169 s: 225 source files,
728,456 stored-site checks and 1,688 complete native local comparisons, as well as
independent scalar/native/self-description agreement, replay of the controller
quotient, all-field raw votes/Hold/commit and physical flags reconstructed from
whole-ring runs. This audit does not independently rerun the long flag trajectory;
that component uses the separately tested exact packed executor. Its first audit
attempt stopped on a parser variable shadowing the imported program module; the
failed v1 log is preserved and the corrected auditor changes no physical code.

The recurrent executor admits the actual committed physical state and coherent
old Signal directly, without upper re-encoding or residue clearing. The first
recurrent driver retained a stale zero-Signal assertion from the fresh prefix.
That owned CPU run was deliberately stopped, with progress and reason saved in
`repair_b_recurrent_stop_v1.json`. The separately named v2 driver compares against
the actual carried Signal and also saves its entire initial stored state for an
independent handoff audit. Its second prefix completed in **517.4365741014481 s**, and the independent
handoff audit passed 236 sources, byte-for-byte equality of its initial stored
state to the first committed state, carried nonzero Signal, all-raw retrievals,
full evaluation, ten deliveries and capture. Its physical suffix then completed
in **67.40795897878706 s**.

The second complete macrostep audit passed in **8.177978985011578 s**: 728,456
stored-site checks, 1,693 full-native local comparisons, full controller replay,
raw votes/Hold/commit and zero physical flags at commit. The final chain audit
`repair_b_two_periods_audit_v1.json` passed: **two successive complete one-link
macrosteps, 2,147,483,648 physical ticks**, joined by the exact physical stored
state. Both periods change active controller fields, not just the clock. The
first simulated WRITE changes the central Data word from zero to
0x123456789ABCDEF0; the second step changes head/PC/rd/value elsewhere as well as
maintenance fields. Both decoded results equal the scalar, native and complete
self-described G. The rule identity is unchanged across periods and requested
initialization depths. These are canonical noiseless results for candidate B.

Additional commands:
```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python -m experiments.fixed_rule.audit_repair_b_execution --input figs/fixed_rule/repair_b_execution_v1 --output figs/fixed_rule/repair_b_execution_audit_v1.json
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python -m experiments.fixed_rule.repair_b_macrostep --input figs/fixed_rule/repair_b_execution_v1 --output figs/fixed_rule/repair_b_macrostep_v1
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python -m experiments.fixed_rule.audit_repair_b_macrostep --input figs/fixed_rule/repair_b_macrostep_v1 --output figs/fixed_rule/repair_b_macrostep_audit_v2.json
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python -m experiments.fixed_rule.repair_b_recurrent_execution_v2 --input figs/fixed_rule/repair_b_macrostep_v1 --output figs/fixed_rule/repair_b_recurrent_execution_v2
```

Full spatial redundancy/repair, organized finite-depth termination, deeper
dynamics and experimentally measured noise robustness remain missing. The flagged
zero-payload cap is still only a tested orbit. These restricted canonical-domain
results do not establish the final Gács/Gray amplification construction.

## Explicit depth costs

For 23 top cells and the same fixed Q, U, alphabet and ROM at every depth:

| Encoded depth | Physical sites | Dense 25-word bytes | Ticks per top transition |
|---|---:|---:|---:|
| 1 | 192,937,984 | 38,587,596,800 | 1,073,741,824 |
| 2 | 1,618,481,116,086,272 | 323,696,223,217,254,400 | 1,152,921,504,606,846,976 |
| 3 | 13,576,803,638,250,229,989,376 | 2,715,360,727,650,045,997,875,200 | 1,237,940,039,285,380,274,899,124,224 |

`repair_b_resources_v2.json` records these exact values with the current complete
identity and timing certificate. The large savings in the one-link executor use
proved canonical physical-domain compression. An equally inspectable execution
representation for complete deeper dynamics has not been implemented. Initial
configuration queries at depths 2/3 do not establish those dynamics.

Final recurrent checks:
```sh
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python -m experiments.fixed_rule.audit_repair_b_recurrent --input figs/fixed_rule/repair_b_recurrent_execution_v2 --output figs/fixed_rule/repair_b_recurrent_audit_v1.json
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python -m experiments.fixed_rule.repair_b_macrostep --input figs/fixed_rule/repair_b_recurrent_execution_v2 --output figs/fixed_rule/repair_b_recurrent_macrostep_v1
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python -m experiments.fixed_rule.audit_repair_b_macrostep --input figs/fixed_rule/repair_b_recurrent_macrostep_v1 --output figs/fixed_rule/repair_b_recurrent_macrostep_audit_v1.json
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 python -m experiments.fixed_rule.audit_repair_b_chain --output figs/fixed_rule/repair_b_two_periods_audit_v1.json
```
