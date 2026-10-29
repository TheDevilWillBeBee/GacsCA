This is the simpler fixed-GR1 split-snapshot witness. Its initial upper
state differs from a coherent-zero upper state only on one current upper
E0 pair. It refutes a period lifting claim that permits that independent
initial upper fault together with a later lower real1 core. It is not a
proved counterexample from Gray's intact hierarchy or to iid reliability.

Use the same GR1 rule F, Q8192, U1048576, pinned ROM, broad lower encoding
E and decoderΔ5. Define upper b with Address_i=i mod Q, Age0, all Flags0
and all simulation fields0. Its Info copies are coherent0. It is a
coherent-zero simulation context, not a fully recursive hierarchy: the
upper Info string does not encode the next level's canonical geometry.

Let z differ from b only in these four raw upper Info copy bits:

    holder1 slots1/2 =1,
    holder2 slots0/1 =1.

Thus z=b outside the adjacent pair{1,2}. Regard that overwrite pair at
upper clock0 by itself. It is exactly one upper E0 group; no other upper
error is specified in that classification. Logical upper Info0 and Info1
each now have two1 copies (held at1/2) and three0 copies. The deciding
copy held at upper0 (slot2/3 respectively) is0. No upper native field
or Flag is changed. In particular upper cell0 is entirely0.

Encode z at lower time0 in E(z), with unrepresented lower logical Info0.
Run cleanly to T=32Q+1=262145. Upper Info slots2/3 have pinned lower
primaries a0=4092 and a1=4188. At T overwrite only these six holders:

    4091,4092,4093,4187,4188,4189.

At x=a+d, d∈{−1,0,1}, set the logical-copy components Info(a)=1 and
Mailbox.R(a)=1, using copy slot2−d. Every other bit remains correct.
In particular Mailbox.L(a)=0 and History2-own(a)=0 are not overwritten.
There is no clock, Address or Flag overwrite. The set is one original
real1 error: its total point width99 and duration1 give condition(iii)
with c104, each three-holder core has no E0 point, and condition(iv) is
vacuous for this isolated six-point error set. The exact classifier agrees.

**Physical injection and period composition: proved for GR1.** The64
complete lower netlist cofactors prove13120 output/lookup identities.
At T+1 the only altered logical fields are Info(a)=1 and the right-going
Mailbox.R packet at a+1=1, each with five coherent copies. Retained
History1 is free/coherent in those cofactors. History2-own remains0;
all other outputs match the clean transition. This gives the literal
post-injection coherence premise for the existing exact transport,
frame/pending, fetch and own-programme certificates.

Native geometry remains correct. The simulated native inputs are unchanged
by this Info-only event, so both early flag results are0. Couriers write0,
the Workspace pulse supplies no source, and every lower Flag stays0.
Hence mail is unblocked and GF-mismatch wipe0 throughout the period.
The changed Info sites are distinct from3 and Q−3 and persist until the
usual boundary. History1 has already captured old0; History2 receives
old0 to the left and at self, but new1 to the right; History3 receives
new1 in all directions. The temporal vote sees source upper0's Info
slots2/3 as0 for receiver j≤0 and1 for receiver j>0.

Define q^(j)=z for j≤0, and z with upper0's Info slots2/3 changed to1
for j>0. Each final physical replay has exactly that local input window.
The actual ROM/front/write identities therefore give

    Y_j=F(q^(j))_j,       X_U∈E(Y),       Δ5(X_U)=Y.

This uses the same explicit physical composition as GR1_REAL1_SPLIT_BOUNDARY.md,
with the own-history overwrite removed. Copy coherence is established by
the new local certificate; it is not assumed through a three-holder error.
There is no long sampled simulation in this proof.

**Boundary contradiction: proved.** At upper computed Age1, each Info
output is its fixed five-holder majority. The two other1 backups make the
value depend on the perceived upper0 copy. Full literal upper cofactors
give

    logical Info0, holders−2,…,2: (0,0,0,1,1),
    logical Info1, holders−1,…,3: (0,0,1,1,1).

The22 upper/reference cofactors also find Y≠F(z) exactly at upper holders
1,2,3. Beyond the radius5 source window the states agree by locality.
No other field can enlarge that support: at computed Age1 only Info,
mail loads and History1-own use the changed Info copies, all on the same
two logical groups; all other outputs are unchanged.

For any v=z outside one adjacent arbitrary upper input pair P, all native
Address/Age votes restore canonical/common values, inconsistency is false
and computed Flags0. This is the same two-error native closure as in the
previous proof and does not require coherent input simulation copies.
Computed Age1 and wipe0 force every Info group of F(v) to have one common
vote across its holders. If Y=F(v) outside an output pair R, the first
pattern must use common vote0, forcing R={1,2}; vote1 would require three
exceptions. The second must use common vote1, forcing R={−1,0}; vote0
would require three exceptions. Those pairs are incompatible. Therefore
no independent adjacent input/output pairs P,R make this boundary step
a noisy upper tick. The counterexample already holds when the initial
upper perturbation is just one E0 pair of a coherent-zero state.

