"""Actual mixed late-native/SF histories via a derived active factor.

No new CA rule, independent future tape or Workspace. C evaluates the
native equations and five-copy readonly/Program update. Python executes
the actual packet step at every affected holder with its computed GF.
The native function rejects any reset/birth/gather/source/commit clock.
"""
from pathlib import Path
from dataclasses import replace
from functools import lru_cache
import ctypes,hashlib,json,random,sys,time
S=Path(__file__).resolve().parent;sys.path.insert(0,str(S))
import search_gaw14_mixed_active as source
k=source.k;own=source.own;base=source.base;prior=source.prior
ROOT=source.ROOT;D=source.D;FIELDS=source.FIELDS;P=source.P;T=source.T
Site=source.sharedmod.Site

class Result(ctypes.Structure):
    _fields_=[(s,ctypes.c_int) for s in ('status','geometry','flags','wipes','dirty_lo','dirty_hi','geometry_lo','geometry_hi')]+[('row_hash',ctypes.c_uint64)]

def library():
    c=ctypes.CDLL(str(D/'gaw14_active_factor.so'))
    c.gaw14_step.argtypes=[ctypes.POINTER(Site),ctypes.POINTER(Site),ctypes.POINTER(ctypes.c_uint8),
        ctypes.POINTER(ctypes.c_uint8),ctypes.POINTER(ctypes.c_uint8),ctypes.c_int,ctypes.c_int,
        ctypes.c_int,ctypes.POINTER(ctypes.c_int),ctypes.POINTER(Result)]
    c.gaw14_step.restype=ctypes.c_int;return c

def vote(v):return v[0] if v.count(v[0])>=3 else k.vote(v)
def record(c):return [hex(v) for v in k.cell_words(c)]

