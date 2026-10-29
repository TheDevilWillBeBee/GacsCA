"""Literal helper algebra, relocation, CFG cost and selected own-ROM replay.

Bit-mask exhaustion checks finite transcription; word quantification is
the independent-bit induction stated in the companion proof.
"""
from pathlib import Path
from dataclasses import asdict
import hashlib,json,sys,time
HERE=Path(__file__).resolve().parent;ROOT=HERE.parents[3]
sys.path[:0]=[str(HERE),str(HERE.parent/'unregistered_gawn0')]
import build_unrolled_gawn1 as b
import unrolled_gawn1 as k
import gawn1_compositional_cost as cost
import probe_normalized_gawn0 as prior_probe
OUT=ROOT/'figs/gray_counterexamples/unregistered_gawn1'

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def structural(rom,listing,labels,a):
    old=a.previous_normalized_rows
    start=a.helper_start_row;end=start+len(a.old_helper_rows)
    assert a.rows==old[:start]+b.helper()+old[end:]
    assert tuple(k.SLOTS)==(0,-2,-1,1,2)
    lo=labels['vote'];hi=labels['slots']
    rows=[r for r in listing if lo<=r['address']<hi]
    assert len(rows)==37
    assert sum(r['opcode']=='LDX' for r in rows)==5
    assert [r['operands'] for r in rows if r['opcode']=='LDX']==[[0,k.PRIMARY_START,11,6,0]]*5
    assert all(r['opcode'] not in ('CODE','STX','BNZ','JMP','READ5','READMASK','FULLCOL') for r in rows)
    assert sum(r['opcode']=='JMPR' for r in rows)==1 and rows[-1]['opcode']=='JMPR'
    assert all(row['address']<lo or row['address']>=hi for row in listing if row['opcode']=='STX')
    assert len(rom.bits)==65536 and len(rom.dictionary)==2048
    assert json.loads((OUT/'GAWN1_rom.json').read_text())==json.loads(json.dumps(asdict(rom)))
    assert json.loads((OUT/'GAWN1_listing.json').read_text())==dict(listing=listing,labels=labels)
    # All entries/branches into the changed block use its declared entry only.
    for name,pc in labels.items():
        if lo<=pc<hi:assert name in ('vote','vote_loop') and pc==lo
    for row in listing:
        if row['opcode']=='BNZ':assert not lo<=row['operands'][1]<hi
        if row['opcode']=='JMP' and lo<=row['operands'][0]<hi:assert row['operands'][0]==lo
    return dict(only_previous_helper_block_replaced_modulo_PC_relocation=True,
        actual_existing_ISA_instructions=37,actual_full_Word100_mem_reads=5,
        branchless_no_store_no_new_primitive=True,all_old_other_unresolved_rows_preserved=True,
        all_helper_call_targets_entry_only=True,all_normalization_masks_preserved=True)

def helper_replay(rom,labels):
    cases=[];full_words=0
    for bits in range(32):
        for centre in range(2,15):
            words=[(k.MASK if bits>>i&1 else 0) for i in range(5)]
            full_words+=1;field=6 if bits%2 else k.FRAME_WORDS-5
            initial=tuple((1<<90)+17*q for q in range(16))
            r=list(initial);r[11]=field;r[12]=centre;r[15]=0
            p=k.Packet(p=1,pc=labels['vote'],regs=tuple(r));position=k.PRIMARY_START+field
            tape={k.PRIMARY_START+field+i:words[i]<<((centre-slot)*k.WORD) for i,slot in enumerate(k.SLOTS)}
            instructions=0;steps=0
            while True:
                oldp=p;position+=1 if p.move==1 else -1 if p.move==2 else 0
                p,ow,sw=k.step_packet(p,position,tape.get(position,0),0,0,k.beta_bit(rom,position),rom)
                assert ow is None and sw is None and p.mode not in (k.ERROR,k.HALT)
                steps+=1;instructions+=int(oldp.mode==k.RUN)
                if oldp.mode==k.RUN and k.decode(k.beta_word(rom,oldp.pc))[0]=='JMPR':break
                assert steps<=50
            u=v=w=0;last=0
            for word in words:
                w|=v&word;last=u&word;v|=last;u|=word
            expected=list(r)
            for dst,val in ((0,w),(1,last),(3,u),(4,v),(5,w),(6,0),(7,16),(8,5),(11,field+5)):expected[dst]=val
            assert tuple(expected)==p.regs and p.pc==0 and p.mode==k.RUN and p.move==0
            assert instructions==37 and steps==42 and position==k.PRIMARY_START+field+4
            cases.append(dict(bits=bits,centre=centre,field=field,instructions=instructions,updates=steps))
    return dict(cases=cases,all32_bit_masks_all13_safe_centres_both_frame_edges=full_words,
        exact_all16_return_registers_checked=True,all100_bit_positions_by_bitwise_independence_in_written_proof=True)

