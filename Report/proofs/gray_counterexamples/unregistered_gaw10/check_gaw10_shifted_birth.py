"""Actual shifted late birth, derived keeper/bank and physical U/2U map."""
from pathlib import Path
from dataclasses import replace
import ctypes,hashlib,json,random,sys,time
sys.path.insert(0,str(Path(__file__).resolve().parent))
import trace_gaw10_birth as trace
k=trace.k;own=trace.own;base=trace.base;S=trace.S;D=trace.D;ROOT=trace.ROOT
sys.path.insert(0,str(S.parent/'unregistered_gaw5'))
import check_gaw5_history_burst as execution
T=trace.T;OFFSET=3;LIMIT=k.Q

class Site(ctypes.Structure):
    _fields_=[('gf',ctypes.c_uint16),('age',ctypes.c_uint32)]+[(n,ctypes.c_uint8) for n in ('f1','f2','w1','w2','info','hist')]
class Result(ctypes.Structure):
    _fields_=trace.mixed.Result._fields_

def library():
    c=ctypes.CDLL(str(D/'gaw10_postbirth_factor.so'))
    c.gaw10_cofactor.argtypes=[ctypes.POINTER(Site),ctypes.POINTER(Site)];c.gaw10_cofactor.restype=ctypes.c_int
    c.gaw10_campaign.argtypes=[ctypes.POINTER(Site),ctypes.POINTER(Site),ctypes.POINTER(ctypes.c_uint8),
        ctypes.c_int,ctypes.c_int,ctypes.c_int,ctypes.POINTER(Result),ctypes.POINTER(ctypes.c_int),ctypes.c_int,ctypes.POINTER(Site)]
    c.gaw10_campaign.restype=ctypes.c_int
    return c

def bank(y):return execution.bank(y)
def item(z,hist):
    return Site(z.addr,z.age,z.f1,z.f2,z.wf1,z.wf2,sum((v&1)<<h for h,v in enumerate(z.info)),hist)

def keeper_prefix(receipt):
    tags={};old={}
    for j,(gf,age,flags) in enumerate(trace.recipe()['payload']):
        x=trace.recipe()['start']+j;old[x]=replace(trace.reference(x,0),addr=gf,age=age)
    for row in receipt['rows'][:OFFSET]:
        t=row['elapsed'];state={x:k.cell_from_words([int(v,16) for v in ws]) for x,ws in row['complete_dirty_words']}
        lo=min(min(old),min(tags,default=min(old)))-8;hi=max(max(old),max(tags,default=max(old)))+8
        newtags={}
        for x in range(lo,hi+1):
            z=state.get(x,trace.reference(x,t));prev=old.get(x,trace.reference(x,t-1))
            wipe=z.f1 and z.addr!=prev.addr
            bits=0
            for h,s in enumerate(k.SLOTS):
                y=x+s;majority=sum((tags.get(y-u,31)>>q)&1 for q,u in enumerate(k.SLOTS))>=3
                bits|=int(majority and not wipe)<<h
                expected=bank(y)*int(majority and not wipe)
                assert all(getattr(z,name)[h]==expected for name in ('history1','history2','history3'))
                assert z.info[h]==base.I(y)*int(majority and not wipe)
            if bits!=31:newtags[x]=bits
        tags=newtags;old=state
    for z in old.values():assert not any(z.heads+z.out+z.courier_l+z.courier_r)
    return old,tags

