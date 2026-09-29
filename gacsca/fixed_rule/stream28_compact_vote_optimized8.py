"""Typed/fused WordCode of the fixed 8Q in-place-vote successor."""
from functools import lru_cache

from . import spatial_codec8,stream28_holder_rule as holder
from . import stream28_compact_vote_description8 as full
from . import stream28_spatial_optimized as previous
from .stream28_holder_identity import optimize
from .word_and_fusion import fuse_exclusive_and
from .wordcode_and import Program,AND,AND_ALU

WIDTHS=tuple(width for _ in range(15)
             for width in (tuple(width for _,width in holder.SCHEMA)+
                           spatial_codec8.WIDTHS))


@lru_cache(maxsize=1)
def compile_description():
    original=full.build()
    normalized=Program(original.inputs,
                       tuple((AND if opcode==AND_ALU else opcode,a,b)
                             for opcode,a,b in original.operations),
                       original.outputs)
    typed,typed_stats=optimize(normalized,WIDTHS,
                               previous.CONSERVATIVE_OUTPUTS)
    fused,fusion_stats=fuse_exclusive_and(typed)
    return fused,dict(original_operations=len(original.operations),
                      normalized_sha256=normalized.digest(),
                      typed_operations=len(typed.operations),
                      typed_rewrites=typed_stats['rewrites'],
                      fused_operations=len(fused.operations),
                      fused_sha256=fused.digest(),
                      fused_exclusive_cones=fusion_stats['exclusive_cones'])


def build():return compile_description()[0]
