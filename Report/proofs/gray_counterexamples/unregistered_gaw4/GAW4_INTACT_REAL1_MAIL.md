# GAW4: an intact real1 temporary-field footprint, with decoded recovery

This checkpoint changes no rule. It uses the frozen GAW2R automaton, Q=8192, U=128Q=1,048,576, lambda=24 and c=104. Its WORD100/radius8/17-lane/h1/immutable270,349-bit-code/102Q-late-start departures remain explicit. It does not instantiate Gray's own Q-bit programme or literal bit layout. No Gray, Gacs, G17, positive iid-rate or shorter-U conclusion follows.

Starting from an actual recursively intact hierarchy, a five-site original-real1 fault during final rest commits one wrong represented Info-copy word. During the next actual gathering window, Info remains wrong in colony0 while Mail carries it into colonies−1 and1 simultaneously. Thus GAW2R does not satisfy the **literal pointwise simulation-structure confinement statement** of Gray's Proposition4 if one transplants that statement to this changed automaton. This is a failure of that proposed transplant, not a contradiction to a previously proved GAW2R confinement theorem or a verified faithful Gray rule. The decoder at U sees a single allowed upper fault; the actual boundary at2U is exactly the noiseless shadow. Temporary-field containment and decoded recovery have different conclusions here.

| Step | Status | Scope |
|---|---|---|
| Intact initializer H=E(H,0), including actual Programme bits | proved by field cases and terminating recursion | entire infinite line, every represented field and all five Info holders |
| Three actual gathers, early flag pass, couriers and fifth pass from H | frozen GAW2R proof applies | banks are derived from H, not independently preloaded |
| Five-site error is one original real1 and no E0 | proved; exact classifier receipt | shared physical history, no other errors |
| Actual first commit gives E(Cprime,0) | proved; actual local_R execution | Cprime is F(H) with upper cell0 Info[0] changed0→1 |
| Three simultaneous disagreement colonies at U+Q+1 | proved transport induction and actual local_R checks | Info in0, MailL in−1, MailR in1 |
| Literal Proposition4 box transplant to GAW2R fails | proved | same initial deterministic shadow, raw simulation fields, one box per original real1 |
| Sacrificed upper error and exact2U decoded/raw recovery | proved | F(Cprime)=F²(H), then the actual noiseless period theorem |
| Earlier102Q start causes this failure | unproved and not claimed | fault is at U−1 in the shared final rest |
| Faithful Gray/Gacs contradiction or iid memory failure | unproved | missing literal own-programme/layout/protocol refinement is not supplied |

## 1. The exact tested claim

[Gray pp35–36, Proposition4](../../../../papers_txt/gray_readers_guide.txt) asserts, for level1-only noise, equality of the simulation-structure fields with the deterministic system outside a union of boxes. Each real0 contributes its own physical singleton/adjacent-pair box; each real1 contributes one box with spatial interval [jQ,(j+2)Q), and temporal interval (kU,(k+2)U), j,k integers. The endpoints in time are open. This is a **pointwise raw-field** statement, not only a statement about decoded boundaries. Its preceding argument explicitly permits incorrect incoming Mail in otherwise undamaged colonies.

Our test keeps those exact quantifiers and covers for the changed GAW2R simulation fields (all its five-copy SF fields, including Info and Mail). The deterministic reference starts from the same H. The error history is one real1 and no real0, so exactly one of those spatial pairs is available. Any temporal choice that leaves the displayed row outside the time box already fails; any choice containing it still fails spatially. The witness also excludes a different adjacent pair at each tick, because three colonies disagree at the same tick. A larger envelope permitting temporary Mail spread is not excluded. Likewise a relation that sacrifices one upper cell at the intermediate boundary and requires decoded recovery at the next boundary is **satisfied**, not refuted.

The frozen [GAW2R theorem](../unregistered_gaw2/GAW2_THREE_GATHER_PERIOD.md) proves noiseless encoded periods. [GAW3](../unregistered_gaw3/GAW3_PURE_E0_PERIOD.md) adds continuing pure-E0 periods. Neither states this real1 raw-field envelope. We therefore do not label the witness a counterexample to either accepted theorem.

## 2. A concrete intact initializer

Use the frozen k.Cell, representation k.cell_words, frame P=3848, width496, slots S=(0,−2,−1,1,2), and fixed emitted beta. Define a logical WORD100 function I on all integers. For y=gQ+a, 0<=a<Q, put i=a−P. If i is outside0..495, set I(y)=0. For native rows0..5, set I(y)=g modQ at row0 and0 at the other five. For the remaining rows, let f be the represented field and h its copy index:

    I(gQ+P+i) = I(g+S[h])             if f=Info,
                 beta_bit((g+S[h]) modQ) if f=Programme,
                 0                      for every other SF field.

