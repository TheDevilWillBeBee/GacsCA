# GBD4 raw-role Head movement radius erratum

The frozen GBD4 proof says that Head movement uses radius3. That is the
support relative to a **logical Head centre**, not a raw output site.
Its component conclusion radius at most7 remains correct. No frozen
source, programme, field, native contract, runtime or constant is changed.

In the literal actor, output role q at physical x uses logical centre
y=x+S[q], S=(0,-2,-1,1,2). Movement examines Head votes at y+d,
d in{-1,0,1}. Each vote reads raw Head slots at y+d+S[h], hence at
x+S[q]+d+S[h]. All such source offsets lie in[-5,5]. Therefore the raw
movement support is at most5, and the radius7 READ/WRITE component bound
continues to cover it. Computed native ports are still explicit premises;
this does not establish full-rule locality after their composition.

The bound5 is necessary for this raw actor operator. Take x=100, q=1,
y=98, and canonical native ports. Place a present travelling Head with
target99 in two of the five raw slots voting the left Head at97, with
every other Head word0. The two witnesses are site97/slot0 and
site96/slot3. The own Head vote at98 and right Head vote at99 stay0,
because their voting slots differ. Change only site95/slot4 from0 to
that same Head word. The left vote now has three equal witnesses, becomes
the travelling Head, and the actual actor emits a present right-moving
Head at output role1. Before the change it emits an absent Head. Thus
changing only a raw site at x-5 changes the output, disproving any raw
radius3 or radius4 bound for this operator.

The checker evaluates these **two exact inputs** against the frozen actor
and enumerates the complete75 source-offset sums. This is a finite
functional cofactor proof, not a noisy trajectory or Gray counterexample.
Status: **proved component erratum**. General self-simulation, autonomous
native ports, whole-period/error repair, iid reliability and faithful Gray
refinement remain **unproved**.
