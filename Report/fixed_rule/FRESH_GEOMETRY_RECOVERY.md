# Geometry restoration after the nine fresh replacement marks

2026-09-27. The fresh damage from [RESIDUAL_REACTIVATION.md](RESIDUAL_REACTIVATION.md)
now has a checked geometry-restoration endpoint: Address is canonical by tick640,
and Flag1 clears at **tick16989**. Uniform Age, zero Flag2 and zero Wf persist.
This is a physical geometry result under the documented projection checks,
**not complete procedure/controller repair**. Full-state literal execution stops
at tick128; the following diagnostic projection does not evolve those fields.

## Literal continuation and the propagating defects

`probe_retimed_holder_fresh_geometry_recovery.py` reloads the actual period-three
endpoint and all nine saved complete replacement records, with their exact times
and sites. It executes both the actual and fault-free complete G trajectories for
128 ticks. The first five complete retained states agree with the independently
scalar-audited preceding experiment. A radius-seven shrinking window contains the
entire possible fault cone; no healthy state is installed into actual evolution.

At tick128 there are six wrong Addresses, 765 Flag1 sites, no Flag2, and no remaining
procedure/Data differences in the complete retained window. Wrong ROM records
are retained because G projects them from the actual wrong Address. The six
Address defects travel in two groups of three, three physical sites rightward
per tick. Flag1 expands behind them. This is not immediate geometry repair.
The run checks **106129408 retained native raw outputs**; its suffix after tick5
has not been independently scalar-checked in every full-state field.

## Why the geometry can be examined independently

The new complete-descriptor certificate uses arbitrary independent physical
Addresses and flags, a common old Age in0..32767, and zero input Wf. All other
raw controller, Data, mail, Signal and metadata words are independent variables
in two otherwise identical geometry inputs. Their four geometry outputs agree;
all ten Wf outputs are zero and Age becomes the common Age+1. This proves closure
of that projection domain through the stated early interval, even when the
untracked computation fields are damaged.

The nine saved marks are separately checked to preserve the common clock and
zero Wf. Consequently this domain applies to the actual early continuation.
`retimed_holder_geometry_projection.py` is an independent NumPy transcription
of physical `core.maintenance`, including candidate-B Flag2 erasure. It is a
diagnostic projection, not a replacement full-state transition kernel and not
an implementation of an upper-layer transition on the host.

The projection evolves one periodic Q-cell geometry ring through tick1024.
Its radius-five influence radius is at most5120, less than Q/2, so copies of the
initial fault island cannot interact. The reference geometry repeats by colony,
allowing this projected window to be identified with the larger ring locally.
This geometry-only radius is justified by the physical maintenance inputs; it
does not replace the radius-seven neighborhood of the full rule.

Every tick checks scalar maintenance at all neighborhood centers around Address
defects and flag boundaries, plus16 reproducibly sampled sites. A total of
136416 scalar geometry words agree. The literal prefix supplies6984 matched
geometry words, including every retained site of its tick128 endpoint.
**Not every vector output is independently scalar-checked.** The complete
descriptor proves independence; the NumPy formula's backend evidence is these
comparisons and the focused random/boundary tests.

| Tick | Wrong Addresses | Flag1 sites | Flag2 sites |
|---|---:|---:|---:|
| 128 | 6 | 765 | 0 |
| 512 | 6 | 3069 | 0 |
| 602 | 6 | 3609 | 0 |
| 603 | 5 | 3614 | 0 |
| 604 | 3 | 3615 | 0 |
| 640 | 0 | 3657 | 0 |
| 1024 | 0 | 4041 | 0 |

The original anchor Address is30960; the right colony boundary is1808 sites
away. The fronts lose their wrong Addresses there. This evidence establishes
canonical Address by640; it does not identify the first canonical tick between
the saved observations605 and640.

## Exact remaining Flag1 recurrence

At tick1024 the Addresses are canonical, Flag2 is zero, and Flag1 is exactly the
interval [27889,31929] in the affected colony. With canonical Address, common
early Age and Wf0, Flag2 remains zero. For any Flag1 configuration, let n be the
number of flagged in-colony sites at offsets1..5 to a cell's right. The printed
candidate recurrence reduces to `new Flag1 = (n>=3) or (old Flag1 and n>=2)`.
This does not depend on the untracked procedure state.

For an interval [l,r] of length at least3, the right-neighbor threshold contributes
[l-3,r-3] and the persistence term contributes [l,r-2]. Their union, clipped at
the colony's left edge, is [max(0,l-3),r-2]. An interval of length1 or2 disappears.
These formulas handle the left boundary explicitly; wrapping the flags into
another colony would be incorrect.

`finish_retimed_holder_geometry_flags.py` executes the exact full-colony bitset
recurrence for15965 more ticks and checks the interval identity at every tick.
Seven complete vector-projection comparisons check688128 geometry words. The
left endpoint reaches zero at tick10321. At16988 only sites0,1 remain flagged;
at **16989** both disappear. Geometry now matches the fault-free trajectory.

## Validation, provenance and limits

Accepted receipts under `figs/fixed_rule/`:

| Receipt | Runtime | Process peak RSS |
|---|---:|---:|
| `retimed_holder_fresh_geometry_recovery_128_v1.json` | 8.801063 s | 86736 KiB |
| `retimed_holder_early_geometry_projection_v1.json` | 1.119248 s | 58292 KiB |
| `retimed_holder_fresh_geometry_projection_v1.json` | 19.420561 s | 73244 KiB |
| `retimed_holder_geometry_flags_v1.json` | 1.099152 s | 56384 KiB |

Nine tests pass in **1.921 s**. They reject computation-to-geometry leakage and
nonzero Wf mutants, compare random geometry against scalar maintenance including
D3 clock phases, check canonical colony boundaries, exhaust all256 eight-bit
Flag1 patterns against scalar maintenance, and test short/boundary intervals.
All watchdogs are terminal exit0 with at most1GiB RAM caps. No GPU allocation,
shared-source change or rule change occurred. Exact commands are in watches.
Final index: `figs/fixed_rule/retimed_holder_fresh_geometry_evidence_v1.json`.

The next obligation is the full procedure state between literal tick128 and the
geometry-restoration interface. Geometry alone cannot certify that a controller,
packet, Data word or encoded Info was repaired or remained correct. A complete
execution or a checked refinement must supply that link before another macrostep
or repeated-fault repair claim is made. The earlier full-ring endpoint relation
also retains its conditional premises. General noise amplification/thresholds,
robust finite caps, depth3, Q/U optimization and Flag2/SimBit source-fidelity gaps
remain open. The full project goal remains active.
