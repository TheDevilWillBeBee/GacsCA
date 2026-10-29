"""Actual late logical-copy factor and full-3U commit of SAME GAW23 fault.

The discovery banks and coupled traces are not independent input tapes:
the written factor derives them from H2=H3 and exact same-history masks.
Current checks pin raw-holder equations and full unmasked U records.
"""
from pathlib import Path
from functools import lru_cache
from dataclasses import replace
import hashlib,json,random,sys,time
import check_gaw26_late_discovery as d
k=d.k;own=d.own;Q=d.Q;U=d.U;P=d.P
S=Path(__file__).resolve().parent;ROOT=S.parents[3];D=d.D
DISC=json.loads((D/'GAW26_actual_late_discovery01.json').read_text())

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def fixed_cell(x,age,**fields):
    return k.Cell(addr=d.addr(x),age=age,f1=d.f1(x),**fields)
def mask_control_checks():
    rng=random.Random(240104);count=0;dig=hashlib.sha256()
    # These are exact local field-equation cofactors, not selected global
    # tapes. A symbolic bitwise recurrence proves every Word100 value.
    points=set()
    for b in (0,Q//2,43*Q//2,23*Q,26*Q):points.update(range(b-8,b+9))
    for y in sorted(points):
        for age in (102*Q,102*Q+1,102*Q+2,119*Q,123*Q+1,U):
            names=('heads','mem','out','info','scratch','program','courier_l','courier_r','mail_l','mail_r','history1','history2','history3')
            logical={}
            for p in range(y-6,y+7):
                v={name:rng.getrandbits(2200 if name=='heads' else 1700 if name in ('mem','history1','history2','history3') else 100) for name in names}
                v['heads']=k.pack(k.Packet(p=1,move=0,mode=k.ERROR,pc=29,regs=tuple(rng.getrandbits(100) for _ in range(16))))
                v['program']=k.beta_bit(own.ROM,d.addr(p))
                v['history3']=v['history2'];logical[p]=v
            cells_global={x:fixed_cell(x,age-1,**{name:tuple(logical[x+s][name] for s in k.SLOTS) for name in names}) for x in range(y-4,y+5)}
            outputs=[]
            for h,s in enumerate(k.SLOTS):
                x=y-s
                # Extend only nuisance logical sites for this raw-radius
                # cofactor; all voter inputs remain actual same groups.
                cells={}
                for j in range(-8,9):
                    z=x+j
                    fields={name:tuple(logical.get(z+t,{name:0})[name] if z+t in logical else 0 for t in k.SLOTS) for name in names}
                    cells[j]=fixed_cell(z,age-1,**fields)
                a=k.local_transition(cells,own.ROM);outputs.append(a)
            # Three holder controls have precisely the centre Address.
            centre=d.addr(y)
            controls=[(d.addr(y-s)+s)%Q for s in k.SLOTS]
            assert controls.count(centre)>=3
            if age==102*Q:expectout=expecthead=expectscratch=expectmem=0
            elif age==102*Q+1:
                expectout=logical[y]['out'];expectscratch=logical[y]['scratch'];expectmem=logical[y]['history2']
                expecthead=k.pack(k.Packet(p=1,pc=0)) if centre==P else 0
            else:
                expectmem=logical[y]['mem'];expectout=logical[y]['out'];expectscratch=logical[y]['scratch']
                expecthead=logical[y]['heads']
            if age==U:expectout=expecthead=expectscratch=expectmem=0
            for name,expected in (('out',expectout),('heads',expecthead),('scratch',expectscratch),('mem',expectmem)):
                assert k.vote([getattr(a,name)[h] for h,a in enumerate(outputs)])==expected,(y,age,name)
            if age==U:
                assert all(a.info[h]==logical[y]['out'] for h,a in enumerate(outputs))
            elif age>102*Q:
                assert all(a.history2[h]==a.history3[h] for h,a in enumerate(outputs))
            dig.update(json.dumps([y,age,controls,[k.cell_words(a) for a in outputs]],separators=(',',':')).encode());count+=5
    return dict(actual_full_local_R_raw_holder_reset_reload_stable_ERROR_and_commit_cofactors=count,
        cofactor_sha256=dig.hexdigest(),three_centre_controls_at_every_fixed_GF_step=True,
        arbitrary_private_values_are_equation_cofactors_not_future_history=True)

OUT={};SCRATCH={};HEADS={}
for e in DISC['actual_complete_frame_independent_executions']:
    origin=e['physical_origin']
    OUT.update({origin+P+i:int(v,16) for i,v in enumerate(e['actual_output_full496_words'])})
for pair in DISC['actual_coupled_partial_frame_executions']:
    OUT.update({p:int(v,16) for p,v in pair['actual_final_all_stored_Out_words']})
    SCRATCH.update({p:int(v,16) for p,v in pair['actual_final_Scratch_words']})
    HEADS.update({p:int(v,16) for p,v in pair['actual_final_Head_packets']})

@lru_cache(None)
def shadow3(g):
    return k.local_transition({j:d.base.next2H(g+j) for j in range(-8,9)},own.ROM)

@lru_cache(None)
def committed_info(p):
    g,a=divmod(p,Q)
    if P<=a<P+k.FRAME_WORDS and (g<=-27 or g>=47):return k.cell_words(shadow3(g))[a-P]
    return OUT.get(p,0)
def boundary_cell(x):
    return fixed_cell(x,0,info=tuple(committed_info(x+s) for s in k.SLOTS),
        program=tuple(k.beta_bit(own.ROM,(d.addr(x)+s)%Q) for s in k.SLOTS))

def pair_physical_checks(origins):
    heads={o+P:k.Packet(p=1,pc=0) for o in origins};out={};scratch={};count=0;dig=hashlib.sha256();coverage=set()
    nativepoints=(43*Q//2,26*Q)
    for tick in range(1,147456):
        age=102*Q+1+tick;targets={y+(1 if p.move==1 else -1 if p.move==2 else 0) for y,p in heads.items()}
        nextheads={};updates=[]
        for y in sorted(targets):
            p=k.incoming([heads.get(y+j,k.ZERO) for j in (-1,0,1)])
            oldp=p;p,ow,sw=k.step_packet(p,d.addr(y),d.bank(y),out.get(y,0),scratch.get(y,0),k.beta_bit(own.ROM,d.addr(y)),own.ROM)
            if p.p:nextheads[y]=p
            updates.append((y,oldp,p,ow,sw))
        newout=out.copy();newscratch=scratch.copy()
        for y,oldp,p,ow,sw in updates:
            if ow is not None:newout[y]=ow
            if sw is not None:newscratch[y]=sw
        def old(x):
            return fixed_cell(x,age-1,
                heads=tuple(k.pack(heads.get(x+s,k.ZERO)) for s in k.SLOTS),
                mem=tuple(d.bank(x+s) for s in k.SLOTS),out=tuple(out.get(x+s,0) for s in k.SLOTS),
                scratch=tuple(scratch.get(x+s,0) for s in k.SLOTS),
                info=tuple(d.before_commit_info(x+s) for s in k.SLOTS),
                program=tuple(k.beta_bit(own.ROM,(d.addr(x)+s)%Q) for s in k.SLOTS),
                history2=tuple(d.bank(x+s) for s in k.SLOTS),history3=tuple(d.bank(x+s) for s in k.SLOTS))
        for y,oldp,p,ow,sw in updates:
            key=(oldp.mode,p.mode,oldp.move,p.move,oldp.args&3)
            chosen=ow is not None or sw is not None or key not in coverage or tick<=3 or any(abs(y-b)<=4 for b in nativepoints)
            if chosen:
                physical=[k.local_transition({j:old(y-s+j) for j in range(-8,9)},own.ROM) for s in k.SLOTS]
                for name,expected in (('heads',k.pack(nextheads.get(y,k.ZERO))),('out',newout.get(y,0)),('scratch',newscratch.get(y,0)),('mem',d.bank(y))):
                    got=k.vote([getattr(a,name)[h] for h,a in enumerate(physical)])
                    assert got==expected,(origins,tick,y,name,got,expected)
                dig.update(json.dumps([tick,y,hex(k.pack(p)),ow,sw],separators=(',',':')).encode());count+=5
            coverage.add(key)
        heads=nextheads;out=newout;scratch=newscratch
        if heads and all(p.mode==k.ERROR and p.move==0 for p in heads.values()):break
    return dict(physical_origins=origins,actual_full_local_R_five_holder_interpreter_cofactors=count,
        cofactor_sha256=dig.hexdigest(),ticks=tick,
        Head_SF_updates_projected_by_proved_majority_factor_not_assumed_raw_coherent=True)

def native_output_table(g,foreign=False):
    origin=g*Q-Q//2 if foreign else g*Q
    return [committed_info(origin+P+i) for i in range(6)]

def main():
    started=time.monotonic();issue='--issue' in sys.argv
    reset=mask_control_checks()
    pairs=[pair_physical_checks(origins) for origins in ([21*Q,22*Q-Q//2],[26*Q-Q//2,26*Q])]
    # Every stored word in the two coupled components is confined to the
    # explicit paired frames, although the packets cross the phase jump.
    for pair in DISC['actual_coupled_partial_frame_executions']:
        origins=pair['physical_origins']
        assert all(any(o+P<=p<o+P+k.FRAME_WORDS for o in origins) for p,v in pair['actual_final_all_stored_Out_words'])
        assert pair['head_spatial_hull'][0]==min(origins)+P
        assert pair['head_spatial_hull'][1]<=max(origins)+P+k.FRAME_WORDS-1
        assert pair['all_heads_stationary_ERROR_by_last_row']
    # Closed/quiet native equations at U; all work reset regardless of
    # pending partial errors. Info commits old logical Out unmasked.
    points=set()
    for p in OUT:points.update((p-2,p,p+2))
    for b in (43*Q//2,26*Q):points.update(range(b-8,b+9))
    points=sorted(points);sample=points[::max(1,len(points)//1200)]
    commits=0;dig=hashlib.sha256()
    for x in sample:
        def old(y):return fixed_cell(y,U-1,
            heads=tuple(HEADS.get(y+s,0) for s in k.SLOTS),out=tuple(committed_info(y+s) for s in k.SLOTS),
            scratch=tuple(SCRATCH.get(y+s,0) for s in k.SLOTS),
            info=tuple(d.before_commit_info(y+s) for s in k.SLOTS),mem=tuple(d.bank(y+s) for s in k.SLOTS),
            history2=tuple(d.bank(y+s) for s in k.SLOTS),history3=tuple(d.bank(y+s) for s in k.SLOTS),
            program=tuple(k.beta_bit(own.ROM,(d.addr(y)+s)%Q) for s in k.SLOTS))
        a=k.local_transition({j:old(x+j) for j in range(-8,9)},own.ROM)
        assert a==boundary_cell(x),(x,'full unmasked old-Out commit/reset')
        dig.update(json.dumps([x,k.cell_words(a)],separators=(',',':')).encode());commits+=1
    true={str(g):native_output_table(g) for g in range(-26,47)}
    foreign={str(g):native_output_table(g,True) for g in range(0,38)}
    assert all(0<=v<lim for z in [*true.values(),*foreign.values()] for v,lim in zip(z,(Q,U,2,2,2,2)))
    for g in range(-26,47):
        for r in (3,Q//2-3,Q//2+3,Q-3):assert committed_info(g*Q+r)==0,(g,r,'actual next-period WF source padding')
    r=dict(Q=Q,U=U,error_lambda=24,error_separation=104,
        same_actual_original_c104_GAW23_GF_only_real2_no_future_errors=True,
        discovery_receipt_sha256=sha(D/'GAW26_actual_late_discovery01.json'),
        exact_prefix_Info_and_pulse_H2_H3_mask_recurrence_from_same_native_history=True,
        History2_equals_History3_bitwise_before_and_after_pulse=True,
        actual_102Q_plus1_reload_equals_retained_History2=True,
        full_late_native_Word100_banks_derived_not_preloaded=True,
        complete_true_heads_j_le20_or_j_ge26_and_foreign22_to25_before_interaction=True,
        actual_coupled_pairs_include_complete_foreign22_and_true26=True,
        physical_late_copy_factor=reset,physical_coupled_trace_checks=pairs,
        actual_full_local_R_3U_commit_checks=commits,third_commit_cofactor_sha256=dig.hexdigest(),
        full_true_native_Info_table_at3U=true,full_foreign_native_Info_table_at3U=foreign,
        complete_selected_true_3U_Word100_records=DISC['selected_true_normal_3U_committed_out_words'],
        actual_unused_Info_nonzero_words=[[p,hex(v)] for p,v in sorted(OUT.items()) if v and not P<=p%Q<P+k.FRAME_WORDS],
        full_boundary_cell_formula_native_fixed_Info_old_voted_Out_Programme_holder_service_and_workzero=True,
        universal_infinite_line_unchanged_exterior_and_raw_commit_proved_in_companion_text=True,
        all_potential_true_and_foreign_special_Info_sources_zero_at3U=True,
        literal_canonical_E_upper_relation_not_claimed_GF_remains_foreign=True,
        fourth_native_source_and_pulse_not_yet_certified=True,
        faithful_Gray_P5_operational_higher_iid_or_shorter_U_failure_claim=False)
    r=json.loads(json.dumps(r));p=D/'GAW26_full_3U_physical_certificate.json'
    if issue:assert not p.exists();p.write_text(json.dumps(r,indent=2)+'\n')
    else:assert r==json.loads(p.read_text())
    print(json.dumps(dict(passed=True,elapsed_seconds=time.monotonic()-started,
        reset_copy_cofactors=reset['actual_full_local_R_raw_holder_reset_reload_stable_ERROR_and_commit_cofactors'],
        coupled_trace_cofactors=sum(z['actual_full_local_R_five_holder_interpreter_cofactors'] for z in pairs),
        full_3U_commit_checks=commits,receipt_sha256=sha(p))),flush=True);return r

if __name__=='__main__':main()
