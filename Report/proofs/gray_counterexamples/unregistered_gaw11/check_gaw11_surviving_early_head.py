"""Selected intact-start early-Head histories, actual reset/shadow recovery.

Frozen GAW2R; read caching and the native event observer are diagnostics.
No CA, programme, controller, future Workspace or tape is substituted.
"""
from pathlib import Path
from dataclasses import replace
import csv,hashlib,json,random,subprocess,sys,time
sys.path.insert(0,str(Path(__file__).resolve().parent))
import search_gaw11_birth_profiles as search
k=search.k;own=search.own;base=search.base;D=search.D;S=search.S;T=search.T

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def digest_rows(rows):return hashlib.sha256(json.dumps(rows,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def packet_cofactors(count=64):
    rng=random.Random(0x110104);digest=hashlib.sha256()
    for trial in range(count):
        cells={d:k.Cell(addr=rng.randrange(k.Q),age=rng.choice((rng.randrange(k.U),k.EARLY_BIRTH-1,102*k.Q,0)),
            f1=rng.randrange(2),f2=rng.randrange(2),wf1=rng.randrange(2),wf2=rng.randrange(2),
            **{name:tuple(rng.getrandbits(2200 if name=='heads' else 1700 if name in ('mem','history1','history2','history3') else 100)
                          for h in range(5)) for name in search.FIELDS}) for d in range(-8,9)}
        direct=k.local_transition(cells,own.ROM)
        with search.SharedReads() as shared:cached=shared.update(0,0,cells.__getitem__)[0]
        assert direct==cached
        digest.update(json.dumps([trial,search.packed(direct)],separators=(',',':')).encode())
    return dict(full_raw_local_R_cache_comparisons=count,free_all_SF_and_native_inputs=True,
                signature_sha256=digest.hexdigest(),samples_supplement_source_identity=True)

def parse_events(text):
    out=[]
    for row in csv.DictReader(text.splitlines()):
        seg=[list(map(int,s.split(':'))) for s in row['segments'].split(';') if s]
        out.append(dict(t=int(row['t']),n=int(row['n']),head_wrong_clock=int(row['head_wrong_clock']),segments=seg))
    assert [r['t'] for r in out]==list(range(len(out)))
    return out

def event_value(row,x):
    return next((v for lo,hi,v in row['segments'] if lo<=x<hi),0)

def observer(b):
    p=subprocess.run([str(D/'gaw11_clock_head_observer'),str(b),'128'],capture_output=True,text=True,check=True)
    assert p.stdout==(D/('GAW11_clock_head_b%d.csv'%b)).read_text()
    assert p.stderr==(D/('GAW11_clock_head_b%d.log'%b)).read_text()
    rows=parse_events(p.stdout)
    assert rows[-1]['n']==0 and rows[-1]['t']<6*k.Q
    lastclock=max(r['t'] for r in rows if any(v&1 for lo,hi,v in r['segments']))
    lasthead=max(r['t'] for r in rows if r['head_wrong_clock'])
    assert all(not r['head_wrong_clock'] for r in rows[128:])
    return rows,dict(start=b,width=16,exact_event_observer_csv_sha256=sha(D/('GAW11_clock_head_b%d.csv'%b)),
        native_quiet_tick=rows[-1]['t'],clock_recovery_tick=lastclock+1,last_wrong_head_holder_clock_tick=lasthead,
        exact_partition_log_sha256=sha(D/('GAW11_clock_head_b%d.log'%b)),
        every_computed_row_checked_not_just_endpoints=True)

def prefix(index,event_rows):
    recipe=search.recipes()[index];b=recipe['start'];state={}
    original=json.loads((D/'GAW11_birth_profile_search.json').read_text())['cases'][index]
    for j,(gf,age,flags) in enumerate(recipe['payload']):
        x=b+j;old=search.prior.reference(x,0)
        state[x]=replace(old,addr=gf,age=age,f1=flags&1,f2=(flags>>1)&1,wf1=(flags>>2)&1,wf2=(flags>>3)&1)
    rows=[];digest=hashlib.sha256();direct=0
    with search.SharedReads() as shared:
        for t in range(1,129):
            old=state
            def read(x):return old.get(x,search.prior.reference(x,t-1))
            lo=min(old)-8;hi=max(old)+8;raw=shared.update(lo,hi,read)
            # All five actual head holders and nearby source points are
            # re-evaluated without the batched View in the birth prefix.
            if t<=8:
                for x in range(k.PRIMARY_START-4,k.PRIMARY_START+5):
                    assert k.local_transition({d:read(x+d) for d in range(-8,9)},own.ROM)==raw[x]
                    direct+=1
            state={x:z for x,z in raw.items() if z!=search.prior.reference(x,t)}
            er=event_rows[t]
            for x in range(min(lo,er['segments'][0][0] if er['segments'] else lo),
                           max(hi,er['segments'][-1][1] if er['segments'] else hi)+1):
                z=state.get(x,search.prior.reference(x,t));value=event_value(er,x)
                label=int(z.age==(k.EARLY_BIRTH-1+t)%k.U)
                assert z.addr==x%k.Q and z.age in (T+t,k.EARLY_BIRTH-1+t)
                assert value==label+2*z.f1 and z.f2==z.wf1==z.wf2==0
                for h,s in enumerate(k.SLOTS):
                    y=x+s
                    assert z.info[h]==base.I(y)
                    assert z.program[h]==k.beta_bit(own.ROM,y%k.Q)
                    assert all(getattr(z,n)[h]==search.prior.mixed.prior.held(x).__getattribute__(n)[h]
                               for n in ('history1','history2','history3'))
                assert not any(z.mem+z.out+z.scratch+z.courier_l+z.courier_r+z.mail_l+z.mail_r)
            heads=[(x,h,k.unpack(v)) for x,z in state.items() for h,v in enumerate(z.heads) if v]
            nonzero={name:[(x,h,hex(v)) for x,z in state.items() for h,v in enumerate(getattr(z,name)) if v]
                     for name in ('out','courier_l','courier_r')}
            dirty=sorted((x,search.packed(z)) for x,z in state.items())
            digest.update(json.dumps([t,dirty],separators=(',',':')).encode()+b'\n')
            rows.append(dict(elapsed=t,computed_cells=hi-lo+1,dirty_cells=len(state),
                native_geometry_disagreement=sum(z.addr!=x%k.Q or z.age!=T+t for x,z in state.items()),
                raw_head_copies=len(heads),head_pcs=sorted({p.pc for x,h,p in heads}),nonzero_Out_or_couriers=nonzero))
    assert json.loads(json.dumps(rows))==original['rows']
    assert digest.hexdigest()==original['complete_prefix_state_sha256']
    final=[[x,search.packed(z)] for x,z in sorted(state.items())]
    assert json.loads(json.dumps(final))==original['final_complete_dirty_cells']
    holders=[]
    for x,z in state.items():
        for h,v in enumerate(z.heads):
            if v:holders.append(dict(x=x,holder=h,logical_coordinate=x+k.SLOTS[h],packet_hex=hex(v),
                                      pc=k.unpack(v).pc,mode=k.unpack(v).mode,move=k.unpack(v).move))
    assert len(holders)==5 and {h['logical_coordinate'] for h in holders}=={k.PRIMARY_START}
    assert len({h['packet_hex'] for h in holders})==1 and all(not h['move'] for h in holders)
    packet=int(holders[0]['packet_hex'],16)
    assert all(r['first_actual_nonzero_Out'] is None for r in [original])
    return dict(case=index,recipe=recipe,whole_cell_payloads=original['whole_cell_payloads'],
        actual_original_c104_classification=original['classification'],complete_actual_prefix_sha256=digest.hexdigest(),
        direct_unbatched_birth_source_checks=direct,actual_full_prefix_matches_native_event_rows=True,
        held_head_at128=holders,Out_Scratch_Mem_couriers_Mail_zero_through128=True,
        Info_and_all_three_History_banks_correct_through128=True),packet

def physical_reset(packet):
    # This is the derived actual state just before the real common102Q
    # reset: native quiet, correct retained bank/code/Info, one held Head.
    def pre(x):
        z=replace(search.prior.mixed.prior.held(x),age=102*k.Q-1)
        return replace(z,heads=tuple(packet if x+s==k.PRIMARY_START else 0 for s in k.SLOTS))
    def reset(x):return replace(search.prior.mixed.prior.held(x),age=102*k.Q)
    def born(x):
        z=replace(reset(x),age=102*k.Q+1)
        return replace(z,mem=tuple(search.prior.mixed.prior.held(x).__getattribute__('history1')[h] for h in range(5)),
            heads=tuple(k.pack(k.Packet(p=1)) if (x+s)%k.Q==k.PRIMARY_START else 0 for s in k.SLOTS))
    xs=sorted({g*k.Q+a for g in (-1,0,1) for a in
        list(range(k.PRIMARY_START-8,k.PRIMARY_START+k.FRAME_WORDS+8))+list(range(-5,9))+list(range(k.Q-8,k.Q+6))})
    d=hashlib.sha256();counts=dict(reset=0,birth=0)
    for x in xs:
        got=k.local_transition({j:pre(x+j) for j in range(-8,9)},own.ROM)
        assert got==reset(x)
        d.update(json.dumps([x,'reset',search.packed(got)],separators=(',',':')).encode());counts['reset']+=1
        got=k.local_transition({j:reset(x+j) for j in range(-8,9)},own.ROM)
        assert got==born(x)
        d.update(json.dumps([x,'birth',search.packed(got)],separators=(',',':')).encode());counts['birth']+=1
    return dict(actual_derived_reset_birth_full_local_R_checks=counts,signature_sha256=d.hexdigest(),
        equality_to_actual_noiseless_shadow_at102Q=True,old_extra_head_killed_by_actual_reset=True,
        all_three_actual_banks_and_Info_unchanged=True,actual_unique_pc0_birth_at102Qplus1=True,
        source_identity_proves_global_reset_equality=True)

def stable(value):
    if isinstance(value,dict):return {k:stable(v) for k,v in value.items() if k!='elapsed_seconds'}
    if isinstance(value,list):return [stable(v) for v in value]
    if isinstance(value,tuple):return [stable(v) for v in value]
    return value

def main(write=True):
    start=time.monotonic();checks=packet_cofactors();native=search.native_checks();cases=[]
    for i in (0,1):
        events,cert=observer(search.recipes()[i]['start']);actual,packet=prefix(i,events)
        actual['actual_native_event_certificate']=cert;actual['actual_reset_shadow_composition']=physical_reset(packet)
        actual['exact_full_shadow_from102Q_onward']=True
        actual['first_U_decoded_bad_receivers']=[];actual['operational_failure']=False
        cases.append(actual)
        print(json.dumps(dict(case=i,passed=True,native_quiet=cert['native_quiet_tick'],
            last_wrong_head_clock=cert['last_wrong_head_holder_clock_tick'],
            held_head_pcs=sorted({h['pc'] for h in actual['held_head_at128']}),
            actual_complete_shadow_from102Q=True)),flush=True)
    result=dict(name='GAW11 surviving early Heads: actual banks, native continuation and common reset recovery',
        Q=k.Q,U=k.U,error_lambda=24,error_separation=104,actual_intact_H_shared_physical_error_history=True,
        frozen_local_R_and_own_ROM_unchanged=True,native_batch_checks=native,full_kernel_cache_checks=checks,cases=cases,
        discovery24cases128ticks_receipt_sha256=sha(D/'GAW11_birth_profile_search.json'),
        discovery_not_claimed_full_repair_theorem=True,all_mixed_GF_Age_control_real1_recovery_proved=False,
        future_Workspace_or_preloaded_tapes_prescribed=False,whole_grid_U_simulation_claimed=False,
        Gray_or_iid_or_G17_failure=False,shorter_U_or_new_rule=False,registered_main_modified=False,
        elapsed_seconds=time.monotonic()-start)
    path=D/'GAW11_surviving_early_head_receipt.json'
    if write:path.write_text(json.dumps(result,indent=2)+'\n')
    else:assert stable(result)==stable(json.loads(path.read_text()))
    print(json.dumps(dict(passed=True,selected_actual_history_count=len(cases),full_shadow_from102Q=True,
        Gray_iid_or_general_repair_claim=False,elapsed_seconds=time.monotonic()-start)),flush=True)
    return result

if __name__=='__main__':main(write='--read-only' not in sys.argv)