Define H(x) to have canonical Address x modQ, Age0, native Flags/WF0, and all work0. Its Info tuple is (I(x+S[h]))_h; its Programme tuple is (beta_bit((x+S[h]) modQ))_h. The beta lookup is the actual fixed GAW2R bit primitive and includes the correct programme choices; no programme is chosen independently of the rule.

Only the five Info representation rows206..210 recurse. Their spatial residues are4054..4058, so every recursive y has |y|>=4054. For such y, |g+S[h]|<|y|: |g|<|y|/Q+1 and |S[h]|<=2, and |y|/Q+3<|y|. Hence the definition terminates on every integer, on both halves of the infinite line. All values are legal WORD100 words. Its only nonzero terminal values are13-bit Addresses or single programme bits.

For every g and every one of496 representation rows, I(gQ+P+i) is exactly k.cell_words(H(g))[i]. Native, every metadata/register/Memory/History/output/scratch/courier/Mail row, Programme and all five Info rows are included by the displayed cases. For every raw holder x=y−S[h], H(x).Info[h]=I(y). Unused and special primaries3/Q−3 are0. Native and all other physical tracks are exactly the reset encoding. Therefore **H=E(H,0)** on the entire line. Repeating the same identity gives an intact hierarchy at every level, with the same fixed rule and Programme choices. All five Info slots of cell0 are0, since each S[h] is an unused residue.

The checker supplements this proof with6,448 field cases and32,240 actual holder identities, including both signs and large coordinates. Those finite checks are not substituted for the all-integer recursion proof.

## 3. The actual error-free prefix and fifth output

Start the physical lower system at H=E(H,0), with no errors before row U−1. The frozen actual gather induction gives each receiving frame the17 states H(g−8)..H(g+8), in all three banks. Those are actual states of this one recursive initializer. No independently chosen upper history, input bank or scratch state is used.

At every upper position, H has canonical GF, common Age0 and native Flags/WF0. Its computed upper native Flags are0. Thus the actual early prefix computes0 flag commands and the real couriers deliver0 to both special primaries. Lower native flags remain0 on the entire first period; there is no Mail erasure or SF wipe. The actual102Q reset and102Q+1 birth therefore execute the complete own beta on the derived bank. Its universal actual-period proof already establishes output equality and completion before120Q.

For colony0, the new checker additionally runs the entire actual step_packet instruction stream on that **derived** readonly bank. It checks all496 words against the actual local_R(H) result, retains the complete17-cell input, final packet, output, scratch and execution digest, and counts66,185 actual updates. Head motion stays3848..4343; its final halt position is3986. After120Q the packet/output/scratch are held, while Mem and all three captured histories retain the derived bank. Work and Mail/couriers outside those explicit positions are0. These equations give the full actual raw row U−1 in the finite commit cone; all its words are retained.

The selected target is

    y=P+FIELD[Info]=3848+206=4054.

It represents upper cell0's Info copy0. Its correct fifth output is F(H)(0).Info[0]=0: the native clock update is1 and Info is held/voted at that phase; the five old logical Info0 holders all contain0. Consequently every lower raw Out holder of y is0 throughout final rest.

## 4. One original real1 and the actual first commit

At the five points (y−S[h],U−1), change only Out[h] from0 to1, leaving every other raw bit exactly as it was. Thus the support is

    {(4052,1048575), ... , (4056,1048575)}.

The receipt retains each complete old cell and replacement cell. This is a legal whole-cell replacement history, with no initial noise or later noise.

The support has width5 and one tick. It contains no actual real0 subset: every singleton/adjacent pair is linked to the remaining points. It is a candidate real1, since two distinct linked singleton candidates occur inside a Q×U box. Condition(iii) holds with original c104 because every pair of nonempty subsets is(104,104)-linked; condition(iv) is vacuous since there are no other errors. The exact classifier gives level0=0, level1=true, sep104. Moreover no proper subset can be an actual real1: it is linked at distance(24Q,24U) to its nonempty complement. This shared error history contains exactly one real1 for the tested cover.

