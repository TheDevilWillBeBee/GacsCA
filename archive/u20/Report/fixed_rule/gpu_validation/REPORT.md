# Continuous dense GPU validation of the U20 fixed-rule candidate

## Physical object and encoding

The only simulated physical transition here is
`gacsca.fixed_rule.stream28_dual_pass20.local_step`. It has radius seven,
Q=8192, U=1048576, 6465 bits/cell and 421 typed raw words/cell. The holder
has 154 words: 49 static metadata words, 90 fivefold procedure words, ten
fivefold Wf words, and five geometry words. The spatial evaluator has 267
words: 253 static circuit/route words and 14 evolving words. Thus the 119
evolving projected words match the Info/Hold bank length. The complete own-F
WordCode has 14830 operations and SHA-256
`16bf88a1d4ff5496cd3b61a1200f8a809db1438472a9191fded26de3a0786257`.

`initial.initialize()` creates a closed physical lower ring of N×8192 sites.
Every physical site has canonical Address and holder/spatial ROM. The Info and
Hold banks of colony j both carry the 119-word projection of represented
upper cell j. All five procedure Data copies at physical site x initially
equal the primary Data at x−2,…,x+2, including the periodic lower wrap. The
390 used static own-rule inputs are derived from the represented upper
Address and placed in the candidate's physical SOURCE Data sites. No upper
oracle runs in the physical transition.

The represented upper segment has varied 64-bit Data with synchronized
upper Age zero, zero Flags/controller/mail and canonical local static ROM.
Because it contains 31 cells rather than all 8192 upper addresses, its
periodic upper seam joins Address 30 to Address 0; that seam is not a clean
upper Address edge. A center needs 2×7k+1 upper colonies for k decoded
radius-seven macrosteps: 15 for one, 29 for two. The 31-colony ring provides
one central site with two complete upper causal cones away from the seam.
Claims about global clean upper-ring self-simulation would require an 8192
colony lower ring, which the current raw double buffer cannot fit in 80 GiB.

## Schedule and diagnostics

The three gather resets are at ages 0, 131072 and 262144, with last audited
arrivals at 65515, 196586 and 327657. Early vote is age 393216, capture
393217, evaluator start 393218, last output 438343 and stop 458754. The
holder SEND witness halts at 630680, its last packet arrives 630685, and
stage-three activity ends 647168. Signal capture is 655360; Wf occupies
688128–704512. Final reset/capture/run are 720896/720897/720898, the last
output arrives 766023, and the evaluator stops 786434. The Info commit is
the transition from old age U−1 to age zero. Checkpoints bracket these
ages and repeat in the second period.

At every read-only checkpoint the runner records a SHA-256 of all 421 words
at every physical site, a SHA-256 of all decoded Info words, selected complete
raw cells, counts of Flags/heads/mail, measured kernel and readback seconds,
and peak host RSS. It checks physical Age, Address, and all 302 static fields
against their initial values, retains predicted Info through the work period,
compares all 761 gathered history words in the central colony with the
independently projected upper state at each gather completion,
and compares complete 119-word Hold/Info states with the independent Python
upper local F at work boundaries for upper sites whose causal cones avoid
the seam. It checks the central evaluator capture against the separately
encoded 8192-site circuit entry. Consecutive checkpoint pairs additionally
compare selected complete 421-word local successors with the literal Python
physical F. On the first failure, it writes a full raw `.npy` state and the
field/age/site to the receipt before stopping.

The CUDA backend is a copied execution wrapper compiled only inside
`figs/fixed_rule/gpu_validation/build/`. It stages the fixed 1151 input raw
words actually used by the compiled F but stores all 421 output words, with
two complete GPU state buffers and no upper callback, depth parameter, or
event skip. The rule description, kernel and physical alphabet are identical
at every tick and represented depth. The host only initializes, calls
`fr_run` for the exact number of ticks between checkpoints, and reads state.
The v3 source SHA-256 values are: backend Python
`ce0f22dab9cc94facc728f3025daadacf15696ac35056caf8c2c1d843f333fb2`,
backend CUDA
`65365a4a302b05c2f66a2dfea3449432dbba3ddf97f0568d11f388aaf1c0c73e`,
initializer
`e9cbd52d0ace6ac518197b57ea5f7c449f26d171f952db5629eea10641ef8b85`,
and runner
`1346a93d26325092f82d0b2b98f52e063d80cfa1e2ebc2c9380f9159cbcf621b`.
The isolated CUDA binary SHA-256 is
`7a099f91fb6bd25c53eb8bcbbff5e61c3a1cf0896b58e559fd4399305789e0b1`.

## Executed checks to date

`python -m unittest -q tests.fixed_rule.gpu_validation.test_dense` passed five
tests in 12.174 seconds. They compare every raw output word on arbitrary
typed 17-cell rings for two ticks against the independent WordCode evaluator;
reject radius-eight dependence; compare initialized lower-ring boundary
sites with Python physical F; and check complete packet-wrap raw parity and
fivefold packet data. The Python dataclass rejects some width-valid route
slot values, so the arbitrary typed oracle is WordCode, while valid physical
fixtures use the Python local transition. This distinction is a test-domain
issue and did not reveal a GPU discrepancy.
`python -m unittest -q tests.fixed_rule.gpu_validation.test_initial` passed
two CPU tests in 9.359 seconds, checking all 390 static SOURCE words in each
of 15 colonies, every Info/Hold word, all fivefold Data copies through the
periodic lower wrap, and the 15/29-colony causal-cone bounds.

