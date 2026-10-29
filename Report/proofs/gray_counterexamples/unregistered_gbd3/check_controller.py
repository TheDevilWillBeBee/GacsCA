"""GBD3 physical CPU/writes, bytecode and universal affine-word checks."""
import argparse,hashlib,json,random
from pathlib import Path
from dataclasses import replace
import controller as k
import layout as l
import helpers as helpermod

ROOT=Path(__file__).resolve().parents[4]
HERE=Path(__file__).resolve().parent
DATA=ROOT/'figs/gray_counterexamples/unregistered_gbd3'

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def copy_beta(split):
    # Both programmes read the real Mem340 at Head-2, lane0. Their
    # BYTECODE, registers, movement and writes are executed by local().
    rows=[('LIT',1,0,0),('LIT',2,0,0),('LIT',3,5,20),
          ('READ',0,1,2,3,0),('LIT',2,5,19)]
    if split:
        rows.extend([('LIT',3,5,16),('WRITE',0,2,3,1),
             ('ALU',12,0,0,3),('LIT',3,3,4),
             ('GETHEAD',4,6),('LIT',5,3,4),('ALU',0,4,4,5),
             ('MOVE',4),('WRITE',0,2,3,1),('HALT',)])
    else:rows.extend([('WRITE',0,2,3,1),('HALT',)])
    beta=tuple(b for row in rows for b in k.encode(*row))
    return rows,beta

def raw_program(A,split,initial_out,random_regs=False):
    rows,beta=copy_beta(split);h=2500;lo=h-20;hi=h+30
    rng=random.Random(273104+A)
    regs=tuple(rng.getrandbits(20) for _ in range(8)) if random_regs else (0,)*8
    entry=k.Head(1,3,k.RUN,0,7139,5192,regs)
    def heads(x):return entry if x==h else k.Head()
    def mem(x):
        return ((A if x==h-2 else ((x*349971)&k.MASK))|
                (((x*513193)&((1<<320)-1))<<20))
    # Shared arbitrary old Out at every logical site, coherent lower copies.
    def out(x):return initial_out[x] if x in initial_out else ((x*191)&k.MASK)
    current={x:k.coherent_cell(x,589999,heads,mem,out) for x in range(lo,hi+1)}
    snapshots=[]
    base,cap=(0,16) if split else (-2,20)
    ticks=0;positions=[];executed=[]
    # Global exterior is constant zero Head, unchanged Mem/Out, common ports.
    while ticks<30:
        live=[]
        for x in range(h-3,h+9):
            v=k.head_vote(current,x)
            if v.present:live.append((x,v))
        assert len(live)<=1,'unique-head copy factor lost'
        if not live:break
        x,v=live[0];positions.append(x)
        if v.mode==k.RUN:executed.append(k.instruction(beta,v.pc)[0])
        extended=dict(current)
        for x in range(lo-10,lo):extended[x]=k.coherent_cell(x,589999+ticks,lambda z:k.Head(),mem,out)
        for x in range(hi+1,hi+11):extended[x]=k.coherent_cell(x,589999+ticks,lambda z:k.Head(),mem,out)
        current={x:replace(k.local(extended,x,beta,base,cap),age=590000+ticks)
                 for x in range(lo,hi+1)}
        ticks+=1
        # Literal FIVE copies remain equal after each actual raw update.
        for x in range(lo+10,hi-9):
            for name in ('head','out'):
                values=[getattr(current[x+s],name)[k.INV[j]] for j,s in enumerate(k.S)]
                assert len(set(values))==1,(ticks,x,name,'raw-copy closure')
        if A==0:
            snapshots.append(dict(tick=ticks,live_positions=[x],
                                  source_mode=v.mode,source_pc=v.pc,
                                  output_words={str(z):k.vote(current,z,'out',k.MASK)
                                                for z in range(h-2,h+7)}))
    assert ticks==(19 if split else 7),ticks
    assert executed==[row[0] for row in rows],executed
    assert positions[0]==h and positions[-1]==(h+4 if split else h)
    base_address=h if split else h-2
    masks={};values={}
    for i in range(20):
        chunk,bit=divmod(19+5*i,20);x=base_address+chunk
        masks[x]=masks.get(x,0)|(1<<bit)
        values[x]=values.get(x,0)|(((A>>i)&1)<<bit)
    for x in range(lo+10,hi-9):
        got=k.vote(current,x,'out',k.MASK)
        want=(out(x)&~masks.get(x,0))|values.get(x,0)
        assert got==want,(split,A,x,got,want)
    return dict(ticks=ticks,code_bits=len(beta),rows=len(rows),positions=positions,
                output={str(x):k.vote(current,x,'out',k.MASK) for x in range(h-2,h+7)},
                snapshots=snapshots)

