# GBP1 / GBP1R: complete emission, and an exact selected clean-period failure

This is an isolated construction diagnostic. It leaves G17, every accepted
checkpoint, and the main Gray report unchanged. Its baseline is
`Q=8192`, `U=128Q=1048576`, `lambda=24`, and integer separation constant
`c=104`. No shorter period is asserted. The physical fault history in the
proved counterexample below is empty. It is a counterexample to the stated
noiseless encoding identity for **GBP1R**, not to Gray, Gács, an intact
recursive hierarchy, or a positive-noise-rate memory theorem.

The concrete resource failures are useful because this emitter includes the
interpreter's own fields and transition. It does not use a whole-rule or host
CPU evaluation instruction. They remain specific to this representation and
emission; they are not lower bounds for all possible evaluators.

## 1. Primary target and departures

Gray's [primary text](../../../../papers_txt/gray_readers_guide.txt), printed
pp.15, 30–35, imposes `Q>=2^13`, sets `U=128Q`, and explains self-simulation
through a programme of at most Q bits and a physical interpreter. The later
fit/runtime conclusions explicitly require Q sufficiently large; the constants
in the logarithmic programme bound and last-stage bound are unspecified.
Consequently his displayed Q lower bound alone is not a concrete programme-fit
certificate at Q8192. Proposition 3 is the relevant self-simulation existence
claim. The fifth-stage description on p.34 has an 8Q active half and an 8Q
rest half; its quoted asymptotic last-stage estimate does not certify this
interpreter. Gács's §§7.3–7.4 are a different programme/interpreter construction.

The diagnostic deliberately changes these interfaces:

* The all-raw final computed SimBit source equation is retained. Its literal
  composition needs radius8 and seventeen gathered input lanes rather than
  the printed radius5/eleven lanes. The already accepted
  [GI0 obstruction](../unregistered_gi0/GI0_TOTAL_SOURCE_INTERFACE.md) explains
  this choice; it is not a new impossibility theorem about Gray.
* The native operator is the existing corrected-h1 scalar operator. The printed
  healthy Flag2-erasure predicate is not used.
* A fixed immutable CODE lookup replaces mutable ProgramBits and the physical
  hardwirer. **GBP1R counts all 73,728 immutable code bits**, and uses17-bit
  PC/return fields. It does not fit a Q-bit programme.
* The service Address of a logical copy is the holder's computed Address plus
  its copy offset modulo Q. It does not read the raw logical source Address.
* Eleven Word20 registers, a407-bit work buffer, generic physical I/O and
  instruction fetch define our interpreter. They are explicit implementation
  choices rather than Gács's programming language.