def cofactor_checks(c,count=1024):
    rng=random.Random(0xa102104);digest=hashlib.sha256()
    for trial in range(count):
        words={y:rng.getrandbits(1700) for y in range(-10,11)};cells={};tags={}
        for d in range(-8,9):
            bits=rng.randrange(32);tags[d]=bits
            history=tuple(words[d+s]*((bits>>h)&1) for h,s in enumerate(k.SLOTS))
            cells[d]=k.Cell(addr=rng.randrange(k.Q),age=rng.choice((T+OFFSET,102*k.Q+OFFSET)),
                f1=rng.randrange(2),f2=rng.randrange(2),wf1=rng.randrange(2),wf2=rng.randrange(2),
                info=tuple(rng.getrandbits(100) for _ in range(5)),
                program=tuple(rng.getrandbits(100) for _ in range(5)),
                mem=tuple(rng.getrandbits(1700) for _ in range(5)),
                scratch=tuple(rng.getrandbits(100) for _ in range(5)),
                mail_l=tuple(rng.getrandbits(100) for _ in range(5)),mail_r=tuple(rng.getrandbits(100) for _ in range(5)),
                history1=history,history2=history,history3=history)
        got=k.local_transition(cells,own.ROM);out=Site()
        assert c.gaw10_cofactor((Site*17)(*[item(cells[d],tags[d]) for d in range(-8,9)]),ctypes.byref(out))==0
        expected=item(got,out.hist)
        assert bytes(out)==bytes(expected)
        assert not any(got.heads+got.out+got.courier_l+got.courier_r)
        for h,s in enumerate(k.SLOTS):
            assert all(getattr(got,name)[h]==words[s]*((out.hist>>h)&1) for name in ('history1','history2','history3'))
        digest.update(bytes(out));digest.update(b''.join(bytes(item(cells[d],tags[d])) for d in range(-8,9)))
    return dict(actual_full_local_R_cofactors=count,free_mem_scratch_mail_programme_inputs=True,
        actual_native_Info_Workspace_and_History_tags_compared=True,signature_sha256=digest.hexdigest())

def continuation(c,state,tags):
    offset=-4*k.Q;n=8*k.Q+32
    initial=(ctypes.c_uint8*n)(*[sum((base.I(offset+x+s)&1)<<h for h,s in enumerate(k.SLOTS)) for x in range(n)])
    a=(Site*n)(*[Site((offset+x)%k.Q,T+OFFSET,0,0,0,0,initial[x],31) for x in range(n)])
    for x in set(state)|set(tags):a[x-offset]=item(state.get(x,trace.reference(x,OFFSET)),tags.get(x,31))
    other=(Site*n)();final=(Site*n)();r=Result();events=(ctypes.c_int*(8*LIMIT))()
    code=c.gaw10_campaign(a,other,initial,n,offset,LIMIT,ctypes.byref(r),events,LIMIT,final)
    result={name:getattr(r,name) for name,_ in Result._fields_};result['return_code']=code
    assert code==0 and r.status==0 and r.steps==LIMIT
    result['event_rows']=[list(events[8*t:8*t+8]) for t in range(r.steps)]
    result['final_History_holder_keep']=[(x+offset,final[x].hist) for x in range(n) if final[x].hist!=31]
    result['final_native_Info']=[(x+offset,[getattr(final[x],name) for name,_ in Site._fields_]) for x in range(n)
        if final[x].gf!=(x+offset)%k.Q or final[x].age!=T+OFFSET+LIMIT or any((final[x].f1,final[x].f2,final[x].w1,final[x].w2)) or final[x].info!=initial[x]]
    keep=dict(result['final_History_holder_keep'])
    def copybits(y):return [(keep.get(y-s,31)>>h)&1 for h,s in enumerate(k.SLOTS)]
    def tag(y):
        bits=copybits(y);assert bits==[bits[0]]*5,(y,bits);return bits[0]
    for y in range(min(keep)-4,max(keep)+5):tag(y)
    for x in range(n):
        y=x+offset
        assert final[x].info==sum(((base.I(y+s)&1)*tag(y+s))<<h for h,s in enumerate(k.SLOTS))
        assert final[x].gf==y%k.Q and final[x].age==T+OFFSET+LIMIT
        assert not any((final[x].f1,final[x].f2,final[x].w1,final[x].w2))
    result['final_coherent_erased_logical_coordinates']=[y for y in range(min(keep)-4,max(keep)+5) if not tag(y)]
    return result,tag