def rejection_witness():
    # x0/copy q1 represents logicaly=-2. The last one-sided stride5
    # write comes from logicalhead=-7. Its leftmost holder is -9.
    beta=k.encode('WRITE',0,1,2,1)
    regs=(1<<19,19,20,0,0,0,0,0)
    request=k.Head(1,0,k.RUN,0,0,0,regs)
    absent=replace(request,present=0)
    raw={d:k.Cell() for d in range(-9,10)}
    z=-7
    # Baseline exactly two present holders; payload/control bits agree in
    # all five holders. The third changed presence bit is at physical-9.
    for j,s in enumerate(k.S):
        at=z+s;slots=list(raw[at].head)
        slots[k.INV[j]]=k.pack_head(request if j in (0,2) else absent)
        raw[at]=replace(raw[at],head=tuple(slots))
    changed=dict(raw);slots=list(changed[-9].head)
    slots[k.INV[1]]=k.pack_head(request)
    changed[-9]=replace(changed[-9],head=tuple(slots))
    assert all(raw[d]==changed[d] for d in range(-8,9))
    a=k.write_out(raw,0,1,beta,0,20)
    b=k.write_out(changed,0,1,beta,0,20)
    assert (a,b)==(0,1<<14)
    return dict(schema='GBD3 stipulated one-sided20 radius witness',
                beta=list(beta),centre=0,copy_role=1,logical_receiver=-2,
                logical_head=-7,changed_physical_site=-9,changed_slot=k.INV[1],
                baseline_head=k.pack_head(absent),replacement_head=k.pack_head(request),
                complete_raw_baseline={str(d):dict(addr=c.addr,age=c.age,
                    head=list(c.head),mem=list(c.mem),out=list(c.out)) for d,c in raw.items()},
                old_output=a,new_output=b,inside_radius8_equal=True,
                all_raw_stipulated_component_obstruction=True,
                general_architecture_lower_bound=False,intact_or_noise_history=False,
                Gray_refutation=False)

def field_program(records):
    """Actual lower raw execution reading a word of an arbitrary UPPER
    raw record bank. No expected word is placed in the input registers.
    """
    chunk,phase=divmod(l.REG0_BASE,20)
    rows=[('LIT',1,4,8),('LIT',2,3,phase),('LIT',3,5,20),
          ('READQ',0,1,2,3,1),('LIT',2,5,19),('WRITE',0,2,3,1),('HALT',)]
    beta=tuple(b for row in rows for b in k.encode(*row))
    assert len(beta)==100
    h=l.P+chunk+2;lo=h-15;hi=h+15
    def heads(x):return k.Head(1,3,k.RUN,0,6197,5113,(117,)*8) if x==h else k.Head()
    def mem(x):return l.bank_container(records,x-l.P) if l.P<=x<l.P+l.CHUNKS else 0
    def out(x):return (x*513719)&k.MASK
    current={x:k.coherent_cell(x,595000,heads,mem,out) for x in range(lo,hi+1)}
    read_word=None;steps=[]
    for tick in range(7):
        v=k.head_vote(current,h)
        assert v.present and v.mode==k.RUN
        name,args,_=k.instruction(beta,v.pc);steps.append(name)
        extended=dict(current)
        for x in list(range(lo-9,lo))+list(range(hi+1,hi+10)):
            extended[x]=k.coherent_cell(x,595000+tick,lambda z:k.Head(),mem,out)
        current={x:replace(k.local(extended,x,beta,-2,20),age=595001+tick)
                 for x in range(lo,hi+1)}
        if name=='READQ':read_word=k.head_vote(current,h).regs[0]
    expected=l.upper_SF_word(records,0,'Head',l.HEAD_REG0_BIT,20)
    assert read_word==expected
    assert not k.head_vote(current,h).present
    assert steps==[r[0] for r in rows]
    masks={};values={}
    for i in range(20):
        c,b=divmod(19+5*i,20);x=h-2+c
        masks[x]=masks.get(x,0)|(1<<b)
        values[x]=values.get(x,0)|(((expected>>i)&1)<<b)
    for x in range(h-2,h+4):
        got=k.vote(current,x,'out',k.MASK)
        assert got==((out(x)&~masks.get(x,0))|values.get(x,0))
    return dict(code_bits=len(beta),updates=7,field='Head',field_bit=44,
                raw_record_bit=l.REG0_BASE,phase=phase,source_chunk=chunk,
                Head_position=h,actual_word=read_word,expected_word=expected,
                upper_records={str(d):z for d,z in records.items()},beta=list(beta))

