#!/usr/bin/env python3
"""New isolated single-middle-gather emission and prepared comparisons.

This is a changed rule, with the existing extra dictionary/WF0 departures.
The physical snapshot certificate and full-period proof are separate.
"""
from pathlib import Path
import hashlib,json,sys,time
import numpy as np
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT))
import gray_token_gather_v7 as k
import build_gray_token_gather_v7 as builder
import check_gray_token_gather_v7_bound as bound
import check_gray_token_word_v6 as previous


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def cases(rom,listing,labels):
    rows=previous.fixtures(rom,listing,labels)
    # The old fixture generator uses F6 for creating arbitrary legal words.
    # Frame/schema equality permits exact conversion to the NEW cell type.
    rows=[(name,{j:k.cell_from_words(previous.k.cell_words(c)) for j,c in cells.items()}) for name,cells in rows]
    for clock in (31*k.Q,32*k.Q-1,32*k.Q,32*k.Q+k.Q-1,37*k.Q-1,37*k.Q):
        cells=previous.previous.fixture(k,age=clock,seed=71)
        rows.append(('GATHER_CLOCK_'+str(clock),cells))
    return rows


def main():
    start=time.monotonic();directory=ROOT/'figs/gray_counterexamples'
    rom,listing,labels,errors=builder.programme().assemble();assert not errors
    assert rom.token_count*9<=8192 and len(rom.dictionary)==512
    beta=directory/'GMW7_token_beta.bin';beta.write_bytes(np.packbits(np.array(rom.bits,np.uint8),bitorder='little').tobytes())
    dictionary=directory/'GMW7_dictionary.json';dictionary.write_text(json.dumps([hex(v) for v in rom.dictionary],separators=(',',':'))+'\n')
    document=directory/'GMW7_token_listing.json';document.write_text(json.dumps(dict(instructions=listing,labels=labels,errors=errors),separators=(',',':'))+'\n')
    for row in listing:
        args=tuple(v&((1<<w)-1) for v,w in zip(row['operands'],k.ARGS[row['opcode']]))
        assert k.decode(k.beta_word(rom,row['address']))==(row['opcode'],args)
    records=[]
    for name,cells in cases(rom,listing,labels):
        expected=k.cell_words(k.local_transition(cells,rom))
        out,ticks,last,_=k.execute(rom,k.input_tape(cells),limit=65535)
        actual=[out.get(k.PRIMARY_START+i,0) for i in range(k.FRAME_WORDS)]
        if actual!=expected or last.mode!=k.HALT:
            stem='GMW7_execution_failure_01';i=1
            while (directory/(stem+'.json')).exists():
                i+=1;stem='GMW7_execution_failure_%02d'%i
            sources={}
            for p in (Path(k.__file__),Path(builder.__file__),Path(__file__)):
                target=directory/(stem+'_'+p.name+'.txt');target.write_bytes(p.read_bytes());sources[target.name]=digest(target)
            (directory/(stem+'.json')).write_text(json.dumps(dict(name=name,ticks=ticks,
                sources_sha256=sources,pending_packet=hex(k.pack(last)),
                inputs=[[hex(v) for v in k.cell_words(cells[j])] for j in range(-5,6)],
                expected=[hex(v) for v in expected],actual=[hex(v) for v in actual],
                wrong_words=[i for i,(x,y) in enumerate(zip(actual,expected)) if x!=y],
                changed_implementation_failure=True,Gray_or_iid_failure=False),indent=2)+'\n')
            raise AssertionError(stem+' '+name)
        records.append(dict(name=name,ticks=ticks,inputs=[[hex(v) for v in k.cell_words(cells[j])] for j in range(-5,6)],
            expected=[hex(v) for v in expected]))
        if name=='canonical' or name.startswith('GATHER'):print(name,ticks,flush=True)
    replay=directory/'GMW7_full_replays.json';replay.write_text(json.dumps(records,separators=(',',':'))+'\n')
    budget=bound.validate();budgetfile=directory/'GMW7_execution_bound.json';budgetfile.write_text(json.dumps(budget,indent=2)+'\n')
    receipt=dict(name='GMW7 changed single-middle-gather full emission/prepared checks',Q=k.Q,U=k.U,
        lambda_original=24,c_original=104,kernel_sha256=digest(k.__file__),builder_sha256=digest(builder.__file__),
        checker_sha256=digest(__file__),bound_checker_sha256=digest(bound.__file__),
        ancestors_sha256={name:digest(Path(__file__).parent/name) for name in ('gray_token_word_v6.py',
            'build_gray_token_word_v6.py','check_gray_token_word_v6.py','check_gray_token_word_v6_bound.py')},
        beta_sha256=digest(beta),dictionary_sha256=digest(dictionary),listing_sha256=digest(document),
        replay_sha256=digest(replay),bound_sha256=digest(budgetfile),tokens=rom.token_count,
        beta_bits=rom.token_count*9,used_dictionary_words=rom.used_dictionary,total_immutable_capacity_bits=59392,
        instructions=len(listing),prepared_comparisons=len(records),min_ticks=min(r['ticks'] for r in records),
        max_ticks=max(r['ticks'] for r in records),prepared_comparisons_measured_only=True,
        execution_bound=budget['total_active_execution_bound'],single_middle_gather_and_MADD5_changes_explicit=True,
        fixed_zero_Workspace_and_extra_dictionary_departures_explicit=True,
        own_beta_universal_semantics_or_full_period_proved=False,
        faithful_Gray_or_iid_or_shorter_U_proved=False,active_rule_modified=False,
        elapsed_seconds=time.monotonic()-start)
    (directory/'GMW7_prepared_execution_certificate.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(dict(beta_bits=receipt['beta_bits'],dictionary=receipt['used_dictionary_words'],
        cases=len(records),max_ticks=receipt['max_ticks'],bound=receipt['execution_bound'])))


if __name__=='__main__':main()
