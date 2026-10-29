"""Finite transcription supplements to GAWN6's universal exterior proof.

No transition, inherited receipt or runtime rule is changed. No recovery
trajectory is run. The written invariant carries the value quantifiers.
"""
from pathlib import Path
import argparse, hashlib, json, random, sys, time
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
sys.path.insert(0,str(ROOT))
sys.path.insert(0,str(HERE.parent/'unregistered_gawn2'))
import small_rule_gawn2 as k
import small_compositional_cost as own
T=100*k.Q+2;L=4*k.Q
NATIVE=('addr','age','f1','f2','wf1','wf2')
SF=('heads','mem','out','info','scratch','program','courier_l','courier_r',
    'mail_l','mail_r','history1','history2','history3')
WIDTHS=dict(heads=k.HEAD_BITS,mem=17*k.WORD,history1=17*k.WORD,
            history2=17*k.WORD,history3=17*k.WORD)

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def partitions(n):
    # 0 is the fixed external reference class. Restricted-growth strings
    # enumerate every equality relation with that distinguished class.
    def rec(prefix,largest):
        if len(prefix)==n:
            yield tuple(prefix);return
        for value in range(largest+2):
            yield from rec(prefix+[value],max(largest,value))
    yield from rec([],0)

def invariant(c,x,a):
    assert c['addr']==x%k.Q and c['age']==(a+1)%k.U,(x,a,c)
    assert c['f2']==c['wf1']==c['wf2']==0,(x,a,c)
    if not -k.Q<=x<0:assert c['f1']==0,(x,a,c)

def native_cofactors():
    centres=(-k.Q-6,-k.Q-5,-k.Q-4,-k.Q-3,-k.Q-2,-k.Q-1,
             -k.Q,-k.Q+1,-k.Q+2,-k.Q+3,-k.Q+4,-k.Q+5,
             -10,-6,-5,-4,-3,-2,-1,
             k.Q,k.Q+1,k.Q+2,k.Q+3,k.Q+4,k.Q+5,
             2*k.Q-4,2*k.Q-1,2*k.Q,3*k.Q+1)
    ages=(0,16,96*k.Q-2,98*k.Q-1,T,k.U-1)
    dig=hashlib.sha256();count=0;partition_counts={}
    for n in range(6):partition_counts[str(n)]=sum(1 for _ in partitions(n))
    assert list(partition_counts.values())==[1,2,5,15,52,203]
    for x in centres:
        internal=[j for j in range(-5,6) if 0<=x+j<k.Q]
        assert len(internal)<=5
        eligible=[j for j in range(1,6) if -k.Q<=x+j<0 and
                  0<=x%k.Q+j<k.Q]
        self_choices=(0,1) if -k.Q<=x<0 else (0,)
        for a in ages:
            assert not 96*k.Q<=(a+1)%k.U<98*k.Q
            for parts in partitions(len(internal)):
                for mask in range(1<<len(eligible)):
                    for selfbit in self_choices:
                        for filler in range(4):
                            c={j:dict(addr=(x+j)%k.Q,age=a,f1=0,f2=0,wf1=0,wf2=0)
                               for j in range(-5,6)}
                            for j,part in zip(internal,parts):
                                c[j]['age']=a if part==0 else (a+193+17*part)%k.U
                                v=(0,15,((j+5)*7)&15,((j+5)*11+3)&15)[filler]
                                for h,name in enumerate(NATIVE[2:]):c[j][name]=(v>>h)&1
                            c[0]['f1']=selfbit
                            for h,j in enumerate(eligible):c[j]['f1']=(mask>>h)&1
                            out=k.scalar_native(c);invariant(out,x,a)
                            # Workspace is returned by the full kernel,
                            # checked separately below. The native scalar's
                            # zero placeholder is not treated as its proof.
                            row=[x,a,parts,mask,selfbit,filler,[out[n] for n in NATIVE]]
                            dig.update((json.dumps(row,separators=(',',':'))+'\n').encode())
                            count+=1
    return dict(checked_cases=count,reference_clocks=list(ages),centres=list(centres),
        distinguished_clock_equality_partition_counts=partition_counts,
        all_equality_partitions_and_eligible_external_F1_masks_enumerated=True,
        arbitrary_internal_flag_irrelevance_proved_algebraically_not_exhausted=True,
        inputs_outputs_sha256=dig.hexdigest())