class Active:
    def __init__(self,recipe):
        self.recipe=recipe;self.shadow=source.Shadow();self.age=T;self.tick=0
        self.offset=-2*k.Q;self.n=6*k.Q+64
        self.a=(Site*self.n)(*[Site((x+self.offset)%k.Q,T,0,0,0,0,31) for x in range(self.n)])
        self.b=(Site*self.n)();self.wipes=(ctypes.c_int*self.n)();self.r=Result();self.c=library()
        self.beta=(ctypes.c_uint8*k.Q)(*[k.beta_bit(own.ROM,x) for x in range(k.Q)])
        self.pb=(ctypes.c_uint8*self.n)(*[sum(self.beta[(x+self.offset+s)%k.Q]<<h for h,s in enumerate(k.SLOTS)) for x in range(self.n)])
        self.nextpb=(ctypes.c_uint8*self.n)()
        self.groups={name:{} for name in ('heads','out','scratch')}
        for name,vals in (('heads',{y:k.pack(p) for y,p in self.shadow.heads.items()}),
                          ('out',self.shadow.out),('scratch',self.shadow.scratch)):
            self.groups[name]={y:(v,)*5 for y,v in vals.items() if v}
        self.payloads=[];support=set();b=recipe['start']
        for x in range(b,b+recipe['width']):
            old=self.raw(x);z=source.replacement(recipe,x,old,0)
            assert z!=old
            self.a[x-self.offset]=Site(z.addr,z.age,z.f1,z.f2,z.wf1,z.wf2,31)
            for name in self.groups:
                for h,s in enumerate(k.SLOTS):
                    y=x+s;values=list(self.groups[name].get(y,(0,)*5));values[h]=getattr(z,name)[h]
                    self.groups[name][y]=tuple(values)
            self.payloads.append(dict(x=x,t=T,old_complete_words=record(old),replacement_complete_words=record(z)))
            support.add((x,T))
        self.classification=base.gray_errors.classify(support,support,Q=k.Q,U=k.U,sep=104,exact_limit=1)
        assert self.classification['level1'] and self.classification['level0']==0 and self.classification['extent']==(16,1)

    @classmethod
    def from_actual_prefix(cls,prefix):
        """Import only the complete already computed local_R prefix state.

        This is checked reconstruction of one chronological state, never
        a preloaded tape. If Mem/Histories no longer share a readonly tag,
        this particular active factor is inapplicable and rejects it.
        """
        self=cls(prefix['recipe']);count=len(prefix['rows'])
        for i in range(count):self.shadow.advance()
        self.age=self.shadow.age;self.tick=count
        self.a=(Site*self.n)(*[Site((x+self.offset)%k.Q,self.age,0,0,0,0,31) for x in range(self.n)])
        self.pb=(ctypes.c_uint8*self.n)(*[sum(self.beta[(x+self.offset+s)%k.Q]<<h for h,s in enumerate(k.SLOTS)) for x in range(self.n)])
        self.groups={name:{} for name in ('heads','out','scratch')}
        for name,vals in (('heads',{y:k.pack(p) for y,p in self.shadow.heads.items()}),
                          ('out',self.shadow.out),('scratch',self.shadow.scratch)):
            self.groups[name]={y:(v,)*5 for y,v in vals.items() if v}
        dirty={x:k.cell_from_words([int(v,16) for v in ws]) for x,ws in prefix['final_complete_dirty_cells']}
        for x,z in dirty.items():
            bits=0
            for h,s in enumerate(k.SLOTS):
                y=x+s;b=prior.B(y);vv=[getattr(z,n)[h] for n in ('mem','history1','history2','history3')]
                assert len(set(vv))==1 and vv[0] in (0,b),(x,h,'unsupported readonly prefix')
                # If B(y)=0, use the actual Info word to retain any tag
                # that matters. Both words zero make either tag equivalent.
                I=base.I(y);assert z.info[h] in (0,I)
                keep=int(vv[0]==b and z.info[h]==I)
                bits|=keep<<h
                assert z.program[h] in (0,1)
            assert not any(z.mail_l+z.mail_r+z.courier_l+z.courier_r)
            self.a[x-self.offset]=Site(z.addr,z.age,z.f1,z.f2,z.wf1,z.wf2,bits)
            self.pb[x-self.offset]=sum(v<<h for h,v in enumerate(z.program))
            for name in self.groups:
                for h,s in enumerate(k.SLOTS):
                    y=x+s;vv=list(self.groups[name].get(y,(0,)*5));vv[h]=getattr(z,name)[h]
                    if any(vv):self.groups[name][y]=tuple(vv)
                    else:self.groups[name].pop(y,None)
        probes=sorted(set(dirty)|{x+d for x in dirty for d in (-4,4)})
        for x in probes:assert self.raw(x)==dirty.get(x,self.shadow.read(x)),(x,'actual prefix reconstruction')
        return self

    def logical(self,name,y):return vote(self.groups[name].get(y,(0,)*5))
    def tag(self,y):return int(sum((self.a[y-s-self.offset].info>>h)&1 for h,s in enumerate(k.SLOTS))>=3)
    def program(self,y):return int(sum((self.pb[y-s-self.offset]>>h)&1 for h,s in enumerate(k.SLOTS))>=3)
    def raw(self,x):
        z=self.a[x-self.offset]
        data=dict(addr=z.gf,age=z.age,f1=z.f1,f2=z.f2,wf1=z.w1,wf2=z.w2,
            info=tuple(base.I(x+s)*((z.info>>h)&1) for h,s in enumerate(k.SLOTS)),
            program=tuple((self.pb[x-self.offset]>>h)&1 for h in range(5)),
            mem=tuple(prior.B(x+s)*((z.info>>h)&1) for h,s in enumerate(k.SLOTS)),
            history1=tuple(prior.B(x+s)*((z.info>>h)&1) for h,s in enumerate(k.SLOTS)),
            history2=tuple(prior.B(x+s)*((z.info>>h)&1) for h,s in enumerate(k.SLOTS)),
            history3=tuple(prior.B(x+s)*((z.info>>h)&1) for h,s in enumerate(k.SLOTS)))
        for name in self.groups:data[name]=tuple(self.groups[name].get(x+s,(0,)*5)[h] for h,s in enumerate(k.SLOTS))
        return k.Cell(**data)

    def step(self,cofactor=False):
        age=self.age+1;r=self.r
        code=self.c.gaw14_step(self.a,self.b,self.pb,self.nextpb,self.beta,self.n,self.offset,age,self.wipes,ctypes.byref(r))
        assert code==0,(self.recipe['tag'],self.tick,r.status,age)
        # Only incoherent holders, current wipes and incoming Heads can
        # change a coherent old Out/Scratch group in this held active stage.
        votedheads={y:k.unpack(vote(v)) for y,v in self.groups['heads'].items() if vote(v)}
        targets={y+d for y in votedheads for d in (-1,0,1)}
        targets.update(y for name in ('out','scratch') for y,v in self.groups[name].items() if len(set(v))!=1)
        targets.update(self.offset+self.wipes[j]+s for j in range(r.wipes) for s in k.SLOTS)
        assert all(self.offset+24<=y<self.offset+self.n-24 for y in targets),('mutable finite boundary',sorted(targets))
        outputs={name:dict(vals) if name!='heads' else {} for name,vals in self.groups.items()}
        writes=[]
        for y in sorted(targets):
            incoming=k.incoming([votedheads.get(y+d,k.ZERO) for d in (-1,0,1)])
            mem=prior.B(y)*self.tag(y);oldout=self.logical('out',y);scratch=self.logical('scratch',y);pb=self.program(y)
            vals={name:[] for name in self.groups}
            for h,s in enumerate(k.SLOTS):
                x=y-s;i=x-self.offset;z=self.b[i];wipe=z.f1 and z.gf!=self.a[i].gf
                if wipe:p=k.ZERO;o=q=0
                else:
                    p,a,b=k.step_packet(incoming,(z.gf+s)%k.Q,mem,oldout,scratch,pb,own.ROM)
                    o=oldout if a is None else a;q=scratch if b is None else b
                    if a is not None:writes.append([x,h,y,'Out',hex(a)])
                    if b is not None:writes.append([x,h,y,'Scratch',hex(b)])
                for name,v in (('heads',k.pack(p)),('out',o),('scratch',q)):vals[name].append(v)
            for name,v in vals.items():
                if any(v):outputs[name][y]=tuple(v)
                else:outputs[name].pop(y,None)
        checks=[]
        if cofactor:
            probes={y-s for y in targets for s in k.SLOTS}
            probes.update(self.offset+self.wipes[j] for j in range(r.wipes))
            probes.update(range(self.recipe['start']-6,self.recipe['start']+22))
            saved=(self.a,self.pb,self.groups)
            for x in sorted(probes):
                cone={d:self.raw(x+d) for d in range(-8,9)};expected=k.local_transition(cone,own.ROM)
                self.a,self.pb,self.groups=self.b,self.nextpb,outputs
                got=self.raw(x);self.a,self.pb,self.groups=saved
                assert got==expected,(self.recipe['tag'],self.tick+1,x,'actual full local_R')
                checks.append([x,source.signature(k.cell_words(got))])
        self.a,self.b=self.b,self.a;self.pb,self.nextpb=self.nextpb,self.pb;self.groups=outputs
        self.age=age;self.tick+=1
        native_quiet=not(r.geometry or r.flags)
        coherent=all(len(set(v))==1 for vals in self.groups.values() for v in vals.values())
        tags_coherent=True
        if native_quiet:
            for y in range(r.dirty_lo+self.offset-4,r.dirty_hi+self.offset+5):
                vv=[(self.a[y-s-self.offset].info>>h)&1 for h,s in enumerate(k.SLOTS)]
                if len(set(vv))!=1:tags_coherent=False;break
        return dict(elapsed=self.tick,geometry=r.geometry,flags=r.flags,wipes=r.wipes,
            native_hull=None if r.dirty_hi<r.dirty_lo else [self.offset+r.dirty_lo,self.offset+r.dirty_hi+1],
            geometry_hull=None if not r.geometry else [self.offset+r.geometry_lo,self.offset+r.geometry_hi+1],
            native_keep_program_row_FNV64=hex(r.row_hash),mutable_groups_sha256=source.signature(self.groups),
            actual_full_local_R_checks=checks,write_events=writes,
            head_logical_group_count=len(outputs['heads']),head_voted_packets=[[y,hex(vote(v))] for y,v in sorted(outputs['heads'].items())],
            native_quiet=native_quiet,SF_coherent=coherent,readonly_tags_coherent=tags_coherent)

    def closure(self):
        keep=[]
        for y in range(self.offset+24,self.offset+self.n-24):
            vv=[(self.a[y-s-self.offset].info>>h)&1 for h,s in enumerate(k.SLOTS)]
            assert len(set(vv))==1,('readonly group',y,vv)
            if not vv[0]:keep.append(y)
        for vals in self.groups.values():assert all(len(set(v))==1 for v in vals.values())
        return dict(age=self.age,readonly_erased_coordinates=keep,
            Head=[[y,hex(v[0])] for y,v in sorted(self.groups['heads'].items())],
            Out=[[y,hex(v[0])] for y,v in sorted(self.groups['out'].items())],
            Scratch=[[y,hex(v[0])] for y,v in sorted(self.groups['scratch'].items())],
            final_native_canonical_common_clock=True,all_SF_holders_coherent=True)

