# GAWN18: two good gathers give complete current-period repair

This concerns the **unchanged frozen GAWN2** rule, Q4096/U524288,
radius8/Word100/h1/own beta/lambda24/c104. All of that proposal's departures
from Gray remain. No new rule, ROM, constant or active candidate is introduced.
The theorem below is conditional recovery, not a random-noise theorem.

## Exact statements

Use F, D, pi, E and the own ROM of
[GAWN2](../unregistered_gawn2/GAWN2_HALF_SCALE_NOISELESS_PERIOD.md).
Let d be any infinite D configuration and B any coherent auxiliary Info
function. Write I(y) for the logical Info in E(d,B), and Y_t=F^t(E(d,B)).
Choose an integer 1<=theta<=32Q-1. At physical row theta take any legal
configuration X_theta satisfying, globally:

* raw native Address is x modQ and raw native Age is theta;
* all four raw native flag/Workspace fields are zero;
* the five-holder logical vote of Info is exactly I(y) at every logical y.

Every other SF word is arbitrary. Raw Info holders need not be coherent;
their voted logical values must meet the stated premise. There are no later
overwrites. Then, as **complete raw infinite configurations**,

    F^(U-theta)(X_theta) = Y_U = E(F^D(d),0).

Both executions agree at every subsequent physical tick. This does not
prove that arbitrary early faults recover native control or preserve Info.
It supplies the remaining SF recovery once those properties hold in time.

**Actual prepared Age-triple corollary.** Let H_2 and C_1=F(H_2) be the
actual recursively intact configurations from GAWN4. Replace only Age at
physical row1 and sites{-1,0,1}, changing1 to2, leaving all actual other
fields unchanged. If Z_0 denotes that row and Z_k=F^k(Z_0), then

    Z_(U-1) = F^U(H_2),

and complete agreement persists thereafter. The false arbitrary-triple
one-update identity from GAWN17 is not used. This corollary does not show
that a lower admitted fault realizes this particular upper triple.

## 1. Canonical control and Info until the second reset — proved

With globally canonical Address and a common clock, both adjusted Address
votes are canonical and both Age votes are the common successor. This is
independent of the old flags/SF. Thus geometry and clock persist and the
computed SF wipe, requiring computed Address different from raw self
Address, is false. Until96Q the actual Workspace guard is closed. Zero old
flags, matching Age votes and no Workspace source keep both flags zero.

Every computed age before32Q is positive and below80Q-1. The Info equation
therefore writes only its old logical Info vote. Native flags do not clear
Info when the wipe is false. Canonical geometry/common clock makes every
holder of a given logical word receive the same result. Consequently Info
is coherent after one update and equals I throughout this interval. This
argument also covers theta=32Q-1: that single update gives the needed
coherent Info at32Q. Head execution writes only Out or Scratch, never Info;
in any event the active Head windows do not begin until72Q+4. The immutable
Programme output regenerates the own beta bit on every update.

At computed age32Q the literal stage reset sets Head, Mem, Out, Scratch,
both couriers and both Mail words to zero. It resets History2/History3
and leaves History1 voted and retained. Info is I and Programme is the
own beta. The clean reference Y_32Q has precisely these same values.
Their native fields also agree. Thus **at32Q every raw component agrees
with the clean reference except possibly History1**, everywhere on Z.
This derives preparation from the actual reset, with no external work
tape, clean private memory or clean Head premise.

## 2. The two later physical gathers — proved

Native flags remain zero before96Q, so Mail is not cleared by Flag1 in
either later gather. For S=32Q or64Q the actual reset sets Mail to zero;
at ageS+1 MailL/MailR load old Info I(y). After n transports, at rowS+1+n,

    MailL(y)=I(y+n),  MailR(y)=I(y-n).

This follows by induction from their literal y+1/y-1 reads. Transport
remains active through all relevant distances |j|Q, |j|<=8. Lane j=0
captures old Info at ageS+1. Lane j!=0 captures old Mail at age
S+2+|j|Q, whose old row is S+1+|j|Q, giving I(y+jQ).
Thus History2 and History3, after their last captures at40Q+2 and72Q+2,
both equal the same coherent 17-word bank

    T(y) = sum_(j=-8)^8 I(y+jQ) << ((j+8)*100).

History2 is not reset at64Q: the literal reset set for bank2 is
GATHER_STARTS[:2]=(0,32Q). Bank3 is reset at64Q and then recaptured.
Info is still I throughout both gathers because their final capture
precedes80Q-1. All frame sources y=gQ+P+i consequently contain exactly
the17 representation words d[g+j][i], without auxiliary Info mixing.

