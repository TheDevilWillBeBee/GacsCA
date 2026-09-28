"""Dependency-preserving construction-time instruction ordering, all outputs kept."""
from .wordcode import Program,LIT


def reorder(program,*,reverse_outputs=False,children='original'):
    if children not in ('original','reverse','deep_first','shallow_first'):raise ValueError('unknown fixed traversal')
    depth=[0]*program.inputs
    for kind,a,b in program.operations:depth.append(1 if kind==LIT else 1+max(depth[a],depth[b]))
    mapping={w:w for w in range(program.inputs)};order=[]
    outputs=reversed(program.outputs) if reverse_outputs else program.outputs
    for output in outputs:
        pending=[(output,False)]
        while pending:
            wire,ready=pending.pop()
            if wire in mapping:continue
            kind,a,b=program.operations[wire-program.inputs]
            if ready or kind==LIT:
                mapping[wire]=program.inputs+len(order);order.append(wire);continue
            operands=list(dict.fromkeys((a,b)))
            if children=='reverse':operands.reverse()
            if children in ('deep_first','shallow_first'):operands.sort(key=lambda w:depth[w],reverse=children=='deep_first')
            pending.append((wire,True));pending.extend((w,False) for w in reversed(operands))
    operations=[]
    for w in order:
        kind,a,b=program.operations[w-program.inputs]
        operations.append((kind,a,b) if kind==LIT else (kind,mapping[a],mapping[b]))
    result=Program(program.inputs,tuple(operations),tuple(mapping[w] for w in program.outputs))
    assert len(result.operations)==len(program.operations)
    return result,tuple(order)


def verify(program,result,order):
    assert sorted(order)==list(range(program.inputs,program.wires))
    mapping={w:w for w in range(program.inputs)}
    for i,w in enumerate(order):
        kind,a,b=program.operations[w-program.inputs]
        expected=(kind,a,b) if kind==LIT else (kind,mapping[a],mapping[b])
        assert result.operations[i]==expected
        mapping[w]=program.inputs+i
    assert result.inputs==program.inputs and result.outputs==tuple(mapping[w] for w in program.outputs)
    return True
