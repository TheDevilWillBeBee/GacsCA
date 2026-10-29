# GBD3: a finite compact Head/controller and literal write windows

The target stays Q8192, U128Q=1048576, lambda24 and original integer
c104. This checkpoint supplies an explicitly changed **component**, not
an autonomous Gray automaton or a full own beta. It leaves the frozen
GBD0/1/2 and all active/accepted rules unchanged. No error history, positive
noise rate, Gray refutation, or shorter U is asserted.

The component has an actual finite interpreter, an immutable **counted
binary beta parameter**, real five-slot Head/Mem/Out accesses, issued
word-copy programmes and two real shared field-access software helpers.
It has no native/full-R instruction,
mutable stack, large instruction dictionary, virtual-register callback or
out-of-Q fetch. Its computed native Address/Age are explicitly declared
input ports, not secretly supplied by a host evaluator. Native composition,
the complete stage schedule and the software for its own entire rule remain
unproved.

## 1. Fields, code resource and total equations

[controller.py](controller.py) defines the local block. A Head has presence1,
movement2, mode2, PC13, return13, target13 and eight Word20 registers:204
binary bits. Each Head, Mem340 and Out20 field has five independent raw
slots. Physical x/slot q represents logical x+S[q], where
S=(0,-2,-1,1,2). The five holders of logical y are y+S[h], with actual
slot INV[h]=(0,4,3,2,1)[h]. Each field is bitwise3/5-voted there.
The Head vote is over204 bits; it does not silently choose one whole
coherent raw Head. Every combination of its fields has defined semantics.

The immutable code is one actual binary string beta of length at most8192.
It is a separately counted fixed-rule resource. It is **not** Gray's
gathered/mutable ProgrammeBits protocol. There is no other instruction or
control data dictionary. The ISA enum/field widths and the18 generic ALU
functions describe circuit wiring; they are not a second code store. The
eventual full beta must contain every transition branch/descriptor, not
only the two issued copy programmes here.

The decoder uses the actual13-bit raw PC, including nonaligned PCs. An
operand extending beyond beta, a LIT width21..31, or opcode15 is INVALID
and halts the Head. CODE reads up to20 bits of this **same beta** at the
whole raw Word20 index: outside-beta bits are0, and counts above20 give0.
No index is silently reduced moduloQ or redirected to an oversized stream.
This self-code read is a generic finite bit lookup, not a whole-rule opcode.

| Opcode | Bits | Defined operation |
|---|---:|---|
| HALT | 4 | clear presence, stop |
| LIT | 12+n, 0<=n<=20 | write one bounded literal |
| ALU | 18 | immediate-function Word20 operation |
| BR | 26 | one of eight total conditions/direct PC13 target |
| READ | 17 | actual voted local packed input bits |
| READQ | 17 | generic diagonal lane/slot bitwise quorum |
| WRITE | 14 | literal output masks described below |
| CODE | 13 | bounded read of the one beta |
| MOVE | 7 | enter travel toward a register's low13 bits |
| CALL | 17 | overwrite the one13-bit return link |
| RET | 4 | jump to that link |
| GETHEAD / SETHEAD | 10 | read/write enumerated scalar metadata |
| ALUR | 16 | register-selected generic ALU function |
| QUORUM | 26 | generic five-word equality quorum or bitwise vote |

All registers are actual carried Word20 Head fields. There is no RAW80
return-bank ABI. CALL supports exactly one link; nested software calls must
save it using counted state/code or overwrite it according to the defined
equation. No stack or caller-liveness theorem is assumed.

ALU arithmetic wraps modulo2^20; division/modulo by0 return0; shifts by
at least20 return0. Functions18..31, or other raw function words in ALUR,
return0. QUORUM equality selects a word occurring at least three times,
otherwise its supplied fallback. Two different such quora cannot coexist
among five words. The bitwise case uses ten triple-ANDs independently at
each bit. These ordinary finite operations are not native CA evaluators.

