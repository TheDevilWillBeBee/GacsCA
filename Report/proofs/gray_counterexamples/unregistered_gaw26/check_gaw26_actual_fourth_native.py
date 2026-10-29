"""Actual fourth pulse from the same fault and the proved raw third boundary.

Commands come from the literal early emissions and actual guarded couriers.
The event tracker is not substituted for Info at the fourth commit.
"""
from pathlib import Path
import hashlib,json,struct,sys,time
import check_gaw26_actual_fourth_sources as sources
import check_gaw26_late_discovery as d
import check_gaw23_actual_native_factor as old
k=d.k;own=d.own;Q=d.Q;U=d.U;P=d.P
S=Path(__file__).resolve().parent;ROOT=S.parents[3];D=d.D

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read_events():
    data=(D/'GAW26_fourth_native_pulse_events01.bin').read_bytes();pos=0;records=[]
    while pos<len(data):
        row,n,ns=struct.unpack_from('<iii',data,pos);pos+=12
        v=list(struct.unpack_from('<'+'i'*(3*n+2*ns),data,pos));pos+=4*len(v)
        seg=[tuple(v[3*i:3*i+3]) for i in range(n)]
        src={v[3*n+2*i]:v[3*n+2*i+1] for i in range(ns)}
        assert all(a<b and 1<=z<=7 for a,b,z in seg)
        assert all(seg[i][1]<=seg[i+1][0] for i in range(n-1))
        records.append((row,seg,src))
    assert pos==len(data) and records[0][0]==0 and records[-1][0]==U
    return records

