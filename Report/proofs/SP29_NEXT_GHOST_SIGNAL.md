# SP29: the first boundary preserves a zero-GF source for the next foreign signal

This is a further theorem for the unchanged isolated SP29 own-ROM rule,
following the exact preparation in SP29_FIRST_SIGNAL.md. No transition,
constant, programme or active G17 file is changed. It proves a particular
second-period signal source, not a second shrinking pulse, an eroder,
an upper error map or iid reliability.

Use Q1024/U475136/TF278401. The initial wrong-GF interval is
[a0,b0)=[128Q−512,144Q); its first certified pulse ends at
t*=TF+6144=284545 with

    [a1,b1)=[122Q−512,136Q)=[124416,139264).

For a physical logical primary y, its Info/Hold copies are the five slots
belonging to y, irrespective of their holders' native phases. Computed
states are before fresh overwrites. There are no errors after the one
specified clock0 native overwrite.

**Theorem.** At computed time U:

1. GF is canonical outside[a1,b1) and shifted512 inside; Age is0.
   Flag1 is1 on[a1−512,a1) and[b1−512,b1), and every non-Info field
   other than GF/Age/Flag1 is0.
2. Every one of the five Info copies of jQ+571,...,jQ+580 is0 for
   j=121,...,135. All other Info values are left unspecified.
3. At computed time U+TF, the next own programme has supplied
   Info-majority1 at every primary jQ+509 for j=122,...,135.
   These are its fourteen complete foreign frames. The theorem does
   not specify the entire MF509 track or any MF1021 track.

The original upper Info payload remains arbitrary. The boundary is not
claimed to encode the correct upper successor, and no intact recursive
state is assumed anew at U.

## Native continuation and reset

The first-pulse certificate gives the exact t* template, with Flag2,
Workspace flags, packet/code validities and backward pressure0.
The native quiet-template proof of J156 applies separately at the
two new edges: their phases moduloQ are unchanged, and their dependency
neighbourhoods are disjoint. With common Age free, the joint refinement
returns the raw GF/age and the native operator preserves GF/Flag1,
returns Flag2=0 and selects that common age. The162 refinement and4258
native cofactors are checked again for[a1,b1).

After t*, the epoch-force, birth and WF1 guards are closed through U−1.
Empty validities cannot create a packet/code/backward source without
birth. Thus the native template persists and the actual keep mask is1.
The legal increment theorem gives the common Age wrap to0 at U.
The807 reset identities in the actual SP29 commit interface depend
on computed GF equalling refined raw self-GF and on the commit clock;
they do not require GF=x modQ or Flag1=0. The new quiet template
supplies that equality. The same universal807-zero/5-Info-forwarding
cofactors are checked with this interface. This proves conclusion1.

## Pending writes do not invent a Hold target

The argument below cannot merely inspect K_HOLD opcodes and ignore
pending metadata. Gács-style bitwise voting could otherwise combine
different Scratch targets into a spurious Hold target.

Here a logical primary y has only two possible computed phase values,
y modQ and(y+512)modQ, throughout the first pulse. At one common
legal clock, its five comb teeth differ by multiples of5 of absolute
size at most20. Their differences never equal512 moduloQ. Therefore
these two phases cannot both arrive at that row. Every arriving holder
for the same logical y consults the same ROM word outside Match.
Match has no store. The complete all-raw arrival theorem excludes a
second arriving slot at one holder.

Consequently the five newly written pending records for y are either0
or copies of one fixed destination kind k. The pending presence bit
and the kind bits are all multiplied by the holder's keep; nonarrival
also gives0. If the five-vote of pending is1, at least three copies
have that same k, so the bitwise vote of every kind bit is exactly k.
If pending votes0 there is no forwarded write. This holds for all32
presence masks and k=0,...,4 (Hold0 and the four Scratch targets).
Pval may be arbitrary; it cannot change the kind. Thus a forwarded
Hold write exists only after an actual K_HOLD issue. An earlier arbitrary
pending seed is excluded here by the initial private-zero encoding.

This lemma permits native phase switches, wipe erasures, arbitrary
register/scratch values and disagreeing Pval copies. It is not an
arbitrary-noise pending-word theorem.

## Zero Hold survives through the first boundary

For physical y=jQ+571+b, j121..135 and b0..9, every native phase used
by a holder of y is either59+b or571+b. The ROM/listing audit examines
all81920 raw key pairs at these twenty phases. Each has exactly one
Hold issue in the actual programme. The input-clock issue ages are

    virtual GF59..68: 276520..278398;
    true H2571..580: 352116..360605.

