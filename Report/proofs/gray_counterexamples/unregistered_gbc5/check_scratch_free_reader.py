"""Issued GBC5 reader, exact caller and counted return-bank audit.

The caller audit is a syntactic certificate for this exact rejected
complete listing. It proves the component's ABI premises, not universal
equivalence, termination or Q-fit of that complete listing.
"""
from dataclasses import asdict, replace
from hashlib import sha256
from pathlib import Path
import argparse, json, time
import scratch_free_reader_emitter as new
e, b = new.e, new.b
from check_early_stage_emission import case_cells


def audit_callers(full):
    rows, marks = full['symbolic_rows'], full['symbolic_marks']
    owners = [('copy_group', 1), ('write_word', 0), ('temporal_word', 1),
              ('virtual_vote', 0), ('virtual_literal', 0)]
    owners += [('scratch_free_head_read_' + str(w), 1)
               for w in full['reader_widths']]
    entries = sorted((marks[name], name, bank) for name, bank in owners)
    owner_at = ['main'] * len(rows)
    for k, (start, name, bank) in enumerate(entries):
        end = entries[k+1][0] if k+1 < len(entries) else marks['common_virtual_continue']
        owner_at[start:end] = [name] * (end-start)
    bank_of = {name: bank for name, bank in owners}
    calls, edges, returns = [], {}, []
    for i, (op, args) in enumerate(rows):
        owner = owner_at[i]
        if op == 'CALL':
            target, bank = args
            assert target in bank_of and bank == bank_of[target]
            assert owner == 'main' or bank != bank_of[owner], (owner,target,bank)
            calls.append({'row': i, 'owner': owner, 'target': target, 'bank': bank})
            edges.setdefault(owner, set()).add(target)
        if op == 'RETURN':
            assert owner != 'main' and args[0] == bank_of[owner]
            returns.append({'row': i, 'owner': owner, 'bank': args[0]})
        if op in ('WGET', 'WSET') and args[0] in (18,19):
            raise AssertionError(('reserved return word explicit access',i,op,args))
        if owner != 'main':
            assert op != 'PUSH', ('helper would flush return words',owner,i)
    # A helper may abandon its saved return via the literal-error branch
    # to main cpu_fail. That is a terminal continuation, not a nested call.
    nonlocal_abort = []
    for i, (op,args) in enumerate(rows):
        if op != 'BR' or owner_at[i] == 'main': continue
        target = args[1]
        dst = owner_at[marks[target]]
        if dst != owner_at[i]:
            assert owner_at[i] == 'virtual_literal' and target == 'cpu_fail'
            nonlocal_abort.append(i)
    def paths(owner, active=()):
        assert owner not in active
        out = [active+(owner,)]
        for child in sorted(edges.get(owner, ())):
            out += paths(child, active+(owner,))
        return out
    call_paths = paths('main')
    max_depth = max(len(p)-1 for p in call_paths)
    assert max_depth == 2
    for path in call_paths:
        banks = [bank_of[name] for name in path[1:]]
        assert len(banks) == len(set(banks))
    callers = []
    for c in full['reader_callers']:
        start, call, end = [marks[c[k]] for k in ('start_label','call_label','end_label')]
        assert owner_at[call] == 'main'
        assert rows[call] == ('CALL',(c['target'],1))
        # The specialized macro itself neither reads nor writes RAW80.
        # Its only data Work store, if any, is the caller's named result.
        writes = [20*args[0] for op,args in rows[start:end] if op=='WSET']
        reads = [20*args[0] for op,args in rows[start:end] if op=='WGET']
        assert writes == ([] if c['destination'] is None else [c['destination']])
        assert e.RAW not in reads and e.RAW not in writes
        assert 0 <= c['offset'] and c['offset']+c['width'] <= b.HEAD_BITS
        assert c['centre'] in (None,-1,0,1)
        callers.append(dict(c, actual_start_row=start, actual_call_row=call,
                            actual_end_row=end, owner='main'))
    assert len(callers) == sum(x['target'].startswith('scratch_free_head_read_') for x in calls)
    return {'caller_count':len(callers),'callers':callers,'calls':calls,
            'returns':returns,'call_paths':call_paths,
            'maximum_nested_calls':max_depth,'nonlocal_literal_abort_rows':nonlocal_abort,
            'RAW80_preserved_at_every_reader_call':True,
            'counted_return_banks_not_overwritten_while_live':True}


