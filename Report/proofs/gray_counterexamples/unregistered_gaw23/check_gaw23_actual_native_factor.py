"""Certify GAW23's actual first native period, not its full late outputs.

The complete prior bank receipt derives the early inputs from H and the
one shared fault. Here exact event records, full-local cofactors and the
written infinite-line factor compose those inputs with their real pulse.
Random private fields below are algebraic independence checks, not tapes
assigned to the actual trajectory. The proof quantifies over those fields.
"""
from pathlib import Path
import bisect,hashlib,json,random,struct,sys,time
import check_gaw23_first_banks as banks
k=banks.k;own=banks.own;Q=k.Q;U=k.U;P=k.PRIMARY_START
S=Path(__file__).resolve().parent;ROOT=S.parents[3]
D=ROOT/'figs/gray_counterexamples/unregistered_gaw23'
SLOTS=k.SLOTS
POTENTIAL={3,Q//2+3,Q-3,Q//2-3}

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def read_events():
    data=(D/'GAW23_first_pulse_events02.bin').read_bytes();pos=0;records=[]
    while pos<len(data):
        row,n,ns=struct.unpack_from('<iii',data,pos);pos+=12
        v=list(struct.unpack_from('<'+'i'*(3*n+2*ns),data,pos));pos+=4*len(v)
        seg=[tuple(v[3*i:3*i+3]) for i in range(n)]
        src={v[3*n+2*i]:v[3*n+2*i+1] for i in range(ns)}
        assert all(a<b and 1<=z<=7 for a,b,z in seg)
        assert all(seg[i][1]<=seg[i+1][0] for i in range(n-1))
        records.append((row,seg,src))
    assert pos==len(data) and records[0][0]==1 and records[-1][0]==U
    return records

def value(seg,x):
    i=bisect.bisect_right([a for a,b,z in seg],x)-1
    return seg[i][2] if i>=0 and x<seg[i][1] else 0
def native_cell(seg,x,row,**fields):
    v=value(seg,x)
    return k.Cell(addr=(x+(Q//2 if v&1 else 0))%Q,age=row%U,
        f1=(v>>1)&1,wf1=(v>>2)&1,**fields)
def nuisance_cells(seg,src,row,x,rng):
    cells={}
    for j in range(-8,9):
        z=x+j;info=[]
        for h,s in enumerate(SLOTS):
            y=z+s
            bit=((src[y]>>h)&1) if y in src else 0
            w=rng.getrandbits(100)
            # Every possible source primary has the actual low bit.
            # Non-source high/private bits are otherwise arbitrary.
            info.append((w&~1)|bit if y%Q in POTENTIAL else w)
        fields={name:tuple(rng.getrandbits(100) for _ in SLOTS) for name in
            ('heads','out','scratch','program','courier_l','courier_r','mail_l','mail_r')}
        fields.update({name:tuple(rng.getrandbits(1700) for _ in SLOTS) for name in
            ('mem','history1','history2','history3')})
        fields['info']=tuple(info)
        cells[j]=native_cell(seg,z,row,**fields)
    return cells

def full_local_checks(records):
    rng=random.Random(230104);rows=[r[0] for r in records]
    selected={0,len(records)-2}
    selected.update(bisect.bisect_left(rows,t) for t in
        (2,3,1024,2048,4096,4098,4099,80*Q-2,80*Q-1,96*Q-1,
         96*Q,96*Q+1,97*Q,98*Q-1,98*Q,99*Q))
    selected.update(int(i*(len(records)-2)/127) for i in range(128))
    count=0;dig=hashlib.sha256()
    for i in sorted(selected):
        if i>=len(records)-1:continue
        row,seg,src=records[i];after,nseg,_=records[i+1]
        if after!=row+1:continue
        points={-24*Q,24*Q,0,Q//2,17*Q,20*Q}
        for a,b,z in seg:
            points.update((a-5,a-2,a,a+2,b-2,b,b+5))
        for p in src:points.update((p-2,p,p+2))
        # Native/Info radius identities are checked at actual phase/front
        # events. Inputs to unused SF ports are free algebraic values.
        order=sorted(points)
        if len(order)>22:order=[order[int(t*(len(order)-1)/21)] for t in range(22)]
        for x in order:
            c=nuisance_cells(seg,src,row,x,rng)
            a=k.local_transition(c,own.ROM);v=value(nseg,x)
            expected=((x+(Q//2 if v&1 else 0))%Q,after%U,(v>>1)&1,0,(v>>2)&1,0)
            actual=tuple(getattr(a,n) for n in k.NATIVE_NAMES)
            assert actual==expected,(row,x,actual,expected)
            dig.update(json.dumps([row,x,list(actual)],separators=(',',':')).encode());count+=1
    return dict(actual_frozen_local_R_native_and_computed_primary_checks=count,
        cofactor_output_sha256=dig.hexdigest(),private_fields_free_in_written_native_factor=True,
        nuisance_private_fields_not_assigned_future_trajectory=True)

def mail_and_courier_contracts():
    fixed=[(0,Q//2,2),(Q//2,16*Q+Q//2,1),(16*Q+Q//2,17*Q,3)]
    masks=0;couriers=0;dig=hashlib.sha256()
    points=set()
    for b in (0,Q//2,16*Q+Q//2,17*Q):points.update(range(b-4,b+5))
    for origin in (0,-Q//2,16*Q+Q//2,17*Q):
        for t in (3,P+2,Q-3):points.update(range(origin+t-3,origin+t+4))
    for y in sorted(points):
        label=value(fixed,y)&1;addr=(y+(Q//2 if label else 0))%Q
        for age in (32*Q+1,32*Q+37,64*Q+1,64*Q+37):
            outputs=[]
            for h,s in enumerate(SLOTS):
                x=y-s
                c={j:native_cell(fixed,x+j,age-1,
                    info=(37,)*5,mail_l=(37,)*5,mail_r=(37,)*5) for j in range(-8,9)}
                z=k.local_transition(c,own.ROM);outputs.append(z.mail_l[h])
            expected=0 if value(fixed,y)&2 else 37
            assert k.vote(outputs)==expected,(y,age,outputs,expected);masks+=1
        for a,b in ((0,0),(0,1),(1,0),(1,1)):
            outputs=[]
            for h,s in enumerate(SLOTS):
                x=y-s;c={}
                for j in range(-8,9):
                    # The arbitrary two-bit local courier inputs prove
                    # the logical centre operator; they are not a tape.
                    vals=tuple(a if x+j+t==y else b if x+j+t==y-1 else 0 for t in SLOTS)
                    c[j]=native_cell(fixed,x+j,75*Q+10,courier_r=vals)
                z=k.local_transition(c,own.ROM);outputs.append(z.courier_r[h])
            expected=((a|b) if addr==Q-3 else b) if P+2<=addr<=Q-3 else 0
            assert k.vote(outputs)==expected,(y,a,b,outputs,expected);couriers+=1
            dig.update(json.dumps([y,a,b,outputs,expected],separators=(',',':')).encode())
    # Explicit finite propagation of the actual nonzero early Out seeds.
    true_heads=(-2,-1,0,17,18,19);foreign_heads=range(1,18)
    active={g*Q+P+2 for g in true_heads}
    active.update(g*Q-Q//2+P+2 for g in foreign_heads)
    seeds=sorted(active);first_arrival={}
    for tick in range(1,5*Q):
        nxt=set()
        for y in active|{x+1 for x in active}:
            label=value(fixed,y)&1;addr=(y+(Q//2 if label else 0))%Q
            bit=((y in active) or (y-1 in active)) if addr==Q-3 else y-1 in active
            if P+2<=addr<=Q-3 and bit:
                nxt.add(y)
                if addr==Q-3:first_arrival.setdefault(y,tick)
        active=nxt
    actual=sorted(y for y in active if (y+(Q//2 if value(fixed,y)&1 else 0))%Q==Q-3)
    certified=list(map(int,(D/'GAW23_derived_actual_first_F1_sources.txt').read_text().split()))
    assert actual==certified and set(active)==set(actual)
    assert len(actual)==21 and max(first_arrival.values())==Q-3-(P+2)==4339
    return dict(actual_Mail_LOAD_shift_erasure_holder_cofactors=masks,
        guarded_courier_five_holder_centre_operator_cofactors=couriers,
        courier_cofactor_sha256=dig.hexdigest(),actual_75Q_nonzero_right_seed_positions=seeds,
        exact_actual_destination_sources=actual,maximum_first_arrival_after75Q=4339,
        partial_true0_foreign17_lineages_killed_not_replaced=True,
        left_couriers_zero_from_actual_early_Flag2_outputs=True,
        all_destination_five_Info_copies1_at80Q_minus1=True)

def main():
    started=time.monotonic();issue='--issue' in sys.argv
    records=read_events();native_rows=0;lastleft=-1
    for row,seg,src in records:
        if row>4099:break
        runs=[(a,b) for a,b,v in seg if v&1]
        assert runs and runs[-1][1]==17*Q
        assert all(runs[i][1]==runs[i+1][0] for i in range(len(runs)-1))
        left=runs[0][0];assert lastleft<=left<=Q//2;lastleft=left;native_rows+=1
    assert native_rows==4099 and lastleft==Q//2
    scalar=json.loads((D/'GAW23_general_native_audit_issue01.log').read_text())
    assert scalar['passed'] and scalar['independent_word_quorum_event_intervals']==20406053
    assert scalar['source_Info_at_U_not_claimed']
    local=full_local_checks(records);contracts=mail_and_courier_contracts()
    last=records[-1];assert last[1]==[(7*Q,15*Q//2,2),(15*Q//2,39*Q//2,1),(39*Q//2,20*Q,3)]
    r=dict(Q=Q,U=U,error_lambda=24,error_separation=104,
        inherited_actual_bank_receipt_sha256=sha(D/'GAW23_actual_first_native_banks.json'),
        native_event_file_sha256=sha(D/'GAW23_first_pulse_events02.bin'),
        interval_source_sha256=sha(S/'gaw23_interval_native.c'),
        independent_native_audit_source_sha256=sha(S/'gaw23_general_native_audit.c'),
        scalar_word_quorum_audit=scalar,actual_local_R_cofactors=local,
        actual_mail_and_courier_contracts=contracts,
        all_prefix_rows_checked=native_rows,
        prefix_GF_changes_only_on_zero_native_Info_colony0_half_frame=True,
        native_GF_Info_snapshots_and_other_five_native_Info_words_derived_from_intact_H=True,
        actual_native_WF2_Flag2_zero_all_rows1_throughU=True,
        first_native_U_GF_foreign_interval=[15*Q//2,20*Q],
        first_native_U_Flag1_intervals=[[7*Q,15*Q//2],[39*Q//2,20*Q]],
        first_native_U_common_Age=0,first_native_U_WF1_WF2_Flag2_zero=True,
        first_native_U_foreign_width=25*Q//2,
        first_prefix_fixed_row=4099,first_postpulse_native_fixed_by_row=99*Q,
        infinite_line_partition_and_fixed_guard_induction_in_written_proof=True,
        actual_source_Info_claim_only_before_U_commit=True,
        sources_at_U_from_auxiliary_tracker_not_claimed_physical=True,
        no_preloaded_future_commands_heads_tapes_or_new_rule=True,
        full_late_pass_all496word_banks_U_encoding_later_orbit_or_operational_repair_proved=False,
        printed_Gray_Address_Proposition5_failure_claim=False,
        faithful_Gray_Gacs_iid_memory_higher_error_or_shorter_U_claim=False)
    r=json.loads(json.dumps(r));path=D/'GAW23_actual_first_native_pulse_certificate.json'
    if issue:assert not path.exists();path.write_text(json.dumps(r,indent=2)+'\n')
    else:assert r==json.loads(path.read_text())
    print(json.dumps(dict(passed=True,elapsed_seconds=time.monotonic()-started,
        complete_prefix_native_rows=native_rows,full_local_R_checks=local,
        actual_courier_sources=21,receipt_sha256=sha(path))),flush=True);return r

if __name__=='__main__':main()