def recipes():
    out=[]
    for b in (P-7,k.Q-8):
        for i,(shift,delta,flags) in enumerate(((1,1,0),(-1,-1,0),(k.Q//2,1,3),(1,0,15))):
            out.append(dict(tag='active_mixed_%d_%d'%(b,i),start=b,width=16,rows=1,
                gf_shift=shift,age=T+delta,flags=flags,packet_kind='cross-store' if b==k.Q-8 else 'stationary-store',
                Out=k.MASK if i<2 else 1,Scratch=k.MASK))
    return out

def run(recipe,limit=5*k.Q,cofactors=True):
    began=time.monotonic();v=Active(recipe);events=[];first_geometry=first_native=None
    for tick in range(limit):
        row=v.step(cofactor=cofactors and tick in (0,1,2,3,4,15,63,255,1023,2047,4095,8191))
        if not row['geometry'] and first_geometry is None:first_geometry=tick+1
        if row['native_quiet'] and first_native is None:first_native=tick+1
        events.append(row)
        if row['native_quiet'] and row['SF_coherent'] and row['readonly_tags_coherent']:break
    else:raise AssertionError(('no complete active closure',recipe['tag'],events[-1]))
    result=dict(recipe=recipe,actual_fault_clock=T,Q=k.Q,U=k.U,error_lambda=24,error_separation=104,
        whole_cell_payloads=v.payloads,original_c104_classification=v.classification,
        actual_chronological_prefix_snapshots=[z[0] for g,z in sorted(v.shadow.snaps.items())],
        events=events,first_geometry_quiet=first_geometry,first_native_quiet=first_native,
        closure=v.closure(),future_tape_Workspace_or_Head_chosen=False,new_rule=False,
        whole_period_or_operational_or_Gray_iid_failure=False,elapsed_seconds=time.monotonic()-began)
    return result,v

def run_seeded(prefix,limit=5*k.Q,cofactors=True):
    began=time.monotonic();v=Active.from_actual_prefix(prefix);events=[];first_geometry=first_native=None
    for tick in range(limit):
        row=v.step(cofactor=cofactors and (tick in (0,1,2,31,255,1023,2047,4095) or v.tick+1 in (1451,5546)))
        if not row['geometry'] and first_geometry is None:first_geometry=v.tick
        if row['native_quiet'] and first_native is None:first_native=v.tick
        events.append(row)
        if row['native_quiet'] and row['SF_coherent'] and row['readonly_tags_coherent']:break
    else:raise AssertionError(('no complete seeded closure',prefix['recipe']['tag'],events[-1]))
    result=dict(recipe=prefix['recipe'],actual_fault_clock=T,Q=k.Q,U=k.U,error_lambda=24,error_separation=104,
        whole_cell_payloads=prefix['whole_cell_payloads'],original_c104_classification=prefix['actual_original_c104_classification'],
        actual_chronological_prefix_snapshots=prefix['chronological_shadow_snapshots'],
        actual_full_local_R_initial_prefix=source.signature(source.stable(prefix)),actual_full_local_R_prefix_rows=len(prefix['rows']),
        events=events,first_geometry_quiet=first_geometry,first_native_quiet=first_native,
        closure=v.closure(),future_tape_Workspace_or_Head_chosen=False,new_rule=False,
        whole_period_or_operational_or_Gray_iid_failure=False,elapsed_seconds=time.monotonic()-began)
    return result,v

def main():
    D.mkdir(parents=True,exist_ok=True);result=[]
    for recipe in recipes():
        rec,_=run(recipe);result.append(rec)
        (D/(recipe['tag']+'_active_receipt.json')).write_text(json.dumps(rec,indent=2)+'\n')
        print(json.dumps(dict(tag=recipe['tag'],closure_tick=len(rec['events']),geometry_quiet=rec['first_geometry_quiet'],
            native_quiet=rec['first_native_quiet'],erased=len(rec['closure']['readonly_erased_coordinates']),
            final_heads=[v[0] for v in rec['closure']['Head']],seconds=rec['elapsed_seconds'])),flush=True)
    return result

if __name__=='__main__':main()
