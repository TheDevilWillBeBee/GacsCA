# Compact complete-state endpoints and executed depth two

2026-09-27. Two complete noiseless depth-two endpoints now execute for the
unchanged compact16 candidate. Every lower bank word is retained and independently
recomputed. This uses a conditional complete-state identity, not literal U^2
replay. General in-period defects, cross-level stochastic correction and the full
Gacs/Gray objective remain open.

## Fixed construction and exact domain

Q16384, U2^30, radius7, physical154words/4090bits, projected105words/2704bits.
Physical descriptor53f7adbf7c34df6b17897b20a0d0654108f23a9c064defb89bb3c6d1a7fb846b;
own ROM4d055889959a880f189539dc213801780f8e2efa3daa7cb31e72cb3003f48b32.
These and the prior775-file evidence are unchanged. The GPU endpoint and tiled
operators use one fixed final instruction stream, complete raw input and static
own-ROM tables. There is no hierarchy-depth argument or evolving host evaluator.
The experiments select initial encoded depth; they do not change the physical
rule, evaluator alphabet, register set, ROM or neighborhood.

The interpretation remains Gray31–32's specialized hard-wiring after ProgramBit
projection and Gacs9.2–9.3's suitably modified self-correcting rule. The original
paper correction/amplification machinery is not established by noiseless endpoint
composition. U<=128Q is not imposed. All Flag2/SimBit qualifications remain.

Define E_loc(y) by the [compact entry relation](COMPACT16_NOISELESS_MACROSTEP.md)
with canonical uniform lower Age0, coherent procedures, valid complete raw Info
iota(y), zero controllers/mail/flags/Wf and zero non-MEM Data. MEM/tail scratch is
arbitrary. Signals have the localized shifted patterns: l<<(5-a) at1..5 and
r<<(Q-1-a) atQ-5..Q-1, zero elsewhere; l,r may vary by colony. Upper y is any typed
projected configuration, including active controllers and noncanonical geometry.
There are no faults during an accelerated period. Arbitrary persistent Signals
outside these groups belong to the wider entry relation but not this exact image.

## Complete terminal identity

The new layout certificate partitions all3447 MEM words and checks every actual
final instruction, reset mask, vote location and allocation destination:

| Category | Words | Terminal value before commit |
|---|---:|---|
| Histories |2067|Three copies of689 actually gathered input operands|
| Votes |689|Same gathered operands|
| Info |154|Complete old iota(y)|
| Hold |154|Complete iota(G(y))|
| Regenerated input metadata |49|Own ROM at old Address+offset, moduloQ|
| Reused results |320|Actual last SSA writer for each physical slot|
| Query workspace |6|(3,Q-1,~z,0,0,z), z=(newAddress+3) modQ|
| Reserved |8|All zero except MASK_ADDRESS6=2^64-1|
| Tail buffers |5|Zero|

The final10821 instructions include98 metadata lookups:49 input and49 output.
Both zero-offset and nonzero-offset queries fold the15-bit raw Address intoQ's
14-bit range. This differs from the older retimed dense-history formula; that
formula was not transferred unchanged. A diagnostic instruction replay and an
independent DAG/last-writer expression agree on all words, and on four previously
executed GPU period boundaries, including the31-cell active fixture.

Write C(y) for this complete image atAgeU-1, B(y) for the same image after copying
Hold to Info at commit. Both retain localized Signals l=G(y).f2,r=G(y).f1.
The sealed compact clock/path/mail/query/period lemmas plus these last-writer
obligations give, at descriptor semantics:

    G^(U-1)(E_loc(y)) = {C(y)}
    G^U(E_loc(y))     = {B(y)}
    G(C(y))          = B(y),   B(y) in E_loc(G(y)).

Reason: first reset erases all arbitrary scratch. Actual gathering fixes histories;
late resets preserve histories/Info, clear other scratch and vote from the common
histories. Input metadata is regenerated from the voted Address. The final
instruction stream determines every remaining writer, including mask/query
residue. Earlier capture fixes Signals; flags clear before final computation.
Final halt removes controllers/mail, quiet evolution preserves the complete image,
and one literal commit changes only Info/clock. No memory category is discarded.
This is certificate-assisted mathematical reasoning, not a proof-assistant result
or a general CUDA equivalence theorem.

Define J_0(y)={y}, J_d(y)=union over z in J_(d-1)(y) of E_loc(z). The same induction
as [the retained-state argument](TERMINAL_STATE_IDENTITY.md), now with the compact
lemmas and layout, gives for every finite d:

    G^(U^d-1)(J_d(y)) = {C^d(y)}
    G^(U^d)(J_d(y))   = {B(C^(d-1)(y))}.

At the start of the final lower period its represented state is C^(d-1)(y);
apply the complete one-period identity and then literal commit. Restored nested
entry gives successive top periods with y replaced by G^(m-1)(y). Depth is encoded
in the initial relation, not a rule branch. In particular depth-two output is
B(C(y)), not fresh encoding of G(y). A single s0_value-bit defect in the active
31-cell fixture is corrected in decoded output but leaves28 different terminal
bank words. CPU and GPU formulas retain all28; fresh re-encoding is rejected.

