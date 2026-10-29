"""Reproduce GBC0 generic local primitives and complete passive slice.

The CPU trajectory reads the actual encoded C(g+j) bit matrix.  The
complete lower-period lift is a separately stated mathematical argument;
no future Head/Workspace/input bank is prescribed as an error history.
"""
from dataclasses import asdict,replace
from hashlib import sha256,shake_256
from itertools import product
from pathlib import Path
import argparse,json,time
import compact_stream_rule as b
from compact_passive_emitter import emit_passive,emitted_map

def digest(value):return sha256(json.dumps(value,sort_keys=True,separators=(',',':')).encode()).hexdigest()

def cell_at(g,theta=123,raw_native=False):
    fields={}
    for name,width in b.FIELDS:
        fields[name]=tuple(int.from_bytes(shake_256(f'GBC0:{g}:{name}:{q}'.encode()).digest((width+7)//8),'little')&((1<<width)-1) for q in range(5))
    if raw_native:
        native={f:int.from_bytes(shake_256(f'GBC0-native:{g}:{f}'.encode()).digest((w+7)//8),'little')&((1<<w)-1) for f,w in b.NATIVE}
        return b.Cell(**native,**fields)
    return b.Cell(addr=g%b.Q,age=theta,**fields)

def tape(g,address):
    colony,local=divmod(address,b.Q)
    if not b.PRIMARY_START<=local<b.PRIMARY_START+b.FRAME_BITS:return 0
    k=local-b.PRIMARY_START
    return sum(b.encode_cell(cell_at(g+colony+j))[k]<<lane for lane,j in enumerate(b.LANES))

def truth_tables():
    count=0
    for aligned in (False,True):
        limit=4 if aligned else 6
        for lane in range(-limit,limit+1):
            for q in range(5):
                for pattern in range(32):
                    mem={d:0 for d in range(-4,5)}
                    centre=lane+(b.SLOTS[q] if aligned else 0)
                    for r in range(5):mem[r-q]|=(pattern>>r&1)<<(8+centre-b.SLOTS[r])
                    assert b.read_vote(mem,lane,q,aligned)==int(pattern.bit_count()>=3)
                    count+=1
    return count

def primitives(beta):
    parser=0
    values={0,b.MASK}
    for n in range(21):
        for k in (0,1,(1<<n)-1):
            v=(1<<n)+k-1
            if 0<=v<=b.MASK:values.add(v)
        for k in range(n):
            v=(1<<n)+(1<<k)-1
            if v<=b.MASK:values.add(v)
    values.update(range(2048))
    for v in sorted(values):
        code=b.encode('LIT',v);decoded=b.decode(code+(0,)*(b.Q-len(code)),0)
        assert decoded==('LIT',(v,),len(code));parser+=1
    # Every possible LIT unary prefix length, both delimiter and overflow.
    for n in range(22):
        payload=tuple((b.OP['LIT']>>i)&1 for i in range(4))+(0,)*n+(1,)+(0,)*n
        z=b.decode(payload+(0,)*(b.Q-len(payload)),0)
        assert (z is None)==(n>20)
        parser+=1
    mem={d:0 for d in range(-4,5)};branch=0
    for cond,a,target in product(range(4),(0,1,1<<19,b.MASK),(0,b.Q-1)):
        op=b.encode('BR',cond,target);bb=op+(0,)*(b.Q-len(op))
        p,z=b.cpu(b.Packet(p=1,a=a),200,mem,bb)
        taken=(True,a==0,a!=0,bool(a&(1<<19)))[cond]
        assert p.pc==(target if taken else len(op)) and z is None;branch+=1
    work=int.from_bytes(shake_256(b'GBC0-work').digest(51),'little')&b.WORK_MASK
    windows=0
    for offset in range(428):
        for bit in range(20):
            value=1<<bit;op=b.encode('WSET');bb=op+(0,)*(b.Q-len(op))
            p,z=b.cpu(b.Packet(p=1,a=value,b=offset,work=work),200,mem,bb)
            expected=work if offset>=407 else ((work&~(b.MASK<<offset))|(value<<offset))&b.WORK_MASK
            assert p.work==expected and p.a==value and p.b==offset and z is None
            op=b.encode('WGET');bb=op+(0,)*(b.Q-len(op))
            r,z=b.cpu(b.Packet(p=1,a=offset,work=p.work),200,mem,bb)
            assert r.a==(0 if offset>=407 else (p.work>>offset)&b.MASK);windows+=2
    for width in range(32):
        op=b.encode('PUSH',width);bb=op+(0,)*(b.Q-len(op))
        p,z=b.cpu(b.Packet(p=1,a=b.MASK,work=work),200,mem,bb)
        if width>20:assert p.mode==b.ERROR
        else:assert p.work==((work<<width)|((1<<width)-1))&b.WORK_MASK
        windows+=1
    for selector in range(16):
        raw=b.Packet(p=1,move=0,pc=0,ret=123,start=345,index=567,buf=3,
                     lane=31,fn=15,kind=3,a=891,b=912,work=work,nc=(1<<35)-1)
        op=b.encode('SELF',selector);bb=op+(0,)*(b.Q-len(op))
        p,z=b.cpu(raw,200,mem,bb)
        expected=(200,0,123,345,567,3,31,15,3,1,0,0,work&b.MASK,b.MASK,(1<<15)-1,0)[selector]
        assert p.a==expected;windows+=1
    # All signed lane/kind combinations in raw pending IO, not just those
    # entered by the compiler. Width/target failures do not require masks.
    pending=0
    for kind,lane in product(range(4),range(32)):
        value=b.signed(lane,5)
        valid=(kind==b.READ_BIT and -8<=value<=8 or kind==b.READ_VOTE and -6<=value<=6 or kind==b.READ_WORD and value==0 or kind==b.WRITE_BIT)
        p,z=b.cpu(b.Packet(p=1,mode=b.IO,start=200,kind=kind,lane=lane,a=1),200,mem,beta)
        assert (p.mode==b.ERROR)==(not valid)
        assert (z is not None)==(valid and kind==b.WRITE_BIT);pending+=1
    for mode in (5,6,7):
        p,z=b.cpu(b.Packet(p=1,mode=mode),200,mem,beta);assert p.mode==b.ERROR
    arithmetic=0
    for selector,fn,a,c in product(range(32),range(16),(0,1,19,20,b.MASK),(0,1,19,20,b.MASK)):
        op=b.encode('ALU',selector);bb=op+(0,)*(b.Q-len(op))
        p,z=b.cpu(b.Packet(p=1,fn=fn,a=a,b=c),200,mem,bb)
        if selector>16:assert p.mode==b.ERROR
        else:assert p.a==b.alu(fn if selector==16 else selector,a,c)
        arithmetic+=1
    dynamic=0
    for fn,kind in product(range(16),range(4)):
        op=b.encode('READ',kind,16);bb=op+(0,)*(b.Q-len(op))
        p,z=b.cpu(b.Packet(p=1,fn=fn,b=200),200,mem,bb)
        lane=b.signed(fn,4)
        valid=(kind==b.READ_BIT and -8<=lane<=8 or kind==b.READ_VOTE and -6<=lane<=6 or kind==b.READ_WORD and lane==0)
        assert (p.mode==b.ERROR)==(not valid)
        if valid:assert p.lane==lane&31 and p.mode==b.IO
        dynamic+=1
    layout=0
    for bit in range(b.FRAME_BITS):
        assert b.pack_cell(b.unpack_cell(1<<bit))==1<<bit;layout+=1
    return {'literal_fetch_cases':parser,'branch_cases':branch,
            'work_metadata_cases':windows,'pending_io_cases':pending,
            'arithmetic_control_cases':arithmetic,'dynamic_read_cases':dynamic,
            'cell_layout_one_hot_cases':layout}

def radius_witness(side,beta):
    logical=-2 if side<0 else 2;centre=6 if side<0 else 3
    service=(centre+logical)%b.Q;q=service%5
    critical_r=0 if side<0 else 4
    true_r=(1,2) if side<0 else (0,1)
    values={}
    for r in true_r+(critical_r,):values[logical+r-q]=1<<(8+6-b.SLOTS[r])
    packet=b.Packet(p=1,mode=b.STREAM,start=service,a=1,index=0,lane=6)
    cells={}
    for x in b.LANES:
        hist=tuple(values.get(x+s,0) for s in b.SLOTS)
        heads=tuple(b.pack(packet) if x+s==logical else 0 for s in b.SLOTS)
        cells[x]=b.Cell(addr=(centre+x)%b.Q,age=112*b.Q+1,
                        history1=hist,history2=hist,head=heads)
    column=logical+critical_r-q; bit=8+6-b.SLOTS[critical_r]
    far=8*side; critical_slot=b.SLOTS.index(column-far)
    # Two true copies, with the farthest third holder decisive.
    good_slots=[k for k in range(5) if k!=critical_slot][:2]
    for k,s in enumerate(b.SLOTS):
        x=column-s
        for field in ('history1','history2'):
            raw=list(getattr(cells[x],field))
            raw[k]=(raw[k]|(1<<bit)) if k in good_slots else raw[k]&~(1<<bit)
            cells[x]=replace(cells[x],**{field:tuple(raw)})
    changed=dict(cells)
    for field in ('history1','history2'):
        raw=list(getattr(changed[far],field));raw[critical_slot]|=1<<bit
        changed[far]=replace(changed[far],**{field:tuple(raw)})
    left=b.total_rule(cells,beta);right=b.total_rule(changed,beta)
    output_slot=b.SLOTS.index(logical)
    assert left.next[output_slot]==0 and right.next[output_slot]==1
    assert all(cells[x]==changed[x] for x in b.LANES if x!=far)
    return {'side':side,'changed_coordinate':far,'output_copy':output_slot,
            'logical_source':column,'raw_holder_slot':critical_slot,
            'history_lane':bit,'before_input':{str(x):asdict(c) for x,c in cells.items()},
            'after_cell':asdict(changed[far]),'before_output':asdict(left),'after_output':asdict(right)}

def execute(g,beta,physical=False,theta=123,first_missing_capture=False,raw_native=False):
    inputs={j:(b.Cell(addr=(g+j)%b.Q,age=b.Q+1,mailL=(1,)*5) if first_missing_capture else cell_at(g+j,theta,raw_native)) for j in b.LANES}
    encoded={j:b.encode_cell(c) for j,c in inputs.items()}
    def source(address):
        assert 0<=address<b.Q
        if not b.PRIMARY_START<=address<b.PRIMARY_START+b.FRAME_BITS:return 0
        k=address-b.PRIMARY_START
        return sum(encoded[j][k]<<lane for lane,j in enumerate(b.LANES))
    shadow=b.total_rule(inputs,beta);expected=b.encode_cell(shadow)
    delta=emitted_map(inputs)
    packet=b.Packet(p=1);address=b.PRIMARY_START;writes={};trace=[]
    physical_checks=0;native_snapshot=None
    for tick in range(1,10000):
        old=packet;old_address=address
        address+=1 if old.move==1 else -1 if old.move==2 else 0
        assert 0<=address<b.Q
        window={d:source(address+d) for d in range(-4,5)}
        if old.mode==b.RUN and b.decode(beta,old.pc)[0]=='NATIVE':
            tags=tuple((f,k) for f,w in b.NATIVE for k in range(w))
            exact=sum((getattr(inputs[j],f)>>k&1)<<(11*i+j+5)
                      for i,(f,k) in enumerate(tags) for j in range(-5,6))
            assert old.work==exact;native_snapshot=hex(exact)
        packet,write=b.cpu(old,address,window,beta)
        assert packet.mode!=b.ERROR
        if physical:
            for copy,s in enumerate(b.SLOTS):
                holder=address-s
                cells={}
                for x in b.LANES:
                    absolute=holder+x
                    histories=tuple(source(absolute+r) for r in b.SLOTS)
                    heads=tuple(b.pack(old) if absolute+r==old_address else 0 for r in b.SLOTS)
                    nexts=tuple(writes.get(absolute+r,0) for r in b.SLOTS)
                    infos=tuple((source(absolute+r)>>8)&1 for r in b.SLOTS)
                    cells[x]=b.Cell(addr=absolute%b.Q,age=112*b.Q+tick,
                                   history1=histories,history2=histories,
                                   history3=histories,head=heads,next=nexts,info=infos)
                output=b.total_rule(cells,beta)
                assert output.head[copy]==b.pack(packet)
                assert output.next[copy]==(writes.get(address,0) if write is None else write)
                physical_checks+=1
        if write is not None:
            assert address not in writes
            writes[address]=write
        trace.append((tick,address,b.pack(packet),write))
        if packet.mode==b.HALT:break
    else:raise AssertionError('declared passive programme failed to halt')
    assert tick==4135 and len(writes)==b.FRAME_BITS
    actual=tuple(writes[a] for a in range(b.PRIMARY_START,b.PRIMARY_START+b.FRAME_BITS))
    assert actual==b.encode_cell(delta)
    wrong=tuple(i for i,(x,y) in enumerate(zip(actual,expected)) if x!=y)
    if first_missing_capture:
        assert wrong==tuple(range(97,102))
        assert shadow.history1==(1<<9,)*5
    elif not raw_native:assert not wrong
    assert min(t[1] for t in trace)==b.PRIMARY_START and max(t[1] for t in trace)==b.PRIMARY_START+b.FRAME_BITS-1
    return {'g':g,'theta':b.Q+1 if first_missing_capture else theta,
            'first_missing_capture':first_missing_capture,
            'prepared_only':raw_native,'physical_period_claim':not raw_native,
            'input_cells':{str(j):asdict(c) for j,c in inputs.items()},
            'upper_output':asdict(shadow),'halt_updates':tick,'writes':len(writes),
            'native_buffer':native_snapshot,'trace_sha256':digest(trace),
            'output_bits_sha256':digest(actual),'physical_local_checks':physical_checks,
            'actual_bits':''.join(map(str,actual)),
            'expected_bits':''.join(map(str,expected)),'wrong_raw_bits':wrong,
            'actual_upper_output':asdict(b.unpack_cell(sum(v<<i for i,v in enumerate(actual))))}

def run(output_dir,full_physical=False):
    t0=time.monotonic();out=Path(output_dir);out.mkdir(parents=True,exist_ok=True)
    beta,listing,length=emit_passive()
    primitive=primitives(beta);truth=truth_tables()
    native=0
    for theta in (1,123,b.Q):
        for g in range(b.Q):
            cells={j:b.Cell(addr=(g+j)%b.Q,age=theta) for j in range(-5,6)}
            r=b.native_at(cells,0)
            assert r=={'addr':g,'age':theta+1,'f1':0,'f2':0};native+=1
    witnesses=[radius_witness(side,beta) for side in (-1,1)]
    cases=[execute(g,beta,full_physical and i==0,theta=theta)
           for i,(g,theta) in enumerate(((0,1),(1,123),(b.Q//2,b.Q),(b.Q-1,123)))]
    missing=execute(0,beta,False,first_missing_capture=True)
    raw_cases=[execute(g,beta,False,raw_native=True) for g in (19,524)]
    receipt={'passed':True,'scope':'total compact primitives and complete passive-upper-phase period slice',
             'Q':b.Q,'U':b.U,'lambda':b.LAMBDA,'c':b.ERROR_SEPARATION,'radius':8,
             'Head_bits':b.HEAD_BITS,'K':b.FRAME_BITS,'2K':2*b.FRAME_BITS,
             'programme_bits':length,'padding_bits':b.Q-length,'instructions':len(listing),
             'beta_sha256':sha256(bytes(beta)).hexdigest(),'primitive_checks':primitive,
             'five_bit_vote_cases':truth,'native_phases':native,'cases':cases,
             'radius_witnesses':witnesses,'listing':listing,
             'first_missing_capture':missing,'passive_upper_Age_interval':[1,b.Q],
             'prepared_all_raw_examples':raw_cases,
             'full_own_beta':False,'all_raw_own_equivalence':False,
             'universal_whole_rule_deadline':False,'gray_refutation':False,
             'noise_theorem':False,'iid_failure':False,'shorter_U':False,
             'elapsed_seconds':time.monotonic()-t0}
    (out/'GBC0_certificate.json').write_text(json.dumps(receipt,indent=2)+'\n')
    (out/'GBC0_passive_beta.json').write_text(json.dumps(list(beta))+'\n')
    print(json.dumps({'passed':True,'programme_bits':length,'halt':4135,
                      'physical_checks':sum(c['physical_local_checks'] for c in cases),
                      'elapsed_seconds':receipt['elapsed_seconds']},indent=2))
    return receipt

if __name__=='__main__':
    ap=argparse.ArgumentParser();ap.add_argument('--output-dir',required=True)
    ap.add_argument('--full-physical',action='store_true');args=ap.parse_args()
    run(args.output_dir,args.full_physical)
