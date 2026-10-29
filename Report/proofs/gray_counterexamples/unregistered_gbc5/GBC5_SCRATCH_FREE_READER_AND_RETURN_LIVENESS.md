# GBC5: scratch-free field access and counted return liveness

This checkpoint changes the software encoder of the frozen GBC4 proposal,
not its total local rule. Q=8192, U=1048576, lambda=24 and c=104 remain the
declared baseline. No state bit, opcode, code table, stack, or new evaluator
primitive is added. The programme still does not fit Q: the exact complete
shared listing contains **40,778 bits, 3,104 instructions and 365 references
outside Q**. GBC4's corresponding listing contains 41,047 bits. This is an
encoder-specific rejection, not a size lower bound for other constructions.

The result closes the RAW80 and software-return liveness premises for this
reader at its actual listed callers. It does not prove full own-programme
equivalence, a complete execution deadline, a physical period, reliability,
or a counterexample to Gray.

## Exact component statement — proved

Use the unchanged GBC4 total binary rule and generic CALL/RETURN/READ-SPAN
semantics in its [rule source](../unregistered_gbc4/compact_completion_rule.py).
There are five SF-holder offsets S=(0,-2,-1,1,2), and seventeen History
lanes -8..8. Let C be an arbitrary tuple of seventeen declared raw cells,
including arbitrary Head bit patterns. Assume a single coherent physical
CPU executes the issued component with correct lower controls, no errors
or wipes, and stable exact captured tape E(C). These are lower execution
premises, not restrictions on the upper raw Head values.

For q in {0,1,2,3,4}, centre c in [-4,4], 1<=w<=20 and
0<=o<=553-w, the component returns

    A = majority_r HeadCopy_r(C[c+S[q]-S[r]])[o:o+w],

where the majority is bitwise and the displayed holder notation means the
five raw SF copies used by the declared decoder. More explicitly, the
result is `(voted(C,c+S[q],'head') >> o) & ((1<<w)-1)`.
The helper preserves every data Work bit, all NC bits and Fn. CALL writes
only the existing return bank Work[380:400]; the wrapper additionally sets
the existing QCOL word Work[100:120]. In particular, RAW80 is preserved
even when its previous value remains live in the caller.

The concrete wrappers issued in this checkpoint are at most 206 bits and
have exactly

    18 + HEAD_BASE + 5*(o+w-1) + q - PRIMARY_START

updates from the specified stationary initial position PRIMARY_START=2553.
HEAD_BASE=2875, so every such wrapper finishes within **3,104 updates**.
This bound is for the component under the premises above; it is not a bound
for the rejected complete programme.

### Data coordinates and locality

The specialized entry receives B=o, QCOL=q, and Fn=c mod16. Its ten listed
instructions compute the physical first column

    T = HEAD_BASE + 5*o + q,

issue the existing aligned stride-five READ-SPAN with A=w, and RETURN1.
No Work store occurs inside the reader. At bit i, the actual consumed
physical column is HEAD_BASE+5*(o+i)+q. This is a raw-holder column, not a
substituted logical head centre.

For holder r, the real local column displacement is r-q in [-4,4]. The
captured History lane is `8+c+S[q]-S[r]`, in [0,16]. Hence the physical
operation samples the five old raw copies at logical centre c+S[q]. The
upper source displacement is at most eight, exactly as required by the
declared radius-eight gather. No hidden input access is used.

### Timing and preservation

There are seven wrapper setup instructions, nine reader instructions
through READ issue, one RETURN and one HLT. The initial target is strictly
right of PRIMARY_START. The first SPAN consume occurs after T-PRIMARY_START
movement updates, and subsequent consumes are five updates apart. Their
total movement/consume cost is T-PRIMARY_START+5*(w-1). This proves the
displayed exact formula. Branch-free arithmetic stays below Word20 and
all targets and return addresses fit the issued wrapper's Q-bit code.

CALL modifies only its counted return word; READ-SPAN modifies packet
metadata/A/B and reads the tape without writing it. The remaining reader
instructions have no Work, NC or Fn side effect. Thus RAW80 and all other
data words remain unchanged for arbitrary initial values, not merely the
selected test seed.

## Actual caller and return-bank theorem — proved, conditional on fetch

The [emitter](scratch_free_reader_emitter.py) specializes only the widths
{1,2,3,4,5,6,13,15,20} actually used by GBC4's Head-read macros. Every one
of its **43 actual reader callers** supplies a constant offset/width in
range, the existing QCOL holder q, and either a constant centre -1/0/1 or
the source selected by `select_virtual_head`.

