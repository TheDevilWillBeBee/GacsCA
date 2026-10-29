"""Compositional RUN/vector-issue bound for the exact own REG branches.

Bounds apply to correct prepared instruction fetch and quiet captured
input. The bounded unary decoder's loop invariant is stated in the proof.
No whole-rule evaluation or sampled-runtime maximum supplies the bound.
"""
from functools import lru_cache
import register_control_emitter as emitter

def bound(full=None):
    full=full or emitter.emit_complete_structural_listing()
    rows,marks=full['symbolic_rows'],full['symbolic_marks']
    stop=marks['cpu_next'];unary=marks['literal_unary']
    @lru_cache(None)
    def visit(i,stack,unary_visits):
        if i==stop:return (0,0)
        if i==unary:
            unary_visits+=1
            if unary_visits>21:return None
        op,args=rows[i]
        if op=='RETURN':
            assert stack
            children=[(stack[-1],stack[:-1],unary_visits)]
        elif op=='CALL':children=[(marks[args[0]],stack+(i+1,),unary_visits)]
        elif op=='BR':
            children=[(marks[args[1]],stack,unary_visits)]
            if args[0]!=0:children.append((i+1,stack,unary_visits))
        else:
            assert op not in ('JMP','HLT'),(i,op)
            children=[(i+1,stack,unary_visits)]
        answers=[v for child in children if (v:=visit(*child)) is not None]
        if not answers:return None
        is_vector=int(op=='PUTWORD' or op=='READ' and args[0]==3)
        return (1+max(x[0] for x in answers),is_vector+max(x[1] for x in answers))
    results={name:visit(marks[name],(),0) for name in ('cpu_reg_entry','cpu_regi_entry')}
    out={name:{'RUN_updates':a,'vector_issues':v,
               'uniform_updates':a+v*(emitter.b.Q+5*19+1)} for name,(a,v) in results.items()}
    return {'scope':'own REG/REGI entry through cpu_next, prepared fetch/controls and quiet tape',
            'unary_visits_cap':21,'branches':out,
            'maximum_uniform_updates':max(x['uniform_updates'] for x in out.values()),
            'full_programme_deadline':False}

if __name__=='__main__':
    from pathlib import Path
    import argparse,json
    p=argparse.ArgumentParser();p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    r=bound();a.output.write_text(json.dumps(r,indent=2)+'\n');print(json.dumps(r,indent=2))
