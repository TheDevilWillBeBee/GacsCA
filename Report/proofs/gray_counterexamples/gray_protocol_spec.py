"""Explicit physical refinement obligations extracted from Gray pp14–41.

This is a specification/checklist, not a full transition rule. Constants
and active/rest arithmetic are exact. Unspecified interpreter/courier
microcode and the computed-SimBit composition remain explicit obligations.
"""
from dataclasses import dataclass,asdict

Q=8192
U=128*Q
LAMBDA=24
C=104


@dataclass(frozen=True)
class Stage:
    number:int
    name:str
    start:int
    active_end:int
    end:int


STAGES=tuple(Stage(i+1,name,start*Q,active_end*Q,end*Q)
    for i,(name,start,active_end,end) in enumerate((
        ('gather1',0,16,32),('gather2',32,48,64),('gather3',64,80,96),
        ('trickle',96,104,112),('update',112,120,128))))


OBLIGATIONS=(
    dict(id='G01',target='Native equations and alphabet',pages=[14,20,21,22],
         requirement='Binary full alphabet, radius5; whole-word native votes. Flag2 h1 is an explicit correction.',
         status='native equations certified; unrestricted full-rule radius refinement unproved'),
    dict(id='G02',target='Represented-state geometry',pages=[33,35],
         requirement='One primary SimBit per upper bit, away from colony edges; reserve3 andQ−3; Q≥2K.',
         status='GR0 layout proved; new variant needs new K/layout certificate'),
    dict(id='G03',target='Spatial copy geometry',pages=[33,34],
         requirement='Five copies at offsets−2..2 for every stored or moving logical simulation bit and every operation; majority every tick.',
         status='GR0 has fivefold operators; full arbitrary-clock refinement and fresh E0 lift unproved'),
    dict(id='G04',target='Computed clock and stage partition',pages=[22,34,41],
         requirement='Computed Age includes+1; first three stages32Q, last two16Q; active first half; correct initial/reset boundary conventions.',
         status='stage arithmetic proved; physical operator boundary refinement unproved'),
    dict(id='G05',target='Gather snapshots and mail geometry',pages=[28,29,34],
         requirement='Three separate same-period state gathers, own and five neighbours per side; all reach destinations before active ends; copies travel in parallel.',
         status='GR0 continuous-mail captures proved conditionally; stage-gated gather operator needs fresh proof'),
    dict(id='G06',target='Separate histories and temporal vote',pages=[34],
         requirement='Retain each of the three gathers in separate Workspace locations; vote in stage5 before full evaluation; own snapshot semantics explicit.',
         status='GR0 votes third stream into first early, so does not satisfy literal separate-storage protocol'),
    dict(id='G07',target='Rest',pages=[34],
         requirement='No noiseless simulation-structure transitions in rest; fivefold correction may repair actual noise; stop fronts and mail.',
         status='GR0 fails this refinement; isolated stuttering operator still to implement/certify'),
    dict(id='G08',target='Selective stage resets',pages=[33,34,35],
         requirement='At each stage start clear Mailbox and all Workspace except expressly necessary earlier gathered data; clear obsolete evaluator/scratch/Hold state.',
         status='GR0 only period-boundary/early-window wipes; true stage-reset dependency proof unproved'),
    dict(id='G09',target='Native simulation wipes',pages=[33],
         requirement='ComputedFlag1 clears Mailbox; computedFlag1 plus changed computedAddress clears all simulation structure at the physical holder.',
         status='GR0 has holder-local wipes; coherent-copy action proved only under intact computed geometry'),
    dict(id='G10',target='Early flag computation and couriers',pages=[34,35,41],
         requirement='Compute upper new Flag1/2 after gather3, deliver primary/backup SimBits toQ−3/3 before80Q; do not overwrite represented state.',
         status='GR0 delivers at selectedAge80Q, a boundary adaptation; early-prefix independence/reset/courier proof needed'),
    dict(id='G11',target='Workspace flag pulse',pages=[41],
         requirement='Use computedAddress, computedAge in[96Q,98Q), computedSimBit at3/Q−3, and computedFlag1 for WF2.',
         status='GR0 uses current correctedInfo/selectedAge; exact literal composition has a conditional radius≥8 witness'),
    dict(id='G12',target='Fetch/Execute/Find/Match/Write interpreter refinement',pages=[30,31,32,34],
         requirement='Hardwire programme by computed Address; universally evaluate own rule after temporal vote within stage5; exact ROM, key routing, execution, result distribution.',
         status='GR0 own abstract programme proved, but timing/physical refinement unproved; these micro-operations are implementation choices not printed Gray pseudocode'),
    dict(id='G13',target='Final output and period commit',pages=[34],
         requirement='All upper output bits reach Workspace before120Q; rest preserves them; commit SimBits at next computedAge0, then gather the new state.',
         status='GR0 evaluation begins70Q and runs across stages; new isolated final-window programme needed'),
    dict(id='G14',target='Sufficient colony size and update runtime',pages=[31,34],
         requirement='Programme length a+b log2(QU) fitsQ and update runtime3Q+a log2Q+b fits8Q, or prove actual replacement compiler universally.',
         status='Published a,b unspecified; Q8192 alone is insufficient; fresh concrete compiler certificate required'),
    dict(id='G15',target='Encoded initialization and physical all-period closure',pages=[15,33],
         requirement='Mailbox/Workspace initially0, native Age/Flags0, recursively encoded SimBits; prove physical self-simulation at every period.',
         status='Static initialization exists; continuing physical corrected-Gray closure unproved'),
    dict(id='G16',target='Noise lifting and recovery hypotheses',pages=[34,35,36,41],
         requirement='Fresh physical E0 lift for all clocks; real1 damage/disruption remains within required boxes; later simulation residue cannot harm native geometry outside boxes.',
         status='Finite bounded-clock native campaigns measured only; unrestricted-clock full-rule lemmas unproved'),
)


def arithmetic_certificate():
    assert STAGES[0].start==0 and STAGES[-1].end==U
    assert all(a.end==b.start for a,b in zip(STAGES,STAGES[1:]))
    assert all(s.active_end-s.start==s.end-s.active_end for s in STAGES)
    assert [s.end-s.start for s in STAGES]==[U//4]*3+[U//8]*2
    assert 3*U//4==96*Q and 3*U//4+2*Q==98*Q
    return dict(Q=Q,U=U,error_lambda=LAMBDA,error_separation_c=C,
                stages=[asdict(s) for s in STAGES],obligations=list(OBLIGATIONS),
                stage_arithmetic_proved=True,physical_refinement_proved=False,
                global_reliability_established=False)