At physical holder x/copy q, the logical actor is y=x+S[q] and its service
Address is `(computedGF(x)+S[q]) modQ`. Its time port is computedAge(x).
The actor votes Head at y and y±1. A stationary self Head takes priority
over incoming left, then incoming right; this is an explicit malformed-
collision convention. A travelling Head moves one cell toward its target
within the service colony, settles into RUN on arrival, and executes its
next instruction on the following update. A stationary Head executes one
decoded instruction. Invalid modes clear the Head. The source movement
word is carried metadata; travel eligibility is derived from mode/target
and the declared service Address, not trusted from a forged move bit.

READ's first actual container is Head−2. It extracts count0..20 bits of
one lane0..16, at phase0..19 and stride1 or5. It votes all five actual Mem340
slots at each container before extracting. Every malformed descriptor gives0.
This is the corrected physical-slot component of GBD1, with incoming-centre
c=0 because arriving travel Heads do not execute instructions on that row.
No virtual tape is substituted for those actual reads.

READQ is an explicitly added generic field-access operation. For bit i,
each outer holder h selects lane `lane+S[h]` and stream position
`phase+stride*i+INV[h]`. It first votes the five real lower Mem340 slots
at the corresponding container, then thresholds the five selected bits.
Thus it has two levels of five-bit vote, not one25-bit threshold. Admitted
lane centres are2..14, phase0..19, stride1/5 and count0..20; every other
raw descriptor gives0. Maximum stream index is19+5*19+4=118, still six
containers at Head−2..Head+3. Its actual source offsets lie in[-6,+7],
with the same INV source identity. No stored helper table or extra state
is introduced. This is generic vector field access, not a native evaluator.

The purpose is precise: in a lower packed input bank of17 **raw upper
records**, a five-backup upper SF bit b has raw record coordinates
`fieldBase+5*b+INV[h]` in upper cell `centre+S[h]`. READQ extracts its exact
upper bitwise3/5 vote in parallel. Upper raw holders may be incoherent;
only the lower input bank's real five-copy encoding is a premise. This
removes the serial five-holder reads for those field words, without asserting
that the entire transition or its own interpreter programme now fits Q.

## 2. Literal WRITE and the scoped radius obstruction

There are three separately declared interfaces; they do not alter prior
rules. A stationary old Head executing WRITE supplies data, phase, count
and stride1/5 from actual registers. Invalid phase/count gives no patch,
while the Head consumes the instruction normally. Bit i of its data updates

    output container = Head + base + floor((phase+stride*i)/20)
    output bit       = (phase+stride*i) mod20.

At receiver y the literal equation votes old Out20, votes each possible
source Head using the real INV slots, decodes that Head's beta instruction,
and applies the indicated mask. Multiple old WRITE Heads use increasing
source-coordinate priority, bit by bit; all collision cases are defined.
Arriving/computed Heads do not write on that same row. There is no source
packet list or external word-deposit callback in the local function.

**One-sided16, base0: radius8, proved.** The maximum container displacement
is floor((19+5*15)/20)=4. For output holder x/role q, receiver y=x+S[q],
source Head z=y−chunk, and its physical holder d=z+S[h]. Thus every raw
source offset is `S[q]−chunk+S[h]`, within[-8,+4]. Old Out reads stay
within radius4. The actual source slot is INV[h], and
`d+S[INV[h]]=z`. The controller and READ require radius at most7; therefore
the complete declared one-sided16 component is radius8 on every raw state,
without any canonical-GF/clock/Head premise.

**One-sided20, base0: radius9 for this stipulated function.** The last
container can be5 away. The exact receipt gives two complete raw inputs
equal on[-8,+8], but differing at physical−9. Observer x0/role1 represents
receiver−2; a WRITE Head at−7 deposits its last bit into receiver−2. Two
of its five holders have presence1 and two presence0. Changing the fifth
presence from0 to1 at−9 changes the voted Head from absent to present;
all other Head/control/payload bits agree. The output changes0→2^14.
Consequently no radius8 function on these same input fields can equal
this stipulated one-sided20 operator on all raw states. This is a component
cofactor obstruction, **not** an architectural lower bound, physical-noise
counterexample or Gray claim. Balanced positioning removes it.

