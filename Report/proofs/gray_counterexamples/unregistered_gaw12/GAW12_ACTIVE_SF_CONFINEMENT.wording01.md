# GAW12: actual late simulation-field faults, confinement and a padding obligation

This checkpoint concerns the **unchanged frozen GAW2R rule**, with
Q=8192, U=128Q=1,048,576, lambda=24 and c=104. It changes no transition,
ROM, schedule, active G17 file, registered report or checkpoint. It does
not refute Gray's construction, a Gray deterministic proposition, or an
iid-memory theorem. It establishes a restricted confinement lemma and
six exact intact-start positive repair instances. One instance also
disproves an additional, explicitly stated narrow-encoding shortcut.

The radius8/17-lane WORD100 representation, h1 Flag2 correction,
computed-holder service Address, immutable large instruction/dictionary
lookup, bounded couriers, early native-only pass and revised102Q late
start remain material departures from Gray. GAW2R's direct emission is
41,162 bits with1,049 distinct dictionary words and270,349 immutable code
bits; it does not meet beta<=Q/dictionary512. Its raw alphabet has49,037
bits, represented by496 WORD100 positions. None of these storage or
schedule gaps is closed here. No shorterU or positive iid rate follows.

## Statements and exact chronological window

Let F be the exact frozen rule from
[gray_three_gather_gaw2r.py](../unregistered_gaw2/gray_three_gather_gaw2r.py)
with the immutable own ROM emitted by its frozen whole compiler. Use the
infinite-line recursively intact H of
[GAW4](../unregistered_gaw4/GAW4_INTACT_REAL1_MAIL.md), with H in E(H,0),
including its actual Programme bits at every level. Let X(t)=F^t(H).
The phase convention is that an error at (x,t) replaces a cell of row t
after its clean update; the following update computes row t+1.

**Late SF confinement theorem (proved).** Choose integers b, w, with
1<=w<=16. Allow arbitrary replacements of the thirteen SF tracks,
including every Head, Mem, Out, Scratch, Info, Programme, History, Mail
and courier bit, at physical sites in B=[b,b+w). All replacements retain
the actual six native fields. Allow errors on at most sixteen consecutive
rows, all within the **closed interval 102Q+2 <= t <= 120Q**, and no other
errors. The SF replacement need not be coherent, nor a valid head or
instruction record. Then native GF remains x modQ, native Age remains
t modU and all four native/workspace flags remain0. Before the first U
boundary, all computed SF differences from X(t), and all raw SF
differences except current overwrites, are confined to one fixed adjacent
pair of colonies containing [b-1,b+w+1). At U all work resets and all Info
copies are coherent. The represented496-word upper records differ from
F(H) only within that same adjacent pair. Unrepresented Info in those
colonies may also differ.

The entire chronological restriction matters: the third gather's last
capture is72Q+2, the real late reset is102Q and birth102Q+1, while the
Workspace source guard is96Q<=Age<98Q. Thus this theorem excludes errors
during gathering, the early pass, flag couriers and the Workspace source
window. It does not assert confinement for earlier SF/Info faults or for
native GF/Age/control replacements. The sixteen-row bound matches the
requested burst family; the spatial induction itself does not use a
temporal separation assumption.

**Conditional2U corollary (proved).** In this theorem, if the six native
WORD100 words of every affected upper record at U have their legal
padding, the actual boundary is E(Cprime,Aprime) for a legal upper
configuration Cprime. Then the complete infinite-line physical state at
2U equals F^(2U)(H), and remains equal at every later tick with no errors.
The padding premise is not automatic for arbitrary Out faults.

**Selected-history result (proved by exact finite execution and physical
composition).** The six complete physical error histories below are
actual original-c104 real1 errors from that same H. Each recovers
completely by2U. Five have legal native padding at U and use the
conditional corollary. The sixth has illegal native padding at U; its
actual eighteen second-period banks and full executions are certified
separately, without applying the legal-upper-state period theorem.

