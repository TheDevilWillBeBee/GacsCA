"""Counted generic-register folding over the complete GBC6 emission.

Only exact old instruction blocks without internal labels are replaced.
Both replacements preserve A/B and every Work bit for arbitrary raw data.
No hidden table, stack, field oracle, or whole-rule primitive is used.
"""
import scratch_free_reader_emitter as old
e,b=old.e,old.b

def emit_complete_structural_listing():
    original=e.Assembler;captured={};accounting={'REG_blocks':0,'REGI_blocks':0}
    class FoldAssembler(original):
        def finish(self,require_fit=True):
            oldrows=self.rows;oldmarks=dict(self.marks);rows=[];mapping={};i=0
            accounting['instructions_before_register_fold']=len(oldrows)
            while i<len(oldrows):
                mapping[i]=len(rows);part=oldrows[i:i+5]
                if (len(part)==5 and [r[0] for r in part]==['WGET','SWAP','WGET','ALU','WSET']
                    and all(0<=part[k][1][0]<=20 for k in (0,2,4))
                    and 0<=part[3][1][0]<16
                    and not any(i<m<i+5 for m in oldmarks.values())):
                    rows.append(('REG',(part[4][1][0],part[2][1][0],part[0][1][0],part[3][1][0])))
                    i+=5;accounting['REG_blocks']+=1;continue
                part=oldrows[i:i+3]
                if (len(part)==3 and [r[0] for r in part]==['WGET','ALUI','WSET']
                    and all(0<=part[k][1][0]<=20 for k in (0,2))
                    and not any(i<m<i+3 for m in oldmarks.values())):
                    rows.append(('REGI',(part[2][1][0],part[0][1][0],*part[1][1])))
                    i+=3;accounting['REGI_blocks']+=1;continue
                rows.append(oldrows[i]);i+=1
            mapping[len(oldrows)]=len(rows)
            self.rows=rows;self.marks={k:mapping[v] for k,v in oldmarks.items()}
            accounting['instructions_after_register_fold']=len(rows)
            captured.update(rows=list(rows),marks=dict(self.marks))
            return super().finish(require_fit)
    try:
        e.Assembler=FoldAssembler
        r=old.emit_complete_structural_listing()
    finally:e.Assembler=original
    r['compiler_change']='new REG/REGI total rule and exact register folding; no added storage'
    r['register_accounting']=accounting
    r['symbolic_rows']=captured['rows'];r['symbolic_marks']=captured['marks']
    return r

if __name__=='__main__':
    from pathlib import Path
    import argparse,json
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    r=emit_complete_structural_listing();a.output.write_text(json.dumps(r,indent=2)+'\n')
    print(json.dumps({k:r[k] for k in ('programme_bits','instructions','Q_fit','register_accounting')},indent=2))