**Independent upper operational variant: proved.** Let b0 be the coherent
baseline above and b1=F(b0). Its native Address is canonical and Age1;
its Flags and all simulation fields are0. Canonical native closure gives
the Address/clock assertion. All native forcing bits are0; computed Age1
is outside the Workspace pulse. The stage route at Age1 only loads zero
mail and captures zero own input, while the inactive front/pending fields
are0. The exact route/frame certificates therefore prove the remaining
zero-field assertion at every Address, without sampling upper phases.

Overwrite the same four Info bits in b1 at upper holders1/2, at upper
tick1. This is one isolated upper E0 pair for that independent upper
process. The new upper z1 has native Age1 instead of0. The22 additional
upper/reference cofactors at computed Age2 give exactly the same two
Info patterns and bad-holder set. The lower physical composition is
also unchanged: local injected lower Info primaries still contain0,
the other clock-bit inputs are consistently Age1, and both early native
Flag results remain0. Thus the boundary-map counterexample holds from
E(z1) as well. This establishes operational reachability in an independently
noised upper copy of F; it does not realize the upper error from the same
physical noise set as the later lower core. At lower initial boundary U,
the represented upper Age1 also has the expected macroclock value.

**Hierarchy/isolation audit: proved exclusions and open reachability.**
The initial upper pair is not a new independent noise source in Gray's
model. Gray starts one physical configuration and one physical error set E;
upper faults must be consequences of the same E and the simulation. His
intact initialization makes the backup Info copies coherent at every
level (primary PDF page33 / text lines1488–1524). The z above fails that
initialization, even though b has coherent-zero Info.

Here are distinct facts; none is a substitute for the others.

1. As an explicitly allowed initial state E(z) with only the six later
   physical errors, the GR1 witness is admissible and its core is real1.
   Any theorem for E(upper-E0-perturbed coherent states) plus an independent
   real1 core must therefore add hypotheses or use a different rule.

2. If a nearby earlier non-E0 physical point is used to generate the
   upper pair, the later six-point core may cease to be real1. Condition(iv)
   requires S and E\(S∪E0) to be(24Q,24U)-separated, i.e. every exterior
   non-E0 point must have spatial distance at least196608 or time distance
   at least25165824 from every point of S. This is primary page17 /
   text lines745–751. Upper faults cannot be grafted onto an isolated lower
   error without checking that complete physical set.

3. The receipt gives an exact geometric example. Shift the witness's
   initial boundary to lower timeU, so its new core occurs atU+262145.
   Propose an earlier physical core at sites2Q−1,2Q,2Q+1 and timeU−1.
   Alone it is real1; with the later core, both are linked at(24Q,24U).
   There are no E0 points. The maximum pair distances are12294 cells and
   262146 ticks, both far below the required distances. The later core
   therefore fails condition(iv). Indeed all proper subsets have linked
   exterior points, and the whole union is too wide for a Q×U candidate1;
   the combined set contains no real1 errors at all. Its two disjoint
   candidate1 cores are linked at the level2 scale, the union fits the
   level2 size bounds, has no104Q/104U-separated candidate2 subsets and
   has empty exterior. The full union is one original real2 error.
   This example does not claim that those three earlier points actually
   generate z; it certifies the isolation obstruction for that proposed
   nearby source geometry.

4. Pure lower E0 histories starting in E(b) cannot generate this decoded
   upper pair at a boundary, by the accepted continuing pure-E0 theorem.
   That theorem allows arbitrary replacements and fresh boundary errors
   and its robust decoder still returns F^n(b). Some earlier non-E0
   physical event or a different initial condition is required.

5. The new boundary's actual bad upper holders1,2,3 at upper tick1 are
   not E0 locations even by themselves. Together with the manually supplied
   pair1,2 at upper tick0, the illustrative five-point upper location set
   has no E0 points and is upper real1. It cannot be treated as two isolated
   upper E0 events. This classification concerns assigned bad locations;
   it is not an independent injection experiment or a proof that the full
   physical hierarchy realizes those events.

The remaining step is unproved: exclusion or construction of every earlier
physical history that could reach this context while satisfying global
level1 isolation and intact recursive initialization. The nearby-source
example does not exclude distant/old sources or more complicated higher
errors. Conversely, the standalone boundary witness does not establish
that one of those admissible histories exists. Reusing Gray's desired
simulation-recovery proposition to rule out every such history would be
circular in an audit of that proposition.

The needed operational hypothesis must control upper Info copies near a
new lower real1 core and couple their allowed defects to the full physical
error set and its separation. It cannot simply permit an arbitrary current
upper E0 pair independently of that core. Proving the appropriate invariant
or modifying the protocol remains open. Literal Gray refinement and all
iid conclusions remain unproved; active rules are unchanged.