Native GF/Age/flags and Programme are unchanged. At the U update, computed Age0 selects the old five-holder Out vote for Info. Every one of the five votes for logical y reads five ones, so all five resulting Info copies become1. Every other logical vote stays correct. Work, Out, Mem, heads, Scratch, couriers, Mail and histories reset globally, and Programme is hardwired. There is no wipe. Hence the **complete actual boundary** is

    X_U=E(Cprime,0),

where Cprime equals F(H) except at upper cell0, whose Info[0] word is1 instead of0. This is an exact global boundary identity with no current errors at U, not just a voted projection. The actual local_R commit checks match it in the retained cone; outside that cone only unaffected held votes and resets occur. The intermediate decoder sees the single sacrificed upper-cell error, as expected for real1 recovery.

## 5. Actual gathering footprint

At U+1, actual LOAD resets/captures and both Mail tracks load current voted Info from E(Cprime,0). Subsequent computed flags stay0 before96Q: geometry is canonical/common and the upper SF-only defect does not change upper native Flags. Thus before the late flag source, the actual transport equations are

    MailL_t(z)=D1prime(z+t−U−1),
    MailR_t(z)=D1prime(z−t+U+1),

while Info remains D1prime. D1prime differs from the noiseless boundary D1 at exactly logical y. This is induction on the actual load/shift equations, with five coherent raw copies and the proven controller; there is no prepared packet assumption. At elapsed Age Q+1, the nonzero differences include

| logical position | field | physical holders | colonies |
|---|---|---|---|
| y−Q=−4138 | MailL | −4140..−4136 | −1 |
| y=4054 | Info | 4052..4056 | 0 |
| y+Q=12246 | MailR | 12244..12248 | 1 |

They are simultaneous at row **U+Q+1=1,056,769**. The checker constructs the previous row from that inductive actual formula and forwards the real local_R at all three cones. It compares every raw output word, actual holder location and voted value with the shadow. The last first-gather lane±1 capture is at AgeQ+2; only the own lane has captured by the displayed row, and that exact History reset/capture timeline is included rather than guessed.

No adjacent pair of colonies contains all three differences. This proves failure of the stated literal Proposition4-shaped pointwise transplant to GAW2R. It does not prove an unbounded spatial footprint or any infinite lifetime: the Mail signals later clear and the complete raw state recovers at2U.

## 6. The second boundary really recovers

At the intermediate upper level, Cprime differs from F(H) at one Info-copy holder. F(H) has coherent five-copy SF values, canonical GF, common Age1 and native Flags/WF0. On its next update, all affected five-holder Info reads see four correct copies; computed geometry/flags are unchanged, the WF guard is closed at computed Age2, and every SF data read is restored before use. Therefore

    F(Cprime)=F²(H)

as complete configurations. Outside the radius8 influence of upper cell0, inputs are identical. The new checker checks the complete actual local_R outputs at all17 potentially affected upper sites, every represented field included.

The actual second physical period begins at the already derived E(Cprime,0). With no later physical noise, the frozen noiseless encoded-period theorem gives

    X_2U=E(F(Cprime),0)=E(F²(H),0).

This is full raw shadow recovery, and the decoder is exact. The new actual colony0 second-pass replay additionally derives its input from Cprime, completes in65,062 updates, and checks every output word, including the formerly damaged Info-copy word. The remaining colonies are covered by the frozen universal all-raw period theorem, not independently prepared runs.

## 7. Rest and attribution

The fault is in final rest120Q..128Q, one tick before commit. Voting cannot heal it before the boundary because all five holders are overwritten at once, and the boundary consumes that old Out majority. It does not exploit execution in104Q..112Q, and it supplies no proof that moving the late start from112Q to102Q caused the temporary spread. Actual first-pass66,185 runtime does exceed the separate D candidate's65,535 budget, but D is a different frozen rule and no D error history is asserted here.

Gray's rest argument concerns native damage lifetime and clean temporal gathering; the present fault alters stored SF output directly without damaging native geometry. Its later Mail spread is precisely the kind of temporary incoming information his preceding discussion permits. A reformulated operational containment statement allowing those Mail/History effects and a sacrificed upper error could remain correct. Our actual decoded recovery supports that distinction.

The already accepted literal-stage audit identified a conditional conflict between raw-field containment and full raw-state transport. GAW4 closes an actual recursively intact, total changed-rule instance of this footprint. It does not close the literal Gray own programme, layout, state alphabet, radius, code storage or rest refinement. It therefore remains a **GAW2R witness to a proposed raw-field statement**, not a certified refutation of Gray's or Gacs's construction or reliability theorem. A finite adversarial history followed by no later errors also gives no positive-rate iid memory conclusion.