def cost_replay():
    old=ROOT/'Report/proofs/gray_counterexamples/unregistered_gaw2/gaw2r_compositional_cost.py'
    source=old.read_text().replace('import gray_three_gather_gaw2r as k','import unrolled_gawn1 as k').replace('import build_gray_three_gather_gaw2r as b','import build_unrolled_gawn1 as b').replace("D=R/'figs/gray_counterexamples/unregistered_gaw2'","D=R/'figs/gray_counterexamples/unregistered_gawn1'").replace('cost+=86+first+4','cost+=37+first+4').replace("name='GAW2R compositional CFG/travel bound'","name='GAWN1 compositional CFG/travel bound'").replace("D/'GAW2R_compositional_cost.json'","D/'GAWN1_compositional_cost.json'")
    source=source.replace("    (D/'GAWN1_compositional_cost.json').write_text","    assert not (D/'GAWN1_compositional_cost.json').exists(),'never overwrite frozen cost receipt'\n    (D/'GAWN1_compositional_cost.json').write_text")
    actual=Path(cost.__file__).read_text();assert actual.split('\n',3)[3]==source
    frozen=json.loads((OUT/'GAWN1_compositional_cost.json').read_text())
    records=[cost.run(clock) for clock in frozen['phase_partition'][:-1]]
    assert records==frozen['records'] and max(row['tick_bound'] for row in records)==frozen['maximum_ticks']==104566
    assert len(records)==72 and frozen['available_ticks']==18*k.Q-1
    return dict(all72_phase_classes_recomputed=True,old_cost_source_sha256=sha(old),
        only_import_name_output_guard_and_proved_helper_cost_changes=True,
        full_bound=104566,late_margin=18*k.Q-1-104566,
        fits13Q_minus1=104566<=13*k.Q-1,thirteen_Q_margin=13*k.Q-1-104566,
        smaller_Q_or_U_rule_compiled_or_proved=False)

def compute():
    started=time.monotonic();rom,listing,labels,a=b.instance()
    syntax=structural(rom,listing,labels,a);helper=helper_replay(rom,labels);costs=cost_replay()
    runs=[]
    for kind in ('canonical_padding','no_GF_quorum_padding','commit_padding','active_upper_head_padding'):
        cells=prior_probe.sample_cells(kind);expected=k.cell_words(k.local_transition(cells,rom))
        out,ticks,p,_=k.execute(rom,k.input_tape(cells),limit=104567)
        values=[out.get(k.PRIMARY_START+i,0) for i in range(k.FRAME_WORDS)]
        assert p.mode==k.HALT and values==expected,(kind,ticks,[i for i,(v,w) in enumerate(zip(values,expected)) if v!=w])
        early,eticks,ep,_=k.execute(rom,k.input_tape(cells),limit=216,early=True)
        assert ep.mode==k.HALT and [early.get(k.PRIMARY_START+i,0) for i in range(6)]==expected[:4]+[0,0]
        runs.append(dict(kind=kind,raw_inputs={str(j):[hex(v) for v in k.cell_words(c)] for j,c in cells.items()},
            full_ticks=ticks,full_output=[hex(v) for v in values],early_ticks=eticks,
            early_output=[early.get(k.PRIMARY_START+i,0) for i in range(6)]))
    return dict(explicit_new_own_ROM=True,no_new_physical_ISA_primitive=True,Q=k.Q,U=k.U,
        structural=syntax,helper=helper,cost=costs,selected_whole_own_ROM_executions=runs,
        selected_executions_are_measured_supplements=True,universal_or_iid_proof_inferred_from_samples=False,
        G17_or_old_frozen_rules_modified=False,seconds=time.monotonic()-started)

if __name__=='__main__':
    p=OUT/'unrolled_probe01.json';assert not p.exists(),'never overwrite frozen probe'
    data=compute();p.write_text(json.dumps(data,indent=2)+'\n')
    print(json.dumps(dict(passed=True,helper_cases=len(data['helper']['cases']),full_bound=data['cost']['full_bound'],
        actual_whole_runs=len(data['selected_whole_own_ROM_executions']),seconds=data['seconds'])))