def helper_program(records,name,field_bit,count,slot,lane=8,
                   prepared_memory=None,birth_from_component=False):
    """Literal raw five-slot execution of the396-bit two-helper caller.

    Sparse updates are exact: no old Head exists outside the retained
    five-holder halo. Absent-head actor/write equations hold every other
    coherent field unchanged. This is not a host MOVE or field evaluator.
    """
    b=l.sf_bit(name,field_bit,0)
    assert field_bit+count<=dict(l.SF)[name]
    rows,beta,labels=helpermod.caller(b,count,slot,lane)
    contract=helpermod.contracts(b,count,slot)
    entry=contract['entry'];lo=entry-12;hi=contract['destination']+20
    rng=random.Random(381974+b+slot)
    registers=tuple(rng.getrandbits(20) for _ in range(8))
    if birth_from_component:registers=(0,)*8
    initial=k.Head(1,3,k.RUN,0,6157,5181,registers)
    def heads(x):return initial if x==entry else k.Head()
    def mem(x):
        if prepared_memory is not None:return prepared_memory.get(x,0)
        return l.bank_container(records,x-l.P) if l.P<=x<l.P+l.CHUNKS else 0
    def out(x):return ((x*513719)^173913)&k.MASK
    start_age=650000;birth_checks=0
    if birth_from_component:
        import binding_kernel as binding
        p=binding.p
        def packet(y):
            return p.Packet(mem(y),y-p.P,1) if p.P<=y<p.P+p.CHUNKS else p.ZERO
        raw={}
        for x in range(lo-10,hi+11):
            c=p.coherent_cell(x,p.DONE,packet,lambda bank,y:0)
            raw[x]=binding.Cell(**vars(c),head=tuple(rng.getrandbits(204) for _ in range(5)),
                               out=tuple(out(x+s) for s in k.S))
        reset={x:binding.local(raw,x,beta) for x in range(lo-5,hi+6)}
        assert all(c.head==(0,)*5 for c in reset.values())
        for x in reset:reset[x]=replace(reset[x],age=binding.BIRTH)
        born={x:binding.local(reset,x,beta) for x in range(lo,hi+1)}
        start_age=binding.BIRTH+1
        current={x:k.Cell(c.addr,start_age,c.head,c.data,c.out) for x,c in born.items()}
        for x in current:
            expected=k.coherent_cell(x,start_age,
                     lambda y:binding.head_birth(y%k.Q),mem,out)
            assert current[x]==expected,('literal binding/reset/birth',x)
            birth_checks+=5
        initial=binding.head_birth(entry)
    else:
        current={x:k.coherent_cell(x,start_age,heads,mem,out) for x in range(lo,hi+1)}
    centre=entry;executed=[];timeline=[];updates=0;local_calls=0
    predicted=l.upper_SF_word(records,lane-8,name,field_bit,count)
    read_value=None;get_return=None;put_return=None
    order=(rows[:4]+helpermod.field_get_rows()+rows[4:6]+helpermod.field_put_rows()+rows[6:7])
    while updates<200:
        live=[]
        for x in range(max(lo+6,centre-2),min(hi-5,centre+2)+1):
            h=k.head_vote(current,x)
            if h.present:live.append((x,h))
        assert len(live)<=1,'new generic caller lost unique Head'
        if not live:break
        centre,h=live[0]
        assert all(h.regs[i]==registers[i] for i in (4,6,7)),('live caller register',updates)
        decoded=k.instruction(beta,h.pc) if h.mode==k.RUN else None
        if decoded:executed.append(decoded[0])
        # If a READ/WRITE executes, all actual container sources and
        # receiver copies fit this halo. On travel rows only the Head
        # holder halo changes. Everything else is algebraically held.
        footprint=range(centre-4,centre+6) if decoded and decoded[0]=='WRITE' else range(centre-3,centre+4)
        assert lo+8<=min(footprint) and max(footprint)<=hi-8
        extended=dict(current)
        for x in list(range(lo-9,lo))+list(range(hi+1,hi+10)):
            extended[x]=k.coherent_cell(x,start_age+updates,lambda z:k.Head(),mem,out)
        changes={x:k.local(extended,x,beta,-2,20) for x in footprint}
        current.update(changes);updates+=1;local_calls+=len(changes)
        current={x:replace(c,age=start_age+updates) for x,c in current.items()}
        next_live=[]
        for x in range(centre-2,centre+3):
            hh=k.head_vote(current,x)
            if hh.present:next_live.append((x,hh))
        assert len(next_live)<=1
        if next_live:
            centre,after=next_live[0]
            assert all(after.regs[i]==registers[i] for i in (4,6,7))
            if decoded and labels['FGET']<=h.pc<labels['FPUT']:
                assert all(after.regs[i]==h.regs[i] for i in (1,2,4,6,7))
            if decoded and h.pc>=labels['FPUT']:
                assert all(after.regs[i]==h.regs[i] for i in (0,1,4,6,7))
            if decoded and decoded[0]=='READQ':
                read_value=after.regs[0];assert read_value==predicted
            if decoded and decoded[0]=='RET':
                if h.pc<labels['FPUT']:get_return=after.pc
                else:put_return=after.pc
        # All Head copies after EACH update, including actual travel and
        # RET rows, must equal the same logical204-bit word. Out-copy
        # closure is checked in the only changing output halo.
        for y in range(min(footprint)-1,max(footprint)+2):
            for field in ('head','out'):
                values=[getattr(current[y+s],field)[k.INV[h]] for h,s in enumerate(k.S)]
                assert len(set(values))==1,(updates,y,field,'helper raw-copy closure')
        if decoded:
            timeline.append(dict(update=updates,source=centre,opcode=decoded[0],old_pc=h.pc,
                                 old_regs=list(h.regs),old_return=h.ret))
    assert updates==contract['updates'],(updates,contract)
    assert executed==[r[0] for r in order]
    assert read_value==predicted
    driver=rows[:7]
    assert get_return==len(helpermod.bits(driver[:4]))
    assert put_return==len(helpermod.bits(driver[:6]))
    masks={};data={}
    for i in range(count):
        chunk,bit=divmod(b+slot+5*i,20);x=l.P+chunk
        masks[x]=masks.get(x,0)|(1<<bit)
        data[x]=data.get(x,0)|(((predicted>>i)&1)<<bit)
    for x in range(lo+6,hi-5):
        assert not k.head_vote(current,x).present
        assert k.vote(current,x,'out',k.MASK)==((out(x)&~masks.get(x,0))|data.get(x,0)),('helper final output',x)
    return dict(field=name,field_bit=field_bit,count=count,copy_slot=slot,
                lane_centre=lane,raw_base=b,contract=contract,labels=labels,
                beta=list(beta),actual_word=read_value,expected_word=predicted,
                initial_registers=list(registers),initial_return=initial.ret,
                actual_get_return=get_return,actual_put_return=put_return,
                preserved_registers=[4,6,7],local_calls=local_calls,
                actual_reset_and_birth=birth_from_component,
                actual_reset_birth_copy_checks=birth_checks,
                packed_memory_from_literal_history=prepared_memory is not None,
                first_execution_computed_port_age=start_age,
                complete_upper_raw_records={str(d):z for d,z in records.items()},
                instruction_timeline=timeline)

