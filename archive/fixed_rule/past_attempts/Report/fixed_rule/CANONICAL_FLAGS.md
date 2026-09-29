# Extending the physical execution domain to nonzero flags

Follow-on: [SIGNAL.md](SIGNAL.md) now implements and tests a separate signal
candidate and short physically generated flag waves. The frozen current-clock
components described below retain their original scope and behavior.

This is prerequisite work for source flag signals/trickle-down, not their
implementation. The current complete clock rule remains unchanged, and the
macrostep executor still rejects nonzero physical flags. The new components
are not used to replace simulated transitions.

## Canonical geometry is invariant with arbitrary flags

Let physical Address be x mod Q and physical Age be uniform t. All adjusted
left/right Address votes equal the center's Address, and all Age votes equal t.
Thus either choice of voting side gives the same Address and Age+1 mod U,
regardless of Flag1/Flag2/Wf1/Wf2. The inconsistency predicate and d3 vanish.
Only the flag equations and the within-colony masks remain. This follows directly
from the printed maintenance equations, not an assumption that flags are zero.

`canonical_flags.py` implements the reduced equations and rejects invalid
geometry. Tests cover 3,328 left-flag/boundary/computed-Flag1 combinations plus
300 arbitrary workspace/flag neighborhoods. They agree with complete maintenance
and the complete clock transition. A witness creates nonzero Flag1 while Address
and Age remain canonical, demonstrating why the old zero-flag shortcut cannot be
reused when signals begin to operate.

`canonical_clock_description.py` describes the **whole clock transition** on this
larger domain, including all controller/data/mail outputs, computed-Flag1 mail
clearing and the Wf time window/reset. It has 1,765 operations. Its native kernel
and word evaluator match complete F on arbitrary raw workspace and flags across
all stage boundaries. It rejects noncanonical local geometry; dense-ring use
additionally requires a whole periodic canonical Address pattern and uniform Age.
This is an exact conditional-domain specialization of the same F, not another
hierarchy-level rule or the complete self-description used by the simulator.
Its exported description is `canonical_clock_description_v1.json`, SHA-256
`2d6fe194fc1600bcfc1be77815ff47c8a75ea51462226f2caa4f38084719e1ed`.

## A closed physical flag projection, and its limits

In the **current** clock rule, four flags form a closed subsystem once geometry
is canonical: flags do not read data/controller/mail, and Wf merely persists or
is cleared by clock conditions. `canonical_flag_world.py` stores the nonzero
four-bit states on a complete Q-site ring. Every step evaluates eleven adjacent
old records at all sites within radius five of the nonzero support. Outside that
set, the all-zero flag neighborhood has zero output for every Address and Age.
This gives an exact sparse physical projection, not a simulation of the omitted
workspace fields. Age is represented through the proved uniform increment.

Every potentially changing output in short randomized/boundary runs is compared
with the complete native clock kernel. The printed isolated Flag2 counterexample
persists. `experiments.fixed_rule.canonical_flag_prefix` records three 256-tick
prefixes on a Q=8,388,608 ring starting at Age 96Q+1:

| Initial flags | Flag1 count at tick 256 | Flag2 count | Local evaluations |
|---|---:|---:|---:|
| Five right-edge Wf1 bits | 773 | 0 | 101,760 |
| Right-edge Wf1 and left-edge Wf2 | 773 | 57 | 110,919 |
| Interior singleton Flag2 | 0 | 1 | 2,816 |

The Wf seeds remain on during this short prefix. The combined case's Flag2
support is [0,56] at tick 256; intermediate profiles are saved at listed sample
times and must not be inferred to be a rigid translating interval. The run took
2.7785717081278563 seconds; it is not a full 2Q trickle window. Sources and sparse
samples are in `canonical_flag_prefix_v1.json`.

These are manually seeded initial flags. There is no signal generator, spatial
redundancy, whole-state recovery or noise law in this experiment. Once Wf reads
signal data, this four-flag subsystem is no longer closed: its representation
must include those dependencies and their local transitions. Mail also responds
to Flag1, so a full physical executor must couple flag and packet evolution.

## Concrete next integration

1. Add preserved signal storage, distinct from workspace that resets in stage
   four. A fixed five-bit packed field can hold five copies without spending five
   full descriptor words; it must still be included in every raw encoding and
   in F's complete description. This protects signals only, not all workspace.
2. Send stage-three computed Flag1/Flag2 toward the source locations Q−3 and 3.
   Selection must use computed Address (Gray p.35); updates of backup copies
   need the same treatment. Padding signal buffers invalidate the present
   zero-data padding representation and require explicit local handling.
3. Implement and distinguish the source's “computed SimBit” alternatives. Voting
   five signal copies can fit the existing radius: the left-boundary target is
   at offset −1..3, with vote holders another ±2. Full neighboring transition
   evaluation can exceed radius five and must not be smuggled into this step.
   Voted-before-clear versus post-transition semantics differ under structural
   damage; the healthy canonical case alone does not resolve D10.
4. Recompile complete F and its fixed P, then measure the added delivery/vote
   budgets. Stage-three evaluation may need to start earlier than 72Q after
   retrieval actually finishes. Sending signal mail during stage five must not
   accidentally cross into a rest; any stage guard belongs in the described
   controller, not a host dispatcher.
5. Couple signal/Wf/flag waves and packet clearing in the physical executor.
   Canonical geometry can be retained with arbitrary flags, but its old
   zero-flag specialization and ballistic-mail assumptions cannot. Keep the
   complete arbitrary-geometry kernel as the reference and reject any unsupported
   physical faults explicitly. Long wave evolution and printed Flag2 behavior
   need measured evidence before full-period robustness claims.

Fivefold protection of data, mail and raw controllers, amplification, organized
termination and deeper dynamic validation remain mandatory after these steps.