Issue produces pending in the next computed state; the Hold materializes
one further update later. In particular the latest GF Hold materialization
278400 is before TF278401, and the earliest H2 materialization352118
is after t*284545. No additional K_HOLD key or pending Hold target is
silently allowed by this timing statement.

Initially each targeted Hold copy is0. For j121..126 the primary is
initially true-phase: it has no early GF Hold issue, and its H2 issue
has not occurred by TF. For j127..135 it is initially wrong-phase,
in the complete foreign frame with origin(j+1)Q−512. That full frame
ends before b0; the initial partial right frame is outside this set.
J167's actual gathered-GF cofactor gives its own computed GF bits0,
and its pre-TF physical interpreter induction materializes those0
Hold values. Thus every targeted Hold copy is0 at TF.

During the pulse there is no Hold issue at either possible phase,
even if the primary switches phase repeatedly. The pending-kind lemma
excludes a Scratch-to-Hold alias; majority updates and wipes preserve0.
At t* all five holders of every target lie inside[a1,b1), at least59
sites from its nearest relevant GF edge. Thereafter they stay wrong-phase.
Their virtual59..68 issue ages have passed, and the late571..580 issue
cannot address those holders. Hold therefore remains0 through U−1.
There is no pending store at the inactive commit clock. The exact Info
commit expression forwards this0, and virtual59..68 is inside its allowed
normal frame. All five Info copies are0 at U, proving conclusion2.

This proof makes no assertion about late programmes in newly recovered
true-phase regions or about their other represented bits.

## The next foreign gather receives only zeros

At U all private fields reset. Native GF/Flag1 are now the new quiet
template, and all other Info may be arbitrary or disagree among holders.
Until the next TF, epoch-force/birth/WF1 are closed. The quiet native
template and keep1 persist; every logical Info majority is constant
until the special write. All early programme input reads and all three
gathers precede that write. Five-holder voting permits arbitrary initial
copy disagreements; it does not assume a correct encoded upper state.

Consider a complete foreign frame of origin hQ−512, h122..135.
Its virtual GF phase59+b is physical(h−1)Q+571+b. For each requested
offset d, a direct/gathered source is(h+d−1)Q+571+b.
If this primary lies inside[a1,b1), conclusion2 gives source0.
If it lies outside, its speed-eight gather path crosses one of the
512-site Flag1 strips[a1−512,a1) or[b1−512,b1). The exact logical
mail recurrence from J167 multiplies by the quiet gate on each step,
so that path also supplies0, regardless of the outside Info payload.
A512-site strip cannot be jumped over by eight-site steps. The checker
verifies26880 actual capture paths and420 direct-source checks across the
three gather stages, including endpoints and every sparse dependency rank,
rather than replacing the path by a continuous interval. All ten virtual GF inputs, including direct ones,
are0 in each complete frame.

The own full-circuit GF0 cofactor again gives Flag1=1 with every other
input free. Each complete foreign frame has its own initial private0,
canonical relative geometry, common clock and quiet Flag1 over its
entire front/courier footprint. The pre-TF physical programme induction
therefore produces early Flag1 Hold1 and the right courier writes
virtual1021, physical hQ+509. This proves conclusion3.

Other partial/true frames may supply additional ones; no contrary
zero claim is made. The next actual WF1 track and shrinking outcome
still require the true-frame/late-data argument. In particular this
result is not an induction proving later shrinkage.

| Step | Status | Exact limit |
| --- | --- | --- |
| First native endpoint persists to commit;807 private reset identities | proved | Specified J167 error, no later errors, actual quiet native template |
| One-kind pending and twenty-phase Hold issue audit | proved | Binary GF phases/common legal clock/own ROM/private-zero start |
| All750 surviving wrong-GF-primary Info copies0 at first U | proved | Initial six true and nine complete foreign source groups; no all-data repair |
| Actual next fourteen complete-frame ghost signals1 | proved | Mail barriers allow arbitrary outside Info; same original physical history |
| Entire second signal, second shrinking pulse, continuing erosion | unproved | MF1021/partial-frame/late-data outputs remain unspecified |
| General higher-error map and positive iid noise rate | unproved | One specific error history is insufficient |

The source, timing/cofactor/route certificate and dependencies are
check_short_force1024_next_ghost_signal.py and
figs/robustness/SP29_next_ghost_signal_certificate.json. No numerical
whole-CA trajectory or newly altered rule is used for this result.