* The third-stage native collect/evaluate/courier procedure follows
  [GFD0's](../unregistered_gfd0/GFD0_BINARY_STAGE3_FLAG_DELIVERY.md) quiet-control
  mechanism with the final layout recomputed here. It is not a proof of the
  full noisy Gray protocol. Final WF inputs use final computed primary Info,
  including its source wipe, rather than a pre-wipe intermediate.
* The actual late birth row is112Q+1. Execution is allowed at computed Ages
  satisfying `112Q+1<Age<120Q`, giving exactly65,534 execution updates. This
  endpoint convention is stated rather than silently counting the birth row.

The original error-class constants are retained as parameters, but no
radius8 higher-error or iid proof is imported from Gray. The empty history
trivially satisfies all error-class conditions.

## 2. A total finite autonomous rule

[binary_own_rule_rom_v2.py](binary_own_rule_rom_v2.py) defines `R_beta` for
every pattern of its declared binary alphabet. The native fields have widths
13/20/1/1/1/1; Q and U are powers of two, so all GF/Age bit patterns are in
range. The following logical SF fields have five backup copies:

| Field | Logical width |
| --- | ---: |
| Info, MailL, MailR, Next, CourierL, CourierR | 1 each |
| History1, History2, History3 | 17 each |
| Head | 746 |

Head is119 metadata bits, eleven20-bit registers, and407 work bits. Thus
`K=37+5*803=4052`, `2K=8104<=8192`. The normal primary interval is
`[P,P+K)=[2070,6122)`. Raw SF bit k/copy q is stored at its field base
plus `5k+q`. Logical offsets are `S=(0,-2,-1,1,2)`; physical holder x stores
the copy of logical position x+S[q]. Work bit407 is a counted finite field,
not external tape or an omitted dictionary.

The only instructions are HLT, MOV, LIT, ALU, BNZ, JMP, WGET, WSET, NATIVE,
CGET, LDV, LDC, LDB, ST, CODE and JREG. Word20 arithmetic, including zero
division and oversized shifts, is total and masked. CODE returns a20-bit
window of the fixed beta, zero outside its73,728-bit domain; instruction
decode uses two actual windows and their explicit bit fields. There is no
external evaluator. NATIVE is only the specified native eleven-word arithmetic
primitive; the programme itself evaluates all SF and interpreter equations.

Physical I/O has an explicit target, one-site head travel, finite read/write
indices, and one output bit per ST I/O update. LDV reads the actual five
holder columns from the captured seventeen-lane bank and performs3/5. Bad
registers, widths, indices, targets, IO kinds, modes and control values have
specified failure/zero behavior. Multiple incoming heads yield a specified
ERROR packet. Out-of-range immutable fetch is zero data, not a host callback.
All packet arithmetic is masked at packing. These facts establish totality
of the declared finite rule, not universal compiler equivalence.

Copy votes and incoming heads need at most radius5. The final source is up
to three sites from a reader, and its native evaluation needs radius5, hence
the complete rule has radius8. No source outside its seventeen inputs is
read. WF1/WF2 pulse only at `96Q<=computedAge<98Q`. The mandatory SF wipe
uses computed Flag1 and comparison with raw self Address, exactly as declared.

**Status: proved** from the explicit finite local definitions. Whether these
definitions are a faithful refinement of all Gray interfaces is **unproved**.

## 3. Exact own-emission resources and retained failures

The full programme attempts include every Head field and all16 generic CPU
opcodes, their I/O modes, immutable code reads, and output/reset/wipe paths.
The interpreter is not an arbitrary integration port.

| Emission | Result | Scope |
| --- | --- | --- |
| GBP0 first one-copy non-Head prefix |16,401 bits,736 instructions | Incomplete; exceeds Q |
| GBP1 full emission before shared loops |76,600 bits,3,458 instructions,365 invalid narrow references | Rejected |
| GBP1 full emission after shared loops/review corrections |65,159 bits,2,918 instructions,372 invalid narrow references | Rejected Q-ROM emission |
| GBP1R full widened-ROM emission |66,815 bits,2,913 instructions,49 data words/980 bits included | Fits73,728 bits; does not fit Q |

The final GBP1R beta includes6,913 zero padding bits. Its full byte-per-bit
SHA256 is
`ac681db3e466cabb3bca8c01a0c1d68b8ac23668e4a4ad8e81db7fc65c5e9418`.
Its CODE primitive and the simulated CODE instructions use this same table.
Changing PC width and removing an unused13-bit target field changes the rule
and its own emission; the rejected Q version is preserved separately.

Early sources had an incorrect layout assertion and a standalone import-path
defect. The full emitter review also fixed the distinction between the
logical output centre used for Mem and the chosen incoming Head source, and
preserved the LDV lane index across the Mem helper. These are prototype
defects, not Gray defects. Old sources and receipts remain in the manifest.
The later strengthened History checker incorrectly expected only one of the
two simultaneously captured +/- lanes to change. Its failed source/log and
the corrected expectation are retained; the rule was unchanged by that fix.

**Status: proved** exact size/reference/resource accounting for these emitted
listings. Universal all-raw emitted-code equivalence and a universal deadline
are **unproved**. No assertion that all Q-sized word/loop programmes fail is
made.

## 4. Actual selected execution evidence

[check_full_rom_execution.py](check_full_rom_execution.py) executes the emitted
beta with actual operand travel on physically placed captured bits. It compares
all4,052 output bits with literal `total_rule`, and retains full input/output
values for the deadline witness. It checks25 selected cases, covering birth,
collect, move-collect, each instruction name, and four I/O kinds. All completed
outputs agree in those cases; this is finite evidence, not a universal proof.

The canonical all-zero-SF case and a canonical coherent HALT-Head case both
halt after147,051 updates. At65,534 the former already has correct represented
outputs despite unfinished execution. The HALT case has1,887 wrong represented
bits. Even at131,070 updates—the hypothetical entire fifth-stage width minus
the reset/birth rows—it still has407 wrong bits. That hypothetical cutoff is
an observation from extended prepared execution, not a changed physical rule.
The head stays in `[2070,6186]`; its last work load reads64 zero unused columns
past the represented interval, with an explicitly masked seven-bit tail.

**Status: measured** selected full execution equivalence and runtimes, with
exact receipts. The selected failure is lifted to the actual rule next.

## 5. Selected global encoding and real three-gather preparation

For every upper site g, let C(g) have GF=`g modQ`, Age123, all native flags
and WF0, all SF0 except all five Head copies equal the same packet h. Packet
h has p1, modeHALT, eleven registers equal `(2^20)-1`, work equal
`(2^407)-1`, and every other metadata field0. This is a legal global raw
configuration. Let `E(C,0)` be its lower encoding: lower GF=`x modQ`, Age0,
native flags/WF0; the five Info copies at primary `gQ+P+k` represent bit k
of C(g), all unrepresented Info0, and every other lower SF0.

No recursive equation `C=E(C,0)` is asserted. This is a one-level encoded
configuration, with an empty physical error history. It is sufficient to
test the universal one-level noiseless identity of this stipulated rule.

Under canonical GF/common Age/zero native flags and WF, the native equations
return the same GF, next common Age and flags0. This follows directly from
the adjusted-GF and clock quorums for every legal clock, including wrap.
The checker additionally checks all8,192 Address phases.

At computed Ages `32gQ+1` for g=0,1,2, Mail loads actual old Info. Thereafter
Mail shifts one logical site per update during the16Q active interval. At
capture `32gQ+2+|j|Q`, the old Mail at logical position z is exactly the
original primary Info at `z+jQ`. At j0 the capture uses old Info at
`32gQ+1`. Both lanes +/-j capture at the same tick. Resets retain earlier
History banks and clear the currently/future gathered banks. Five-holder
voting preserves these actual coherent logical updates. Thus all three
History banks, on every tape column read by the late head, equal

`T_g(a) = sum_{j=-8}^8 bit(C(g+j),a-P) * 2^(j+8)`

inside the represented interval and0 outside it. The furthest capture is
72Q+2; no late computation, selected future tape or external source is used
in this derivation. Mailbox erasure sees computed F1zero here.

At72Q+3, the37 actual native columns seed407 bits of Work in37 consecutive
logical cells. The subsequent36 speed-one moves collect their disjoint bits
at P+36. At72Q+40 the real native operator applied to that buffer returns
the canonical upper GF and Age124, flags0. Consequently both couriers are
seeded0, remain0 under the bounded forwarding rules, and deliver0 to unused
Info at3 andQ−3 on row80Q−1. All other unused Info remains0. Therefore the
actual final computed-primary sources in the96Q..98Q pulse are0. Both WF
fields stay0 throughout the lower period, closing the native-quiet induction.
The raw-self wipe is consequently false.

The checker directly checks745 reset/capture/native-seed/evaluation/delivery/
source identities at actual holder coordinates. Their algebra above, not
sampling a future bank, supplies the infinite-line gather and native closure.
**Status: proved** for this selected global encoding.

## 6. Literal late evolution and old-Next commit

The112Q reset clears Head and Next. Actual birth at112Q+1 creates p1/pc0
at logical AddressP, with all five copies; all other heads are zero. Since
every computed holder Address plus its offset is the same logical Address,
coherent copies have identical controls. With GF canonical and wipe false,
the Head/Next factor is closed under the actual `total_rule`. Mail, Info and
couriers cannot affect it after112Q because their relevant guards are closed;
the derived History banks remain unchanged. No future controller is supplied.

For the entire65,534-step active interval,
[check_selected_clean_period.py](check_selected_clean_period.py) compares the
literal local `total_rule` Head and Next result with the actual finite CPU,
including current position, old movement packet, full registers/Work and
actual previous Next. It also checks literal native/WF fields at every step.
The trace hash is
`5ae6359baa0522d46b2b36c32f8b654b38b48aeeabe77a62ec88b0e68935e5c8`.

This factor lifts to all colonies of E(C,0), not just the retained g100
neighborhood. Their input records differ only in the thirteen native GF
bits. The canonical native primitive returns g, Age124 and flags0. In the
emitted control path, workspace, delivery, collect, birth, active-CPU and
all Address-specific service branches on the simulated state are excluded
by that Age124. The raw-GF wipe comparison is equality for every g. After
that comparison, all SF reads and packet metadata/register/work values are
independent of g. GF data appears only in the first native output writes
and unused logical Address control values; ST's written bit value does not
change its target, count or branch. Thus the actual instruction/control/travel
path is identical for every g, with only those native data bits varying.
Every head remains inside its own lower colony, so neighboring heads never
interfere. This argument uses the displayed branch structure, not an assumed
common *upper* execution history.

At65,534 updates, the partial output has1,887 wrong encoded bits relative
to `R_beta(C(100))`, first at bit324. Parsed without masking, its native GF
is100, Age124 and flags/WF0. Its five represented Head p bits are
`(1,1,0,0,0)`, whereas literal `R_beta(C(100))` has `(1,1,1,1,1)`.
All output writes are within `[2070,6122)`, so unrepresented Next stays0.

At computed Age120Q the active predicate closes. Actual Head stutters even
if its held movement flag is nonzero, and Next stays fixed. At computed
Age0 the rule writes Info from **old** Next before clearing all private SF.
The canonical native fields and WF0 remain valid. Hence the actual global
output is an exact lower encoding `E(Cprime,0)` of the partial raw record,
whose discrepancy at upper site100 includes the stated Head p bits.
All binary field widths of Cprime are legal; it need not have coherent
upper SF copies. No decoder projection is used to erase the discrepancy.

It follows that the proposed noiseless identity

`R_beta^U(E(C,0)) = E(R_beta(C),0)`

is **false** for this fixed GBP1R beta and this legal global encoded C.
This is an exact finite execution certificate plus the proved gather/control/
commit lift; it is not merely an unfinished-head observation. It says nothing
about bit-memory failure or errors in an intact recursive hierarchy.

## 7. What remains and what this rules out

| Step | Status |
| --- | --- |
| Declared total finite radius8 rule and counted layout | proved |
| Q-sized GBP1 emitted listing fits its declared programme/PC | disproved for that listing |
| GBP1R emission fits9Q immutable ROM | proved |
| Selected25 completed prepared outputs equal literal R | measured exact finite evidence |
| Selected E(C,0) actual three-gather/native/courier preparation | proved |
| Selected literal65,534-update late factor and old-Next boundary | proved |
| Selected universal noiseless one-level identity for GBP1R | disproved by Section6 |
| Universal all-raw compiler equivalence/full completion deadline | unproved |
| Mutable ProgramBits/hardwirer, Gray-faithful interpreter/layout | unproved |
| Noisy E0/real1/higher/iid repair for this rule | unproved |
| Intact recursive realization of the HALT witness | unproved |
| Shorter U, or a globally smallest architecture/schedule repair | unproved |

The completed emission is66,815 bits; reducing it to8192 needs a new
representation/emission proof. Merely enlarging immutable ROM does not solve
the physical deadline. Merely using the full fifth stage still leaves407
wrong bits on this selected input. Optimizing the work patch loops, using a
different finite interpreter, parallel evaluation, or changing the schedule
are possible next construction steps. None has been silently applied here.
A later fix needs a fresh own beta, counted storage, actual three-gather and
native-flag timing, and physical reset/commit proof. No universal minimum
colony size or period is established by these two specific failures.

The standalone validator pins all rule/compiler/checker sources, primary
texts, failure snapshots, full-value receipts and replay logs. It re-emits
both the rejected Q listing and the executable9Q listing, replays every new
selected mathematical certificate, and compares all claims except wall time.
Registered Gray/main/root files are only hash-checked and never changed.
