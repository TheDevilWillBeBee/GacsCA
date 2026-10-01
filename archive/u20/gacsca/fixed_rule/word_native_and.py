"""Owned native compiler for the fixed word description with AND opcode."""
from .wordcode_and import LIT,NAND,ADD,SHR,EQ,LT,AND


def expression_source(program,name):
    lines=[f'void {name}(const uint64_t *in,uint64_t *out) {{',
           f' uint64_t w[{program.wires}];',
           f' memcpy(w,in,{program.inputs}*sizeof(uint64_t));']
    for i,(op,a,b) in enumerate(program.operations,program.inputs):
        aa,bb=f'w[{a}]',f'w[{b}]'
        if op==LIT:expr=f'UINT64_C(0x{a:016x})'
        elif op==NAND:expr=f'~({aa}&{bb})'
        elif op==AND:expr=f'{aa}&{bb}'
        elif op==ADD:expr=f'{aa}+{bb}'
        elif op==SHR:expr=f'{bb}<64?{aa}>>{bb}:0'
        elif op==EQ:expr=f'{aa}=={bb}'
        elif op==LT:expr=f'{aa}<{bb}'
        else:raise ValueError(('unsupported physical arithmetic',op))
        lines.append(f' w[{i}]={expr};')
    lines.extend(f' out[{i}]=w[{wire}];' for i,wire in enumerate(program.outputs))
    lines.append('}')
    return '\n'.join(lines)+'\n'
