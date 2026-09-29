"""Typed and fused complete description of the fixed dual-pass rule."""
from functools import lru_cache

from . import stream28_compact_vote_optimized8 as previous
from . import stream28_dual_pass_description20 as full
from . import stream28_spatial_optimized as identities
from .stream28_holder_identity import optimize
from .word_and_fusion import fuse_exclusive_and
from .wordcode_and import Program,AND,AND_ALU

WIDTHS=previous.WIDTHS


@lru_cache(maxsize=1)
def compile_description():
    original=full.build()
    normalized=Program(original.inputs,
                       tuple((AND if opcode==AND_ALU else opcode,a,b)
                             for opcode,a,b in original.operations),
                       original.outputs)
    typed,stats=optimize(normalized,WIDTHS,
                         identities.CONSERVATIVE_OUTPUTS)
    fused,fusion=fuse_exclusive_and(typed)
    return fused,dict(full_operations=len(original.operations),
                      typed_operations=len(typed.operations),
                      optimized_operations=len(fused.operations),
                      optimized_sha256=fused.digest(),
                      typed_rewrites=stats['rewrites'],
                      fused_exclusive_cones=fusion['exclusive_cones'])


def build():return compile_description()[0]
