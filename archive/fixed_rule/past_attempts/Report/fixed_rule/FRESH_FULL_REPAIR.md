# Conditional complete repair of the selected fresh-fault sequence

2026-09-27. The missing procedure-state link is now checked. Under the existing
full-ring endpoint and geometry-refinement premises, the actual configuration
rejoins its **complete fault-free state at tick16989**, local physical time
8589951581. This includes controllers, encoded Info, all raw copies, packets,
Signals, geometry and the three old nonMEM residual words. Those old words were
erased during the fresh fault sequence; they are not omitted from this claim.

The nine fresh marks follow the earlier physical burst and three subsequent
lower periods. This gives a conditional complete-state result for that specific
two-burst sequence. It is not a general repeated-noise theorem, threshold result,
new literal noisy suffix after tick128, or new full-ring GPU execution.

## Complete local identities

`certify_retimed_holder_geometry_procedure_effects.py` checks two identities of
the unchanged complete physical descriptor for old Ages128..16988.

First compare two neighborhoods with the same own Address, raw procedure words,
Signals and metadata, but arbitrary differing neighbor Addresses and flags. The
comparison neighborhood has canonical geometry and zero flags. All90 procedure
outputs of the damaged-geometry neighborhood equal the comparison outputs with
only the documented clearing operations:

- Nonmail procedure fields are cleared only if computed Flag1 is set and the
  computed own Address differs from the old own Address.
- Mail fields are cleared when computed Flag1 is set.
- Signal differs only by the same Address-change clearing. All ten Wf outputs
  remain zero and the common early clock advances normally.

The second identity allows arbitrary Addresses, flags and raw ROM metadata, but
requires every raw procedure word, Signal and Wf in the neighborhood to be zero.
All101 corresponding outputs are then zero. No one-head or coherent-geometry
assumption is used in this identity.

A separate structural dependency check establishes that **none of the154 outputs
reads any of the686 neighbor raw metadata inputs**. Only the physical holder's
own hard-wired metadata can matter. This closes a necessary detail: neighbors
with wrong Addresses have different projected ROM records, even when the own
Address is correct. The first join is preserved; accepted v2 adds this explicit
check. Their diagnostic NPZ artifacts are identical.

## Actual entry and healthy reference evolution

The tick128 literal checkpoint from
[FRESH_GEOMETRY_RECOVERY.md](FRESH_GEOMETRY_RECOVERY.md) has complete equality
with the fault-free reference in every field except Address/flags and their
projected ROM. Its retained window contains the whole radius-seven fault cone,
so the equality applies outside it too. Uniform Age, zero Signal and zero Wf
are checked. The inherited full-ring interpretation remains conditional on the
previous endpoint relation.

The healthy reference starts from the actual saved terminal bank and ordinary
native reset, keeping every encoded Info word. The existing compiled physical
event executor advances a complete colony to Ages128,640,9912,9913 and16989.
It checks3112960 complete procedure/Signal words: Data is unchanged after reset,
mail and Signals are zero, and exactly one complete head/controller exists.
This is an independently evolved reference, never installed into a noisy world.

An independent scalar trace follows all16988 head transitions. At Age t the head
is at physical address t-1. It moves right without a wait or reflection. At9913
it fetches the first LIT instruction, entering WRITE phase with value2^64-3 and
destination9905. Its first Data write is scheduled at65349, after the recovery
endpoint. Changing the encountered Data from zero to all-one bits changes none
of these next-controller states; no represented Info has been read yet. No
packet can be born along this trace.

This behavior is uniform across colonies despite different Info contents. Only
Info survives the reset in ordinary MEM; its addresses are outside the affected
tail. The tail buffers are checked zero in the saved neighboring colonies. The
full healthy decoded flags are zero, so their terminal captured Signals are zero
as well. Nonzero edge Signals in the periodic73-colony diagnostic fixture are
not silently treated as global zeros; the relevant four central colonies are
checked explicitly and the full-ring relation supplies the global reference.

## Covering every possibly dangerous local step

For every old Age128..1023, the join replays the checked geometry projection and
collects every output site whose old **or new** Address is wrong. There are5718
such site/time cases. All lie in the tail at physical addresses at least30960.
For each case, all logical offsets -9..9 have zero healthy Data and no healthy
head/controller:108642 checked operands. This covers the complete raw
radius-seven input neighborhood, including the additional two-site replica span.
Mail and Signal are zero as established above. No defect or controller is removed
by this check; it tests the existing reference state against the actual geometry
support. The first canonical input Age found is607.

Induct on complete procedure equality. At a site with wrong old or new Address,
the shared procedure neighborhood is zero, so the zero-domain identity makes
both outputs zero. At every other site, own Address and projected own ROM are
correct. Neighbor metadata cannot be read; the clearing identity applies despite
arbitrary neighboring geometry. Address-change clearing is absent there, and
Flag1 mail clearing changes nothing because the healthy mail output is zero.
Signals and Wf remain zero. Thus every procedure/controller/Data output agrees
with the healthy physical trajectory throughout the moving geometry damage.

After Address is canonical, the same argument continues while Flag1 clears:
only zero mail could be removed. The previously checked exact recurrence clears
the last Flag1 at16989. G's ROM projection then agrees everywhere too. This
establishes complete equality at that time. Subsequent fault-free dynamics agree
by determinism; no special recovery kernel or top-level transition is introduced.

## Evidence and remaining limits

Accepted receipts under `figs/fixed_rule/`:

| Receipt | Runtime | Process peak RSS |
|---|---:|---:|
| `retimed_holder_geometry_procedure_effects_v1.json` | 1.224755 s | 57164 KiB |
| `retimed_holder_fresh_full_repair_v2.json` | 9.325502 s | 288920 KiB |

Seven tests pass in **1.997 s**. They reject hidden geometry writes, head creation
in the zero domain, neighbor-metadata reads, a nonzero Data operand, and a nearby
healthy controller. The healthy-controller test requires the actual FETCH-to-WRITE
change and full64-bit value. All watchdogs are terminal exit0 with at most1GiB
caps. Exact commands are in watches. No GPU use or shared-source change occurred.
Final index: `figs/fixed_rule/retimed_holder_fresh_full_repair_evidence_v1.json`.

This is a conditional descriptor-semantics composition, not a proof-assistant
theorem. It inherits the geometry projection's stated backend coverage: complete
literal prefix comparisons and scalar boundary/random checks, rather than an
independent scalar check of every projected output. The new local identities and
neighborhood checks close the procedure-state gap; they do not erase those earlier
qualifications. A separate complete noisy suffix run would strengthen the evidence.

General fault families and damage amplification, persistent-noise thresholds,
robust finite-depth caps, depth3, Q/U optimization and the Flag2/SimBit source
ambiguities remain open. The full fixed-rule self-simulation goal is active.