**Rejected shortcut (proved false).** The stronger assertion that every
such real1 SF burst produces literal E(Cprime,Aprime) at U for some
legal Cprime is false. The sixth history supplies an exact counterexample
to that assertion for this changed implementation. This shortcut is not
an assertion of the frozen noiseless or pure-E0 theorem, and its failure
is not an operational or Gray counterexample.

## 1. Frozen source identity and the actual fault row — proved

[check_gaw12_active_sf.py](check_gaw12_active_sf.py) imports the frozen
GAW2R local kernel and its exact own ROM, through the frozen GAW11
diagnostic imports. It never supplies a future tape or command. The
standalone manifest pins all inherited GAW11 assets, the earlier physical
period/own-programme proofs, actual emitted ROM, primary papers and all
new sources/receipts. The read-only validator checks every hash before
and after execution, checks the exact dataclass ROM against its emitted
JSON, replays the frozen period validator, and repeats all new checks.
No new CA rule is introduced.

The intact initializer is the terminating recursive I/H definition of
GAW4. With S=(0,-2,-1,1,2), P=3848, H has canonical GF, Age0, flags0,
Info copies I(x+S[h]), Programme copies beta((x+S[h]) modQ), and reset
work. The actual three quiet gathers produce, at each logical y,

    B(y) = sum_{j=-8}^8 I(y+jQ) * 2^((j+8)*100).

All three histories agree with B. The actual early native evaluation and
bounded couriers write zero flag sources. Native flags and Workspace are
quiet before the actual102Q reset. That reset clears Head/Mem/Out/Scratch
and Mail/couriers, preserves History and Info, and the102Q+1 birth loads
the bitwise temporal-majority bank B and creates the legitimate PC0 head
at P. These are the frozen noiseless physical-period identities, applied
to the actual H, not independently prepared execution premises.

The six errors occur at the actual row

    T = 102Q+1+4096 = 839681.

Starting at that actual birth, the checker executes4096 actual head
updates in colonies0 and1. Each update first moves the old packet by its
movement bit, then calls the actual `step_packet` at the destination,
with the actual B, current Out/Scratch and mutable Programme bit. The
two real heads are both at local4035 at T, have visited3848..4035 and
have written42 Out positions each. Scratch is empty. Complete packet,
Out and chronological trace hashes are retained, not just the PC.

To supplement the universal five-holder physical lift, the checker
compares the full local_R at all1008 frame/guard cells on the final
T-1→T update, and verifies992 identities between the actual17 upper H
records and their retained bank words. The entire4096-row prefix is
lifted by the coherent-copy local equation, not inferred from those
finite endpoint comparisons alone.

## 2. Actual late SF factor — proved

Canonical native GF/common Age with zero flags is a closed family when
the overwritten six native fields are retained. Both adjusted GF votes
and both Age votes agree; no native mismatch or flag quorum exists. The
Workspace guard is closed throughout the stated late window and rest,
regardless of SF Info at special primaries. ComputedF1=0, so the SF wipe
is false even at the physical error sites. This derives all future
native and Workspace values from the actual rule; it does not impose
external zero commands.

For every logical y and SF field v, its old input is exactly

    V_v(y) = majority_{h=0..4} raw_v(y-S[h])[h].

Every holder x=y-S[h] has the same computed logical service Address
(x modQ+S[h]) modQ = y modQ and the same computed clock. With the wipe
false, the full local_R therefore computes the same logical update for
all five holders, even if the old SF holders are incoherent. It does not
substitute a raw centre cell for the actual five holder reads.