def main():
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True)
    p.add_argument('--witness-output',type=Path,required=True);a=p.parse_args()
    # Exact field offsets/bit shape, all six metadata words plus eight regs.
    assert k.HEAD_BITS==204
    rng=random.Random(812704)
    for _ in range(64):
        z=rng.getrandbits(204)
        assert k.pack_head(k.unpack_head(z))==z
    # Literal receiver source ports for both accepted new choices and the
    # rejected one-sided20 interface, all five output roles and Head holders.
    radius_ports={};identities=0
    for base,cap in ((0,16),(0,20),(-2,20)):
        offsets=set()
        last=(19+5*(cap-1))//20
        for q,sq in enumerate(k.S):
            for chunk in range(last+1):
                z=sq-base-chunk
                for h,sh in enumerate(k.S):
                    d=z+sh;slot=k.INV[h]
                    assert d+k.S[slot]==z
                    offsets.add(d);identities+=1
        radius_ports[f'{base}:{cap}']=sorted(offsets)
    assert max(abs(d) for d in radius_ports['0:16'])==8
    assert max(abs(d) for d in radius_ports['0:20'])==9
    assert max(abs(d) for d in radius_ports['-2:20'])==7
    # Literal READ stencil includes only fixed indices and actual slots.
    read_ports=set();read_identities=0
    for q,sq in enumerate(k.S):
        for chunk in range(6):
            z=sq-2+chunk
            for h,sh in enumerate(k.S):
                d=z+sh;slot=k.INV[h]
                assert d+k.S[slot]==z
                read_ports.add(d);read_identities+=1
    assert max(abs(d) for d in read_ports)==7
    # Whole-cell selected raw PC/field decodes, all unused LIT width and
    # all forbidden-opcode/truncated cases, exact CODE bounds.
    samples={
      'HALT':(), 'LIT':(7,20,k.MASK),'ALU':(31,7,6,5),
      'BR':(7,7,6,8191),'READ':(7,6,5,4,1),'WRITE':(7,6,5,1),
      'CODE':(7,6,5),'MOVE':(7,),'CALL':(8191,), 'RET':(),
      'GETHEAD':(7,7),'SETHEAD':(7,7),'ALUR':(7,6,5,4),
      'QUORUM':(1,7,6,5,4,3,2,1),'READQ':(7,6,5,4,1)}
    rows=fields=0
    for name,args in samples.items():
        beta=k.encode(name,*args);decoded=k.instruction(beta,0)
        assert decoded==(name,args,len(beta)),decoded
        for cut in range(len(beta)):
            assert k.instruction(beta[:cut],0)[0]=='INVALID'
        rows+=1;fields+=len(args)
    malformed_widths=0
    for n in range(21,32):
        beta=k.encode('LIT',0,n,0)
        assert k.instruction(beta,0)[0]=='INVALID';malformed_widths+=1
    for op in (15,):
        assert k.instruction(tuple((op>>i)&1 for i in range(4)),0)[0]=='INVALID'
    beta=tuple(rng.getrandbits(1) for _ in range(193))
    for pc in range(8192):
        name,args,n=k.instruction(beta,pc)
        assert name=='INVALID' or (name in k.OPS and pc+n<=len(beta))
    for index in (0,172,173,192,193,8191,8192,k.MASK):
        for count in range(32):
            got=k.code_word(beta,index,count)
            if count>20:assert got==0
            else:assert got==sum((beta[index+j] if index+j<len(beta) else 0)<<j
                                 for j in range(count))
    # All defined ISA kinds exercise actual execute semantics. The finite
    # supplements are not substituted for the symbolic per-opcode proof.
    supplements=[]
    entry=k.Head(1,3,k.RUN,0,7741,3179,tuple([31,k.MASK,0,5,3,7,16,20]))
    cases=[('HALT',()),('LIT',(2,20,k.MASK)),('ALU',(1,2,2,1)),
      ('BR',(0,0,1,7000)),('READ',(2,0,1,2,0)),('WRITE',(0,1,2,0)),
      ('CODE',(2,1,0)),('MOVE',(1,)),('CALL',(7000,)),('RET',()),
      ('GETHEAD',(2,7)),('SETHEAD',(1,4)),('ALUR',(0,2,1,2)),
      ('QUORUM',(1,2,3,4,4,4,4,4)),('READQ',(2,0,1,2,0))]
    for name,args in cases:
        b=k.encode(name,*args);out=k.execute(entry,2477,589831,19739,b)
        assert k.pack_head(k.unpack_head(k.pack_head(out)))==k.pack_head(out)
        if name=='WRITE':assert out.regs==entry.regs and out.pc==len(b)
        if name in ('READ','READQ'):assert out.regs[2]==19739
        if name=='CODE':assert out.regs[2]==0
        if name=='ALUR':assert out.regs[2]==0
        supplements.append(dict(op=name,code_bits=len(b),output_head=k.pack_head(out)))
    # Quorum all32 bit truth values; word equality partitions pin the lack
    # of two distinct >=3 quora for a list of lengthfive.
    for bits in range(32):
        values=[(bits>>i)&1 for i in range(5)]
        assert k.majority5(values)==int(sum(values)>=3)
    import itertools
    word_quora=0
    for values in itertools.product((0,17,k.MASK),repeat=5):
        valid=[v for v in set(values) if values.count(v)>=3]
        assert len(valid)<=1
        assert k.equal_quorum(values,9)==(valid[0] if valid else 9)
        word_quora+=1
    # Each issued copy code is linear in A, all control/timing independent
    # of A. Execute zero/basis/allones through actual raw holders; retain
    # symbolic masks proof for universal A and arbitrary coherent old Out.
    rawruns={};bases=[0,*[1<<i for i in range(20)],k.MASK]
    initial_out={x:rng.getrandbits(20) for x in range(2480,2531)}
    for split in (False,True):
        results=[raw_program(A,split,initial_out,random_regs=True) for A in bases]
        assert all(r['ticks']==results[0]['ticks'] for r in results)
        code=copy_beta(split)[1]
        name='one_sided16_plus4' if split else 'balanced20'
        rawruns[name]=dict(code_bits=len(code),instruction_rows=len(copy_beta(split)[0]),
                          updates=results[0]['ticks'],basis_cases=len(results),
                          baseline_trace=results[0],beta=list(code),
                          forall_Word20_data=True,quiet_copy_premise=True,
                          full_own_programme=False)
    # READQ literal25-port composition has two nested majority levels.
    # Physical inverse-slot identity holds independently of all bit values.
    diagonal_identities=0;diagonal_offsets=set()
    for q,sq in enumerate(k.S):
        for phase in range(20):
            for stride in (1,5):
                for i in range(20):
                    for h in range(5):
                        c,b=divmod(phase+stride*i+k.INV[h],20)
                        u=sq-2+c
                        for g,sg in enumerate(k.S):
                            d=u+sg;slot=k.INV[g]
                            assert d+k.S[slot]==u and 20*c+b==phase+stride*i+k.INV[h]
                            assert abs(d)<=7
                            diagonal_offsets.add(d);diagonal_identities+=1
    assert diagonal_offsets==set(range(-6,8))
    for lane in range(2,15):assert all(0<=lane+s<17 for s in k.S)
    # Twenty actual upper-bit basis inputs plus random FULL K-bit records.
    # The upper copies themselves are arbitrary/incoherent, not pre-voted.
    field_runs=[]
    for n in range(8):
        records={d:rng.getrandbits(l.K) for d in range(-8,9)}
        field_runs.append(field_program(records))
    for i in range(20):
        records={d:0 for d in range(-8,9)}
        for h in (0,1,2):
            d=k.S[h];b=l.sf_bit('Head',44+i,k.INV[h]);records[d]=1<<b
        r=field_program(records);assert r['actual_word']==1<<i
        field_runs.append(r)
    assert l.K==3387 and 2*l.K<=k.Q
    # Counted shared software and exact ABI/travel, using actual packed
    # arbitrary full records, not expected words loaded into registers.
    helper_runs=[]
    for slot in range(5):
        records={d:rng.getrandbits(l.K) for d in range(-8,9)}
        helper_runs.append(helper_program(records,'Head',44,20,slot))
    records={d:rng.getrandbits(l.K) for d in range(-8,9)}
    helper_runs.append(helper_program(records,'Head',44+7*20,20,4))
    helper_runs.append(helper_program(records,'Info',0,1,4,lane=2))
    helper_runs.append(helper_program(records,'Head',44,0,0,lane=14))
    assert (len(helpermod.bits(helpermod.field_get_rows())),len(helpermod.bits(helpermod.field_put_rows())))==(140,137)
    assert all(r['contract']['beta_bits']==396 for r in helper_runs)
    assert helper_runs[0]['contract']['updates']==155
    assert helper_runs[5]['contract']['updates']==190
    w=rejection_witness();a.witness_output.parent.mkdir(parents=True,exist_ok=True)
    a.witness_output.write_text(json.dumps(w,indent=2)+'\n')
    proof=HERE/'GBD3_FINITE_HEAD_AND_LITERAL_WRITE.md'
    receipt=dict(schema='GBD3 finite Head and generic word write component v1',
        passed=True,Q=k.Q,U=k.U,lambda_=24,c=104,
        Head_bits=k.HEAD_BITS,register_words=8,register_width=20,
        proposed_total_K=3387,proposed_twoK=6774,
        literal_Head_source_slot_identities=identities,write_source_offsets=radius_ports,
        read_source_slot_identities=read_identities,read_source_offsets=sorted(read_ports),
        accepted_one_sided16_radius=8,rejected_one_sided20_radius=9,
        accepted_balanced20_radius=7,complete_component_radius=8,
        fixed_PC_decodes=8192,roundtrip_opcodes=rows,roundtrip_operands=fields,
        malformed_LIT_width_cases=malformed_widths,
        word_equality_quorum_cases=word_quora,execute_supplements=supplements,
        actual_raw_copy_programs=rawruns,
        diagonal_source_slot_identities=diagonal_identities,
        diagonal_source_offsets=sorted(diagonal_offsets),
        actual_upper_field_word_programs=field_runs,
        shared_helpers_bits=dict(FGET=140,FPUT=137,caller_with_both=396),
        actual_shared_helper_callers=helper_runs,
        helper_register_4_6_7_liveness=True,
        helper_actual_single_link_and_RET=True,
        helper_nested_CALLs=False,helper_global_packed_bank_is_premise=True,
        captured_raw_records_not_prevoted=True,
        generic_diagonal_field_access=True,
        beta_resource_one_counted_bitstream=True,ISA_dictionary_bits=0,
        extra_stack_or_table_bits=0,computed_native_ports_are_premise=True,
        total_Controller_and_ISA_component=True,conditional_copy_programs=True,
        native_port_composition=False,actual_reset_birth=False,
        autonomous_three_gathers=False,full_own_beta=False,beta_fit=False,
        complete_finite_CA=False,full_period=False,full_runtime_bound=False,
        faithful_Gray=False,Gray_refutation=False,iid_failure=False,shorter_U=False,
        witness_sha256=sha(a.witness_output),
        source_hashes={str(p.relative_to(ROOT)):sha(p) for p in
                      (Path(__file__),Path(k.__file__),Path(l.__file__),Path(helpermod.__file__),proof)})
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(receipt,indent=2)+'\n');print(json.dumps(receipt,indent=2))

if __name__=='__main__':main()
