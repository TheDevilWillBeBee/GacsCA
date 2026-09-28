# Colony size and the factor 128

Source review, 2026-09-26. No implementation or experiment changed.

The holder fixes Q=2^30 and U=128Q. This is not a theorem requiring U<=128Q.
Gray chooses equality for his schedule (printed pp.15,31,34): active gathering
windows are 16Q, final active update is 8Q. His p.34 computation/distribution
bound is 3Q+a log2 Q+b with unspecified constants, for sufficiently large Q.
This is an existence argument, not an efficient numerical prescription.

The ratio also enters repair estimates: pp.25–26 bound local structure repair
by 200+500+2(Q+200)=2Q+1100, below U/32=4Q for Q>=8192. On pp.35–36 a short
damage interval relative to separated active stages supports temporal voting
and Proposition 4. These uses constrain timing; they do not establish a
universal upper bound of 128 on U/Q. A modified schedule needs its repair,
trickle-down and amplification arguments rechecked. The printed Flag2 issue
is not resolved by this parameter discussion.

Gacs Condition 9.20 / Theorem 9.3 (pp.95–96) require
U>=3Q+interpr-coe*(|Trans-prog2|+1)^2*||S2||, with separate space and cell-capacity
constraints. That is basic block simulation, not the complete noisy theorem.
For the amplifier, (11.16) requires U'_k>=R*Q_k/w_k; (11.17) couples Q_k*U'_k
to error probability, and (11.8) uses that product in recursive error estimates.
U'_k belongs to that construction and is not automatically our Age modulus.
None of these conditions specifies 128.

Our serial sweeping evaluator uses 57,332 computation cells and 4,533,298,561
ticks for voting plus full rule evaluation. Keeping an 8Q window alone requires
Q>=566,662,321 if that cost is held fixed. Gathering and flag delivery impose
additional deadlines. The current Q=1,073,741,824 fits the complete measured
schedule; it is an implementation choice, not a paper-imposed minimum.
Changing Q changes encoded constants and potentially descriptor costs, so
this arithmetic does not certify a smaller-Q construction.

Smaller colonies with a longer period relative to Q could substantially reduce
physical space across levels, but do not remove serial computation time.
A better specialized evaluator could reduce both space and time. Either needs
full-controller closure and sufficient local storage; neither permits rules
that vary with requested depth. Numerical costs also need measurement: at fixed
U the conservative causal window contains more colonies, proportional to U/Q,
which can increase overhead in the current per-colony execution representation.

Recommended next architectural comparison: preserve the holder fixture and
compare a smaller-colony relaxed schedule against a faster specialized
evaluator before a substantial GPU port. Do not treat 128 as a universal
obligation or claim an altered schedule inherits the repair proof unchanged.

Validation: read Gray pp.15,17–18,25–26,31,34–36; Gacs pp.95–96,110–112;
holder_core.py, HOLDER.md, EVALUATOR_BUDGET.md and recorded holder execution
timings. No tests or jobs launched for this documentation review.
