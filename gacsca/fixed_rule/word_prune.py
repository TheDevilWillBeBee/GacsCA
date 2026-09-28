"""Remove unreachable pure expression wires, retaining every declared input/output.

This is compile-time graph simplification of the hard-wired description, not
partial evaluation on initial data or a restriction of the physical alphabet.
"""
from .wordcode import Program,LIT


def prune(program):
    reachable=set();pending=list(program.outputs)
    while pending:
        wire=pending.pop()
        if not isinstance(wire,int) or not 0<=wire<program.wires:raise ValueError('invalid expression wire')
        if wire<program.inputs or wire in reachable:continue
        reachable.add(wire);op,a,b=program.operations[wire-program.inputs]
        if op!=LIT:
            if not 0<=a<wire or not 0<=b<wire:raise ValueError('expression is not an ordered DAG')
            pending.extend((a,b))
    mapping={i:i for i in range(program.inputs)};operations=[]
    for wire,(op,a,b) in enumerate(program.operations,program.inputs):
        if wire not in reachable:continue
        mapping[wire]=program.inputs+len(operations)
        operations.append((op,a,b) if op==LIT else (op,mapping[a],mapping[b]))
    return Program(program.inputs,tuple(operations),tuple(mapping[wire] for wire in program.outputs))