A 15-colony three-tick pilot passed. Its initial full-state SHA-256 was
`669107963c8ac7013f6c3ca27f4e4630bf6e5b99b5ba7b05651486c3f1087525`.
A 31-colony initialized 1000-tick pilot passed; its initial full-state
SHA-256 was
`ad67a932651da9446e9ccc5089bfd1708ee6b4e141fe2bc15e9e95aeae3ecfeb`
and tick-1000 SHA-256 was
`e466b539efb253af730d15a46fa69ecb363b6dac3fa2553922ae5a38d875b9f9`.
The 997-tick uninterrupted segment measured 14.006 seconds (14.048 ms/tick).
The total 31-colony pilot was 60.699 seconds including initialization and
five complete readbacks. Explicit GPU allocation was 4,751,491,072 bytes;
peak host RSS was 3,978,144 KiB. Its longest readback was 3.555 seconds.
The earlier 14.037 ms/tick active-evaluator fixture agrees with this rate,
but neither pilot is a work-period result.

A two-U run started at 15:09 UTC on 2026-09-29 and **failed at its first
gather checkpoint**, before one U period. Its receipt is
`figs/fixed_rule/gpu_validation/receipts/dense31_2u_v3.json`; full raw
states at ticks 0 and 65,515 are preserved beside it. The preceding v1 and
v2 attempts were stopped by this agent early to strengthen the checks; their
partial receipts are retained. The uninterrupted segment from tick 3 to
65,514 took 918.2 seconds, 14.016 ms/tick. At tick 65,515 the central
colony's stage-zero history site 14 held 14 instead of upper Address 8.
Across all 31 colonies that site held each immediate-left upper Address,
not the requested seven-left Address.
The tick-65,514 full-state SHA-256 was
`4fb975d5867f033a3247a57dce50276ff307db98839df1c9b22307a3b51977af`;
the saved divergent tick-65,515 raw state SHA-256 is
`5648e6141b874f4bcea0857d1ffe9debedf061bc7b7cc7f63aa3bab59baa3148`.
The attempt lasted 957.592 seconds, with peak host RSS 4,019,772 KiB.

The focused trace moved the first divergence back to the **emission at old
age 2,392**, physical site 2,491, raw field 101 (`s2_rp_remaining`). The
literal Python `local_step` emits count 7, but the existing optimized WordCode
and CUDA kernel emit 1. All other 420 output words matched on that transition.
In `stream28_dual_core_clock_description20.py`, the builder computes
`band(selected, abs(offset))` with Boolean `selected`, which turns every odd
long-range count into one and every even one into zero. The CUDA kernel
faithfully executes this wrong WordCode. This is a **compiled-description
parity defect**, not a CUDA arithmetic defect. The event-composed gather
audits had evaluated literal `_clock_step` at endpoints and skipped packet
flight; they did not validate this compiled all-fields path.

The isolated successor replaces that expression with a select of the full
hop count. The same Python physical F, 421-word alphabet, radius and U are
retained. Its 14,830-operation WordCode digest is
`232fa6b96f3e2887975337ff52564e54d3a2f7fc59cbf59580e2adf8e1429f88`.
It matches literal F on all fifteen gather offsets and on the first failing
emission; corrected CUDA matches all 421 words there. The corrected circuit
still fits the existing 8Q layout: 14,851 gate instances, 25,912 operand
packets and latest gate completion 39,517, within 65,536 ticks. Its own-rule
ROM must use the corrected program; `run_corrected.py` compiles that ROM as
initial data in a process-local context, without changing any physical tick.
Four corrected tests passed in 46.845 seconds. A three-tick corrected-ROM
pilot passed with initial state SHA-256
`ea9528306dad99f14cc102392b49637cb5a929f1a45f70e0d63e6ef706320f1e`.
The corrected backend Python SHA-256 is
`c886753a315e8c97c25fa1f279efe8318eca98bc7dce428476d316d194189ece`;
its CUDA source SHA-256 is unchanged because only the generated description
changed. The corrected compiled binary SHA-256 is
`3531ee71e916f67a71f7898da166b5c2925f5c973f640b79d51e3ce005772ce1`.
The bounded corrected first-gather run **passed** 65,516 uninterrupted
physical ticks in 517.246 seconds. At both ticks 65,515 and 65,516 all 761
central stage-zero history words matched independent upper inputs. The
65,511-tick main segment took 509.44 seconds (7.776 ms/tick); explicit device
allocation was 3,868,590,080 bytes and peak host RSS 2,049,036 KiB. Its
tick-65,515 full-state SHA-256 was
`dc18ac7e322a8fc03c0768f07a5448bcc8d703cb27955911dd9829b075b69ee1`.
See the full read-only checkpoints in
`figs/fixed_rule/gpu_validation/receipts/corrected_gather15_v1.json`.
No full U or successive decoded macrostep has yet been established.

## Scientific interpretation

Gray pp. 31–34 permits specialized hard-wiring and Address projection of
ProgramBit; Gács §§9.2–9.3 formulates encoded retrieval, evaluation and
update. Neither source makes the present candidate's dynamic ROM closure,
finite tower, repair, or noise robustness automatic. The historical Flag2
persistence counterexample and computed-SimBit timing question remain
source-fidelity caveats. Raw CUDA parity establishes executor fidelity on
tested inputs; a decoded clean work cycle would establish only that specific
clean physical trajectory. A divergence in a matched Python/CUDA local step
would be an executor defect. A divergence in decoded upper state with raw
local parity intact would be a construction or initialization defect, to be
traced to its first physical field and age.