def run(output):
    t0=time.monotonic();full=new.emit_complete_structural_listing()
    audit=audit_callers(full)
    seed=b.Packet(p=1,pc=0,move=0,a=777,b=999,fn=13,buf=3,lane=31,
                  work=(1<<407)-7,nc=(1<<35)-9)
    cells=case_cells(112*b.Q+2);enc={j:b.encode_cell(c) for j,c in cells.items()}
    def tape(position):
        if not b.PRIMARY_START<=position<b.PRIMARY_START+b.FRAME_BITS:return 0
        return sum(enc[j][position-b.PRIMARY_START]<<lane for lane,j in enumerate(b.LANES))
    cases=[]
    for centre in range(-4,5):
        for q in range(5):
            for width in full['reader_widths']:
                for offset in sorted({0,b.HEAD_BITS-width}):
                    beta,listing,size=new.emit_component(q,centre,offset,width)
                    p=seed;position=b.PRIMARY_START;trace=sha256()
                    for tick in range(1,20000):
                        position += 1 if p.move==1 else -1 if p.move==2 else 0
                        assert 0<=position<b.Q
                        p,bit=b.cpu(p,position,{d:tape(position+d) for d in range(-4,5)},beta)
                        assert bit is None and p.mode!=b.ERROR
                        trace.update(repr((tick,position,p)).encode())
                        if p.mode==b.HALT:break
                    else:raise AssertionError('reader did not halt')
                    want=(b.voted(cells,centre+b.SLOTS[q],'head')>>offset)&((1<<width)-1)
                    assert p.a==want
                    changed=(b.MASK<<100)|(b.MASK<<380)
                    assert p.work&~changed==seed.work&~changed
                    assert (p.work>>80)&b.MASK==(seed.work>>80)&b.MASK
                    assert p.nc==seed.nc and p.fn==centre&15
                    exact_time=18+e.HEAD_BASE+5*(offset+width-1)+q-b.PRIMARY_START
                    assert tick==exact_time
                    cases.append({'centre':centre,'q':q,'offset':offset,'width':width,
                                  'programme_bits':size,'programme_sha256':sha256(bytes(beta)).hexdigest(),
                                  'updates':tick,'result':want,'trace_sha256':trace.hexdigest()})
    out={'passed':True,'Q':b.Q,'U':b.U,'lambda':24,'c':104,
         'scope':'scratch-free generic Head window and actual emitted reader/return ABI',
         'component_cases':cases,'caller_audit':audit,
         'complete_programme_bits':full['programme_bits'],'complete_instructions':full['instructions'],
         'invalid_references':full['invalid_references'],'reader_widths':full['reader_widths'],
         'largest_issued_component_bits':max(c['programme_bits'] for c in cases),
         'largest_selected_component_updates':max(c['updates'] for c in cases),
         'universal_issued_component_bound':18+e.HEAD_BASE+5*(b.HEAD_BITS-1)+4-b.PRIMARY_START,
         'actual_input_cells':{str(j):asdict(c) for j,c in cells.items()},
         'sources':{str(p):sha256(p.read_bytes()).hexdigest() for p in
                    (Path(__file__),Path(new.__file__),Path(e.__file__),Path(b.__file__))},
         'unchanged_total_rule':True,'no_added_state_or_opcode':True,
         'complete_emitter_equivalence':False,'complete_universal_runtime':False,
         'whole_own_beta':False,'physical_period':False,'gray_refutation':False,
         'iid_failure':False,'shorter_U_proved':False,
         'elapsed_seconds':time.monotonic()-t0}
    output.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:v for k,v in out.items() if k not in ('component_cases','caller_audit','actual_input_cells','invalid_references')},indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True)
    run(p.parse_args().output)
