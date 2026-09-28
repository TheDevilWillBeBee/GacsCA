"""Generate fixed-DAG arithmetic using verified reusable caller-owned storage.

This is an execution-backend emitter. The physical description and hard-wired
colony ROM are unchanged. Input/output/workspace rows may be interleaved across
workers by a fixed positive stride, avoiding unbounded per-thread CUDA stacks.
"""
from .word_allocation import allocate,verify
from .wordcode import LIT,NAND,ADD,SHR,EQ,LT


def expression_source(program,name,*,stride=1):
    if type(stride) is not int or stride<1:raise ValueError('positive storage stride required')
    allocation=allocate(program);verify(program,allocation)
    def reference(wire):
        return f'in[{wire*stride}]' if wire<program.inputs else f'tmp[{allocation.slots[wire-program.inputs]*stride}]'
    lines=[f'void {name}(const uint64_t *in,uint64_t *out,uint64_t *tmp) {{']
    for i,(op,a,b) in enumerate(program.operations):
        aa,bb=(reference(a),reference(b)) if op!=LIT else ('','')
        if op==LIT:expr=f'UINT64_C(0x{a:016x})'
        elif op==NAND:expr=f'~({aa}&{bb})'
        elif op==ADD:expr=f'{aa}+{bb}'
        elif op==SHR:expr=f'{bb}<64?{aa}>>{bb}:0'
        elif op==EQ:expr=f'{aa}=={bb}'
        elif op==LT:expr=f'{aa}<{bb}'
        else:raise ValueError('unsupported fixed arithmetic')
        lines.append(f' tmp[{allocation.slots[i]*stride}]={expr};')
    lines.extend(f' out[{i*stride}]={reference(wire)};' for i,wire in enumerate(program.outputs))
    lines.append('}')
    return '\n'.join(lines)+'\n',allocation