def physical_late_contracts(tag,first_execution,upper):
    # Mem before the reset need not be known: the actual reset equation
    # ignores every old Mem word. All other stated inputs below are derived.
    def held(x,age,mem):
        return k.Cell(addr=x%k.Q,age=age,mem=mem,
            info=tuple(base.I(x+s)*tag(x+s) for s in k.SLOTS),
            program=tuple(k.beta_bit(own.ROM,(x+s)%k.Q) for s in k.SLOTS),
            history1=tuple(bank(x+s)*tag(x+s) for s in k.SLOTS),
            history2=tuple(bank(x+s)*tag(x+s) for s in k.SLOTS),
            history3=tuple(bank(x+s)*tag(x+s) for s in k.SLOTS))
    def reset(x):return held(x,102*k.Q,(0,)*5)
    def born(x):
        return replace(held(x,102*k.Q+1,tuple(bank(x+s)*tag(x+s) for s in k.SLOTS)),
            heads=tuple(k.pack(k.Packet(p=1)) if (x+s)%k.Q==k.PRIMARY_START else 0 for s in k.SLOTS))
    def data(y):
        g,a=divmod(y,k.Q);i=a-k.PRIMARY_START
        return k.cell_words(upper(g))[i] if 0<=i<k.FRAME_WORDS else 0
    def committed(x):
        return k.Cell(addr=x%k.Q,info=tuple(data(x+s) for s in k.SLOTS),
            program=tuple(k.beta_bit(own.ROM,(x+s)%k.Q) for s in k.SLOTS))
    _,out,scratch,packet,address=first_execution
    def precommit(x):
        z=held(x,k.U-1,tuple(bank(x+s)*tag(x+s) for s in k.SLOTS))
        return replace(z,out=tuple(data(x+s) for s in k.SLOTS),
            heads=tuple(k.pack(packet) if x+s==address else 0 for s in k.SLOTS),
            scratch=tuple(scratch.get(x+s,0) for s in k.SLOTS))
    xs=sorted({g*k.Q+a for g in (-1,0,1) for a in
        list(range(k.PRIMARY_START-8,k.PRIMARY_START+k.FRAME_WORDS+8))+list(range(-5,9))+list(range(k.Q-8,k.Q+6))})
    digest=hashlib.sha256();counts=dict(reset=0,birth=0,commit=0)
    for x in xs:
        for probe in range(3):
            mem=tuple(0 if probe==0 else ((1<<1700)-1) if probe==1 else ((x+h)&k.MASK)<<((h+4)*k.WORD) for h in range(5))
            got=k.local_transition({d:held(x+d,102*k.Q-1,mem) for d in range(-8,9)},own.ROM)
            assert got==reset(x),(x,'reset')
            digest.update(json.dumps([x,probe,k.cell_words(got)],separators=(',',':')).encode());counts['reset']+=1
        got=k.local_transition({d:reset(x+d) for d in range(-8,9)},own.ROM)
        assert got==born(x),(x,'birth');counts['birth']+=1
        digest.update(json.dumps([x,'birth',k.cell_words(got)],separators=(',',':')).encode())
        got=k.local_transition({d:precommit(x+d) for d in range(-8,9)},own.ROM)
        assert got==committed(x),(x,'commit');counts['commit']+=1
        digest.update(json.dumps([x,'commit',k.cell_words(got)],separators=(',',':')).encode())
    return dict(actual_reset_birth_commit_cofactors=counts,signature_sha256=digest.hexdigest(),
        old_Mem_reset_independence_proved_by_actual_branch=True,
        old_Head_Scratch_Mem_History_commit_independence_proved_by_actual_branch=True,
        actual_derived_info_and_history_used=True,no_independent_preloaded_bank=True)