During active late execution, three voted old packets at y-1,y,y+1 enter
the original `incoming` function. Its priority is stationary centre,
right-moving left packet, then left-moving right packet; multiple
candidates produce the original failure packet. The chosen packet is
passed to the actual `step_packet` with voted Mem, Out, Scratch and
Programme at y. Writes affect only logical y. Programme is rewritten to
beta(y modQ). Info, the three Histories, Mem, Mail and couriers only hold
their voted local values: there is no LOAD, capture, courier transport,
early reset, birth or source commit in this window. The120Q+1..U-1 rest
holds Head too; it does not execute a pending movement bit.

The checker compares96 full local_R instances with all raw SF holders
arbitrary and incoherent. These are finite cofactor supplements. The
universal factor follows directly from each frozen local_R branch and
the service-Address identity above. The actual six error rows additionally
compare298 first computed full local_R cones, including each correct head
far from the overwrite and the entire fault/movement cone.

## 3. One possible escape, followed by inward control — proved

A forged old movement bit can cross a colony boundary on its first
active update. This is allowed here. Every computed packet subsequently
has movement0,1 or2 and cannot move outward at local Address0 or Q-1:

* Missing presence gives ZERO. Invalid move/mode, invalid PC/instruction,
  branch target, IO target or descriptor gives ERROR with move0.
  HALT/ERROR and a collision also give move0.
* A RUN arithmetic/CODE/branch operation gives move0. An accepted RUN
  IO operation verifies target<Q and chooses movement toward that target.
* SEEK verifies target<Q, chooses movement toward it, and on arrival
  executes local IO and returns move0. The guard applies to arbitrary
  raw target/descriptor/register values, not only compiler-generated heads.

Every allowed target is in0..Q-1. Thus at Address0 no computed movement
is left, and at Q-1 none is right. This is an inspection of the total
packet cases, not an assumption that a forged PC follows the own
programme's usual frame path. The checker independently exhausts all
8192 legal SEEK targets at both endpoints,16384 actual transitions.

Suppose the preceding computed SF row is coherent. A current overwrite
inside B can change a five-holder vote only for a logical y inside B:
outside B its group meets at most two overwritten physical cells and
its three unmodified holders still agree with the preceding logical row.
The next incoming movement can therefore create a new discrepancy only
inside B+{-1,0,1}. This interval has at most18 integer sites and intersects
at most two adjacent Q-colonies. Choose one fixed adjacent pair covering
it. All normalized packets inside either colony stay there until a new
raw fault; every subsequent raw fault is still inside B, and its first
escape is still in the same fixed pair. Packet collisions and local
Out/Scratch writes cannot enlarge that pair. Correct heads in other
colonies remain on their proved normal-frame routes and never enter it.

The other SF tracks hold/vote locally in this chronology. Induction on
computed rows therefore confines every SF discrepancy to the same pair.
Current raw overwrites are inside B as well. If an overwrite occurs on
the last permitted row120Q, its pending movement is never executed in
the following rest and remains inside the same pair. At U the actual
old-Out Info commit is followed by the global work reset, with exact
beta regeneration and canonical native row0. The committed Info has
all five copies coherent. This proves the first-boundary statement on
the infinite line; the finite execution is not using a fixed ring or
an assumed clean exterior which a packet could reach.

## 4. Conditional legal records give complete2U recovery — proved

Write V_g for the actual496 normal Out words at U in each colony g.
All nonnative words are already in0..2^100-1. If its first six words
are in the native legal ranges (Q,U,2,2,2,2), V_g is the raw record of
a legal upper cell. Put Cprime(g)=cell_from_words(V_g), and take Aprime
to be the actual unrepresented Info words. The full boundary is exactly
E(Cprime,Aprime). Cprime equals F(H) outside the fixed adjacent pair.