## Executions and validation

Fresh3-colony run starts with random typed raw upper fields, random MEM/tail
scratch and localized Signals. Two physical periods are run without replacing
state. At both U-1 and U, every bank word, raw controller/mail/Signal record and
flag agrees with the independent formula and new GPU endpoint operator. Physical
evolution22.927559s; four endpoint calls0.013243s; explicit buffer bound3848426bytes.
The build took4.621690s. Watchdog28.951972s/169264KiB, exit0. These are fixed coherent
trajectories, not arbitrary noisy evolution.

The tiled implementation extracts the same GPU terminal body and changes only
its input access to full seven-cell halos. Raw and complete-image inputs use a
fixed accessor. Device-only decode collects actual output Info; incomplete sinks,
bad raw widths/metadata and partial-image freezing reject. Host F/G/evaluator and
diagnostic image/formula routines are forbidden during evolution.

Depth-two experiment: one periodic random typed top cell, Q^2=268435456 physical
sites, two successive endpoints representing2U^2=2305843009213693952 ticks.
Initial bottom Info is materialized completely. Every output bottom MEM/tail word
and Signal is saved; subsequent top input is decoded from actual GPU output.
Top raw words change77 then1. This aliased top fixture does not establish sustained
top arithmetic or an arbitrary-size healthy top ring; the separate31-cell
one-link active trajectory remains its own evidence.

| Measurement | Result |
|---|---:|
| GPU calls across both nested endpoints |2.696662s|
| Entire run including transfer/storage/hashing |11.176365s|
| Explicit device buffer peak |25220232bytes|
| Sampled child host RSS |610580KiB|
| Retained lower bank words per endpoint |56557568|
| Retained bank bytes per endpoint |452460544|
| Complete intermediate raw words checked per endpoint |2523136|

Two independent audits pass. The first checks complete initialization, all
intermediate/top raw fields, bank integrity and28 selected complete scratch rows.
The second vectorizes the SSA semantics without allocation reuse, and recomputes
**all113115136 saved bank words** plus every Signal across both endpoints.
It uses batches of512 rows; unused descriptor inputs are never read, and all
actual raw Info remains in the physical banks. Watchdog18.211468s/602056KiB.
This exhaustive endpoint recomputation still is not an independent U^2 trace.

Thirteen tests PASS:5terminal/layout/image tests(4.674s),2GPU endpoint tests
(2.106s),6tiled/halo/decode tests(8.097s). They reject changed mask literals,
omitted controller writes, wrong allocation, erased scratch, malformed typed
fields/own-ROM metadata, incomplete output collection and invalid budgets.
Literal complete native F commit is checked at317 selected physical sites.
All new checks pass; no failed approach was discarded in this milestone.

## Reproduction, ownership and next work

All new files are within fixed_rule namespaces. Implementation modules:
compact16_holder_terminal_reference/dag/checks/image, endpoint_gpu(.py/.cu),
endpoint_tiles(.py/.cu), endpoint_image_array. Experiments:
certify_compact16_holder_terminal_layout, audit_compact16_holder_terminal,
validate_compact16_holder_endpoint, run_compact16_holder_streamed_depth2,
audit_compact16_holder_streamed_depth2, audit_compact16_holder_all_scratch,
seal_compact16_holder_endpoints. Tests are the three compact terminal/endpoint
modules. Existing physical/CPU/CUDA code and prior evidence remain unchanged.

Use fresh output names. Commands are `python -m experiments.fixed_rule.NAME`
with `--output OUT.json`; layout/audit use the matching names above. Endpoint
validation is90s/768MiB. Streamed run is90s/1024MiB. Both streamed audits also take
`--reference figs/fixed_rule/compact16_holder_streamed_depth2_v1.json`;
their watchdogs are90s/1024MiB and90s/1536MiB respectively. All watchdogs use
`experiments.fixed_rule.bounded_cuda_probe --output WATCH.json --seconds LIMIT
--rss-mib RSS -- COMMAND`. CPU tests run `python -m unittest
tests.fixed_rule.test_compact16_holder_terminal -v`; GPU tests require
`FIXED_RULE_GPU_TESTS=1` and modules test_compact16_holder_endpoint_gpu and
test_compact16_holder_endpoint_tiles. Their limits are90s/512MiB,
60s/512MiB and90s/768MiB respectively.

Only small GPU probes ran, each below64MiB explicit buffers. Context/graph/runtime
allocations are excluded from these bounds. No total GPU process peak is claimed.
Host use stayed far below40GB, including overlapping audits. Main agent retains
substantial GPU scheduling; the8GiB request is stillunused. No shared job/build/
source/data was changed. MAIN_AGENT_NOTES.md remains its unedited reply channel.
Evidence seal: compact16_holder_endpoints_evidence_v1.json.

Next: compact physical encoded-controller defects and in-period repair, negative
controls and complete-state rejoin before any endpoint skip. Then broader top
rings, sustained depth-two top arithmetic and noise across levels. Arbitrary
faults inside skipped intervals, general full-alphabet correction/amplification,
malformed encoding/geometry repair, reliable finite caps, depth3 and source-fidelity
qualifications remain unresolved. The project goal stays active.
