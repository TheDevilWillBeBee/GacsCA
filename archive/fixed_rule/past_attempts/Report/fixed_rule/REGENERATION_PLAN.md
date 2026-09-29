# Next mechanism: local regeneration after computed Address changes

Historical plan; the implementation and its measured limitations now appear in
[REGENERATION.md](REGENERATION.md). The text below records the original proposal,
not evidence that every part of the larger maintenance integration exists. The static-Address
projection is insufficient once local maintenance repairs Address. Preserve the
executable stale-program counterexample in `test_projected.py` as the failing
extension that motivates this work.

## Required relation

Let F be the complete unprojected evaluator, P its description-derived colony
program, J_P(a) its static program/boundary record at Address a, iota_P the lift
that restores that record, and pi the projection that drops it. The current
physical rule is G = pi F iota_P. With Address unchanged, F iota_P = iota_P G.
After Address changes, merely keeping the old record breaks that identity.

A source-aligned extension should regenerate the **represented** static record
by reading the colony's own P at the computed represented Address before committing
Info. Gray pp.31–32 performs a simulated-ProgramBit overwrite; here the projected
record contains several fields rather than one bit. The controller implementing
that read must itself be represented in the complete description. Embedding the
entire address-indexed ROM truth table into its own circuit risks recreating the
size circularity that Gray's construction avoids.

## Candidate fixed local primitives

The existing head has 16-bit ra/rb/rd and a three-bit phase. These can support
regeneration without a register pair per depth. Proposed opcodes are additions
to one candidate rule, never depth-selected hardware:

- CLEAR: reset the head's rd accumulator and advance pc.
- LOAD: fetch one encoded Address bit from a designated memory location; shift it
  into rd, modulo 2^16. A fixed MSB-first sequence loads the logical Address.
- META: take an output memory location and a selector for one bit of the current
  static record. Scan to the physical cell whose Address equals rd, read that
  bit **locally at the head**, then store it in the designated output location.

With a three-bit opcode field, the static record has 69 bits (kind/index/a/b/d/
first/last). It remains ordinary state in F and becomes address-derived data in
G. META must read these raw local fields in F, not call a host rule interpreter
or use a hidden global ROM access. Its projected physical realization reads the
same locally derived fields at the head's current Address.

A META query can be timed independently of its encoded target:

1. At fetch, set phase META and value=0, indicating that the initial partial pass
   is not yet a lookup pass. Keep rd=target Address; load ra=output and rb=selector.
2. On returning to the first cell, start a full rightward scan and mark value=1
   as the ready flag. Only that scan may match Address=rd.
3. On a match, latch the selected bit, set rd=output and enter a distinct waiting
   phase. Complete the traversal back to the first cell before starting WRITE.
4. If the full scan ends without a match, generate the declared out-of-range
   fallback record (MEM, index=target Address, other static fields zero), then
   start WRITE at the same phase boundary.
5. Write the latched value. Reload the encoded Address before the next META query
   rather than silently adding an unrepresented persistent register.

The existing unused phase values 5/6/7 can represent LOAD, META, and waiting for
WRITE; one carried bit suffices to distinguish the initial and complete scans.
This proposed assignment needs an explicit total transition for malformed raw
states, collisions and boundary cases, and a regenerated self-description.

For a META instruction at site p and output memory at h, the processing after
fetch takes 4Q+h−p ticks under this schedule, independent of the queried Address.
This is a proposed routing calculation to test against literal local execution,
including target 0, target Q−1, and absent targets. It must not be used as an
acceleration certificate before those tests and the total rule exist.

## Integration and distinguishing tests

Stage computed output in a true-bit Hold bank. Read Hold.Address through LOAD,
regenerate every static-record bit into Hold through META, then commit the
complete word. The resulting shadow word should equal iota_P of the projected
computed state even when its Address changed. Initial reconstruction, a stored
opcode inventory, or an unchanged-Address example is not sufficient evidence.

Test the raw controller/circuit equivalence for all new phases; packet and head
locality; fixed META timing across targets; output record regeneration after a
changed encoded Address; and successive full projected macrosteps with the
complete expanded evaluator description. When actual maintenance is added,
compare repaired-Address outputs against the published scalar maintenance rule,
with D8/D10 alternatives explicitly labeled. Do not introduce an artificial
Address-changing top kernel as a substitute for that integration.

After this mechanism closes, incorporate the actual maintenance rule and its
clock, reset and correction schedule. Static Address still lacks repair; program
projection by itself supplies no noise-robustness result.
