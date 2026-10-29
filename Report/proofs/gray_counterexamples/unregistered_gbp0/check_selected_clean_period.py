"""Exact selected GBP1R clean-period HEAD/Next factor and cutoff witness.

All sources derive from the written global E(C,0). This uses the literal
total_rule at each active tick, not an independent head transition chosen
after the fact. The written proof lifts this finite factor to the line.
"""
import argparse,hashlib,json,time
from dataclasses import replace,asdict
from pathlib import Path
from check_full_rom_execution import compile_program,tape,canonical,coherent
import binary_own_rule_rom_v2 as b

def decode(bits):
    index=0;d={}
    for f,w in b.NATIVE:
        d[f]=sum(bits[index+k]<<k for k in range(w));index+=w
    for f,w in b.FIELDS:
        d[f]=tuple(sum(bits[index+5*k+q]<<k for k in range(w)) for q in range(5));index+=5*w
    assert index==b.FRAME_BITS
    c=b.Cell(**d);assert b.encode_cell(c)==tuple(bits);return c

def selected_cells(g=100):
    h=b.Packet(p=1,mode=b.HALT,regs=(b.MASK,)*b.REGISTERS,work=(1<<b.WORK_BITS)-1)
    return coherent(canonical(123,g),{j:h for j in range(-10,11)})

def native_closure():
    for phase in range(b.Q):
        cells={j:b.Cell(addr=(phase+j)%b.Q,age=123) for j in b.LANES}
        n=b.native_at(cells,0)
        assert n=={'addr':phase,'age':124,'f1':0,'f2':0}
    return b.Q

def local_input(observer,old_position,p,age,mem,out):
    d={}
    for x in b.LANES:
        z=observer+x
        def at(a):return mem[a] if 0<=a<b.Q else 0
        heads=tuple(b.pack(p) if z+s==old_position else 0 for s in b.SLOTS)
        history=tuple(at(z+s) for s in b.SLOTS)
        # Info/Mail/couriers are irrelevant to this closed post112Q Head/Next
        # projection; their actual earlier histories are proved separately.
        d[x]=b.Cell(addr=z%b.Q,age=age,head=heads,
          history1=history,history2=history,history3=history,
          next=tuple(out.get(z+s,0) for s in b.SLOTS))
    return d

def gather_and_source_checks(beta,mem):
    checks=0;z=b.PRIMARY_START+50
    for stage in range(3):
        field='history'+str(stage+1)
        for lane,offset in enumerate(b.LANES):
            for q,s in enumerate(b.SLOTS):
                for value in (0,1):
                    observer=z-s;cells={}
                    for x in b.LANES:
                        bits=tuple(value if observer+x+t==z else 0 for t in b.SLOTS)
                        cells[x]=b.Cell(addr=(observer+x)%b.Q,age=b.capture(stage,offset)-1,
                          info=bits,mailL=bits,mailR=bits,
                          **{f:((1<<17)-1,)*5 for f in ('history1','history2','history3')})
                    got=b.total_rule(cells,beta)
                    captured=[i for i,j in enumerate(b.LANES) if b.capture(stage,j)==b.capture(stage,offset)]
                    mask=sum(1<<i for i in captured)
                    want=(((1<<17)-1)&~mask)|(mask if value else 0)
                    assert getattr(got,field)[q]==want;checks+=1
        for q,s in enumerate(b.SLOTS):
            observer=z-s
            cells={x:b.Cell(addr=(observer+x)%b.Q,age=(32*stage*b.Q-1)%b.U,
                     **{f:((1<<17)-1,)*5 for f in ('history1','history2','history3')}) for x in b.LANES}
            got=b.total_rule(cells,beta)
            for previous in range(stage,3):assert getattr(got,'history'+str(previous+1))[q]==0
            checks+=1
    # Real native-bit seeds from C's captured encoded columns, all five holders.
    work=0
    for k in range(37):
        seed=((mem[b.PRIMARY_START+k]>>3)&2047)<<(11*k);work|=seed
        for q,s in enumerate(b.SLOTS):
            observer=b.PRIMARY_START+k-s
            got=b.total_rule(local_input(observer,-1,b.ZERO,b.COLLECT-1,mem,{}),beta)
            assert b.unpack(got.head[q]).work==seed;checks+=1
    assert b.native_buffer(work)==100|(124<<13)
    for q,s in enumerate(b.SLOTS):
        observer=b.COLLECTOR-s
        got=b.total_rule(local_input(observer,b.COLLECTOR,b.Packet(work=work),b.EVALUATE-1,mem,{}),beta)
        assert got.courierL[q]==0 and got.courierR[q]==0;checks+=1
    for phase in (*range(5),*range(b.Q-5,b.Q)):
        for age in (96*b.Q-1,98*b.Q-2):
            cells={j:b.Cell(addr=(phase+j)%b.Q,age=age) for j in b.LANES}
            got=b.total_rule(cells,beta);assert got.wf1==0 and got.wf2==0;checks+=1
    for address in (3,b.Q-3):
        for q,s in enumerate(b.SLOTS):
            cells={j:b.Cell(addr=(address-s+j)%b.Q,age=b.DELIVERY-1,info=(1,)*5) for j in b.LANES}
            got=b.total_rule(cells,beta);assert got.info[q]==0;checks+=1
    return checks

