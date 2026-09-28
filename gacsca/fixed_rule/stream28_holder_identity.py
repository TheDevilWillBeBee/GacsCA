"""Conservative typed compilation for the stream rule's hop counters.

The generic identity optimizer is exact on typed values, but its bounded-mask
rewrite gives a structurally different expression for ten output hop counters.
Only within those outputs' dependency cones, widen the temporary known-bit
bound used for a redundant NAND mask. Widening is conservative: it prevents a
rewrite and cannot introduce an unsound known bit. All other optimizations
and all original outputs remain available for independent equivalence tests.
"""
from .word_identity_and import IdentityBuilder
from .wordcode_and import LIT,NAND,MASK
from .word_prune import prune


class ConservativeBuilder(IdentityBuilder):
    avoid_mask_rewrite=False

    def op(self,opcode,a,b):
        saved=[]
        if self.avoid_mask_rewrite and opcode==NAND:
            for wire,constant in ((a,b),(b,a)):
                value=self.constants.get(constant)
                if value is not None and wire!=constant and self.bounds[wire][0]&~value==0:
                    saved.append((wire,self.bounds[wire]))
                    self.bounds[wire]=(MASK,0)
        try:return super().op(opcode,a,b)
        finally:
            for wire,bound in saved:self.bounds[wire]=bound


def dependency_cone(program,outputs):
    pending=[program.outputs[i] for i in outputs];cone=set()
    while pending:
        wire=pending.pop()
        if wire<program.inputs or wire in cone:continue
        cone.add(wire)
        opcode,a,b=program.operations[wire-program.inputs]
        if opcode!=LIT:pending.extend((a,b))
    return frozenset(cone)


def optimize(program,widths,conservative_outputs):
    if len(widths)!=program.inputs:raise ValueError('complete typed inputs required')
    cone=dependency_cone(program,conservative_outputs)
    builder=ConservativeBuilder(tuple(widths));mapping=list(range(program.inputs))
    for index,(opcode,a,b) in enumerate(program.operations):
        builder.avoid_mask_rewrite=program.inputs+index in cone
        mapping.append(builder.const(a) if opcode==LIT else
                       builder.op(opcode,mapping[a],mapping[b]))
    result=prune(builder.finish(tuple(mapping[wire] for wire in program.outputs)))
    return result,dict(cone_operations=len(cone),rewrites=dict(builder.rewrites),
                       original_operations=len(program.operations),
                       optimized_operations=len(result.operations))