**Balanced20, base−2: radius7, proved.** Its six containers run from Head−2
through Head+3. A receiver's source offset is now
`S[q]+2−chunk+S[h]`, within[-7,+6]. Thus every five-holder request is local
within7; it supports all20 stride-five bits. This balanced base agrees
with READ and avoids the extra movement of the one-sided split below.
It is an explicitly changed generic word primitive, not Gray's binary
Write protocol. Allowing incoming-source execution would require its own
equations/analysis; that feature is absent here.

The earlier planning statement that a20-bit write required9 applied only
to base0. It must not be read as ruling out this balanced component or
other radius8 architectures.

## 3. Two real issued programmes and conditional raw execution

[check_controller.py](check_controller.py) emits and executes actual beta
bits through `local`, not through a host word-copy primitive.

The balanced programme is93 bits/seven instructions: set lane0, phase0,
count20, READ; set phase19; WRITE stride5; HALT. The one-sided programme
is207 bits/15 instructions. After READ it writes16 bits at phase19, shifts
the carried data right16, sets count4, computes current Address+4, MOVEs
four real cells, writes the remaining4 bits, and HALTs. The second phase
is still19 because19+5*16=99=4*20+19. No bits overlap or are omitted.

**Conditional universal copy theorem.** Assume a single coherent Head in
RUN/PC0 at interior h, canonical/common native ports, coherent Mem/Out
copies, and no errors during this component execution. Every initial
register, return, target and movement word may be arbitrary; the programme
overwrites every value it uses. Let A be lane0 Word20 at actual container
h−2; all other Mem payloads may be arbitrary. Old logical Out20 values may
also be arbitrary. Then the balanced code halts after7 actual updates and
overwrites exactly bit i of A at container

    h−2 + floor((19+5*i)/20),  bit(19+5*i) mod20,

preserving every other old Out bit. The split code does the same with base h,
halts after19 updates, and visits only h..h+4. Its extra four updates are
actual travel; no instant relocation or future head/tape is supplied.

**Raw-copy closure.** Under canonical/common ports, each holder/copy q
calls the same logical actor at y=x+S[q]. The INV vote returns that logical
field, for arbitrary coherent field values. Instruction decode, source
collision priority, READ and receiver patches then agree across all five
holders. Therefore the actual raw block is exactly the five-copy encoding
of its logical operator at every update. This applies even to arbitrary
coherent logical Head patterns; the unique-head premise is needed for the
specific copy-programme execution, not this closure identity.

**Universal data and initial-state proof.** All control and movement in
these two issued programmes are independent of A. The only A operations
are READ, the fixed right16 shift and masked deposits of its individual
bits. Each targeted output bit is exactly one distinct A bit; every other
bit is the corresponding old Out bit. Hence the conclusion holds for all
2^20 values A and all old Out values. The checker supplements this algebra
with actual raw zero/20-basis/all-ones executions, independent initial
registers, and verifies every five-copy field after every update. It does
not substitute those22 runs for the universal proof.

The finite replay is an exact infinite-line restriction: outside the shown
interior cone the Head stays absent, Mem is unchanged and old Out is held.
The initial exterior is specified by that rule, not zero-padded arbitrary
boundary dynamics. No native error or recursively intact initializer is
assumed or constructed here.

