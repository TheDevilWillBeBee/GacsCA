# Compressed-schedule cache initialization: a non-vacuity failure

Updated 2026-09-24. This is an **experimental initialization correction**, not
a change to Gray's printed local rule or to the NumPy/CUDA transition.

## Cause and distinguishing experiment

The compressed schedule interprets upper instructions using a colony-wide cached
upper Address/Age. `compile_register_load(..., source="HOLD")` refreshes the
cache at the **end** of interpretation. Supplying only encoded Info while leaving
the first period's caches zero therefore does not establish a correct initial
simulation relation. An arbitrary zero-cache state is still a legal CA state;
it simply need not simulate the desired first upper transition.

The canonical initialization for this compressed middle layer is

\[
\mathrm{SimAge}(iQ+a)=\mathrm{Age}_{upper}(i),\quad
\mathrm{SimAddr}(iQ+a)=\mathrm{Addr}_{upper}(i),\quad 0\le a<Q.
\]

Raw upper register fields remain part of Info and are not confused with these
cache values. This is a one-time initial encoding, never a host-side replacement
of a running state. The full Gray schedule already loads voted input controls
before interpretation; this finding is not a demonstrated defect in that stage.

The [paired CPU experiment](../experiments/cache_bootstrap.py) evolves both
initializations for all **16,384 middle transitions**, with identical encoded
top state, 11 top cells, seed 1350, R=3, and the unchanged transition rule.
Runtime: 286.50 s.

| Initialization | Controls at evaluation holder | Active BITOP? | Wrong decoded top fields | Wrong top track copies |
|---|---|---|---|---:|
| Zero caches | 0 / 0 | No | none | 8 |
| Input Age/Address caches | 901 / 10 | Yes | none | 0 |

[Exact phase states](../figs/cache_bootstrap_pair_20260923.npz),
[results/hashes](../figs/cache_bootstrap_pair_20260923.json),
[source/backend archive](../figs/cache_bootstrap_pair_20260923_sources.tar.gz).
The dataset retains initial states and middle ages 10691, 10692, 10693, 16382,
16384. This is CPU evidence, not a full physical third-link history.

## Consequences for previous evidence

The 268-million-physical-step one-top-cell run remains a valid match of every
middle transition to the reference. But its top Address is 5, outside the BITOP
interval [8,59), and its entire top raw track array is unchanged by the tested
top transition. That witness did not expose the missing caches. It cannot prove
nontrivial nested computation by itself; instruction-family tests remain separate.

The 11-top-cell continuation was stopped deliberately at its saved **192-period**
prefix. Its [independent audit](../figs/third_link_nonaliased_stopped_audit_20260923.json)
checks 678,656 encoded bits with zero mismatches and zero physical Address/clock
errors. Metadata still says `running`/`sampling`, but both processes were stopped.
No data were removed. Do not resume it as a valid first-top-transition experiment.

The first [phase-targeted fault pilots](nested_phase_faults.md) also used cold
caches. Both completed and recovered the clean cold-cache state, but the intended
BITOP was inactive. They remain negative setup/control experiments, not
active-computation robustness evidence.

## Corrected validation and execution

`cached_initial` supplies the initial caches while preserving every encoded
field/raw copy. The revised phase protocol rejects inactive or value-preserving
targets before physical evolution. For seed 1350, top cell **8**, Address 13,
middle holder **2133** has a clean HOLD bit transition **1→0** at IEVAL index 2,
middle age 10692. This is the corrected fault target.

Full GPU middle periods at **R=3 and R=5**, with 11 top cells, match every top
field/raw copy under initialized caches; the R=3 cold control reproduces eight
errors. The corrected clean driver also passes exact direct/skip/restart parity
and independent decoding: [three tests, 17.36 s](../figs/initialized_third_link_tests_20260924.xml).
The revised phase tools pass [eight focused tests](../figs/nested_phase_cached_tests_20260924.xml)
in 23.44 s. These do not replace a full regression of the core, which was unchanged.
The final combined tools pass [11 tests in 52.84 s](../figs/cache_and_phase_verified_tests_20260924.xml),
including the extended two-stage rollover audit.

The historical clean driver is frozen. Use the separately versioned
[initialized-cache driver](../experiments/third_link_initialized.py) for new runs:

```bash
python -m experiments.third_link_initialized --output figs/new_initialized_run \
  --certified-skip --stop-after 16 --checkpoint-every 4
python -m experiments.third_link_initialized --output figs/new_initialized_run \
  --certified-skip --resume
```

The default is 11 top cells; 64 gives a whole top colony. Run identity records
`cache_initialization=input_age_address` and archives the initializer. Physical
evolution remains autonomous; every decoded middle transition is checked.
The corrected full physical middle period remains to be completed.

The [source/audit/plot bundle](../figs/cache_phase_sources_20260924.tar.gz) has
63 verified members, SHA-256
`4c1641976a57751d3e47711f2fb4cb048e0a5a37c61b001cae97a10c22b3e8b7`.
Its [manifest](../figs/cache_phase_sources_20260924.json) also records 18 immutable
external data hashes and verifies that all 22 core/backend files are unchanged
from the earlier 340-test archive. The mutable long-run checkpoint is excluded.
