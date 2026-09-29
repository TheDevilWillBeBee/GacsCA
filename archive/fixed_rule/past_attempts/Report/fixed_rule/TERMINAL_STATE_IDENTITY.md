# Complete terminal state and endpoint composition

2026-09-27. The unchanged retimed candidate now has two independent diagnostic
formulas for every terminal Data word, full physical reconstruction, a finite
layout certificate, and fresh GPU endpoint comparisons. This strengthens the
existing noiseless simulation argument to an exact endpoint identity on a stated
entry domain. It supplies a possible route around U^2 temporal replay. No new
macrostep executor or complete depth-two execution is claimed.

## Fixed construction and domain

The physical rule remains G=pi F iota, with Q=32768, U=2^31, radius seven,
105 mutable words/2704 bits, and 154 lifted words/4090 bits. Its full controller,
communication and evaluator transition are included in F. Neither formula has a
depth parameter. No physical rule, ROM, existing CPU/CUDA backend or shared file
changed. Descriptor and ROM hashes remain those in
[RETIMED_NOISELESS_MACROSTEP.md](RETIMED_NOISELESS_MACROSTEP.md).

The source interpretation remains Gray pp. 31–32's specialized hard-wiring after
ProgramBit projection and Gacs sections 9.2–9.3's suitably modified self-correcting
rule. This work does not remove the candidate-B Flag2, voted-old-Signal D10,
printed Flag2 persistence or SimBit timing qualifications. It does not establish
the papers' correction/amplification hypotheses. U<=128Q is not imposed.

Let E_loc(y) restrict the existing raw entry relation E(y): lower geometry is
canonical with uniform Age zero; procedures are coherent; controller, mail,
flags and Wf are zero; Info contains every raw field of iota(y); non-MEM Data
is zero. Other MEM and tail Data are arbitrary. Signals are confined to the two
five-holder groups. With left/right bits l,r, their complete physical words are
l<<(5-a) at addresses a=1..5 and r<<(Q-1-a) at a=Q-5..Q-1, zero elsewhere.
The bits may differ by colony. Upper y is any typed configuration, including
noncanonical geometry, high-bit Age and every raw controller/transport field.
No faults occur during the period. Arbitrary Signals outside these groups are
allowed by the earlier simulation relation, but are outside this exact-image
claim because their old values can persist.

## Complete terminal Data formula

For each colony, the new formula accounts for all 9916 bank words:

| Category | Words | Value just before commit |
|---|---:|---|
| Three neighbor histories | 6930 | Three complete copies of iota(y[-7..7]) |
| Voted inputs | 2310 | The same complete neighborhood |
| Info | 154 | iota(y[0]) |
| Hold | 154 | iota(G(y)[0]) |
| Reused result slots | 349 | Last SSA value assigned to each physical slot |
| Query workspace | 6 | Final actual metadata-query residue |
| Reserved | 8 | Zero |
| Tail buffers | 5 | Zero |