**Actual upper-field reader,100 bits.** The new [layout.py](layout.py)
counts all proposed native/SF bits and gives Head register0's first raw
column2587 (`HeadBase2367+5*44`). In the actual170-container input bank
its chunk is129 and phase7. A100-bit/seven-instruction programme sets
lane centre8, phase7, count20, executes READQ stride5, then writes the result
at phase19 and halts. It starts at physical Head=P+129+2. The checker
constructs the input from entire arbitrary17 raw K-bit upper records,
including arbitrary native words and incoherent SF holders; it does **not**
insert an expected word into lower registers/Mem. Its actual raw output
equals the literal upper five-slot vote of register0. Eight arbitrary
full-record runs and20 upper-field basis runs supplement the universal
index/vote identity. The helper works for every raw upper record value
under the coherent lower-bank premise. It is a prepared-bank component,
not an autonomous gather or a complete own-beta evaluation.

### 3.1 Actual shared FGET/FPUT software and liveness

[helpers.py](helpers.py) issues two actual nine-instruction helpers. FGET
is **140 binary code bits**, FPUT is **137 bits**, and a complete
seven-instruction caller with both helpers is **396 bits**. These are ordinary ISA instruction sequences,
not additional hardware opcodes or host field-access callbacks. The caller
contains both real CALL addresses119 and259; its HALT is at115. Every
instruction and target is within the counted396-bit stream. There is no
additional descriptor table, return bank or stack.

FGET's inputs are R0=b (the raw record-bit coordinate of slot0 of the
first requested logical SF bit), R1=n (0..20) and R2=lane centre (2..14).
It computes b%20 into R3 and b//20 into R0, adds the counted constant
P+2, travels there, READQs n bits with stride5 into R0, then RETs. The
three constants20,20,P+2 use17,17,24 bits, respectively. Its six other
instructions use18,18,18,7,17,4 bits, giving140 in total. FGET preserves
R1,R2,R4,R6,R7 on every one of its instruction and travel updates. Its
clobbered registers are R0,R3,R5; its target/mode and one return link have
the explicitly declared semantics.

FPUT inputs are R0=data, R1=n and R2=b+q, where q is the output copy slot.
It computes the stream phase into R3 and container index into R2, adds
P+2, travels there, WRITEs stride5 using balanced base-2/cap20, then RETs.
Its WRITE is14 bits, three shorter than READQ, hence the137-bit size.
It preserves R0,R1,R4,R6,R7, and clobbers R2,R3,R5. Both helpers make no
CALL themselves: the one return field written by the caller remains
unchanged throughout each helper and RET returns to the exact caller
continuation. Saving a link for nested calls is not claimed.

**Universal prepared-bank/helper theorem.** Take arbitrary raw K-bit
upper records at lanes -8..8, including arbitrary and incoherent upper
SF copies. Let a lower prepared Mem bank be their actual coherent
17-lane packing. Assume canonical/common computed native ports, one
coherent RUN/PC0 Head at P+2, arbitrary coherent old Out, no other Heads,
and no errors while the396-bit caller executes. All initial registers,
return, movement and target may be arbitrary. Select a represented
logical SF word whose slot0 base is b, with all n requested bits within
the same declared field, and q in0..4. Then FGET returns its actual raw
upper five-holder bitwise vote and FPUT writes precisely those n bits
into output coordinates b+q+5i, preserving every other Out bit. R4,R6,R7
retain their arbitrary initial values throughout the entire caller.

The proof first computes phase/index using exact nonzero divisor20.
At Head=P+floor(b/20)+2, READQ's outer h selects upper lane
`lane+S[h]` and raw column `b+5i+INV[h]`. The inner lower vote
reconstructs that actual raw record bit. Thresholding the five upper
bits is therefore exactly the upper SF vote. At output Head
P+floor((b+q)/20)+2, balanced WRITE places bit i at raw coordinate
b+q+5i. No projection or coherent-upper assumption occurs. The absence
of data-dependent control, and these literal bit/index identities,
prove the statement for all raw upper records and arbitrary old Out.
Register liveness follows by inspecting every helper destination;
travel preserves all eight registers and the link. CALL/RET arithmetic
is over actual13-bit PCs, and no truncation occurs at these addresses.

