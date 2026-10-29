# Native-padding projection is not a quotient of unchanged GAW2R

**Status: proved local obstructions; no physical/noise counterexample.**
The frozen changed GAW2R rule, own ROM and legal-record period theorem
remain unchanged. Its constants are Q8192/U128Q/c104. This is a check of
the broader decoder alternative mentioned in the separate, unimplemented
[commit-mask proposal](../unregistered_gaw13/GAW13_PADDING_PROPOSAL.md).
It does not apply to Gray's published bit layout or the active G17 rule.

Let D be the set of 496-word records whose every word has 100 bits.
The legal GAW2R alphabet A is the subset with native widths
(13,20,1,1,1,1). Define pi:D->A by these six masks and leave all SF words
unchanged. Evaluate the existing Python local_transition on D by its
literal formula, without claiming that D is the rule's legal alphabet.
Two tempting extensions are false:

1. pi(local_R(raw)) = local_R(pi(raw)) for every radius-eight D input.
2. The unchanged immutable emitted evaluator implements that existing
   local_R extension for every such input.

The second statement is distinct from the accepted evaluator/period
theorem on legal native input records. No claim in that theorem is
disproved here.

## First obstruction: wiping observes the old padded GF

For j=-8,...,8 put GF(j)=200+j, Age(j)=123, F1(j)=1 and all other native
flags zero. All five Info copies are 7; all other SF fields are zero.
Call this legal input z. Replace only its central GF by 8392=200+Q,
obtaining raw input d. Every d word has at most 100 bits and pi(d)=z.

The native_at input builder masks every GF by Q-1, every Age by U-1 and
every flag by 1. Therefore it receives the same native neighborhood
from d and z. Both adjusted side-GF lists are constant 200, both Age
lists constant 123, and the entire radius-five F1 list is 1. The native
equations give new GF200, Age124, F1=1, F2=0, WF1=WF2=0. In particular
the left F2 population is zero; the changed h1 erasure sets F2=0.

The SF transition uses the literal predicate

    wipe = newF1 and newGF != cells[0].addr

The old addr in this predicate is unmasked. Thus wipe is true on d and
false on z. Age124 is outside every gather/reset/capture/courier/head
event; the ordinary Info identity applies before the final wipe. All
five voted Info values are 7. Consequently

    local_R(d).Info = (0,0,0,0,0)
    local_R(z).Info = (7,7,7,7,7).

Projection does not change SF, so the proposed commutation equality is
false. This argument uses the literal equation, not a sample-based
universal inference. The exact immutable evaluator also returns the
literal padded-input output in 2646 steps and HALTs. It therefore
exhibits the same obstruction; this is not an interpreter-only issue.

The same wipe argument works for every central b with 5<=b<=Q-6, every
nonzero legal Info word v, and every positive n with b+nQ<=2^100-1,
using canonical GF(b+j), Age123, F1=1 and raw central GF=b+nQ. The
central high bits are discarded by native_at but observed by wipe.
One exact member already suffices to refute the universal quotient.

## Second obstruction: the emitted GF fallback retains raw bits

Now set legal GF(j)=200+17j for -8<=j<=8, Age123, all native flags zero,
Info7 in every copy, and other SF fields zero. Replace only central GF
200 by 8392. The adjusted right list is 216,232,248,264,280 and the left
list is 184,168,152,136,120. Neither has a three-of-five quorum. The Age
lists still have quorum123. F1=1 because the right GF quorum is absent;
source3 is off since (123+1) mod16 is nonzero, no F2/WF2 is present, and
h1 erases F2. The Python native_at first masks the central GF to200 and
returns GF200/Age124/F11/F20/WF0. Its subsequent wipe again erases SF.

The immutable programme instead loads the raw central GF into its
fallback register12. READ5/VADDINDEX constructs the two distinct adjusted
lists above; VMAJ returns register12 when no quorum exists. Both the
left and right GF fallback values therefore remain8392. The selected
left fallback is written to output word0 without a 13-bit mask. The
emitted wipe compares that8392 with raw old8392 and does not wipe.
The exact unchanged emission HALTs after63872 steps, before its65535-step
late-pass limit, with native words

    (8392,124,1,0,0,0).

The Python native output is (200,124,1,0,0,0). The complete 496-word
outputs differ at indices0,206,207,208,209,210,217,220. Info206..210 is7
in the emission and0 in Python; the two Programme differences are also
retained in the full receipt. This refutes an unrestricted malformed
extension of the accepted emitter-refinement statement. Its legal-input
premise remains essential.

## What this establishes and leaves open

Both inputs are prepared local neighborhoods. No intact encoded initial
configuration, legal physical fault support or later bank trajectory
has been constructed for them. They are not operational repair failures,
iid failures, or counterexamples to Gray/Gacs. Existing actual malformed
boundary histories are separate evidence, not supplied by these tapes.

A larger alphabet with projected decoding cannot reuse the current
kernel/period theorem by simply dropping its legal-native premise. A
different relation that tracks padding, or a complete malformed-record
physical-period theorem, is still unproved. It may still be possible.

The previously proposed commit mask is an explicit **rule change**, not
implemented here. In a canonical/common-clock lower colony it makes each
normal native word legal for arbitrary old Out, because all five holders
select the same represented word and apply the same mask. That range/copy
identity alone does not prove own-beta compilation, timing, damaged-holder
coherence, upper repair, higher error maps or positive iid reliability.
Changing U or the separation constant does not alter either local
padding predicate demonstrated here. No globally sufficient or smallest
reliability fix follows from these two obstructions.

The [checker](check_padding_quotient.py) verifies all443 inherited frozen
assets, rebuilds the same ROM and compares every bit/dictionary entry
with the retained ROM, then executes both exact prepared inputs. It
retains all input/output words in
[the certificate](../../../../figs/gray_counterexamples/unregistered_gaw_padding_quotient/padding_quotient_certificate.json).
Default replay is read-only. The algebra above supplies the proof; the
finite execution gives the exact emitted witness and independent receipt.
