"""GBD4 actual native listing, literal raw-holder checks and cost contracts.

The universal argument is the written loop/register proof. These receipts
replay its finite structural/algebra checks plus selected complete literal
executions; the executions are not represented as exhaustive raw testing.
"""
import argparse,hashlib,json,random,sys,time
from itertools import product
from pathlib import Path
from dataclasses import replace
import controller as c
import layout as l
import native_emitter as n
import execution as e
import cost_contract as cost

ROOT=Path(__file__).resolve().parents[4]
sys.path.insert(0,str(ROOT))
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from gacsca.maintenance import maintenance_scalar
import literal_maintenance as printed

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def record(cell,extra=0):
    return sum(cell[name]<<bit for name,bit in
           (('addr',0),('age',13),('f1',33),('f2',34),('wf1',35),('wf2',36)))|(extra<<37)
def unpack(records):
    return {j:dict(addr=records[j]&8191,age=(records[j]>>13)&c.MASK,
         f1=(records[j]>>33)&1,f2=(records[j]>>34)&1,
         wf1=(records[j]>>35)&1,wf2=(records[j]>>36)&1) for j in range(-5,6)}

def partitions(n):
    if not n:yield ();return
    for p in partitions(n-1):
        for v in range(max(p,default=-1)+2):yield p+(v,)

def contracts():
    # Equality-only loop is invariant under every injective relabeling;
    # Bell(5)=52 partitions exhaust its word-equality decisions.
    labels=list(partitions(5));assert len(labels)==52
    comparisons=0
    for p in labels:
        for fallback in range(max(p)+2):
            candidate=None
            for v in p:
                if sum(v==w for w in p)>=3:candidate=v;break
            want=fallback if candidate is None else candidate
            assert c.equal_quorum(p,fallback)==want
            comparisons+=1
    # Saved link13 + index3 + count3 occupy19 actual register bits.
    packed_checks=0
    for link in (0,1,4095,8191):
        for candidate in range(5):
            for matches in range(6):
                z=(link<<6)|candidate|(matches<<3)
                assert z<c.MASK+1 and (z>>6)==link and (z&7)==candidate
                assert ((z>>3)&7)==matches
                assert ((z&(c.MASK^56))&63)==candidate
                packed_checks+=1
    # Exact printed/h1 healthy erasure predicates on all five-left
    # eligibility and flag assignments, with both current Flag1 values.
    flag_checks=0;printed_h1_differences=0
    for inside in product((0,1),repeat=5):
        for flags in product((0,1),repeat=5):
            m=sum(a*b for a,b in zip(inside,flags));eligible=sum(inside)
            ordinary=sum(flags)
            for f1 in (0,1):
                literal=(not f1 and all(not a or b for a,b in zip(inside,flags))) or (f1 and not any(flags))
                healthy=(not f1 and m<=1) or (f1 and not any(flags))
                assert literal==((m==eligible) if not f1 else ordinary==0)
                assert healthy==((m<=1) if not f1 else ordinary==0)
                printed_h1_differences+=literal!=healthy;flag_checks+=1
    # Four nibbles sum up to11 each. No arithmetic carries can enter
    # an adjacent counter field or overflow the Word20 accumulator.
    counter_checks=0
    for counts in product(range(12),repeat=4):
        z=sum(value<<(4*i) for i,value in enumerate(counts))
        assert z<1<<16
        for i,value in enumerate(counts):assert ((z>>(4*i))&15)==value
        counter_checks+=1
    return dict(equality_partitions=52,quorum_relabeling_checks=comparisons,
        packed_link_checks=packed_checks,Flag2_predicate_checks=flag_checks,
        printed_h1_predicate_differences=printed_h1_differences,
        packed_counter_checks=counter_checks)

def reader_checks():
    rng=random.Random(492384);checks=0;maximum=0
    # New mutable-Out selector really reads independent physical raw
    # slots, not a virtual RAM word. Invalid lanes/descriptors return0.
    for phase in range(20):
        for stride in (1,5):
            for count in (0,1,4,16,20):
                raw={x:c.Cell(addr=rng.randrange(c.Q),age=rng.randrange(c.U),
                     head=tuple(rng.getrandbits(204) for _ in range(5)),
                     mem=tuple(rng.getrandbits(340) for _ in range(5)),
                     out=tuple(rng.getrandbits(20) for _ in range(5))) for x in range(-10,11)}
                for q,s in enumerate(c.S):
                    values=[]
                    for i in range(count):
                        chunk,bit=divmod(phase+stride*i,20);y=s-2+chunk
                        holder_bits=[(raw[y+d].out[c.INV[h]]>>bit)&1 for h,d in enumerate(c.S)]
                        values.append(int(sum(holder_bits)>=3))
                    want=sum(v<<i for i,v in enumerate(values))
                    assert c.read(raw,0,q,0,phase,stride,count,False,1)==want
                    assert c.read(raw,0,q,1,phase,stride,count,False,1)==0
                    for i in range(count):
                        chunk=(phase+stride*i)//20
                        maximum=max(maximum,max(abs(s-2+chunk+d) for d in c.S))
                    checks+=2
    assert maximum==7
    invalid=0
    raw={x:c.Cell(out=(c.MASK,)*5) for x in range(-8,9)}
    for q in range(5):
        for lane,phase,stride,count in ((1,0,1,20),(0,20,1,20),(0,0,1,21),(0,0,2,20)):
            assert c.read(raw,0,q,lane,phase,stride,count,False,1)==0;invalid+=1
    return dict(actual_raw_holder_checks=checks,invalid_descriptor_checks=invalid,
                exact_READ_bank_source_radius=maximum)