def courier_contracts():
    fixed=[(21*Q,43*Q//2,2),(43*Q//2,51*Q//2,1),(51*Q//2,26*Q,3)]
    points=set()
    for b in (21*Q,43*Q//2,51*Q//2,26*Q):points.update(range(b-4,b+5))
    for origin in (21*Q,22*Q-Q//2,26*Q-Q//2,26*Q):
        for r in (3,P+2,Q-3):points.update(range(origin+r-3,origin+r+4))
    mails=cs=0;dig=hashlib.sha256()
    for y in sorted(points):
        for age in (1,37,32*Q+1,32*Q+37,64*Q+1,64*Q+37):
            vals=[]
            for h,s in enumerate(k.SLOTS):
                x=y-s
                c={j:old.native_cell(fixed,x+j,age-1,
                    info=(37,)*5,mail_l=(37,)*5,mail_r=(37,)*5) for j in range(-8,9)}
                vals.append(k.local_transition(c,own.ROM).mail_l[h])
            expect=0 if old.value(fixed,y)&2 else 37
            assert k.vote(vals)==expect,(y,age,vals,expect);mails+=1
        for a,b in ((0,0),(0,1),(1,0),(1,1)):
            vals=[]
            for h,s in enumerate(k.SLOTS):
                x=y-s;c={}
                for j in range(-8,9):
                    c[j]=old.native_cell(fixed,x+j,75*Q+10,
                        courier_r=tuple(a if x+j+t==y else b if x+j+t==y-1 else 0 for t in k.SLOTS))
                vals.append(k.local_transition(c,own.ROM).courier_r[h])
            q=d.addr(y)
            expect=((a|b) if q==Q-3 else b) if P+2<=q<=Q-3 else 0
            assert k.vote(vals)==expect,(y,a,b,vals,expect);cs+=1
            dig.update(json.dumps([y,a,b,vals,expect],separators=(',',':')).encode())
    previous_argv=sys.argv
    try:
        sys.argv=[str(S/'check_gaw26_actual_fourth_sources.py')]
        actual=sources.main()
    finally:sys.argv=previous_argv
    active={g*Q+P+2 for g in actual['actual_true_positive_Flag1_heads']}
    active.update(g*Q-Q//2+P+2 for g in actual['actual_foreign_positive_Flag1_heads'])
    seeds=sorted(active);first={}
    for tick in range(1,5*Q):
        nxt=set()
        for y in active|{x+1 for x in active}:
            q=d.addr(y)
            bit=(y in active or y-1 in active) if q==Q-3 else y-1 in active
            if P+2<=q<=Q-3 and bit:
                nxt.add(y)
                if q==Q-3:first.setdefault(y,tick)
        active=nxt
    certified=list(map(int,(D/'GAW26_derived_actual_fourth_F1_sources.txt').read_text().split()))
    assert sorted(active)==certified and max(first.values())==4339
    assert actual['actual_positive_Flag2_receivers']==[] and actual['actual_all_left_sources_zero']
    return dict(actual_Mail_LOAD_shift_Flag1_erasure_holder_cofactors=mails,
        actual_guarded_right_courier_holder_cofactors=cs,cofactor_sha256=dig.hexdigest(),
        actual_75Q_positive_right_seed_positions=seeds,
        exact_source_positions=certified,maximum_first_arrival_after75Q=4339,
        partial_true21_foreign26_lineages_killed_by_guard=True,
        actual_left_couriers_zero_from_computed_early_Flag2_zero=True,
        all_actual_source_five_Info_copies1_at_fourth80Q_minus1=True)

def observed_Address_envelope():
    names=(('unregistered_gaw23','GAW23_first_pulse_events02.bin'),
        ('unregistered_gaw24','GAW24_second_native_pulse_events01.bin'),
        ('unregistered_gaw25','GAW25_third_native_pulse_events01.bin'),
        ('unregistered_gaw26','GAW26_fourth_native_pulse_events01.bin'))
    low=high=None;maximum_width=0;records=0
    for directory,name in names:
        data=(ROOT/'figs/gray_counterexamples'/directory/name).read_bytes();pos=0
        while pos<len(data):
            row,n,ns=struct.unpack_from('<iii',data,pos);pos+=12
            v=struct.unpack_from('<'+'i'*(3*n+2*ns),data,pos);pos+=4*len(v)
            runs=[(v[3*i],v[3*i+1]) for i in range(n) if v[3*i+2]&1]
            if runs:
                lo=min(a for a,b in runs);hi=max(b for a,b in runs)
                low=lo if low is None else min(low,lo);high=hi if high is None else max(high,hi)
                maximum_width=max(maximum_width,sum(b-a for a,b in runs))
            records+=1
        assert pos==len(data)
    assert low==0 and high<2*Q*Q and 4*U-1<U*U//16
    return dict(all_four_actual_native_event_records=records,
        exact_Address_disagreement_union_spatial_hull=[low,high],
        maximum_instantaneous_native_Address_wrong_cell_count=maximum_width,
        witnessed_rows1_through4U_fit_spatial_0_to2Q_squared_and_time1_to1_plusU_squared_over16=True,
        future_Address_P5_allowance_violation_or_all_SF_envelope_claim=False)

def main():
    started=time.monotonic();issue='--issue' in sys.argv;records=read_events()
    scalar=json.loads((D/'GAW26_fourth_native_audit_issue01.log').read_text())
    assert scalar['passed'] and scalar['exact_final_native_segments']==[list(z) for z in records[-1][1]]
    assert records[0][1]==[(21*Q,43*Q//2,2),(43*Q//2,51*Q//2,1),(51*Q//2,26*Q,3)]
    local=old.full_local_checks(records);courier=courier_contracts();envelope=observed_Address_envelope()
    r=dict(Q=Q,U=U,error_lambda=24,error_separation=104,
        third_full_raw_boundary_receipt_sha256=sha(D/'GAW26_full_3U_physical_certificate.json'),
        fourth_actual_early_source_receipt_sha256=sha(D/'GAW26_actual_fourth_sources_certificate.json'),
        actual_fourth_event_file_sha256=sha(D/'GAW26_fourth_native_pulse_events01.bin'),
        actual_fourth_analysis_driver_sha256=sha(S/'gaw26_fourth_native_pulse.c'),
        independent_fourth_native_audit_source_sha256=sha(S/'gaw26_fourth_native_audit.c'),
        same_original_shared139264_site_row1_GF_only_real2_no_later_errors=True,
        initial_source_Info_zero_from_actual_old_Out_at3U_not_assumed=True,
        actual_fourth_native_WF2_and_Flag2_zero_all_rows=True,
        all_actual_right_sources_derived_from_unmasked3U_records_noncommon_upper_Ages=True,
        scalar_word_quorum_computed_primary_and_source_wipe_audit=scalar,
        actual_frozen_local_R_native_cofactors=local,actual_courier_contracts=courier,
        actual_finite_Address_allowance_check=envelope,
        native_GF_shifted_intervals_at4U=[[a,b] for a,b,v in records[-1][1] if v&1],
        native_GF_width_at4U=sum(b-a for a,b,v in records[-1][1] if v&1),
        native_Flag1_intervals_at4U=[[a,b] for a,b,v in records[-1][1] if v&2],
        native_common_Age_at4U=0,native_WF1_WF2_Flag2_zero_at4U=all(v<4 for a,b,v in records[-1][1]),
        fourth_native_fixed_by_relative_row=next(row for row,seg,src in records if row>=98*Q and seg==records[-1][1]),
        fourth_full_Out_commit_encoding_decoded_damage_or_later_orbit_proved=False,
        auxiliary_source_bits_at4U_not_claimed_physical_Info=True,
        faithful_Gray_Proposition5_iid_memory_higher_or_shorterU_claim=False)
    r=json.loads(json.dumps(r));path=D/'GAW26_actual_fourth_native_pulse_certificate.json'
    if issue:assert not path.exists();path.write_text(json.dumps(r,indent=2)+'\n')
    else:assert r==json.loads(path.read_text())
    print(json.dumps(dict(passed=True,elapsed_seconds=time.monotonic()-started,
        actual_fourth_right_sources=len(records[0][2]),actual_fourth_native_event_intervals=scalar['independent_event_intervals'],
        actual_local_R_cofactors=local['actual_frozen_local_R_native_and_computed_primary_checks'],
        receipt_sha256=sha(path))),flush=True);return r

if __name__=='__main__':main()
