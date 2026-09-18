# Design: self-simulation machinery (uniform rule, finite-depth executable hierarchy)

Status: design fixed 2026-09-18, implementation in progress. Sources: Gray (2001) Secs 5.3-5.5;
Gacs (2001) Secs 4.2-4.5, 9.2-9.3, 12, 18, 19.

## 1. Why not Gacs' interpreter literally
Gacs (Sec 9.3, Thm 9.2) evaluates the simulated transition Tr* on a universal computing track
(`Cpt`) by interpreting a rule program `My-rules` (written into the colony as a hard-wired constant,
Alg. 9.7 / 19.5). The interpreter time is `interpr-coe (|P|+1)^2 |S|` steps; for any realistic
program (|P| ~ 10^3-10^4 bits) this forces U ~ 10^7+, and a level-2 step costs U^2 level-0 steps.
Explicit level-2 dynamics would then be impossible. Gray (Sec 5.3) explicitly leaves the
computation "implicit".

## 2. Chosen architecture: Age-scheduled distributed microprogram
The transition function is uniform (same rule at all levels) and consists of:

1. **Local structure** (Address, Age, Flag1, Flag2): exactly Gray Sec 5.2 (implemented, verified).
2. **Simulation structure**, one bit per cell per *track*, every track R-fold redundant
   (cell x holds copies of the track bits of x-1..x+1 for R=3, or x-2..x+2 for R=5; majority
   restored each step, Gray Sec 5.4). Tracks:
   - `Info` (1): primary SimBit. The colony's Info bits at addresses [b0, b0+K) are the K-bit
     state of the simulated cell, laid out bit-serially (little-endian fields, same layout as a
     real cell's state).
   - `Arg_j`, j in {-5..5} (2 bits each): retrieved states of the 10 neighbour colonies (+ own),
     with a 2-bit accumulator for the majority over the three gathering stages.
   - `Hold` (1): the new simulated state being assembled.
   - `Work` (T1..T4, Sig, Bc: 6): temporaries, carry/signal, broadcast bit.
   - `BF` (log U + log Q): broadcast field holding the simulated cell's Age_1 and Address_1
     (needed only to interpret the simulated cell's microstep, Sec 4 below).
   - `MailL`, `MailR` (1 each): two timed streams.
   - `wf1`, `wf2`: Workspace.Flag1/2 (Gray Sec 5.5).
   K = 28 + 57 R bits: R=3 -> 199 (Q=256), R=5 -> 313 (Q=512).  (Masumori's 293-bit cell is
   consistent with R=5.)
3. **Microprogram**: a table of ops `(age_start, age_end, opcode, params)` compiled from a small
   Python DSL. At each step every cell executes the op active at its own Age (Gacs 9.7:
   "R1; R2 ... can be replaced with a conditional on Age"). Op kinds are per-cell rules of O(1)
   complexity: SHIFT (track moves one cell per step), COPY/BITOP between tracks at the same
   address, SWEEP (signal walking along an address range computing AND/OR/carry: comparison,
   increment mod 2^w, add constant), BROADCAST (write a sweep result or a bit-serial field into
   every cell's `Bc`/`BF`). Fields are little-endian bit-serial along addresses; Q and U are
   powers of two so "mod Q/U" is free.
4. **Interpretation (self-reference)**: the simulated cell's transition = Tr_local on the Arg
   fields (a fixed microprogram) + "the op active at Age_1" applied to the simulated tracks.
   Each cell reads Age_1/Address_1 from its `BF` field, looks up the *same op table* (a fixed
   finite function of BF, hence a legitimate CA rule; this is Gacs' `My-rules`/Gray's hard-wired
   ProgramBit made concrete), and applies the op to the bit it holds. Because every op is a
   per-cell rule of the simulated cell, interpreting one simulated step costs O(K) level-0
   steps (cross-track bit offsets are realised by SHIFTs). No infinite regress: the table is
   finite and its interpretation code is written in the same op kinds.

## 3. Colony work period (all colonies synchronised through Age; timed protocols)
Retrieval uses two streams: at age t0 every cell posts its Info bit on MailL (moving left) and
MailR (moving right); the stream is a rigid shift, so at age t0 + jQ the MailL bit at address a
is exactly the Info bit of address a of colony +j. Receivers sample at t0+Q, 2Q, ..., 5Q: one
stream per direction retrieves all five neighbours. Gray's special rule (Mailbox := 0 where
computed Flag1 = 1) blocks communication through damaged/misaligned regions.

| stage | length | action |
|---|---|---|
| G1, G2, G3 | 5Q+1 each, separated by rest periods >= 2Q | gather; G3 majority-votes into Arg |
| C | ~(1+alpha)K + sweeps, x3 with vote (optional) | Tr_local microprogram -> Hold; interpretation of the simulated microstep -> Hold; write F1*/F2* into SimBit at addresses Q-3 / 3 (Gray p.35) |
| T | 2Q | trickle-down window for wf1/wf2 (Gray p.41) |
| F | 1 | Info := Hold (Age = U-1) |

## 4. Cost model and what is reachable
Level-1 step = U level-0 steps on Q cells; level-2 step = U^2 on Q^2 cells. With Q=256,
U ~ 50Q ~ 1.3e4: one level-2 cell-step ~ 1e13 cell-updates (~1e3 s on the A100 at ~1e10
updates/s). Consequence: level-1 dynamics can be studied for thousands of level-1 steps; level-2
dynamics for O(10-100) steps; level 3 only as static encoded structure. This is intrinsic to any
faithful implementation (Gray's U=128Q is worse); it is documented rather than worked around.

## 5. Revision after stage 2 (finite tower)
Section 2.4's "same op table used to interpret the simulated cell" holds for one nesting level:
the interpreting cell needs the simulated cell's age and address as integers (registers `simage`,
`simaddr`). Interpreting a cell that itself interprets needs its registers too, i.e. one register
pair per depth. The implemented system is therefore a finite tower (see selfsim_stage2.md), with
level-specific (Q, U) chosen so that the top level is local-only and small: level-2 steps become
affordable (U₀U₁ ≈ 6.7×10⁷ level-0 steps instead of U² ≈ 2.7×10⁸).

## 6. Interpretation choices vs Gray/Masumori (see Report/discrepancies.md)

## 7. Depth 3 (design, not implemented)
A fourth level (level-2 cells running the full rule, simulating local-only level-3 cells) requires
the level-1 cells to carry an interpretation phase, hence the level-0 interpreter must reproduce
level-1 ops of kinds IINIT/ILATCH/ICHAIN/IBC/IEVAL/IWF/REGWIN/BUSLATCH_INT. Each of these is a
per-cell rule of the level-1 cell parameterised by the *level-2* active ops (table lookup keyed by
the level-1 cell's `simage` register) and by the level-1 cell's slot geometry. Implementation:
(a) a second register pair (`simage2`, `simaddr2`) in every level-0 cell, loaded each period from
the SIMAGE/SIMADDR fields of the simulated level-1 cell (Arg_0), colony-locally repaired;
(b) `_needs`/`_ieval` extended with a nested case that, for a level-1 op of an interpretation kind,
computes the level-1 cell's latch/eval decision from (level-2 active ops at `simage2`, level-1
address = `simaddr`, level-1 slot geometry of the level-1 layout L1, level-1 pass step
= `simage` − op.t0) and reads the corresponding level-1 bits from the passes (they are ordinary
track bits of the level-1 neighbours). Cost: U₁ grows to ≈ 2·U₁ (its own I-phase), a level-3 step
is U₀U₁U₂ ≈ 3×10¹¹ level-0 steps — its dynamics are unobservable; only the static structure and
per-phase correctness (acid test at level 1 through its I-phase, ≈ 25 GPU-minutes per phase) can
be verified. Deferred in favour of depth-2 experiments.
