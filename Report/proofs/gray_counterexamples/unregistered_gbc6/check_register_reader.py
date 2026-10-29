"""Actually issued Q-bit raw-register reader and new ABI certificate.

This finite experiment supplements the universal coordinate/ABI proof.
It does not issue the rejected complete own listing or call a host rule.
"""
from dataclasses import asdict,replace
from hashlib import sha256
from pathlib import Path
import argparse,json,time
import compact_completion_rule as b
import complete_branch_emitter as e
import register_control_emitter as emitter
from check_early_stage_emission import case_cells

def abi(full):
    rows,marks=full['symbolic_rows'],full['symbolic_marks']
    start=marks['virtual_register_read']
    end=next(i+1 for i in range(start,len(rows)) if rows[i][0]=='RETURN')
    body=rows[start:end]
    writes=sorted({20*a[0] for op,a in body if op=='WSET'})
    assert writes==[e.ADDRESS,e.LENGTH]
    assert not any(op in ('PUSH','CALL') for op,a in body)
    assert rows[end-1]==('RETURN',(1,))
    assert all(op not in ('WGET','WSET') or a[0] not in (18,19) for op,a in body)
    out={}
    for name in ('cpu_reg_entry','cpu_regi_entry'):
        next_name='cpu_regi_entry' if name=='cpu_reg_entry' else 'reg_destination'
        part=rows[marks[name]:marks[next_name]]
        calls=[args for op,args in part if op=='CALL']
        want=[('virtual_register_read',1)]*2 if name=='cpu_reg_entry' else [('virtual_literal',0),('virtual_register_read',1)]
        assert calls==want,(name,calls)
        out[name]=calls
    return {'helper_work_writes':writes,'helper_return_bank':1,
            'helper_has_no_nested_CALL_or_PUSH':True,'direct_entry_calls':out,
            'RAW80_VALUE300_CTRL0_VRET260_VA200_VB220_preserved':True}

def run(output):
    start=time.monotonic();full=emitter.emit_complete_structural_listing();audit=abi(full)
    a=e.Assembler();a.call('virtual_register_read',380);a.emit('HLT');e.emit_register_read_helper(a)
    beta,listing,size=a.finish();assert size<=b.Q
    cells=case_cells(112*b.Q+2);enc={j:b.encode_cell(c) for j,c in cells.items()}
    def tape(x):
        if not b.PRIMARY_START<=x<b.PRIMARY_START+b.FRAME_BITS:return 0
        return sum(enc[j][x-b.PRIMARY_START]<<lane for lane,j in enumerate(b.LANES))
    cases=[]
    for centre in (-1,0,1):
        for q in range(5):
            old=b.unpack(b.voted(cells,centre+b.SLOTS[q],'head'))
            for selector in range(32):
                work=(1<<407)-11
                for off,value in ((e.CENTRE,centre&15),(e.QCOL,q),(e.VSTART,selector),
                                  (e.VA,old.a),(e.VB,old.b)):
                    work=(work&~(b.MASK<<off))|(value<<off)
                seed=b.Packet(p=1,a=777,b=123,fn=13,work=work,nc=(1<<35)-9)
                p=seed;pos=b.PRIMARY_START;h=sha256()
                for tick in range(1,15000):
                    pos+=1 if p.move==1 else -1 if p.move==2 else 0
                    assert 0<=pos<b.Q
                    p,bit=b.cpu(p,pos,{d:tape(pos+d) for d in range(-4,5)},beta)
                    assert bit is None and p.mode!=b.ERROR
                    h.update(repr((tick,pos,p)).encode())
                    if p.mode==b.HALT:break
                else:raise AssertionError('issued register reader did not halt')
                assert p.a==b.register_read(old,selector),(centre,q,selector,p.a,old)
                changed=(b.MASK<<e.ADDRESS)|(b.MASK<<e.LENGTH)|(b.MASK<<380)
                assert p.work&~changed==seed.work&~changed
                assert (p.work>>e.RAW)&b.MASK==(seed.work>>e.RAW)&b.MASK
                assert p.nc==seed.nc and p.fn==(centre&15 if selector<=20 else seed.fn)
                cases.append({'centre':centre,'q':q,'selector':selector,'updates':tick,
                              'result':p.a,'trace_sha256':h.hexdigest()})
    out={'passed':True,'Q':b.Q,'U':b.U,'lambda':24,'c':104,
         'issued_component_bits':size,'issued_component_listing':listing,
         'issued_component_beta_sha256':sha256(bytes(beta)).hexdigest(),
         'component_cases':cases,'maximum_selected_updates':max(x['updates'] for x in cases),
         'actual_input_cells':{str(j):asdict(c) for j,c in cells.items()},'caller_abi':audit,
         'whole_own_beta':False,'universal_full_emitter':False,'physical_period':False,
         'gray_refutation':False,'iid_failure':False,'shorter_U_proved':False,
         'sources':{str(p):sha256(p.read_bytes()).hexdigest() for p in
                    (Path(__file__),Path(b.__file__),Path(e.__file__),Path(emitter.__file__))},
         'elapsed_seconds':time.monotonic()-start}
    output.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:v for k,v in out.items() if k not in ('component_cases','actual_input_cells','issued_component_listing')},indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);run(p.parse_args().output)