The 10450-operation optimized DAG retains its actual allocation, so result
scratch is not replaced by fresh zero memory. If a' is the new represented
Address and z=(a'+3) mod Q, the six query words are
(3,Q-1,~z mod 2^64,0,0,z). All 49 Hold metadata words are regenerated from the
same ROM at a'+offset. The fixed final instruction stream has 10733 instructions.
At commit only Info is replaced by its adjacent Hold.

`retimed_holder_terminal_reference.py` diagnostically replays that fixed final
instruction stream, including LOAD/META. Independently,
`retimed_holder_terminal_dag.py` uses DAG last writers and explicit query residue.
Neither function evolves a physical world or installs its answer into one.
`retimed_holder_terminal_image.py` reconstructs every projected physical field
from a bank, canonical geometry, zero controllers/mail/flags/Wf, and all Signal
replicas. Its coherent procedure copies read adjacent logical records, including
across colony boundaries. Static metadata is derived by iota as usual.

## Exact endpoint identity at descriptor semantics

Write C(y) for the complete precommit image at Age U-1, and B(y) for its complete
committed image at Age zero. Signals in both are the localized patterns with
l=G(y).f2 and r=G(y).f1. Together with the existing instruction, timed-memory,
packet, query and whole-period lemmas:

    G^(U-1)(E_loc(y)) = {C(y)}
    G^U(E_loc(y))     = {B(y)}
    G(C(y))          = B(y)
    B(y) belongs to E_loc(G(y)).

These are mathematical descriptor-semantics claims, conditional on the semantic
lemmas already recorded in RETIMED_NOISELESS_MACROSTEP.md. They are not a
proof-assistant result or a universal equivalence theorem for every backend.
The additional reasoning is:

1. First reset removes arbitrary scratch. Gather induction fixes all three
   histories to the normalized complete neighborhood. The earlier timed-memory
   and packet lemmas establish these as actual physical values.
2. First evaluation computes the complete output and delivers both Signal
   groups before capture. Capture establishes all five copies. These patterns
   are fixed points of later Signal voting. Existing flag clearing gives zero
   flags/Wf before the last evaluation.
3. The late resets preserve histories and Info, clear other scratch, and the
   last vote restores the common neighborhood inputs. The certificate partitions
   every MEM address and checks the actual masks, including vote-over-reset
   priority supplied by the earlier clock lemma. No omitted memory survives.
4. Existing instruction/query refinement identifies every final write. The
   certificate rebuilds the exact final instruction stream, checks all raw
   outputs and all metadata queries, and checks the actual last-writer allocation.
   This yields the complete bank formula, including scratch and query residue.
5. Final HALT consumes all controller/mail state. Quiet evolution preserves the
   bank and localized Signals until U-1. Commit changes only Info and the clock;
   coherent physical reconstruction gives the stated images and restored domain.

No equality of decoded outputs is substituted for physical equality. In the
saved repair fixture, healthy and damaged parents have the same next decoded
state but **120 different terminal bank words**; both formulas retain them.

## Consequence for finite encoded depth

Define J_0(y)={y} and J_d(y)=union over z in J_(d-1)(y) of E_loc(z).
These are initial-state relations, not depth-dependent transition rules. For
every finite d>=1 on the corresponding periodic rings, the identities imply

    G^(U^d-1)(J_d(y)) = {C^d(y)}
    G^(U^d)(J_d(y))   = {B(C^(d-1)(y))}.

Here composition expands the configuration by Q each time. Proof: at the start
of the last lower work period, repeated one-link simulation puts the state in
E_loc(G^(U^(d-1)-1)(z)) for its initial upper z. The induction hypothesis makes
that represented precommit state C^(d-1)(y). Apply the complete one-period
precommit identity to obtain C^d(y), then one literal G tick gives the committed
image. The d=1 case is the preceding identity. The restored nested entry relation
also permits successive top periods; replace y with G^(m-1)(y) for endpoint m.

In particular, an exact depth-two endpoint is B(C(y)), not a fresh encoding of
G(y). This is a consequence of the complete-state identity, not an executed
nested GPU trajectory. It does not cover faults during a skipped interval or
provide intermediate-time states. A backend must validate its domain, retain the
complete image and use one fixed implementation on encoded data. Host-side
simulated transitions remain prohibited. A GPU realization of these operators,
with separately checked reconstruction and composition, is the next step.

The lower terminal bank for depth two with one top cell alone occupies
32768*9916*8 = 2599419904 bytes (about 2.42 GiB); this excludes other workspace.
A fully materialized projected input row array for that operator is 26.25 MiB.
These are proposed representation costs, not allocations or runtime results.
The prior 7.18 GiB resident-backend estimate describes a different implementation.
The 40 GB host-RAM allowance from the user is now the ceiling; these probes kept
their much smaller existing limits. Large GPU scheduling remains coordinated.

## Executed evidence and failures retained

Fresh n=15 GPU run: two full work periods, 4294967296 physical ticks, with random
values in every typed upper field and every initial MEM/tail scratch word except
valid Info. All initial localized Signal copies are supplied. One physical state
is retained throughout. Host evaluator/local-step/formula calls are blocked while
GPU evolution runs. Both independent formulas and scalar complete G outputs are
computed only outside evolution as diagnostics; no answer is installed.

At each U-1 and U endpoint, all 148740 bank words, every live 25-field logical
record, all flags and distributed Signals match. Canonical coherent reconstruction
then specifies all 491520 physical cells including every raw controller field.
The represented states change 1272 then 412 mutable words. This random-geometry
fixture mainly tests broad typed inputs; active coherent upper computation and
operand repair retain their earlier separate evidence.

| Check | Result | Seconds | Host peak KiB |
|---|---|---:|---:|
| Structural certificate | All memory categories/writers/outputs covered | 0.953328 | 60876 |
| Old saved GPU states | Seven bank comparisons; 120-word rejection witness | 1.767682 | 69764 |
| Fresh GPU evolution | Two periods, four complete endpoints | 43.350940 | 193424 reported |
| Full experiment | Pass | 46.294618 | 198252 sampled by watchdog |
| Independent saved-state audit | Four endpoints pass | 2.144950 | 72644 |
| Formula/layout/snapshot tests | Ten pass | 4.922 | 512 MiB VM cap |
| Complete-image/literal-commit tests | Two pass | 2.545 | 512 MiB VM cap |

Conservative explicit GPU bound: 6406062 bytes. Watchdog: 60 seconds, sampled
512 MiB host RSS. No new CUDA build was needed. All jobs are terminal.

Preserved failures: initial CPU test v1 imported the active fixture from the
wrong module (six other tests passed); corrected v2 passes seven. Initial GPU
v1 passed bank checks but its new checker omitted noncentral Signal replicas.
It failed at the first precommit check, in 20.639012 seconds /190052 KiB sampled
RSS. The initialization also supplied only central bits. Both source versions
and failed logs remain; corrected v2 initializes/checks all copies and changes no
physical rule or backend. New literal tests check the distributed Signal motif
against G for all four left/right patterns. Mutations reject changed scratch,
hidden controller state, dropped Signal replicas/rows, wrong flags, missing raw
outputs and wrong allocation destinations.

Reproduce from the repo root (CPU commands use `ulimit -v 524288` and
`OPENBLAS_NUM_THREADS=1`; the CUDA runtime must not inherit a VM limit):

```
python -m experiments.fixed_rule.certify_retimed_holder_terminal_layout --output figs/fixed_rule/retimed_holder_terminal_layout_v1.json
python -m experiments.fixed_rule.audit_retimed_holder_terminal_reference --output figs/fixed_rule/retimed_holder_terminal_reference_v1.json
python -m unittest discover -s tests/fixed_rule -p 'test_retimed_holder_terminal*.py' -v
python -m experiments.fixed_rule.bounded_cuda_probe --output figs/fixed_rule/retimed_holder_cuda_terminal_watch_v2.json --seconds 60 --rss-mib 512 -- python -m experiments.fixed_rule.retimed_holder_cuda_terminal --output figs/fixed_rule/retimed_holder_cuda_terminal_v2.json
python -m experiments.fixed_rule.audit_retimed_holder_cuda_terminal --reference figs/fixed_rule/retimed_holder_cuda_terminal_v2.json --output figs/fixed_rule/retimed_holder_cuda_terminal_audit_v1.json
```

Use fresh output names: experiments reject overwriting evidence. The reported ten
and two test groups were run separately. Evidence index:
`figs/fixed_rule/retimed_holder_terminal_evidence_v1.json`.

The overall goal remains active. Practical depth-two execution, general noise
correction across levels, malformed Info repair and reliable finite caps remain
open. The next implementation should realize the complete image operator on GPU,
validate it against these four actual endpoints and the 120-word witness, then
address domain-checked depth composition without a depth-specific kernel.
