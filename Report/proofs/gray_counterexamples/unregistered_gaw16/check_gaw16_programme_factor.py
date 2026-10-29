"""Full-word Programme factor cofactors and actual delayed-output witness."""
from pathlib import Path
import hashlib,json,random,sys,time
S=Path(__file__).resolve().parent;sys.path.insert(0,str(S))
import search_gaw16_word_bursts as m
k=m.k

def check():
    started=time.monotonic();rng=random.Random(0xa16010424);signature=hashlib.sha256();checks=reads=0;cases=[]
    events=(0,1,32*k.Q,64*k.Q,72*k.Q+2,k.EARLY_RESET,k.EARLY_BIRTH,k.EARLY_BIRTH+1,
        75*k.Q,80*k.Q-1,96*k.Q,96*k.Q+1,98*k.Q,102*k.Q,102*k.Q+1,102*k.Q+2,120*k.Q,120*k.Q+1)
    for event in events:
        for variant in range(3):
            state=m.Phase(m.recipes()[0]);state.diff.clear();state.words.clear()
            for x in range(-8,9):
                flags=rng.randrange(16) if variant==1 else 15 if variant==2 else 0
                gf=x%k.Q
                if variant==2 and x==0:gf=1
                state.a[x-state.offset]=m.previous.Site(gf,(event-1)%k.U,flags&1,(flags>>1)&1,(flags>>2)&1,(flags>>3)&1,0)
                state.words[x]=tuple(rng.getrandbits(100) for _ in range(5))
                for h,slot in enumerate(k.SLOTS):
                    y=x+slot;row=state.diff.setdefault(y,{})
                    for name in m.previous.FIELDS:
                        values=list(row.get(name,(state.clean(name,y),)*5))
                        width=k.HEAD_BITS if name=='heads' else 1700 if name in ('mem','history1','history2','history3') else 100
                        value=rng.getrandbits(width)
                        if name=='heads' and variant==0:
                            value=k.pack(k.Packet(p=1,mode=k.SEEK,pc=m.STORE_PC,target=y%k.Q,args=k.descriptor(0,dst=0,source=3)))
                        values[h]=value;row[name]=tuple(values)
            old_programmes=[state.logical('program',y) for y in k.SLOTS]
            row=state.step(check=True);checks+=len(row['actual_full_local_R_checks'])
            z=state.raw(0)
            assert z.age==event and all(v in (0,1) for v in z.program)
            active=k.EARLY_BIRTH<event<75*k.Q or 102*k.Q+1<event<=120*k.Q
            if variant==0 and active:
                assert [k.unpack(v).regs[0] for v in z.heads]==old_programmes
                assert any(v>1 for v in old_programmes);reads+=5
            cases.append([event,variant,len(row['actual_full_local_R_checks']),z.age,z.f1,z.f2,z.wf1,z.wf2])
            signature.update(json.dumps([event,variant,row,state.snapshot()],separators=(',',':')).encode())
    recipe=m.recipes()[0];state=m.Phase(recipe)
    for tick in range(16):
        if tick:state.fault(tick)
        state.step(check=True)
    y=recipe['start'];before=state.copies('heads',y)
    assert all(k.unpack(v).regs[0]==k.MASK and k.unpack(v).pc==m.STORE_PC for v in before)
    assert not state.words and all(v in (0,1) for x in range(y-4,y+5) for v in state.raw(x).program)
    row17=state.step(check=True);prepared=state.copies('heads',y)
    assert all(k.unpack(v).mode==k.SEEK and k.unpack(v).target==y%k.Q and k.unpack(v).regs[0]==k.MASK for v in prepared)
    row18=state.step(check=True);written=state.copies('out',y);assert written==(k.MASK,)*5
    witness=dict(recipe=recipe,logical_y=y,actual_H_T_start=True,physical_fault_rows=16,
        last_fault_time=m.T+15,actual_first_fresh_Programme_time=m.T+16,
        actual_computed_Head_after_last_fault=[hex(v) for v in before],
        actual_Head_after_next_STX=[hex(v) for v in prepared],
        actual_Out_two_updates_after_last_computed_fault_row=[hex(v) for v in written],
        actual_full_local_R_checks=row17['actual_full_local_R_checks']+row18['actual_full_local_R_checks'],
        Word100_Programme_consumed_without_host_immutable_ROM_change=True,
        raw_Programme_boolean_refresh_does_not_truncate_derived_registers=True,
        previous_boolean_byte_factor_inapplicable_to_this_payload=True,
        operational_or_Gray_or_iid_counterexample=False)
    return dict(passed=True,phase_full_Programme_cofactors=len(cases),phase_full_local_R_checks=checks,
        actual_nonboolean_Programme_read_holder_checks=reads,phase_cases=cases,
        cofactor_signature_sha256=signature.hexdigest(),actual_delayed_Programme_to_Out=witness,
        all_raw_Programme_refresh_boolean_by_equation=True,arbitrary_Programme_tracks_are_diagnostic_not_new_CA=True,
        universal_sampling_or_mixed_repair_or_Gray_iid_proof=False,elapsed_seconds=time.monotonic()-started)

if __name__=='__main__':
    r=check();(m.D/'GAW16_programme_factor_certificate.json').write_text(json.dumps(r,indent=2)+'\n')
    print(json.dumps({key:r[key] for key in ('passed','phase_full_Programme_cofactors','phase_full_local_R_checks',
        'actual_nonboolean_Programme_read_holder_checks','cofactor_signature_sha256','elapsed_seconds')}),flush=True)
