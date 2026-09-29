# Conditional one-step colony separation

2026-09-27. A new symbolic check of the unchanged complete F descriptor establishes
colony separation under explicit input hypotheses. The result extends to G
because Address is preserved and G regenerates fixed ROM metadata locally.
It is a candidate-rule reduction, not a full noisy boundary or amplification theorem.

## Statement and representation

Assume canonical physical Address, a common legal Age, fixed ROM, coherent
copies of every procedure word, zero mail, zero flags/Wf/Signals, and zero
controller words outside each ROM region (addresses 0–27720).

Every checked output depends only on mutable procedure inputs in its logical
owner colony, together with the common clock and fixed metadata. No head-count,
phase, operand or Data-value restriction is imposed inside the ROM region.
Arbitrary 64-bit Data remains allowed everywhere, including nonMEM space.

Replica ownership is explicit. Procedure or Wf slot k at physical site x belongs
to logical site x+k−2, and Signal bit k uses that same owner. A raw cell next to
a colony edge can therefore contain copies belonging to its neighbor. The
certificate does not discard those copies or falsely claim independence of
whole raw cells across a physical cut.

The checker evaluates the full descriptor at sites −11 through 10 around a
boundary. Physical radius seven and replica offset two bound all potential
cross-boundary dependence to this region. It checks **3388 raw output words**,
including **990 controller outputs** and all **110 Signal output bits**, for
every one of the **2147483648 legal Ages**. Canonical Address and clock advance
are checked directly. The successful certificate takes **2.382273 s**, using
69224 KiB process RSS.

This is a one-step conditional result. A controller can generate mail inside a
colony, and capture can make Signal nonzero. The hypotheses are not asserted
invariant. Applying this result to a trajectory requires proving or checking
the relevant input conditions at every necessary step and matching the physical
boundary data. In particular, the burst itself may violate canonical geometry
or create controllers outside the ROM region. A cut must enclose that affected
region, rather than assuming its interior satisfies this lemma.

## Distinguishing tests and a preserved checker failure

The first checker tracked dependencies of whole Signal words and then assigned
that conservative set to an extracted bit. It rejected site −2, Signal bit 4:
at capture time the word can depend on left-colony Data through bit 1, although
bit 4 remains zero. A scalar/native probe confirms that setting this Data to one
changes Signal from 0 to 2, while the right-colony-owned bit stays zero. Both
values give Signal zero during the actual late recovery interval.

The corrected checker tracks dependencies per bit, using constant Boolean
identities, typed-variable widths, explicit addition carries and shifts. Unknown
bits conservatively retain owner dependencies. No physical transition, domain
assumption or rule description changed to obtain the passing result. The failed
checker source/log/watch and distinguishing probe are preserved.

Five tests pass in **3.206 s**. They check the complete certificate, reject a
cross-boundary Data-output mutation, reject attempts to admit mail or unconfined
controllers, and exhaustively compare the bit abstraction with concrete
three-bit operand cases involving carries, shifts and comparisons. This is an
inspectable symbolic Python check with tested abstractions, not a proof-assistant
development.

Separate complete scalar/native witnesses show why the two domain restrictions
matter. A head at the left colony's final tail site, outside its ROM, enters the
right colony with PC 42. A right-moving packet at that same left site writes
85 into the right colony's address-zero Data. Thus these are real possible
crossings when the corresponding hypotheses are removed, not merely warnings
from a conservative dependency analysis.

## Files and next application

Owned sources are `certify_retimed_holder_colony_cut.py`,
`retimed_holder_symbolic_bits.py`, their test module, and
`retimed_holder_colony_cut_counterexamples.py`. Accepted receipts are
`retimed_holder_colony_cut_v2.json`, `retimed_holder_colony_cut_tests_v1_watch.json`
and `retimed_holder_colony_cut_counterexamples_v1.json` under `figs/fixed_rule/`.
The certificate and tests use 120 s /2 GiB watchdogs; the concrete witnesses use
60 s /1 GiB. No GPU is used. Exact commands are retained in the watches.

Next verify suitable outer collars of the actual wider trajectory and their
matching full-ring noiseless context. The completed event audits already check
mail-free post-burst execution, but a global audit domain must not be confused
with the local hypotheses needed at a chosen cut. Initial full-ring collar
agreement and conditions through the noncanonical burst remain separate
obligations. This certificate alone does not discharge either one.
