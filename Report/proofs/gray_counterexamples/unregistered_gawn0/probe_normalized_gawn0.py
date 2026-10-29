"""Structural premises and selected full-word supplements for GAWN0.

Universal quantifiers are supplied by the written projection/period proof.
Selected executions are measured supplements, never a reliability test.
"""
from pathlib import Path
from collections import Counter
from functools import lru_cache
from dataclasses import asdict
import hashlib,json,sys,time
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
sys.path[:0]=[str(HERE),str(HERE.parent/'unregistered_gaw2')]
import build_normalized_gawn0 as builder
import normalized_gawn0 as k
OUT=ROOT/'figs/gray_counterexamples/unregistered_gawn0'

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def row_size(row):
    name,args=row
    return 0 if name=='LABEL' else len(args[0]) if name=='DATA' else 1

def structural(rom,listing,labels,a):
    original=builder.old_builder.programme().rows
    assert a.original_unresolved_rows==original
    extra={m['new_mask_row']:m for m in a.normalization_masks}
    assert [row for i,row in enumerate(a.rows) if i not in extra]==original
    mask_pcs=[];pc=0
    for i,row in enumerate(a.rows):
        if i in extra:
            m=extra[i];d=m['destination_register']
            assert row==('ALUI',(d,k.ALU['AND'],d,(1<<m['width'])-1))
            assert a.rows[i-1][0]=='LDX'
            mask_pcs.append(pc)
        pc+=row_size(row)
    rows={r['address']:r for r in listing}
    def sig(pc):return rows[pc]['opcode'],tuple(rows[pc]['operands'])
    raw_native=[];raw_sf=[];vectors=[];flags=[]
    for pc,row in rows.items():
        name,args=sig(pc)
        if name=='LDX' and args[4]==0:
            assert args[1]==k.PRIMARY_START and args[2]==11
            if args[3]==7:
                assert pc+1 in mask_pcs
                assert sig(pc+1)[0]=='ALUI'
                raw_native.append(pc)
            else:
                assert args[3]==6 and labels['vote_loop']<=pc<labels['early_entry']
                raw_sf.append(pc)
        if name=='READ5':
            assert args[0]==11 and 6<=args[2]<=11
            before=sig(pc-1);assert before[0]=='MOVI' and before[1][0]==11
            field=before[1][1]-k.PRIMARY_START;assert field in (0,1)
            if field==0:
                assert sig(pc+1) in [('MOVI',(1,-1)),('MOVI',(1,1))]
                assert sig(pc+2)==('MOVI',(15,13))
                assert sig(pc+3)==('ALU',(0,k.ALU['VADDINDEX'],0,1,15))
                assert not any(v in range(pc+1,pc+4) for v in labels.values())
            vectors.append(dict(pc=pc,field=field,centre=args[2],side=args[1]))
        if name in ('READMASK','FULLCOL'):
            before=sig(pc-1);assert before[0]=='MOVI' and before[1][0]==9
            field=before[1][1]-k.PRIMARY_START;assert field in (2,3,4,5)
            flags.append(dict(pc=pc,field=field,operation=name))
    assert len(raw_native)==24 and len(raw_sf)==1
    assert len(vectors)==32 and Counter(v['field'] for v in vectors)=={0:16,1:16}
    assert len(flags)==32 and Counter(v['operation'] for v in flags)=={'READMASK':8,'FULLCOL':24}
    assert not any(v in mask_pcs for v in labels.values())
    sys.setrecursionlimit(20000)
    def recent_literal(pc,reg):
        for q in range(pc-1,max(-1,pc-20),-1):
            if q not in rows:continue
            name,args=sig(q)
            if name in builder.WRITES and args and args[0]==reg:
                assert name=='MOVI';return args[1]
        raise AssertionError((pc,reg,'no typed return'))
    def max_masks(start,stop=None):
        visiting=set()
        @lru_cache(None)
        def go(pc):
            if pc==stop:return 0
            assert pc not in visiting,('unexpected native-prefix loop',pc)
            visiting.add(pc);name,args=sig(pc);weight=int(pc in mask_pcs)
            if name=='HLT':result=weight
            else:
                if name=='JMP':dest=[recent_literal(pc,15)] if args[0]==labels['vote'] else [args[0]]
                elif name=='BNZ':dest=[pc+1,args[1]]
                else:
                    assert name!='JMPR';dest=[pc+1]
                result=weight+max(go(q) for q in dest)
            visiting.remove(pc);return result
        return go(start)
    prefix=max_masks(0,labels['main']);early=max_masks(labels['early_entry'])
    main_masks=[pc for pc in mask_pcs if labels['main']<=pc<labels['copy_loop']]
    assert prefix==6 and early==2 and len(main_masks)==1
    assert not any(labels['copy_loop']<=pc<labels['early_entry'] for pc in mask_pcs)
    assert len(rom.bits)==65536 and len(rom.dictionary)==2048
    return dict(unresolved_deletion_recovers_every_original_instruction_and_label=True,
        all_new_listing_ROM_bytes_rebuilt_from_changed_source=True,
        native_direct_load_masks=len(raw_native),Address_masks=16,Age_masks=8,
        sole_remaining_raw_mem_LDX_is_old_SF_vote_helper=raw_sf,
        native_READ5_sites=vectors,lowbit_native_flag_sites=flags,
        no_branch_label_enters_partial_normalization_macro=True,
        maximum_added_full_pass_mask_updates=prefix+len(main_masks),
        maximum_added_early_pass_mask_updates=early,
        all_original_SF_vote_and_generic_instruction_code_preserved_modulo_PC_relocation=True,
        old_legal_compositional_argument_needed_for_whole_evaluator=True)