The entire caller executes25 instructions. Travel to the input takes
`max(1,floor(b/20))` extra updates: a MOVE to its present position
still settles for one update; arrival from a distinct site settles
on its last travel update. Input-to-output travel takes exactly1 extra
update because adding q changes the container by0 or1. Thus the exact
total is

    26 + max(1,floor(b/20)) updates.

For Head register0, b2587/chunk129, this is155 actual updates; for
register7, b3287/chunk164, it is190. These are prepared component
deadlines, not a full late-pass bound. All positions stay within the
interior input/output frame, and each emitted CALL target points to
the actual helper in the396-bit beta.

The checker executes eight complete callers through the literal raw
`local` equation: all five output slots of register0, register7/slot4,
an Info bit with lane centre2, and count0 with lane centre14. It checks
the five-copy Head/Out closure after every update, all actual READQ
results, the unmasked output bits, both actual RET PCs, and preservation
of R4/R6/R7 from arbitrary initial Word20 values. The sparse replay is
an exact restriction: only old Head halos and actual WRITE receiver
halos can change; every other coherent Head is absent and Out is held
by its literal voted equation. This gives a finite faithful execution
of the component, not prescribed future Head or a prepared result word.

The first shared-helper checker failed its size assertion: FPUT had
been mistakenly counted140 instead of137 bits. Its exact sources and
log are retained under failed attempt03; the corrected396-bit caller
retains the same semantics and instruction/tick counts. That failed
check is a component accounting defect, not a Gray construction failure.
Attempt04 then reached all helper executions but failed its final size
assertion because a checker loop index shadowed the imported helper module.
Its source/log are also retained; the corrected module alias changes only
the checker, with no transition change or passing claim from that attempt.

### 3.2 Fresh K3387 packing and actual reset/birth binding

[packing_kernel.py](packing_kernel.py) and [check_packing.py](check_packing.py)
instantiate the GBD2 equations **afresh** with this new K3387 layout,
P2403 and170 chunks. They do not import the old K3262 kernel. The unchanged
generic source-set and route proofs apply after the new bounds are checked:
seed at computed-port Age72Q+3, nineteen left merges, load at72Q+23,
and maximum travel3217. The last packing action has computed-port Age
593064, strictly below73Q. There are3387 seed/load positions and64353
merge identities; every one is rechecked using the new constants, as are
every transport row and each actual inverse-slot port.

For clarity, these ages label the **computed native input port used by
each synchronous local action**, not a separately asserted raw-clock
trajectory. The last packing action outputs the170 complete packets.
The next action, port Age593065, births a Head, and the following action,
port Age593066, executes its first instruction. The native rule producing
these ports and their relationship to an autonomous raw clock remain open.

Let the three coherent History banks contain arbitrary17-lane binary
columns at each represented primary. Their temporal majority is packed
without examining or changing its data values. At seed, every column
occupies a distinct bit phase within its chunk. After nineteen merges
each chunk end contains exactly that chunk's columns. Load retains only
those ends and the final partial chunk is masked to its seven real columns.
Packet h then follows

    position_h(e) = max(P+h, source_h-e),

so two packet positions never coincide, and every payload is held intact
at its destination. The proof includes the actual raw lower-slot vote,
conditional on coherent fields and canonical/common computed native ports.
It does not assume remote packet lists as an input to the local rule.

[binding_kernel.py](binding_kernel.py) defines the new **total local
component** joining packing and the Head controller. Its History/data/tag/
valid/Head/Out fields have actual raw five-copy slots. During computed
ages SEED..DONE it clears every Head slot. At BIRTH=DONE+1 it writes a
zero-register RUN/PC0 Head precisely where `(computedGF(x)+S[q]) modQ`
equals P+2, and writes an absent Head in every other slot. In both reset
and birth rows, Out is voted old Out; no forged old WRITE Head can act.
Other ages use the literal old Head/Out CPU equation. Packet packing and
CPU read **old** data independently in the synchronous update. All missing
native/gather/other-field operators remain absent; this component is not
represented as a complete CA.

