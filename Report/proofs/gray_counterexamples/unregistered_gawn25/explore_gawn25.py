"""UNFROZEN many-offset projection exploration. No universal recovery claim."""
from pathlib import Path
import ctypes, hashlib, json, random, subprocess, sys, tempfile, time
import numpy as np

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[3]
sys.path.insert(0,str(ROOT))
sys.path.insert(0,str(HERE.parent/'unregistered_gawn10'))
import check_gawn10_two_offset_projection as c
k=c.k; own=c.own
Q=k.Q; U=k.U; T0=100*Q+2
class Site(ctypes.Structure):
    _fields_=[('offset',ctypes.c_uint16)]+[(n,ctypes.c_uint8) for n in ('f1','f2','wf1','wf2')]
class Event(ctypes.Structure):
    _fields_=[(n,ctypes.c_int32) for n in ('step','gf','f1','f2','wf1','wf2','gf_lo','gf_hi','active_lo','active_hi','no_quorum_inputs','source3_updates')]
DT=np.dtype([('offset','<u2'),('f1','u1'),('f2','u1'),('wf1','u1'),('wf2','u1')])

def library(tmp):
    so=Path(tmp)/'gawn25.so'
    subprocess.run(['gcc','-std=c11','-O3','-fPIC','-shared','-Wall','-Wextra',str(HERE/'gawn25_many_offset_native.c'),'-o',str(so)],check=True)
    lib=ctypes.CDLL(str(so))
    assert lib.gawn25_site_size()==ctypes.sizeof(Site)==DT.itemsize==6
    assert lib.gawn25_event_size()==ctypes.sizeof(Event)==48
    lib.gawn25_local.argtypes=[ctypes.POINTER(Site),ctypes.c_int,ctypes.c_int,ctypes.POINTER(Site)]
    lib.gawn25_local.restype=ctypes.c_int
    lib.gawn25_run.argtypes=[ctypes.POINTER(Site)]+[ctypes.c_int]*5+[ctypes.POINTER(Event),ctypes.POINTER(Site),ctypes.POINTER(ctypes.c_int)]
    lib.gawn25_run.restype=ctypes.c_int
    return lib

def actual_check(lib,rows,x,oldage,rng,dig):
    assert len(rows)==17
    cells={}
    for j,v in zip(range(-8,9),rows):
        vals=list(map(int,v))
        cells[j]=k.Cell(addr=(x+j+vals[0])%Q,age=oldage,
            **dict(zip(('f1','f2','wf1','wf2'),vals[1:])),
            **{name:tuple(rng.getrandbits(c.WIDTHS.get(name,k.WORD)) for _ in k.SLOTS) for name in c.SF})
    raw=(Site*11)(*(Site(*map(int,v)) for v in rows[3:14]))
    result=Site()
    assert lib.gawn25_local(raw,x,(oldage+1)%U,ctypes.byref(result))==0
    actual=k.local_transition(cells,own.ROM)
    got=[getattr(actual,n) for n in k.NATIVE_NAMES]
    expect=[(x+result.offset)%Q,(oldage+1)%U,result.f1,result.f2,0,0]
    assert got==expect,(x,oldage,got,expect,rows)
    dig.update((json.dumps([x,oldage,rows,got],separators=(',',':'))+'\n').encode())

def cofactors(lib,count=512):
    rng=random.Random(0x4741574e323501);dig=hashlib.sha256()
    phases=(-Q-3,-8,-3,-1,0,1,2,3,4,5,Q-6,Q-3,Q-1,Q,Q+3)
    # Include true no-majority and a mix of single/2/3/many offset voters.
    for i in range(count):
        x=phases[i%len(phases)]
        palette=[0]+[rng.randrange(1,Q) for _ in range((i%5)+1)]
        rows=[[rng.choice(palette),*(rng.randrange(2) for _ in range(4))] for _ in range(17)]
        oldage=(T0-1,T0+13,U-1,0,96*Q-2,98*Q-1)[i%6]
        actual_check(lib,rows,x,oldage,rng,dig)
    return {'selected_kernel_checks':count,'digest':dig.hexdigest()}

def run(lib,forcing,b,maxstep):
    duration,width=forcing.shape
    events=(Event*(maxstep+1))()
    final=(Site*(10*maxstep+width+33))()
    summary=(ctypes.c_int*9)()
    start=time.perf_counter()
    status=lib.gawn25_run(forcing.ctypes.data_as(ctypes.POINTER(Site)),width,duration,b,T0,maxstep,
        events,final,summary)
    assert status>=0,(status,list(summary))
    assert summary[7]==summary[8]==1,list(summary)
    trace=np.frombuffer(events,dtype=np.int32).reshape(maxstep+1,12)[:summary[1]+1].copy()
    native=np.frombuffer(final,dtype=DT).copy()
    return {'status':status,'steps':summary[1],'base':summary[2],'n':summary[3],
        'maxgf':summary[4],'maxGFspan':summary[5],'maxactive':summary[6],
        'offsetdomain':summary[7],'causal_bounds':summary[8],'elapsed':time.perf_counter()-start},trace,native

def profiles(b,width=104):
    i=np.arange(width,dtype=np.int64)
    palette=np.asarray([(-b-p)%Q for p in (0,16,32,48,64,96)],dtype=np.uint16)
    profiles={
        'endpoints_run4':palette[(i//4)%6],
        'endpoints_run16':palette[(i//16)%6],
        'endpoints_run34':palette[np.minimum(i//34,2)],
        'endpoints_cycle':palette[i%6],
        'endpoints_3plus':palette[np.minimum(i//3,5)],
        'three_quorum':np.asarray([0,(-b)%Q,(-b-48)%Q],dtype=np.uint16)[(i//3)%3],
        'no_quorum':((171*i+19)%Q).astype(np.uint16),
        'random_words':np.asarray([random.Random(0x250000+b+int(j)).randrange(Q) for j in i],dtype=np.uint16),
    }
    return profiles

def main():
    out=ROOT/'figs/gray_counterexamples/unregistered_gawn25'
    out.mkdir(parents=True,exist_ok=True)
    records=[]
    with tempfile.TemporaryDirectory(prefix='gawn25_explore_') as tmp:
        lib=library(tmp);print(json.dumps(cofactors(lib)),flush=True)
        for b in (0,Q-52):
            for label,offsets in profiles(b).items():
                for duration in (1,104):
                    forcing=np.zeros((duration,104),dtype=DT)
                    forcing['offset']=offsets
                    forcing['f1']=forcing['f2']=1
                    forcing['wf1']=forcing['wf2']=1
                    rec,trace,native=run(lib,forcing,b,4*Q)
                    rec.update(b=b,profile=label,duration=duration)
                    records.append(rec)
                    np.savez_compressed(out/f'explore_b{b}_{label}_d{duration:03d}.npz',forcing=forcing,events=trace,final=native)
                    print(json.dumps(rec),flush=True)
        (out/'exploration_records.json').write_text(json.dumps(records,indent=2)+'\n')
if __name__=='__main__':main()
