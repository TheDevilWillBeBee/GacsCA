"""Semantics diagnostic for the complete GBC4 structural listing.

NOT theQ-bit rule: instruction dispatch is a separate finite table at
the exact emitted bit addresses (wide branches), while CODE still reads
the stipulatedQ-bit target programme. This explicitly changed diagnostic
tests real generic opcode/IO/travel behaviour, not own beta/selfidentity.
No wrapped out-of-Q branch is ever executed as if it were validQ code.
"""
from dataclasses import asdict,replace
from hashlib import sha256
from pathlib import Path
import inspect,json,argparse,time
import compact_completion_rule as b
import complete_branch_emitter as e
from check_early_stage_emission import case_cells


def make_machine(listing):
    table={pc:(name,tuple(args),length) for pc,name,args,length in listing}
    limit=max(pc+n for pc,_,_,n in listing)
    def instruction_at(pc):
        return table.get(pc)
    def continuation(p,pc):
        return b.fail(p) if not 0<=pc<limit else replace(p,pc=pc,mode=b.RUN,move=0)
    original=inspect.getsource(b.cpu)
    source=original.replace('def cpu(', 'def diagnostic_cpu(',1)
    assert source.count('decoded=decode(beta,p.pc)')==1
    source=source.replace('decoded=decode(beta,p.pc)','decoded=instruction_at(p.pc)')
    assert source.count('nextpc>=Q')==5
    source=source.replace('nextpc>=Q','nextpc>=LISTING_LIMIT')
    scope=dict(vars(b));scope.update(instruction_at=instruction_at,
                                     continue_pc=continuation,LISTING_LIMIT=limit)
    exec(compile(source,'<explicit separate-listing diagnostic>','exec'),scope)
    return scope['diagnostic_cpu'],{'instruction_table_limit':limit,
             'original_cpu_sha256':sha256(original.encode()).hexdigest(),
             'diagnostic_cpu_source_sha256':sha256(source.encode()).hexdigest(),
             'changes':['separate finite instruction table with wide physical PC/ret',
                        'target CODE remainsQ-bit immutable programme',
                        'prepared physical continuation uses listing-size bound'],
             'own_programme_test':False}


def execute(cells,beta,listing,max_updates=1000000):
    cpu,identity=make_machine(listing)
    encoded={j:b.encode_cell(c) for j,c in cells.items()}
    desired=b.encode_cell(b.total_rule(cells,beta))
    def tape(a):
        if not 0<=a<b.Q:return 0
        if not b.PRIMARY_START<=a<b.PRIMARY_START+b.FRAME_BITS:return 0
        bit=a-b.PRIMARY_START
        return sum(encoded[j][bit]<<lane for lane,j in enumerate(b.LANES))
    p,position=b.Packet(p=1),b.PRIMARY_START
    writes={};digest=sha256();counts={}
    for tick in range(1,max_updates+1):
        position+=1 if p.move==1 else -1 if p.move==2 else 0
        assert 0<=position<b.Q,(tick,position,asdict(p))
        old=p
        p,bit=cpu(p,position,{d:tape(position+d) for d in range(-4,5)},beta)
        if old.mode==b.RUN:
            row=next(x for x in listing if x[0]==old.pc)
            counts[row[1]]=counts.get(row[1],0)+1
        digest.update(json.dumps((tick,position,asdict(p),bit),sort_keys=True).encode())
        if p.mode==b.ERROR:
            return {'passed':False,'failure':'diagnostic lowerCPU ERROR',
                    'tick':tick,'position':position,'packet':asdict(p),
                    'previous_packet':asdict(old),'identity':identity}
        if bit is not None:writes[position]=bit
        if p.mode==b.HALT:break
    else:
        return {'passed':False,'failure':'diagnostic max_updates',
                'updates':max_updates,'position':position,'packet':asdict(p),
                'identity':identity}
    actual=tuple(writes.get(a,0) for a in range(b.PRIMARY_START,b.PRIMARY_START+b.FRAME_BITS))
    wrong=[i for i,(u,v) in enumerate(zip(actual,desired)) if u!=v]
    return {'passed':not wrong and len(writes)==b.FRAME_BITS,
            'input_cells':{str(j):asdict(c) for j,c in cells.items()},
            'target_beta_sha256':sha256(bytes(beta)).hexdigest(),
            'computed_native':b.native_at(cells,0),'updates':tick,
            'actual_output_bits':''.join(map(str,actual)),
            'desired_output_bits':''.join(map(str,desired)),
            'wrong_raw_bits':wrong,'unique_written_columns':len(writes),
            'trace_sha256':digest.hexdigest(),'opcode_counts':counts,
            'identity':identity}