**Conditional packing-to-software theorem.** Assume the stated quiet
native ports and coherent History inputs. If two banks hold the same
arbitrary raw upper17-record columns and the third is arbitrary, then
their actual temporal majority is that raw record bank. The fresh packing
equations construct the real Mem340 bank by the last packing action.
Reset clears arbitrary old Head copies. The next birth creates exactly
one coherent Head in the interior frame of each native colony. The bank
is held during the following396-bit helper caller. Therefore the theorem
of3.1 applies to this **derived** bank and Head, with first execution
port593066. All data/Head/Out words are derived from the same prefix;
there is no independently assigned future tape or Head.

The packet positions and the entire helper path lie far inside one
colony. Other simultaneously born colony Heads have disjoint execution
cones for these at most190 updates. The finite raw replay explicitly
checks reset and birth, all five slots, then the actual helper execution.
It derives the170 packets from the two good/one arbitrary History banks,
rather than inserting the expected field word. Three complete cases
cover register0/slots0 and4 and register7/slot4. The symbolic proof above
supplies the universal record-value statement; these cases supplement it.
The origin of the two good History banks in authentic gathers is still a
premise. There is no noisy or whole-period conclusion.

## 4. Resource account and remaining whole-rule obligations

Replacing the old179-bit proposed Head by this204-bit Head adds25 logical
SF bits. Keeping GBD0's other listed fields gives670 logical SF bits and
37 native bits: **K=37+5*670=3387; 2K=6774<=8192**. The native/output
ports used in this component account for33 bits; Head/Mem/Out slots account
for5*(204+340+20)=2820. The remaining4 native bits and530 other SF bits
are only counted proposal fields, not supplied transition equations.
This is a complete count of the listed proposal, not a full-state rule
or code-fit proof. The two small issued programmes do not evaluate it.

The immutable binary beta must also be counted, with length<=8192; only
the93/207/100-bit standalone programmes and396-bit helper caller
are issued here. There is no second dictionary,
code stream, mutable return stack, or controller data table. The ISA circuit
and arbitrary-beta decoder are specified; whole gate count, full own software,
all descriptor/control bytes and universal whole-programme runtime are
unproved. In particular, no host/native evaluation is used to claim an
own-beta identity.

Frozen GBD2's K3262 packing trajectory is **not automatically a caller**
for this enlarged K3387 record. Section3.2 supplies a newly checked
170-chunk instantiation and conditional computed-port reset/birth binding.
Authentic three gathers and
late output expansion, Head birth/reset, computed-SimBit/wipe/Workspace
order, mutable ProgrammeBits refinement and every passive stage remain
integration obligations. The supplied native ports could themselves be
damaged; that composition is unproved.

| Step | Status |
|---|---|
| Total finite Head/ISA decoder/controller | proved component |
| Actual inverse-slot READ/WRITE/Head accesses | proved |
| One-sided16 radius8 / balanced20 radius7 | proved component |
| One-sided20 stipulated radius8 impossibility | proved all-raw cofactor |
| Raw-copy closure under canonical/common ports | proved conditional |
| Actual93/207-bit copy programmes,7/19 updates | proved conditional |
| Actual100-bit upper raw SF-word reader | proved conditional lower-bank identity |
| Actual140-bit FGET /137-bit FPUT /396-bit caller, register/link ABI | proved conditional prepared-bank component |
| Fresh K3387/170-chunk literal History packing | proved conditional quiet-port component |
| Computed-port reset/birth and derived-bank software binding | proved conditional component |
| Proposed K3387 binary layout inequality | proved count only |
| Complete own beta<=8192 / whole software runtime | unproved |
| Autonomous native/gather/reset/birth/whole-period composition | unproved |
| Gray programme/rest/final-source refinement | unproved |
| Error-map, positive epsilon, iid or Gray refutation | unproved |

Read-only reproduction will pin every inherited frozen component and
recompute every new equation/witness/programme check. No active rule or
main report is edited.
