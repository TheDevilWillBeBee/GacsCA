# Selected noisy commit embedded in the full lower ring

2026-09-27. A conditional gluing argument now connects the recorded 73-colony
burst and faulty commit to the full 32768-colony lower ring: 1073741824 physical
cells, the same fixed G rule and the same 8404 replacement marks. At commit,
only represented upper position **9566** has a wrong Info record. It is all zero,
with **26 raw word /12 mutable word differences**, including controller fields.

This is a descriptor-semantics proof composition using the existing independent
trajectory audits and noiseless refinements. It is **not** a new literal full-ring
GPU execution or a proof-assistant theorem. Subsequent full-ring physical repair
is not established here. The full project goal remains active.

## Why the earlier finite light cone was insufficient

[PREFIX_EMBEDDING.md](PREFIX_EMBEDDING.md) established agreement in seven complete
central colonies after 116418 noisy ticks, but its ordinary radius-seven cone
became empty before commit. Agreement at that single time could not justify an
unaffected full-ring exterior.

The new construction instead proves that the noisy window agrees with its own
noiseless comparison in two boundary collars throughout the interval. Its
noiseless comparison agrees with the full noiseless ring in those collars by the
existing prefix dependence argument. This supplies a valid full trajectory by
local gluing; it does not assume exterior confinement from a late snapshot.

## New descriptor identities

`certify_retimed_holder_late_confinement.py` covers every old Age from 1232000001
through U-1 in three bounded symbolic intervals: active final evaluation,
inactive waiting, and commit. At each colony boundary it checks all nonmail raw
outputs at physical sites -11 through 10. Mutable inputs are assigned to the
logical colony that owns each procedure replica; Flag1 belongs to its physical
colony. Signals are arbitrary shared raw inputs, **not assumed zero**.

Given canonical geometry, fixed ROM, coherent procedures, zero input mail,
Flag2/Wf zero, and locally empty controllers outside ROM:

- Each nonmail output depends only on mutable inputs in its owner colony.
- Flag2/Wf remain zero, geometry remains canonical, and shared Signals remain
  shared. Flag1 may have any pattern.
- The complete-state separation additionally requires **zero output mail in
  both trajectories**. The checker explicitly excludes 880 mail outputs per
  interval; it checks the other 2508 outputs. This exclusion is a premise, not
  an unproved assertion that arbitrary controllers cannot emit mail.

`certify_retimed_holder_late_procedure_image.py` independently checks all 50
nonmail procedure copies in each interval, at every canonical Address, with
arbitrary simultaneous head/controller records and coherent metadata. Their
five output replicas agree even with arbitrary physical Flag1 and Signals.
There is no one-head assumption. Shared Signal inputs evolve identically;
Flag2/Wf remain zero. Zero output mail restores the complete procedure image.

Ordinary tails are the addresses 27721 through 32767 between successive ROM
cores. The first/last marker identities give zero outgoing controllers at the
two tail endpoints, with arbitrary neighboring core controllers. The separate
`certify_retimed_holder_empty_tail_interior.py` proves all 45 target controller
copies zero when only the three old logical controller records at offsets
-1,0,1 and the target first marker are zero. All other controllers, metadata,
flags, Wf, Signals and mail remain arbitrary; canonical uniform geometry is
required. This covers all 5045 interior tail sites without falsely requiring
the whole radius-seven raw neighborhood to be empty.

Together these facts keep every initially empty ordinary tail empty. They do not
erase, truncate or ignore controllers in the one exceptional tail, colony 36.

## Applying the identities to the recorded trajectory

The new join checks every complete raw post-burst entry field through the
existing full-state reconstruction. At tick 34:

1. Address/Age and fixed metadata are canonical, procedures coherent, all mail
   and Flag2/Wf zero. Signals equal the noiseless window everywhere, including
   the nonzero edge Signals.
2. Primary procedure differences occur only in colony 36; Flag1 differences lie
   inside the enclosed group. Every ordinary tail is empty except colony 36's
   two extra controllers.
3. The receiving colony 37's tail is empty. Its last marker prevents an entering
   extra head from escaping to colony 38. The first marker at colony 36 prevents
   escape to colony 35. The exceptional controllers can move and interact inside
   colonies 36/37; no healthy-controller behavior is assumed for them.

