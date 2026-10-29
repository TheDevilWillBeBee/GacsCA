GPN0 is an explicit bit-packed SSA Boolean programme and total abstract
evaluator. It is not a physical whole-rule completion. Its exact native
prefix already fails both the Q8192 storage allowance and the8Q fifth-
stage runtime of a serial one-programme-bit/tick implementation. This
is a precise obstruction for a stated separate-module encoding/evaluator,
not a lower bound for compact word/loop programmes or for every Gray CA.
The baseline remains Q8192, U128Q, lambda24 and c104. No active source
or accepted GT0/GV0 source is changed.

**Primary sources and version.** Gray pp30-32 describes a programme beta
containing the interpreter, moving/storing and native rules; beta must fit
in Q ProgramBits. Its mild-dependence bound has unspecified constants.
The hardwirer first obtains the simulated Address, reads the corresponding
physical ProgramBit and writes it into the primary SimBit representing
upper ProgramBit. Projection then removes the explicit ProgramBit field
because it is a function of Address. This does not make a missing beta
free: its bitstring and the actual interpreter must first exist and fit.
The early hardwirer, its represented-field layout and retained output
must also compose with the actual gather/update phases.

Gray cites Gacs §§7.3-7.4. The supplied file named gacs_2001.txt says on
its title page “January24,2024(last printing)” and calls itself a corrected
and strengthened version of the journal article. Its §§7.3-7.4 concern
canonical simulations and primitive variable-period media. The relevant
available evaluator material is instead §§9.1-9.3, particularly Theorem9.2,
Algorithm9.7 and Condition9.20 on printed pp89-96. This is a version
distinction, not evidence that Gray incorrectly cited his contemporaneous
paper. The retained PDFs/text hashes fix the actual sources examined.

Gacs's available Rule Language theorem supplies an interpreter string and
an unspecified integer coefficient C. Its time guarantee is

    C (|P|+1)^2 K,

and its space guarantee is C (|P|+K+1), where K is the represented cell's
bit capacity. The basic block-simulation conditions require sufficient
colony space and U>=3Q+C(|P|+1)^2 K. The complete formalization that
would emit its simulation strings is not present in the supplied paper.
These are existence/asymptotic results, not an emitted beta, numerical
coefficient or physical fit certificate at Q8192. A large upper bound
does not prove actual runtime failure; we do not infer one from it.
For scale, even an optimistic transplantation with C=1 and the GT0
preliminary K277 would guarantee completion in8Q only if |P|<=11 after
reserving3Q. This is arithmetic of a sufficient bound, not a programme-
length impossibility theorem. The available theorem uses three inputs;
an eleven-input interpreter also needs an explicit adaptation and constants.

**The stated encoder.** GPN0 compiles native, data and future interpreter
field modules separately, concatenating their programmes without cross-
module circuit optimization. Its native module is the exact existing
literal_maintenance.py Boolean transcription at k13,m20. No paged or
two-index GR1 ROM is used. There are407 input bits,2919 live two-input
gates and35 output bits: new Address13, Age20 and Flag1/Flag2. Its
3328 nodes include constants0/1 and input nodes. A node index needs12 bits.
The gate destination is implicit in topological order. Each gate takes
a2-bit opcode and two12-bit source indices, or26 programme bits. The
output map uses35 twelve-bit indices. The actual emitted bitstring also
has a75-bit format header; padding of the last byte is not programme data.

The byte-packed beta_N is exactly

    75 + 2919*26 + 35*12 = 76389 bits.

Even dropping every format-header bit leaves76314 bits. This is over
nine times the Q8192 ProgramBit allowance. The native prefix's3328-node
one-bit memory could fit inside Q, but its programme cannot. Adding
interpreter/service fields, their own transition, transport or hardwirer
code cannot shorten that independently emitted native prefix. This last
conclusion is restricted to the stated separate-module encoder; a
different circuit or compressed word/loop language can avoid the bound.

**Exact semantic certificate.** The retained programme is decoded back
into every opcode/source pair and output node. Source indices always
precede the current destination, and all decoded instructions equal the
actual compiled native graph. Constants and inputs agree. Induction on
the destination index therefore proves that every computed node and
output agree for every raw native input word, including all20-bit Ages
and arbitrary native/Workspace flags. The raw native transition is total.
The abstract parser/evaluator also has a defined response for every
programme/input bitstring: truncated headers, invalid parameters,
reserved opcodes, forward references or out-of-range outputs return an
invalid flag and zero output. A legal programme produces its encoded
outputs; extra padding is ignored. This defines an abstract evaluator,
not a cellular-automaton service transition with a locality certificate.

Replays on retained random raw inputs compare the actual decoded
evaluator with the compiled native circuit. They are measured evidence,
separate from the all-input structural induction. Malformed/truncated
parser cases are retained as validation of the specified invalid response.
The native Flag2 printed-clause issue remains: code equivalence is not
a reliability claim. A separately labelled h1 programme is counted to
check that this single predicate correction does not resolve the
encoder's fit obstruction.

**Serial fetch runtime obstruction.** Consider implementations of this
evaluator that read at most one fresh ProgramBit per physical tick and
start with no prefetched programme bits at the fifth active stage. They
interpret the entire straight-line bitstream once in gate order. They
do not skip instructions or synthesize un-read programme bits. Every
input-independent native instruction is fetched, even if some raw
inputs make its output0. Consequently programme fetch alone takes at
least76389 ticks. Operand reads, writes, transport and initialization
can only add time. This exceeds8Q=65536 by10853 ticks. Even the
header-free payload exceeds8Q by10778 ticks. The failure holds for
this serial-fetch model despite granting instantaneous operand memory;
it is not a runtime lower bound for parallel code delivery, preloading,
native-specialized word instructions or arbitrary interpreters.

The same format is counted at larger power-of-two Q with U128Q. The
first tested power-of-two scale at which the native prefix alone fits
one colony is Q131072. This is an encoder-specific native-prefix result,
not a sufficient Q for its complete self-programme, and not the
smallest change that makes Gray reliable. Merely lengthening U cannot
fix Q8192's programme-storage failure. Parallel programme fetch alone
also cannot repair its space failure. A new compact word/loop encoder
is required if Q8192 is retained.

**What remains open.** No final whole-rule alphabet/layout, physical
interpreter/service equation, compact self-beta, self-referential hardwirer
or period composition is claimed. The failure occurs before those can
be emitted in this evaluator family. The frozen GT0/GV0 checkpoints and
their component scopes remain unchanged. No legal-noise counterexample
to a fully specified Gray rule, decoded memory failure, iid threshold or
global reliability proof follows from a compiler/evaluator fit failure.