def bank_and_outputs(tag,erased):
    receivers=sorted({y//k.Q for y in erased if k.PRIMARY_START<=y%k.Q<k.PRIMARY_START+k.FRAME_WORDS})
    records=[];outputs={};runs={}
    for g in receivers:
        tape={k.PRIMARY_START+i:bank(g*k.Q+k.PRIMARY_START+i)*tag(g*k.Q+k.PRIMARY_START+i) for i in range(k.FRAME_WORDS)}
        run=execution.run(tape);words=[int(v,16) for v in run[0]['out_words']]
        z=k.cell_from_words(words);assert k.cell_words(z)==words
        outputs[g]=z;runs[g]=run;records.append(dict(receiver=g,actual_derived_late_tape=[[p,hex(v)] for p,v in sorted(tape.items())],
            actual_execution=run[0],actual_output_native_words=words[:6]))
    bad=[g for g,z in outputs.items() if z!=base.nextH(g)]
    assert bad==[0] and outputs[0]==replace(base.nextH(0),f1=1)
    def upper(g):return outputs.get(g,base.nextH(g))
    second=[]
    for b in bad:
        for g in range(b-8,b+9):
            actual=k.local_transition({j:upper(g+j) for j in range(-8,9)},own.ROM)
            assert actual==base.next2H(g),(g,k.cell_words(actual)[:6],k.cell_words(base.next2H(g))[:6])
            second.append(dict(receiver=g,actual_second_upper_output=[hex(v) for v in k.cell_words(actual)]))
    physical=physical_late_contracts(tag,runs[0],upper)
    return dict(affected_first_receivers=receivers,actual_late_receiver_executions=records,
        actual_literal_reset_birth_commit_contracts=physical,
        sole_upper_difference_Field_Flag1_at_cell0=True,
        first_boundary_bad_upper_cells=bad,derived_first_boundary_E_Cprime=True,
        actual_second_upper_transitions=second,complete2U_shadow=True,
        ordinary_sacrificed_upper_error_permitted=True,operational_or_Gray_iid_failure=False)

def main(write=True):
    start=time.monotonic();prefix,_=trace.prefix(write=False,verbose=False)
    old=json.loads((D/'GAW10_shifted_birth_prefix.json').read_text())
    a=dict(prefix);a.pop('elapsed_seconds');old.pop('elapsed_seconds');assert json.loads(json.dumps(a))==old
    assert len(prefix['rows'][0]['heads'])==5 and len(prefix['rows'][1]['heads'])==2
    assert all(not r['heads'] for r in prefix['rows'][2:])
    assert all(not any(r['nonzero_Out_or_couriers'].values()) for r in prefix['rows'])
    state,tags=keeper_prefix(prefix);c=library();cofactors=cofactor_checks(c)
    factor,tag=continuation(c,state,tags);outputs=bank_and_outputs(tag,factor['final_coherent_erased_logical_coordinates'])
    result=dict(name='GAW10 actual shifted late-Head birth: disappearance, derived bank and U/2U map',
        Q=k.Q,U=k.U,error_lambda=24,error_separation=104,actual_same_H_and_shared_error_history=True,
        whole_cell_payload=prefix['payload'],actual_prefix_sha256=hashlib.sha256((D/'GAW10_shifted_birth_prefix.json').read_bytes()).hexdigest(),
        actual_head_counts=[5,2,0],actual_no_extra_Head_Out_courier_after3_proved=True,
        actual_prefix_History_keeper_tags=sorted(tags.items()),actual_postbirth_local_R_cofactors=cofactors,
        actual_native_Info_History_continuation=factor,actual_bank_and_output_map=outputs,
        no_preloaded_future_tapes_or_Workspace=True,all_arbitrary_birth_near_faults_proved=False,
        direct_whole_period_grid_simulation_claimed=False,Gray_iid_or_shorter_U=False,
        active_rule_modified=False,registered_main_modified=False,new_rule_created=False,
        elapsed_seconds=time.monotonic()-start)
    path=D/'GAW10_shifted_birth_receipt.json'
    if write:path.write_text(json.dumps(result,indent=2)+'\n')
    else:
        old=json.loads(path.read_text());a=dict(result);a.pop('elapsed_seconds');old.pop('elapsed_seconds');assert json.loads(json.dumps(a))==old
    print(json.dumps(dict(passed=True,head_disappears_by=3,postbirth_updates=factor['updates'],
        geometry_quiet_by=OFFSET+factor['first_geometry_quiet'],native_flags_quiet_by=OFFSET+factor['first_native_quiet'],
        erased_logical_count=len(factor['final_coherent_erased_logical_coordinates']),
        erased_logical_interval=[min(factor['final_coherent_erased_logical_coordinates']),max(factor['final_coherent_erased_logical_coordinates'])+1],
        first_bad_upper_cells=outputs['first_boundary_bad_upper_cells'],complete2Ushadow=True,
        operational_Gray_iid_failure=False,elapsed_seconds=time.monotonic()-start)),flush=True)
    return result

if __name__=='__main__':main()