There are no further captures after72Q+2 and no further resets of these
two banks until the age0 boundary. Canonical Address excludes wipe,
and retaining a coherent bank by five-holder vote retains that same T,
regardless of later flag values. Hence both correct banks persist through
the old row consumed by the boundary commit.

## 3. History1 cannot change any other output — proved

Inspect the actual physical equations. History1 enters other fields only
as one of the three bitwise-majority operands when Mem is loaded at
EARLY_RESET=72Q+3 and100Q+1. Otherwise Mem is retained or reset to zero;
the other equations do not consume History1. In particular native
maintenance consumes native fields, and computed-primary consumes voted
Info, Out or courier words, never a History bank. Head instructions read
Mem, Out, Scratch or Programme; they do not directly read History1.

For each bit a,b, majority3(a,b,b)=b; hence for arbitrary1700-bit A,
majority3(A,T,T)=T. At both Mem-load rows, History2 and History3 are the
proved correct T. At every other row, replacing History1 in otherwise
identical neighborhoods cannot change any component except History1.
This statement includes the native Workspace window and all Head
movement/opcode guards. It does not require Mail to remain coherent during
that window; actual Mail/native outputs equal their clean reference.

Induct from the complete equality outside History1 at32Q. Until the first
load its value has no other effect; at that load the two good banks give
the identical reference Mem. The same identity applies at the second
load. Thus all components except History1 agree with Y_t at every row
32Q<=t<U. At U, computed age0 resets History1 too. The commit consumes
old voted Out **before** resetting work; this Out already equals the
reference. Complete raw equality at U follows. GAWN2's proved physical
period theorem then identifies this common boundary as E(F^D(d),0).

The early221 and normal104572 all-payload deadlines, actual own ROM,
typed addresses, packet movement and complete frame output are reused
from GAWN2 under their proved preparation premises. The equality induction
also supplies their exact clean reference execution, so no sample
execution substitutes for those universal contracts.

## 4. Application to the actual Age-only triple — proved

GAWN4 proves H_2=E(cell_words(H_2),0) and the actual C_1 fields. GAWN17's
corrected native proof gives canonical Address/correct physical Age on
every row2..2050, with Flag1 erased and all native fields quiet at physical
row q=2050 (elapsed2049 from the faulty row1). Its proof allows actual
arbitrary evolving SF and uses the closed actual Workspace guard.

The overwrite does not change Info. On every subsequent update through
q, computed Address is canonical and agrees with raw self Address, so
wipe is false; computed age lies in[2,2050], excluding0 and80Q-1. Thus
the literal Info equation retains the initial coherent I everywhere.
At q all hypotheses above hold, and1<=2050<=32Q-1=131071. The theorem
therefore gives complete raw current-U repair, and determinism gives
agreement at all later ticks. This supersedes the prepared-case full-SF
gap in the frozen historical GAWN17 proof; its unrestricted-triple and
lower-fault reachability gaps remain.

## 5. Evidence, statuses and limits

The checker supplements this written induction with literal reset and
Mem-load kernel comparisons, paired arbitrary legal SF inputs differing
only in History1 across critical phases, exact gather coordinate checks,
and the elementary bit-majority truth table. They are finite measured
transcription checks. It does not simulate an evolving2049-step full-SF
trajectory or U-tick physical line. Receipt and manifest are issued once;
read-only replay checks frozen hashes before and after recomputation.

| Step | Status | Scope |
|---|---|---|
| Canonical control, Info retention and32Q reset | proved | Exact global hypotheses stated above |
| Two later gathers, two equal retained banks | proved | Literal source-coordinate/holder induction |
| History1 noninterference/two Mem loads/complete U equality | proved | Complete raw infinite configurations |
| Own execution deadlines and encoded reference U | GAWN2's proved argument applies | Same frozen rule/ROM and derived preparation |
| Actual Age-only triple/native quiet at2050 | GAWN17/GAWN4 proved arguments apply | No arbitrary upper-triple quantifier |
| Full current-U repair of that prepared Age-only triple | proved | No further errors |
| Kernel/coordinate/bit checks | measured transcription supplements | No full trajectory simulation |
| Info-changing early faults, arbitrary clocks or multiple GF offsets | unproved | The theorem does not establish its premises after those faults |
| Actual lower-burst reachability/general reachable upper triple | unproved | Prepared corollary is not a reachability proof |
| Surrounding E0, higher-error closure, positive iid rate, all-time memory | unproved | No complete reliability theorem |
| Faithful corrected Gray refutation/minimum globally sufficient change | unproved | All GAWN2 departures remain |
| Rule/ROM/constants/CURRENT change or commit | none | Earlier frozen assets preserved |
