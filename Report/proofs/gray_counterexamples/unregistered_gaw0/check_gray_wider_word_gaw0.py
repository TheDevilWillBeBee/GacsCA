#!/usr/bin/env python3
"""Full GAW0 emission, explicit larger-ROM semantic/runtime diagnostics.

Finite all-field comparisons are measurements, not universal identity.
Q-bit and512-word storage failures are exact emission statements.
"""
from pathlib import Path
import hashlib,json,random,time,types
from dataclasses import replace
import gray_wider_word_gaw0 as k
import build_gray_wider_word_gaw0 as builder
ROOT=Path(__file__).resolve().parents[4]
D=ROOT/'figs/gray_counterexamples/unregistered_gaw0'

def digest(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def instance():
    engine=types.SimpleNamespace(**{n:getattr(k,n) for n in dir(k) if not n.startswith('__')})
    engine.TOKEN_BITS=10;engine.DICTIONARY_SIZE=1024
    rom,listing,labels,errors=builder.programme(engine=engine).assemble()
    assert not errors and len(rom.bits)<=32768
    rom=replace(rom,bits=rom.bits+(0,)*(32768-len(rom.bits)))
    return rom,listing,labels

def fixture(name,age,rom,seed=11,address=4000,dense=False,head=None):
    rng=random.Random(seed);cells={}
    for j in range(-8,9):
        native=dict(addr=(address+j)%k.Q,age=age,f1=0,f2=0,wf1=0,wf2=0)
        if dense:
            words=[rng.getrandbits(100) for _ in range(k.FRAME_WORDS)]
            for i,n in enumerate(k.NATIVE_NAMES):words[i]=native[n]
            c=k.cell_from_words(words)
        else:c=k.Cell(**native)
        if head is not None:c=replace(c,heads=(k.pack(head),)*5)
        cells[j]=c
    return name,cells

def fixtures(rom,labels):
    cases=[]
    rng=random.Random(91028)
    for trial in range(24):
        age=rng.randrange(k.U)
        name,cells=fixture('arbitrary_'+str(trial),age,rom,seed=trial+991,dense=True)
        cells={j:replace(c,addr=rng.randrange(k.Q),age=rng.randrange(k.U),f1=rng.randrange(2),f2=rng.randrange(2),wf1=rng.randrange(2),wf2=rng.randrange(2)) for j,c in cells.items()}
        cases.append((name,cells))
    for age in (0,31*k.Q,32*k.Q-1,32*k.Q,32*k.Q+k.Q-1,40*k.Q-1,
        42*k.Q-1,42*k.Q,42*k.Q+1,42*k.Q+2,74*k.Q,75*k.Q-1,75*k.Q,
        75*k.Q+1,80*k.Q-2,80*k.Q-1,96*k.Q,98*k.Q-1,98*k.Q,112*k.Q,
        112*k.Q+1,112*k.Q+2,120*k.Q-1,120*k.Q,k.U-1):
        cases.append(fixture('clock_'+str(age),age,rom,dense=True))
    for address in (0,1,2,3,4,k.Q-5,k.Q-4,k.Q-3,k.Q-2,k.Q-1):
        cases.append(fixture('WS_'+str(address),96*k.Q,rom,address=address,dense=True))
        for sourceage in (k.U-1,80*k.Q-2):
            name,cells=fixture('WS_source_'+str(address)+'_'+str(sourceage),96*k.Q,rom,address=address,dense=True)
            src=k.Q-3-address if address>=k.Q-5 else 3-address
            for j in range(src-5,src+6):cells[j]=replace(cells[j],age=sourceage)
            cases.append((name,cells))
    for side in ('LEFT','RIGHT'):
        address=3 if side=='LEFT' else k.Q-3
        cases.append(fixture('special_'+side,80*k.Q-1,rom,address=address,dense=True))
    for opcode in k.OP_NAMES:
        index=next(row['address'] for row in LISTING if row['opcode']==opcode)
        p=k.Packet(p=1,mode=k.RUN,pc=index,regs=tuple([0]*16))
        cases.append(fixture('virtual_'+opcode,112*k.Q+2,rom,dense=True,head=p))
    for kind in range(4):
        for lane in (0,5,8,11,16,17,31):
            p=k.Packet(p=1,mode=k.SEEK,target=4000,args=k.descriptor(kind,dst=2,lane=lane,source=0,side=1))
            cases.append(fixture('IO_'+str(kind)+'_'+str(lane),112*k.Q+2,rom,address=4000,dense=True,head=p))
    return cases

LISTING=[]
def main():
    global LISTING
    start=time.monotonic();D.mkdir(parents=True,exist_ok=True)
    base,listing,labels,errors=builder.programme().assemble()
    baseline=dict(tokens=base.token_count,beta_bits=base.token_count*9,used_dictionary=base.used_dictionary,
        required_dictionary_token_bits=(base.used_dictionary-1).bit_length(),errors=errors,
        Q_bit_fit=base.token_count*9<=8192,dictionary512_fit=base.used_dictionary<=512)
    rom,LISTING,labels=instance()
    for row in LISTING:
        expected=(row['opcode'],tuple(v&((1<<w)-1) for v,w in zip(row['operands'],k.ARGS[row['opcode']])))
        assert k.decode(k.beta_word(rom,row['address']))==expected
    (D/'GAW0D_rom.json').write_text(json.dumps(dict(bits=list(rom.bits),dictionary=[hex(v) for v in rom.dictionary],
        token_bits=rom.token_bits,token_count=rom.token_count,used_dictionary=rom.used_dictionary),separators=(',',':'))+'\n')
    (D/'GAW0D_listing.json').write_text(json.dumps(dict(instructions=LISTING,labels=labels),separators=(',',':'))+'\n')
    records=[]
    for name,cells in fixtures(rom,labels):
        expected=k.cell_words(k.local_transition(cells,rom))
        out,ticks,last,trace=k.execute(rom,k.input_tape(cells),limit=300000,record=True)
        actual=[out.get(k.PRIMARY_START+i,0) for i in range(k.FRAME_WORDS)]
        record=dict(name=name,ticks=ticks,halted=last.mode==k.HALT,inputs=[[hex(v) for v in k.cell_words(cells[j])] for j in range(-8,9)],
            expected=[hex(v) for v in expected],actual=[hex(v) for v in actual],wrong_words=[i for i,(x,y) in enumerate(zip(actual,expected)) if x!=y],
            min_head_address=min(x[0] for x in trace),max_head_address=max(x[0] for x in trace))
        if actual!=expected or last.mode!=k.HALT:
            stem='GAW0D_semantics_failure_%02d'%len(records)
            (D/(stem+'.json')).write_text(json.dumps(record,indent=2)+'\n')
            for source in (Path(k.__file__),Path(builder.__file__),Path(__file__)):
                (D/(stem+'_'+source.name+'.txt')).write_bytes(source.read_bytes())
            raise AssertionError(stem+' '+name+' '+str(record['wrong_words']))
        if not records or ticks>max(r['ticks'] for r in records):print(name,ticks,flush=True)
        records.append(record)
    (D/'GAW0D_prepared_replays.json').write_text(json.dumps(records,separators=(',',':'))+'\n')
    receipt=dict(name='GAW0 complete wider word-rule emission; larger-ROM prepared measurements',Q=k.Q,U=k.U,
        lambda_original=24,c_original=104,baseline=baseline,diagnostic=dict(token_bits=10,ROM_bits=32768,dictionary_words=1024,
        dictionary_bits=102400,total_immutable_capacity_bits=135168,used_token_bits=rom.token_count*10,
        used_dictionary_words=rom.used_dictionary),frame_words=k.FRAME_WORDS,frame_start=k.PRIMARY_START,
        raw_state_bits=37+5*k.HEAD_BITS+5*17*k.WORD+6*5*k.WORD,
        complete_total_autonomous_rule_defined=True,full_own_programme_emitted=True,
        all_raw_own_programme_equivalence_proved=False,prepared_comparisons_measured_only=True,
        min_ticks=min(r['ticks'] for r in records),max_ticks=max(r['ticks'] for r in records),prepared_cases=len(records),
        fifth_usable_ticks=8*k.Q-1,early_usable_ticks=33*k.Q-2,
        radius8_and17_lanes_and_FULLCOL_and_single_snapshot_and_early42Q_and_extra_dictionary_changes=True,
        full_noiseless_period_or_Gray_faithfulness_or_iid_or_shorter_U=False,active_rule_modified=False,
        sources_sha256={p.name:digest(p) for p in (Path(k.__file__),Path(builder.__file__),Path(__file__))},
        assets_sha256={p.name:digest(p) for p in (D/'GAW0D_rom.json',D/'GAW0D_listing.json',D/'GAW0D_prepared_replays.json')},
        elapsed_seconds=time.monotonic()-start)
    (D/'GAW0_complete_emission_certificate.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(dict(baseline=baseline,diagnostic_cases=len(records),max_ticks=receipt['max_ticks'],elapsed=receipt['elapsed_seconds'])))

if __name__=='__main__':main()