def with_packet(cells,logical,packet):
    cells=dict(cells);word=b.pack(packet)
    for q,s in enumerate(b.SLOTS):
        j=logical-s;parts=list(cells[j].head);parts[q]=word
        cells[j]=replace(cells[j],head=tuple(parts))
    return cells


def target_programme(name,args=(),at=31):
    bits=list(b.encode(name,*args));beta=[0]*b.Q
    beta[at:at+len(bits)]=bits
    return tuple(beta),at


def run(output,caseset):
    start=time.monotonic();r=e.emit_complete_structural_listing()
    listing=r['listing'];cases=[]
    if caseset=='stages':
        phases=(0,b.COLLECT,b.COLLECT+1,b.EVALUATE-1,b.EVALUATE,
                b.EVALUATE+1,b.DELIVERY,96*b.Q,96*b.Q+1,
                98*b.Q-1,98*b.Q,112*b.Q,112*b.Q+1,120*b.Q)
        for phi in phases:
            # Coherentzero heads keep staged mutableWork path controlled;
            # arbitrary remainingSF still pass actual storage/defaults.
            cells={j:replace(c,head=(0,)*5) for j,c in case_cells(phi).items()}
            rr=execute(cells,(0,)*b.Q,listing)
            cases.append({'case':'stage','phi':phi,**rr})
            print(json.dumps({'case':'stage','phi':phi,'passed':rr['passed'],
                              'updates':rr.get('updates'),'wrong':rr.get('wrong_raw_bits',[])[:10]}),flush=True)
            if not rr['passed']:break
    else:
        tests=[('HLT',()),('LIT',(b.MASK,)),('SWAP',()),('ALU',(16,)),
               ('ALU',(31,)),('SETFN',()),('BR',(3,77)),('JMP',()),
               ('READ',(0,0)),('READ',(1,16)),('READ',(2,0)),
               ('READ',(3,0,1)),('WRITE',()),('WGET',(31,)),
               ('WSET',(31,)),('NATIVE',()),('NCGET',()),('CODE',()),
               ('STREAM',(1,1,0)),('SELF',(14,)),('ALUI',(b.ALU['div'],0)),
               ('PUSH',(20,)),('PUSH',(29,)),('FILL',(1,1)),
               ('PUTWORD',(13,1)),('PUTWORD',(0,0)),('PUTWORD',(31,1)),('CALL',(77,0)),('RETURN',(1,))]
        if caseset=='one':tests=tests[:1]
        for name,args in tests:
            beta,pc=target_programme(name,args)
            cells={j:replace(c,head=(0,)*5) for j,c in case_cells(112*b.Q+2).items()}
            packet=b.Packet(p=1,pc=pc,a=13,b=17,fn=9,
                            work=int.from_bytes(sha256(b'rawwork').digest(),'little'),
                            nc=(1<<35)-1)
            cells=with_packet(cells,0,packet)
            rr=execute(cells,beta,listing)
            cases.append({'case':'run','name':name,'args':args,**rr})
            print(json.dumps({'case':name,'passed':rr['passed'],
                              'updates':rr.get('updates'),'wrong':rr.get('wrong_raw_bits',[])[:10]}),flush=True)
            if not rr['passed']:break
    result={'passed':all(c['passed'] for c in cases),'Q':b.Q,'U':b.U,
            'lambda':24,'c':104,'scope':'separate-listing diagnostic; notQ-bit ownbeta',
            'programme_bits':r['programme_bits'],'instructions':r['instructions'],
            'out_of_Q_references':len(r['invalid_references']),
            'sources':{str(p):sha256(p.read_bytes()).hexdigest() for p in
                       (Path(e.__file__),Path(b.__file__),Path(__file__))},
            'cases':cases,'universal_raw_equivalence':False,'whole_own_beta':False,
            'physical_period':False,'gray_refutation':False,'iid_failure':False,
            'elapsed_seconds':time.monotonic()-start}
    output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='cases'},indent=2))
    return result['passed']


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True)
    p.add_argument('--cases',choices=('one','stages','run'),default='one')
    a=p.parse_args();raise SystemExit(0 if run(a.output,a.cases) else 1)
