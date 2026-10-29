# SP30: two explicit intact initializations and restricted all-time bit memory

This uses the **already changed SP30** of J189, with its own ROM,
Q=1024 and U=475136. It changes neither that rule nor active G17.
The choice of origin below is a translation of the encoding, not a
new local rule. [Checker](check_signal_reservation1024_memory.py),
[receipt](../../figs/robustness/SP30_intact_memory_certificate.json),
[complete-start physical simulation proof](SP30_OWN_RULE.md).

## Statement

There are two explicitly defined configurations X_0 and X_1 on Z of
the same finite SP30 alphabet, each an intact infinite self-encoding
hierarchy, and the radius-two observable

    D(Z) = majority5( Z(-s).Info[s+2], s=-2,-1,0,1,2 ),

such that D(F30^t X_b)=b for every integer t>=0 and b in {0,1}.
The same equality holds for the actual raw states at every tick under
arbitrary whole-cell overwrites whose **entire location set, including
tick0, is globally isolated E0 with lambda24**, in the precise sense of
J189. In that case each computed state also has all five indicated
copies equal to b. There is one physical error history, not an
independent error history at each decoded level.

The noise premise is deterministic and restrictive. Positive-rate iid
errors on the infinite lattice almost surely fail it. Thus this is
**not** a positive-iid reliability or memory theorem.

## Explicit infinite configurations

Write E_a=T_a E30 for the translated encoding with a=-94 and
(T_a Z)(x)=Z(x-a). Its colony g consists of physical sites
a+gQ,...,a+(g+1)Q-1. The actual new dependency table places native GF
bits at59,...,68 and the five upper Info bits at92,...,96; the
Info component indexed s+2 represents logical primary x+s at holder x.

For b in {0,1}, define a binary function A_b on all signed integers.
For y=-2,...,2 put A_b(y)=b. Otherwise let (g,p)=divmod(y+94,Q),
using Euclidean division, and set

    A_b(y) = bit_k((g+94) modQ)        if p=59+k, 0<=k<10;
    A_b(y) = A_b(g+p-94)              if 92<=p<=96;
    A_b(y) = 0                       otherwise.

This recursion terminates. In a recursive case y=gQ+s with
s=p-94 in[-2,2]. If g=0, y is one of the five base points, already
handled. If g!=0, |y|>=Q|g|-2, whereas |g+s|<=|g|+2; the latter
is strictly smaller because (Q-1)|g|>4. Thus absolute value is a
strictly decreasing nonnegative integer rank off the base points.
Each base equation points to itself, so its freely chosen value b is
consistent. This proves existence and uniqueness for these five base
values on Z, including negative and arbitrarily large coordinates.

At every physical site x define X_b by

    native GF = (x+94) modQ, native Age=0;
    Info[s+2] = A_b(x+s), s=-2,...,2;
    every other state field = 0.

This is a legal finite-alphabet configuration. All five holders of a
logical primary y contain A_b(y). Every encoded upper native GF bit
is correct by the first defining equation. Every encoded upper Info
bit is correct by the second. Every other represented upper field is
zero, as are the unused primaries and the two auxiliary early-flag
primaries58/965: upper native flags are zero. The new h2:77/h2:83
positions901/902 are also zero. Hence, **field by field**,

    X_b = E_a(X_b).

The same equality initializes every level simultaneously. The two
configurations differ at each of the five centre Info primaries,
and D(X_b)=b. No compactness choice or sampled payload is needed.

## All-time noiseless memory

The already proved complete-start theorem gives
F30^U E30=E30 F30. Translation invariance of this fixed CA gives
F30^U E_a=E_a F30. Consequently, from the explicit fixed point,

    F30^(nU) X_b = E_a(F30^n X_b), n>=0.

The centre primary0 has virtual address94 at all five of its holders.
It is a represented ordinary Info bit, never a special signal primary.
The actual native induction keeps computed and refined-self GF correct
and the legal common clock advancing, so keep=1. The literal five
Info output equations therefore carry their old common majority at
this primary on every input row except the commit row U-1. At commit
they use the forwarded Hold value; the period theorem supplies the
exact boundary encoding. This argument permits arbitrary evolving
private fields and flags. The checker proves the actual centre carry
and commit identity with a symbolic clock and all other inputs free,
conditional on the canonical GF premise supplied by the native proof.

In particular, these five computed copies are coherent at every
noiseless tick: they start coherent, carry the same majority between
boundaries, and the exact encoding makes them coherent at boundaries.
Let B(t)=D(F30^t X_b). Within a period it is constant, and decoding
the centre at a boundary gives

    B(nU+r) = B(nU) = (F30^n X_b)(0).Info[2] = B(n),
    0<=r<U.

The middle equality uses the actual address94 encoding equation;
the last uses centre-copy coherence. For t<U, B(t)=b. For t>=U,
n=floor(t/U)<t. Strong induction on t now proves B(t)=b for all t.
This is a finite-rank time induction, not an assumption about an
infinite limiting decoder. QED.

## Globally isolated E0 memory

Translate the physical J189 theorem by the same a. Its error premise
is translation invariant. Starting at X_b=E_a X_b, it gives computed
boundary states

    w_(nU) = E_a(F30^n X_b), n>=0,

for the single allowed physical history. Their five centre copies
are b by the noiseless result. In each intervening input row at most
two of the five distinct holders are overwritten; their majority is
therefore b. The native E0 induction supplies correct computed and
refined-self GF, hence keep=1, so all five new computed copies again
become b on a noncommit row. The complete-start theorem handles the
commit row. Induction within each period proves computed coherence
and D(raw state)=b at every tick, including current-error rows and
tick0. Whole-cell payloads may otherwise be arbitrary. QED.

For iid errors with any epsilon>0, disjoint triples of consecutive
sites in one row are all error locations with probability epsilon^3.
Independence implies such triples occur almost surely. They violate
the globally isolated E0 premise, so the theorem provides no iid
threshold. This observation does not prove iid memory failure.

| Step | Status | Limit |
| --- | --- | --- |
| Explicit A_0/A_1 on Z and strict-rank termination | proved | Actual SP30 table, translated origin -94 |
| Literal full-state fixed points X_b=E_a X_b | proved | Intact initialization; auxiliary flags initially zero |
| Centre carry/commit identities and exact period commutation | proved | Canonical GF/common clock supplied by J189 |
| All-time local bit memory without noise | proved | Two specified infinite initializations |
| All-time raw/computed memory under actual global E0 | proved | One physical isolated-E0 history, arbitrary payloads |
| Positive-iid reliability, higher-error map and general eroder | unproved | Global E0 is almost surely violated under iid noise |
| Smallest globally sufficient change | unproved | No new rule change or sufficiency claim here |

The finite initializer checks and source identities in the receipt
supplement the universal rank, encoding and time inductions above.
No numerical whole-CA trajectory is used. G17/CURRENT and all retained
programmes, constants and proposals remain unchanged; no commit.