def full_kernel():
    rng=random.Random(0x4741574e36);dig=hashlib.sha256();count=0
    centres=(-k.Q-1,-k.Q,-k.Q+1,-5,-4,-3,-2,-1,
             k.Q,k.Q+1,k.Q+2,k.Q+3,k.Q+4,k.Q+5,2*k.Q-1,2*k.Q)
    ages=(0,96*k.Q-2,98*k.Q-1,T,k.U-1)
    for x in centres:
        for a in ages:
            cells={}
            for j in range(-8,9):
                y=x+j;bad=0<=y<k.Q
                native=dict(addr=y%k.Q,age=rng.randrange(k.U) if bad else a,
                    f1=rng.randrange(2) if -k.Q<=y<k.Q else 0,
                    **{n:rng.randrange(2) if bad else 0 for n in ('f2','wf1','wf2')})
                data={name:tuple(rng.getrandbits(WIDTHS.get(name,k.WORD)) for _ in k.SLOTS)
                      for name in SF}
                # All SF is arbitrary, including outside. The one-step
                # native invariant does not require an Info hypothesis.
                cells[j]=k.Cell(**native,**data)
            out=k.local_transition(cells,own.ROM)
            invariant({n:getattr(out,n) for n in NATIVE},x,a)
            row=[x,a,[[hex(v) for v in k.cell_words(cells[j])] for j in range(-8,9)],
                 [getattr(out,n) for n in NATIVE]]
            dig.update((json.dumps(row,separators=(',',':'))+'\n').encode());count+=1
    return dict(seed=0x4741574e36,selected_cases=count,
        all13_SF_tracks_arbitrary=True,actual_computed_Workspace_guard_checked=True,
        inputs_outputs_sha256=dig.hexdigest(),universal_payload_quantifier_from_written_proof=True)

def compute():
    native=native_cofactors();full=full_kernel()
    vmin=96*k.Q-1;vmax=k.U-L-1
    assert vmin<=T<=vmax and vmax+L==k.U-1 and vmin+1==96*k.Q
    sources=[Path(__file__),HERE/'GAWN6_CANONICAL_ADDRESS_CLOCK_CONFINEMENT.md',
             HERE.parent/'unregistered_gawn2/small_rule_gawn2.py',
             HERE.parent/'unregistered_gawn2/small_compositional_cost.py',
             HERE.parent/'literal_maintenance.py',ROOT/'gacsca/maintenance.py']
    return dict(name='GAWN6 unchanged GAWN2 arbitrary-payload late native exterior invariant',
        passed=True,Q=k.Q,U=k.U,lambda_original=24,error_separation=104,
        fault_row=T,native_confinement_last_row=k.U,retained_Address_required=True,
        unrestricted_legal_Age_flags_and_all_SF_payloads_in_one_true_colony=True,
        Age_damage_confined_to_true_colony0_proved=True,
        external_Flag2_Workspace_zero_and_Flag1_only_left_neighbor_proved=True,
        proof_uses_actual_outside_Workspace_pulse_guard=True,
        subset_support_does_not_automatically_mean_real1=True,
        conditional_repair_Age_interval=[vmin,vmax],conditional_native_quiet_deadline=L,
        conditional_complete2U_reduction_for_only_Age_flags_Info_replacements_proved=True,
        universal_native_quiet_deadline_proved=False,any_new_quiet_trajectory_measured=False,
        complete2U_physical_simulation=False,GF_changing_E0_surroundings_higher_iid=False,
        Gray_G17_counterexample_or_global_minimal_change=False,
        rule_ROM_constants_G17_changed=False,native_cofactors=native,full_kernel_supplements=full,
        source_sha256={str(p.relative_to(ROOT)):sha(p) for p in sources})

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--outdir',type=Path,
        default=ROOT/'figs/gray_counterexamples/unregistered_gawn6');args=parser.parse_args()
    started=time.monotonic();result=compute();args.outdir.mkdir(parents=True,exist_ok=True)
    path=args.outdir/'GAWN6_clock_confinement_certificate.json'
    path.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps(dict(passed=True,native_cofactors=result['native_cofactors']['checked_cases'],
        full_kernel=result['full_kernel_supplements']['selected_cases'],
        elapsed=time.monotonic()-started,no_native_termination_claim=True,full_reliability=False)),flush=True)
if __name__=='__main__':main()