def run(output):
    start=time.monotonic();beta,labels,rows=compile_program();cells=selected_cells();mem=tape(cells)
    # Literal five-holder birth, with actual already captured histories.
    birth=b.Packet(p=1)
    for q,s in enumerate(b.SLOTS):
        lower=local_input(b.PRIMARY_START-s,-1,b.ZERO,112*b.Q,mem,{})
        r=b.total_rule(lower,beta)
        assert r.head[q]==b.pack(birth)
    p=birth;position=b.PRIMARY_START;out={};first_wrong=None;control=hashlib.sha256()
    ticks=8*b.Q-2
    for step in range(ticks):
        old_position=position;old=p
        if p.move==1:position+=1
        elif p.move==2:position-=1
        assert b.PRIMARY_START-8<=position<b.PRIMARY_START+b.FRAME_BITS+80
        current_age=112*b.Q+1+step
        actual=b.total_rule(local_input(position,old_position,old,current_age,mem,out),beta)
        expected,write=b.cpu(old,position,mem[position],beta)
        assert actual.head==tuple(b.pack(expected) if s==0 else 0 for s in b.SLOTS),(step,'head')
        wanted=tuple(write if s==0 and write is not None else out.get(position+s,0) for s in b.SLOTS)
        assert actual.next==wanted,(step,'Next')
        assert (actual.addr,actual.age,actual.f1,actual.f2,actual.wf1,actual.wf2)==(position%b.Q,(current_age+1)%b.U,0,0,0,0)
        control.update(position.to_bytes(2,'little')+old.pc.to_bytes(3,'little')+
          bytes((old.mode,old.kind,old.index,old.move)))
        p=expected
        if write is not None:out[position]=write
    expected_cell=b.total_rule(cells,beta);expected_bits=b.encode_cell(expected_cell)
    bits=tuple(out.get(b.PRIMARY_START+k,0) for k in range(b.FRAME_BITS));wrong=[k for k,v in enumerate(expected_bits) if bits[k]!=v]
    assert all(b.PRIMARY_START<=address<b.PRIMARY_START+b.FRAME_BITS for address in out)
    assert wrong[0]==324 and len(wrong)==1887
    actual_cell=decode(bits)
    assert tuple(b.unpack(h).p for h in actual_cell.head)==(1,1,0,0,0)
    assert actual_cell.addr==100 and actual_cell.age==124 and all(getattr(actual_cell,f)==0 for f in ('f1','f2','wf1','wf2'))
    # Rest suppresses migration/execution even if the held packet move is1.
    # Next stays fixed and commit uses the OLD Next before resetting it.
    for age in (120*b.Q-1,127*b.Q,b.U-1):
        lower=local_input(position,position,p,age,mem,out);r=b.total_rule(lower,beta)
        if age<b.U-1:
            assert r.head[0]==b.pack(p);assert r.next[0]==out.get(position,0)
        else:assert r.info[0]==out.get(position,0) and r.head[0]==0 and r.next[0]==0
    result={'passed':True,'scope':'EXACT selected globally encoded clean-period deadline failure of GBP1R only',
      'Q':b.Q,'U':b.U,'lambda':b.LAMBDA,'c':b.ERROR_SEPARATION,'physical_fault_support':[],
      'K':b.FRAME_BITS,'ROM_bits':b.CODE_BITS,'emitted_bits':sum(x[3] for x in rows),
      'active_execution_ticks':ticks,'literal_total_R_active_checks':ticks,'literal_birth_holder_checks':5,
      'native_phases_checked':native_closure(),'gather_reset_seed_delivery_source_checks':gather_and_source_checks(beta,mem),'cutoff_wrong_bits':wrong,
      'actual_decoded_C_100':asdict(actual_cell),'desired_successor_C_100':asdict(expected_cell),
      'output_write_address_bounds':[min(out),max(out)],'unrepresented_next_stays_zero':True,
      'source_C_neighborhood':{str(j):asdict(c) for j,c in cells.items()},
      'cutoff_raw_record':''.join(map(str,bits)),'control_trace_sha256':control.hexdigest(),
      'beta_sha256':hashlib.sha256(bytes(beta)).hexdigest(),'elapsed_seconds':time.monotonic()-start,
      'full_R_period_identity_for_selected_E_C_false':True,
      'universal_compiler_equivalence':False,'Q_beta_fit':False,'intact_recursive_start':False,
      'gray_counterexample':False,'iid_failure':False,'shorter_U_proved':False}
    output.write_text(json.dumps(result,indent=2)+'\n');return result

if __name__=='__main__':
    a=argparse.ArgumentParser();a.add_argument('--output',type=Path,required=True);args=a.parse_args()
    r=run(args.output);print(json.dumps({k:v for k,v in r.items() if k not in ('actual_decoded_C_100','desired_successor_C_100','source_C_neighborhood','cutoff_raw_record','cutoff_wrong_bits')},sort_keys=True))
