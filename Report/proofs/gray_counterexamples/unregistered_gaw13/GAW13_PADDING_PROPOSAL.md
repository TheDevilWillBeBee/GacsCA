# Proposed native-padding mask at commit: explicit, unimplemented rule change

This is a coding-agent proposal for the frozen WORD100 GAW2R variant,
not a change made in GAW13 and not a repair to Gray's published bit rule.
No existing trace, ROM, transition, proof or receipt has been modified.
The completed GAW12/GAW13 executions still contain their actual high bits.

At a computed-Age0 commit, for each SF copy s use the existing computed
service Address a=(computedGF(x)+s) mod8192. If a=P+i, 0<=i<6, replace
the current Info assignment from voted old Out by

    newInfo_s = votedOldOut(x+s) AND (2^width[i]-1),
    width = (13,20,1,1,1,1),       P=3848.

At other residues retain the ordinary100-bit old-Out commit. Keep the
actual old-Out-before-reset order and the later mandatory wipe. This is
a proposed **RULE CHANGE**: it changes the all-raw local equation and
therefore its own beta. It has not been implemented or compiled.

For the canonical/common-clock lower geometry of GAW12's late-SF class,
all five holders of a logical y obtain the same a=y modQ and voted Out.
The six normal native words at U would then lie in exactly their legal
ranges Q,U,2,2,2,2, regardless of their100-bit Out values. Every other
represented word already has100 legal bits. Their coherent Info copies
and reset work would thus give a legal E(Cprime,Aprime) boundary for this
restricted class. This is the elementary mask-range/copy identity; it
does not establish the simulation theorem for the proposed changed rule.
For GAW13's selected high-GF record the projected GF would be8191 rather
than2^100-1, still potentially a sacrificed upper error.

Before this proposal is a usable candidate, rebuild the whole immutable
own ROM/listing so its evaluator reproduces the new assignment on all
raw upper cells, including computed service addresses and SF wipes.
Recheck code/dictionary/state counts, operand ranges, the exact late-pass
deadline at unchanged U128Q, physical period composition and the chosen
fault histories against that new source/ROM. Neither beta<=Q nor a timing
fit is inferred from the small local change. Under damaged GF/clock,
different holders can select different masks or stages; the legal-record
argument above has not proved higher-error coherence or repair.

The proof-only alternative is a broader encoding/decoder relation which
allows native padding, decodes13/20/1-bit projections and proves that the
actual emitted evaluation and all commands are compatible with those
projections. Merely naming that decoder does not prove insensitivity to
every high input bit. A universal malformed-record kernel/period theorem
for the existing rule remains unproved; selected finite2U recoveries do
not supply it.

This addresses a specific introduced WORD100 representation obligation.
It is neither a globally sufficient nor a globally minimal reliability
fix. It does not address Gray's programme/layout refinement, the radius8
and102Q schedule departures, general real1/higher maps or positive iid
rates. The baseline remains Q8192/U128Q/lambda24/c104.