F(H) has canonical GF, common Age1, flags0 and coherent SF logical
copies. Changing any two adjacent legal upper cells cannot affect their
next computed SF votes: every five-holder group retains at least three
correct copies. Each left/right native five-vote also retains at least
three correct GF and Age inputs. WF sources and the native mismatch
sources require larger quorums than the two erroneous upper sites.
Thus computedF1=0; for computedF2, an erroneous positive self has at
most one other positive left neighbour, so the literal h1 erase clause
applies. Both native refinements equal the clean geometry, the wipe is
false, and computed Age2 is outside every WF and execution guard.
Every actual SF source vote is consequently the corresponding clean
vote. This is the already-proved canonical one-pair E0 local argument
of [GAW3](../unregistered_gaw3/GAW3_PURE_E0_PERIOD.md), here with no
previous wipe wake and upper clock1. It gives

    F(Cprime) = F²(H)

as full raw upper cells, including work, Mail, Histories and Programme.
The frozen arbitrary-legal-upper noiseless period theorem now applies
to the **derived** E(Cprime,Aprime), with arbitrary coherent unrepresented
Info allowed, and gives E(F²(H),0) at2U. This equals the clean physical
shadow by its own period theorem. Equality then persists by determinism.
No independent upper error or chosen upper chronology is introduced.

## 5. Exact six actual errors and results — proved selected instances

Each history overwrites a dense sixteen-site row at T, preserves all
native fields and all fields outside its stated SF payload, and has no
later errors. The receipt contains all16 chronological old/replacement
496-word records, including every unchanged word. A passive Head with
presence0/PC1 makes every overwritten physical cell a genuine error.
The full classifier uses the original c104 geometry. Extent16x1 and
diameter15 prevent any isolated singleton/adjacent-pair real0 component;
the linked dense support is one real1 and cannot be104-separated into
two nonempty candidate1 subsets. This is an exact adversarial history,
not a claim about iid occurrence or reliability.

| Payload | Physical support | Bad normal upper records at U | Complete2U |
|---|---|---|---|
| Two forged heads moving across the boundary in opposite directions | [Q-8,Q+8) | 0,1 | yes |
| Only the left-moving forged head | same | 0 | yes |
| Only the right-moving forged head | same | 1 | yes |
| Out=1 in all five slots, near the represented Info0 primary | [4047,4063) | none | yes |
| Out=2^99 in all five slots, near the native primaries | [3841,3857) | 0; native padding illegal | yes, finite raw-bank lift |
| Scratch=2^100-1 in all five slots near local3969 | [3969,3985) | none | yes |

The crossing heads are coherent forged logical packets at Q-1 and Q.
They have presence1, movement1/2, SEEK mode, targetP+FIELD['info']=4054,
an Out-store descriptor, register0=1 and PC3742, the first padded HLT
instruction after the own programme. All other overwritten Head words
are the passive presence0/PC1 packet. The complete packet bits and actual
first computed holders are retained. Both cross the boundary on the
first actual update; no synthetic future Head is supplied.

