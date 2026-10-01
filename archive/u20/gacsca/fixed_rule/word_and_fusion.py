"""Compile-time fusion of exclusive NAND inversion cones into fixed AND opcodes.

This changes only the ROM expression DAG.  The physical evaluator implements
AND for every encoded instruction, independent of hierarchy depth.  Each
rewrite uses NAND(NAND(a,b), NAND(a,b)) = a & b on full 64-bit words.
"""
from collections import defaultdict

from .wordcode_and import AND, LIT, NAND, Builder, Program
from .word_prune import prune


def fuse_exclusive_and(program: Program):
    consumers = defaultdict(set)
    for wire, (kind, a, b) in enumerate(program.operations, program.inputs):
        if kind != LIT:
            consumers[a].add(wire)
            consumers[b].add(wire)
    for output in program.outputs:
        consumers[output].add(-1)

    outer_to_inner = {}
    for outer, (kind, a, b) in enumerate(program.operations, program.inputs):
        if kind != NAND or a != b or a < program.inputs:
            continue
        inner_kind, _, _ = program.operations[a - program.inputs]
        if inner_kind == NAND and consumers[a] == {outer}:
            outer_to_inner[outer] = a

    builder = Builder(program.inputs)
    mapping = list(range(program.inputs))
    for wire, (kind, a, b) in enumerate(program.operations, program.inputs):
        if wire in outer_to_inner:
            _, left, right = program.operations[a - program.inputs]
            mapping.append(builder.op(AND, mapping[left], mapping[right]))
        else:
            mapping.append(builder.const(a) if kind == LIT else
                           builder.op(kind, mapping[a], mapping[b]))
    fused = prune(builder.finish(tuple(mapping[wire] for wire in program.outputs)))
    fused = Program(fused.inputs, fused.operations, fused.outputs)
    assert fused.inputs == program.inputs and len(fused.outputs) == len(program.outputs)
    return fused, dict(exclusive_cones=len(outer_to_inner),
                       operations_before=len(program.operations),
                       operations_after=len(fused.operations),
                       original_sha256=program.digest(), fused_sha256=fused.digest())