For the subsequent interval, the already completed recovery audit checks zero
mail output on every physical tick. The completed macrostep audit supplies the
same property: each scalar literal event asserts zero mail output; guarded
transport moves only controller words; inactive intervals retain procedures;
commit changes only Data and all its full native outputs are compared. Input
receipt/artifact and source hashes are checked again. The healthy comparison's
noiseless schedule has no live mail or SEND during this entire late interval.

Induct simultaneously on canonical geometry, coherent procedure images, zero
Flag2/Wf, shared Signals and empty ordinary tails. Apply nonmail separation at
the boundaries of colonies 36/37; append the independently verified zero mail
outputs. Procedure differences remain in these two logical colonies, and raw
replicas extend the support by at most two physical sites. Thus all raw
differences after tick 34 lie in **[36Q-2,38Q+2)** through commit. This reasoning
uses the actual multihead trajectory and the explicit no-mail condition.

For ticks 0 through 34, ordinary radius-seven locality and the fault locations
give the conservative support **[36Q-238,37Q+238)**, without any canonical-geometry
assumption during the burst. Both support bounds leave the collars at **35Q and
39Q** untouched.

## Full-ring gluing

Let W be the audited noisy window, H its noiseless comparison, and B the full
noiseless lower-ring trajectory from the inherited complete bank checkpoint.
Translate the window by 9529Q physical sites. The prefix dependence result gives
H=B on the relevant central colonies at every late precommit time. One additional
ordinary local step supplies the necessary agreement at commit itself.

Define a diagnostic full configuration P at each time by taking W inside
[35Q,39Q) and B outside. W=H=B on the complete seven-site collars on both sides
of each cut. Every local neighborhood used by P is therefore identical either
to the corresponding W neighborhood or to the B neighborhood. Consequently P
obeys the unchanged local rule at every site, with exactly the translated fault
marks. At burst start P=B. Determinism identifies P with the intended full-ring
faulted trajectory. This construction establishes the unaffected exterior as a
conclusion; it was not an input assumption.

The witness NPZ stores the four-colony logical procedure/Signal patch and full
committed Info array. A full upper G step is computed only for diagnostic
comparison with the healthy successor; it is never installed into the evolving
lower state. The all-zero wrong Info retains its malformed static metadata.
It is not silently normalized into a valid encoded entry relation.

## Validation, provenance and limits

Accepted receipts under `figs/fixed_rule/`:

| Receipt | Time | Process peak RSS |
|---|---:|---:|
| `retimed_holder_late_confinement_v1.json` | 3.633350 s | 66820 KiB |
| `retimed_holder_late_procedure_image_v1.json` | 1.506681 s | 61900 KiB |
| `retimed_holder_empty_tail_interior_v1.json` | 1.334952 s | 57740 KiB |
| `retimed_holder_noisy_commit_embedding_v2.json` | 28.233728 s | 1006796 KiB |

The 13 final focused tests pass in **5.069 s**. They reject missing first/last
markers, unconfined tail controllers, a foreign Data output, a dropped controller
replica, hidden distance-two controller dependence, and an undersized gluing
collar. The generic gluing test compares complete-word neighborhood substitution;
it is explicitly an abstract local-map test, not another physical automaton.

The first join and its exact source are preserved. The accepted second join adds
the explicit three-record interior-tail premise; its diagnostic artifact is
byte-for-byte identical to the first. A whole-stencil empty-controller lemma alone
would not justify tail sites whose raw neighborhood also contains a core head.
No previous physical trajectory or rule was changed. All new jobs are terminal;
all CPU watchdogs are at most 2 GiB, and no GPU allocation was made.

Final evidence index:
`figs/fixed_rule/retimed_holder_commit_embedding_evidence_v1.json`.
The fixed descriptor/ROM and physical alphabet remain those documented in the
noiseless self-reference construction. Gray's ProgramBit projection and Gacs
9.2–9.3 justify the specialized modified-rule target; these new confinement
identities are checked properties of this candidate, not quoted paper lemmas.

The next obligation is to extend the full-ring correspondence through the
physical reset and normalization prefix, then join to the existing later-period
identities and receiving-layer repair. The 73-colony repair and diagnostic full
upper repair are already measured, but their full lower-ring physical link is
not claimed here. General amplification, thresholds, robust finite caps, Q/U
optimization, depth three and the Flag2/SimBit source-fidelity issues remain open.