In the bidirectional case the left packet collides with the legitimate
head at physical4221 at Age843652. The right packet stores Out=1 at
physical12246 (upper receiver1's Info0 primary) at Age843736; its stationary
HLT then collides with the legitimate head there at Age846560. There are
two actual collisions. The damaged output native words are respectively
(0,1,0,0,0,0) and (1,1,0,0,0,0); their padding is legal. This is a single
permitted adjacent upper error pair, followed by complete2U repair.
Unexpected writes and cross-boundary packet motion alone do not violate
the operational relation. The one-way cases have one collision each.

All selected heads are terminal before120Q. Each run retains all writes,
collisions, final packets/Out/Scratch and a chronological trace hash.
All first-boundary commits are checked against the full local_R at1057
cells per case (6342 total), including normal and special-primary cones.
Five cases check18 full next-upper kernels against the complete F²(H)
records before applying the physical next-period theorem.

## 6. High native padding: what fails, and what is recovered — proved

At T the real programme has already written the native output rows at
3848..3853 and will not rewrite them. The direct Out=2^99 replacement
changes the voted Out at every logical position in[3841,3857). At U,
the native representation words of upper receiver0 therefore have
bit99 set. In particular the GF representation is2^99 rather than any
legal13-bit GF. All five stored Info copies of that represented word
coherently carry the same high bit.

These native WORD100 high positions are specified **zero padding** in
the declared E encoding, not ignored unrepresented Info. Aprime may
change positions outside the496-word frame; it cannot change a represented
GF row. Thus this actual U boundary is not E(Cprime,Aprime) for any
legal upper cell configuration. A decoder which truncates these native
words would define a different, broader relation. Proving that broader
kernel/period relation for arbitrary malformed native records remains
open. This checkpoint does not silently truncate the actual tape or
apply the legal-upper all-raw theorem to an invalid record.

For this **one selected malformed boundary** the checker instead takes
its actual496 words, including bit99, in receiver0; receiver1 has its
actual unaffected clean words. All other receiver records are the exact
F(H) records. It derives each actual17-lane bank for receivers -8..9,
the complete radius8 upper dependence cone of receivers0/1. All18
complete raw input banks are retained. The real early native-only
programme executes on each bank and writes Flag1=Flag2=0. The real
complete late programme executes on each same bank and writes exactly
the corresponding complete F²(H) record. Every execution retains its
physical address range, halt deadline, full Out/Scratch, packet and trace.
High native bits are included unchanged in those executions.

The finite physical lift is as follows. First-U work is globally reset
and its native geometry/clock canonical. The first three next-period
gathers preserve that normal record snapshot, and their captured normal
lanes are exactly the derived raw banks: each shifts by an integer Q
multiple, preserving its primary residue. The nonzero unrepresented
Info at3841..3847 has different residues, so it never enters a normal
bank operand. The early resets/births are actual; the18 evaluated zero
flag outputs and the clean exterior produce zero bounded courier sources.
Hence special Info, computed Workspace and native flags are0, not
independent chosen inputs. All Histories/Mem remain the derived banks;
the actual102Q reset clears prior Out/Scratch/Head and the late birth
creates the real PC0 evaluation. The finite traces stay on the normal
frame and finish within147455 actual late updates. No SF wipe or
mail erasure invalidates them. At2U old-Out commit and full reset yield
the exact clean global boundary, with every auxiliary Info0 because
Out was reset and only normal primaries were written. Outside -8..9
the normal operands are the unchanged clean ones; the same controller
and source derivation applies. This proves complete2U for this instance
without a universal malformed-record completion.

## Proof status and remaining obligations

| Step | Status |
|---|---|
| Exact frozen rule/ROM identity, actual intact H and actual T row | proved; finite full-kernel supplements retained |
| Canonical native closure and actual closed Workspace in the stated late window | proved |
| Five-holder SF factor with arbitrary incoherent raw SF holders | proved from source;96 cofactor supplements |
| Total packet target guards and one-step-escape/inward confinement | proved;16384 endpoint checks |
| General late SF16x16 first-U fixed adjacent-pair bound | proved with the stated chronological/native premises |
| Legal-record conditional complete2U corollary | proved using frozen canonical E0 local and legal-upper period lemmas |
| Six exact chronological physical real1 histories and complete2U outputs | proved finite executions and physical composition |
| Literal legal E at U for arbitrary Out faults | false; actual high-padding instance |
| General malformed-padding decoder/period/real1 recovery | unproved |
| Earlier SF/Info faults, mixed native-control bursts, general real1/higher map | unproved |
| Gray-faithful beta<=Q/layout/rest/Flag2 refinement, shorterU, iid reliability or failure | unproved |

The first discovery receipt and checker, generation logs and a pre-run
missing-directory launch failure are preserved. That launch error
preceded any CA execution; it is an instrumentation failure. The first
discovery intentionally left the malformed-padding2U claim false. The
new receipt adds the actual raw-bank executions rather than retroactively
borrowing a theorem whose legal-record premise fails. All registered
documents and all earlier accepted assets remain unchanged.