def sample_cells(kind):
    cells={}
    for j in range(-8,9):
        age=123 if kind in ('canonical_padding','no_GF_quorum_padding') else k.U-1 if kind=='commit_padding' else 102*k.Q+1
        addr=200+(17*j if kind=='no_GF_quorum_padding' else j)
        words=[0]*k.FRAME_WORDS
        words[:6]=[addr,age,1 if kind=='canonical_padding' else 0,0,0,0]
        for field in range(6):
            words[field]|=(1<<(k.NATIVE_WIDTHS[field]+3+(j+8)%4))|(1<<99)
        for name,value in [('info',7),('out',(1<<99)+19),('scratch',(1<<76)+5),('program',(1<<80)+3)]:
            words[k.FIELD[name]:k.FIELD[name]+5]=[value]*5
        if kind=='active_upper_head_padding':
            c=k.cell_from_words(words)
            packet=k.Packet(p=1,move=0,mode=k.RUN,pc=0,regs=tuple((1<<90)+r for r in range(16)))
            c=k.replace(c,heads=(k.pack(packet),)*5)
        else:c=k.cell_from_words(words)
        cells[j]=c
    return cells

def compute():
    start=time.monotonic();rom,listing,labels,a=builder.instance()
    artifact=json.loads((OUT/'GAWN0_rom.json').read_text())
    assert asdict(rom)=={key:tuple(value) if key in ('bits','dictionary') else value for key,value in artifact.items()}
    assert dict(listing=listing,labels=labels)==json.loads((OUT/'GAWN0_listing.json').read_text())
    syntax=structural(rom,listing,labels,a)
    oldcost=json.loads((HERE.parent.parent.parent.parent/'figs/gray_counterexamples/unregistered_gaw2/GAW2R_compositional_cost.json').read_text())
    assert oldcost['maximum_ticks']==141557 and oldcost['available_ticks']==147455
    full_bound=oldcost['maximum_ticks']+syntax['maximum_added_full_pass_mask_updates']
    assert full_bound==141564<18*k.Q-1
    cases=[]
    for kind in ('canonical_padding','no_GF_quorum_padding','commit_padding','active_upper_head_padding'):
        raw=sample_cells(kind);legal=k.project_neighborhood(raw)
        expected=k.cell_words(k.local_transition(raw,rom))
        assert expected==k.cell_words(k.original.local_transition(legal,rom))
        actual_runs=[]
        for cells in (raw,legal):
            out,ticks,packet,_=k.execute(rom,k.input_tape(cells),limit=full_bound+1)
            result=[out.get(k.PRIMARY_START+i,0) for i in range(k.FRAME_WORDS)]
            assert packet.mode==k.HALT and result==expected,(kind,ticks,packet.mode,
                [i for i,(v,w) in enumerate(zip(result,expected)) if v!=w])
            actual_runs.append(dict(ticks=ticks,HALT=True,complete_output=[hex(v) for v in result]))
        assert actual_runs[0]==actual_runs[1]
        early_runs=[]
        for cells in (raw,legal):
            out,ticks,packet,_=k.execute(rom,k.input_tape(cells),limit=215+1,early=True)
            result=[out.get(k.PRIMARY_START+i,0) for i in range(6)]
            assert packet.mode==k.HALT and result==expected[:4]+[0,0]
            early_runs.append(dict(ticks=ticks,HALT=True,complete_native_output=result))
        assert early_runs[0]==early_runs[1]
        cases.append(dict(kind=kind,raw_input_words={str(j):[hex(v) for v in k.cell_words(c)] for j,c in raw.items()},
            projected_native_input={str(j):k.cell_words(c)[:6] for j,c in legal.items()},
            exact_normalized_local_output=[hex(v) for v in expected],actual_full_runs=actual_runs,actual_early_runs=early_runs))
    return dict(Q=k.Q,U=k.U,native_widths=k.NATIVE_WIDTHS,rom_sha256=sha(OUT/'GAWN0_rom.json'),
        listing_sha256=sha(OUT/'GAWN0_listing.json'),probe_sha256=sha(__file__),structural=syntax,
        inherited_full_pass_bound=141557,new_full_pass_bound=full_bound,new_early_pass_bound=215,
        available_late_updates=18*k.Q-1,new_full_pass_margin=18*k.Q-1-full_bound,
        early_birth_to75Q_margin=75*k.Q-(k.EARLY_BIRTH+215),
        selected_cases=cases,selected_full_word_executions_measured_supplements=True,
        universal_projection_execution_period_or_iid_proved_by_samples=False,
        explicit_new_own_ROM_proposal=True,active_G17_or_frozen_GAW2R_modified=False,
        seconds=time.monotonic()-start)

if __name__=='__main__':
    path=OUT/'normalization_probe01.json';assert not path.exists()
    result=compute();path.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(passed=True,mask_sites=result['structural']['native_direct_load_masks'],
        full_bound=result['new_full_pass_bound'],early_bound=result['new_early_pass_bound'],
        measured_pairs=len(result['selected_cases']),seconds=result['seconds'])),flush=True)
