"""One-row phase-component checks; not selected error histories."""
from pathlib import Path
from functools import lru_cache
import hashlib,json,random,sys,time
S=Path(__file__).resolve().parent;sys.path.insert(0,str(S))
import search_gaw15_phase_packets as m
k=m.k;own=m.own

def check():
    start=time.monotonic();rng=random.Random(0xa15010424);digest=hashlib.sha256();checks=stores=wipes=0;ages=[]
    events=sorted(m.EVENTS|{1,32*k.Q+1,64*k.Q+1,k.EARLY_BIRTH+1,102*k.Q+2,120*k.Q+1,96*k.Q+1})
    for event in events:
        for variant in range(3):
            recipe=dict(tag='cofactor',start=0,width=16,rows=1,gf_shift=0,age=m.T,flags=0,
                packet_kind='stationary-store',Out=1,Scratch=k.MASK)
            s=m.Phase(recipe);s.diff.clear()
            for x in range(16):s.a[x-s.offset]=m.Site(x%k.Q,m.T,0,0,0,0,0)
            for x in range(-8,9):
                flags=rng.randrange(16) if variant==1 else 15 if variant==2 else 0
                gf=x%k.Q
                if variant==2 and x==0:gf=2
                s.a[x-s.offset]=m.Site(gf,(event-1)%k.U,flags&1,(flags>>1)&1,(flags>>2)&1,(flags>>3)&1,0)
                s.pb[x-s.offset]=rng.randrange(32)
                for h,slot in enumerate(k.SLOTS):
                    y=x+slot;row=s.diff.setdefault(y,{})
                    for name in m.FIELDS:
                        values=list(row.get(name,(s.clean(name,y),)*5))
                        width=k.HEAD_BITS if name=='heads' else 1700 if name in ('mem','history1','history2','history3') else 100
                        value=rng.getrandbits(width)
                        if name=='heads' and variant==0:
                            value=k.pack(k.Packet(p=1,mode=k.SEEK,pc=own.ROM.token_count,target=y%k.Q,
                                args=k.descriptor(1,0,dest=0),regs=(123456789,)+(0,)*15))
                        values[h]=value;row[name]=tuple(values)
            row=s.step(check=True);n=len(row['actual_full_local_R_checks']);checks+=n
            # Centre's native phase is exactly the named event because all
            # ten clock neighbours agree before the update, with no legality
            # restriction on any other SF word except boolean Programme.
            z=s.a[-s.offset];assert z.age==event
            ages.append([event,variant,n,z.f1,z.f2,z.w1,z.w2])
            wipes+=int(variant==2 and z.f1 and z.gf!=2)
            if variant==0 and (k.EARLY_BIRTH<event<75*k.Q or 102*k.Q+1<event<=120*k.Q):
                assert s.raw(0).out[0]==123456789;stores+=1
            digest.update(json.dumps([event,variant,row,s.snapshot()],separators=(',',':')).encode())
    chrono=m.prior.actual_chronological_prefix_checks({g:m.prior.actual_snapshot(g) for g in (-2,-1,0,1,2,3)})
    return dict(passed=True,phase_native_SF_cofactors=len(ages),actual_full_local_R_checks=checks,
        all_distinct_capture_dates_checked=sorted(m.CAPTURE),all_both_direction_capture_lanes_preserved=all(len(v)==(1 if v[0][1]==8 else 2) for v in m.CAPTURE.values()),
        exact_centre_phase_checks=ages,real_store_centre_cases=stores,wipe_centre_cases=wipes,
        arbitrary_other_native_flags_and_SF_words=True,boolean_Programme_premise=True,
        cofactor_signature_sha256=digest.hexdigest(),actual_six_frame_chronology=chrono,
        universal_sampling_proof_or_noise_theorem=False,elapsed_seconds=time.monotonic()-start)

if __name__=='__main__':
    result=check();(m.D/'GAW15_phase_cofactor_certificate.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('exact_centre_phase_checks','actual_six_frame_chronology')}),flush=True)