def cases():
    rng=random.Random(731044)
    rows=[]
    for a,t in ((0,0),(1,15),(4,c.MASK),(5,c.MASK-1),(8188,15),(8191,c.MASK)):
        cells={j:dict(addr=(a+j)%c.Q,age=t,f1=rng.randrange(2),f2=rng.randrange(2),
                     wf1=rng.randrange(2),wf2=rng.randrange(2)) for j in range(-8,9)}
        rows.append((f'canonical{a}_Age{t}',cells))
    rows.append(('allzero',{j:dict(addr=0,age=0,f1=0,f2=0,wf1=0,wf2=0) for j in range(-8,9)}))
    for case in range(3):
        cells={j:dict(addr=rng.randrange(c.Q),age=rng.randrange(c.U),
             f1=rng.randrange(2),f2=rng.randrange(2),wf1=rng.randrange(2),wf2=rng.randrange(2))
             for j in range(-8,9)}
        if case==1:
            for j in (3,4,5):cells[j]['addr']=(17+j)%c.Q;cells[j]['age']=c.MASK
            for j in (-5,-4,-3):cells[j]['addr']=(29+j)%c.Q;cells[j]['age']=15
        rows.append((f'arbitrary{case}',cells))
    return [(name,{j:record(cell,rng.getrandbits(l.K-37)) for j,cell in cells.items()},
            tuple(rng.getrandbits(20) for _ in range(8)),rng.randrange(c.Q))
             for name,cells in rows]

def main(out):
    started=time.monotonic();out=out.resolve();out.mkdir(parents=True,exist_ok=True)
    structure={};traces=[]
    for is_printed in (False,True):
        p=n.native_program(is_printed);key='printed' if is_printed else 'h1'
        assert p['bits']==(7106 if is_printed else 7051)
        assert len(p['rows'])==(411 if is_printed else 408)
        assert not p['invalid_targets'] and len(p['beta'])<=c.Q
        decoded=[c.instruction(p['beta'],pc) for pc in p['positions'][:-1]]
        assert [name for name,args,width in decoded]==[r[0] for r in p['rows']]
        assert all(width==p['positions'][i+1]-p['positions'][i] for i,(_,_,width) in enumerate(decoded))
        (out/f'GBD4_{key}_beta.bits').write_text(''.join(map(str,p['beta']))+'\n')
        listing={k:v for k,v in p.items() if k!='beta'}
        (out/f'GBD4_{key}_listing.json').write_text(json.dumps(listing,indent=2)+'\n')
        b=cost.bound(p);assert b['total_updates']==33937<8*c.Q-1
        structure[key]=dict(code_bits=p['bits'],instructions=len(p['rows']),labels=p['labels'],
             invalid_targets=p['invalid_targets'],universal_cost=b,
             accounting_remainder=c.Q-p['bits'],full_own_beta=False)
        for index,(name,records,regs,ret) in enumerate(cases()):
            print(key,name,flush=True)
            got=e.run(p,records,regs,ret,physical_every=127 if index==0 else 0)
            want=(printed.scalar(unpack(records)) if is_printed else maintenance_scalar(unpack(records),c.Q,c.U))
            want.pop('age_now')
            assert got['result']==want,(key,name,got['result'],want)
            assert got['ticks']<=b['total_updates']
            assert got['Head_range'][0]>=l.P+2 and got['Head_range'][1]<=n.RAM_BASE+11
            entry=dict(name=name,variant=key,raw_upper_records={str(j):z for j,z in records.items()},
                 initial_registers=list(regs),initial_link=ret,expected=want,execution=got)
            path=out/f'GBD4_{key}_{name}_execution.json'
            path.write_text(json.dumps(entry,indent=2)+'\n')
            traces.append(dict(name=name,variant=key,ticks=got['ticks'],
                    role_checks=got['raw_role_checks'],path=path.name,sha256=sha(path)))
    cert=dict(schema='GBD4 counted native-only software component v1',Q=c.Q,U=c.U,lambda_=24,c=104,
        layout=dict(K=l.K,P=l.P,Head_bits=c.HEAD_BITS,Scratch_Out_coordinates=[n.RAM_BASE+i for i in n.RAM.values()],
                    Scratch_Out_positions=9,Scratch_interval_inclusive=[n.RAM_BASE,n.RAM_BASE+9],
                    unused_Scratch_coordinate=n.RAM_BASE+8),
        ISA_departure=dict(READ_bits=18,bank_selector_bits=1,mutable_Out_source=True,
                           immutable_beta=True,stored_dictionary_bits=0),
        programmes=structure,contracts=contracts(),raw_reader=reader_checks(),complete_selected_runs=traces,
        universal_native_equivalence_by_written_loop_contract=True,universal_native_runtime=33937,
        raw_upper_native_range=dict(GF=[0,8191],Age=[0,1048575],flags=[0,1]),
        lower_coherent_quiet_ports_and_prepared_Mem_required=True,
        autonomous_native_ports=False,authentic_gather_origin=False,full_own_beta=False,
        full_rule=False,full_period=False,noise_theorem=False,Gray_refutation=False,shorter_U=False,
        elapsed=time.monotonic()-started)
    # Elapsed duration is printed, not part of the reproducible receipt.
    elapsed=cert.pop('elapsed')
    target=out/'GBD4_certificate.json';target.write_text(json.dumps(cert,indent=2)+'\n')
    print(json.dumps(dict(passed=True,elapsed=elapsed,certificate_sha256=sha(target))),flush=True)

if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('--out',type=Path,required=True)
    main(parser.parse_args().out)