The latter block examines self/left/right incoming raw heads. It stores
CENTRE only when the first eligible head is found; zero eligible heads
take `cpu_empty`, and more than one takes `cpu_fail`, before any variable
centre read. Thus any continuing metadata/opcode path has exactly one
selected centre in {-1,0,1}. Other branches that flush Work with PUSH
return directly to `cpu_next`; they do not re-enter a reader before the
next source-selection block. This supplies the reader's centre premise.

The scratch-free macro preserves RAW80. Its only data Work store is the
caller's explicit result destination, if present. Consequently there is
no RAW80-deadness premise left to discharge at these 43 callers.

The exact symbolic listing has 75 CALL sites. Its callable blocks are:

| Block | Own return bank | Nested call |
|---|---:|---|
| copy_group | 1 (Work380) | write_word, bank0 |
| write_word | 0 (Work360) | none |
| temporal_word | 1 (Work380) | none |
| virtual_vote | 0 (Work360) | temporal_word, bank1 |
| virtual_literal | 0 (Work360) | none |
| each specialized reader | 1 (Work380) | none |

All reader calls originate in the main block. Every RETURN reads its
block's own bank. No helper contains PUSH or an explicit WGET/WSET of a
return bank; in particular no helper flushes or overwrites its own live
return. The call graph is acyclic, has maximum depth two, and its two
nested paths use distinct banks. The literal decoder's error branches
abandon their saved return and transfer to main `cpu_fail`; they never
return through a subsequently overwritten bank. Therefore both counted
return words remain intact whenever used as live software returns.

This is a theorem about the exact listed control graph assuming its
specified instructions are fetched at valid entry points. Since the
complete listing exceeds Q, it is not a claim that those complete caller
paths form an issued Q-bit own programme. The small components above are
actually issued and need no such larger-code diagnostic assumption.

## Receipts and retained failure

[The component checker](check_scratch_free_reader.py) certifies every
listed caller, all 75 CALL sites and the return graph. It runs 810 issued
components: every centre -4..4, holder q, used width, and both extreme
valid offsets. All return values, raw Work/NC/Fn preservation checks and
exact timing formulas pass in
[attempt03](../../../figs/gray_counterexamples/unregistered_gbc5/GBC5_scratch_free_reader_attempt03.json).
The numerical replays are measured evidence; the algebraic component and
ABI claims above are proved from the listed instructions.

The [complete diagnostic](check_complete_scratch_free_listing.py) retains
the inherited separate instruction-table/wider-PC diagnostic, not an
issued own beta. All 104 selected full raw comparisons pass in
[its receipt](../../../figs/gray_counterexamples/unregistered_gbc5/GBC5_complete_diagnostic_attempt01.json).
They cover stage, malformed/pending, output, CALL and RETURN families;
they do not exhaust all raw configurations or prove full equivalence.
The diagnostic's larger instruction table is an extra experimental
resource, explicitly excluded from the Q-fit claim.

The first ownership checker wrongly classified the appended common
continuation/header tails as part of the last reader. Its exact failed
[source](check_scratch_free_reader_initial_owner_failure.py) and
[log](../../../figs/gray_counterexamples/unregistered_gbc5/GBC5_scratch_free_reader_attempt01.log)
are retained. Correcting that checker partition did not change the rule
or emitted programme. Attempt02 passed; attempt03 adds deterministic
call-path ordering and the exact timing assertion.

## Status and remaining bottleneck

| Step | Status |
|---|---|
| Scratch-free generic reader equations/locality | proved |
| Component input/result/storage and <=3104 deadline | proved under stated execution premises |
| Actual reader macro RAW80 preservation | proved |
| Counted return-bank liveness of exact listed call graph | proved under valid fetch/entry |
| Complete size and 365 invalid references | proved for this encoder |
| 810 issued reader and 104 complete comparisons | measured only |
| Universal complete emitted equivalence/runtime | unproved |
| Own beta<=Q, hardwirer/final full layout, physical period | unproved |
| Faithful Gray refinement, general errors, iid reliability | unproved |
| Shorter U or Gray proof counterexample | unproved |

The full listing is 269 bits smaller than GBC4, but still exceeds Q by
32,586 bits. Specializing a safe reader closes a component proof gap; it
does not solve the dominant complete-software encoding budget. Existing
h1, radius-eight/seventeen-lane, immutable-code, representation/service,
source-order and stage departures remain material to comparison with
Gray. No frozen earlier source, main report, CURRENT or active rule was
changed.
