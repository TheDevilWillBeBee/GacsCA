"""Typed, fused description of the one-lap physical lookup successor."""
from functools import lru_cache

from .. import spatial_codec8
from .. import stream28_dual_holder_rule20 as holder
from ..stream28_holder_identity import optimize
from ..word_and_fusion import fuse_exclusive_and
from ..wordcode_and import AND,AND_ALU,Program
from . import successor as rule
from . import successor_description


WIDTHS=tuple(width for _ in range(15) for width in
             (tuple(w for _,w in holder.SCHEMA)+spatial_codec8.WIDTHS+
              tuple(w for _,w in rule.BUS_SCHEMA)))
CONSERVATIVE_OUTPUTS=tuple(i for i,(name,_) in enumerate(holder.SCHEMA)
                           if name.endswith(('_lp_remaining','_rp_remaining')))


@lru_cache(maxsize=1)
def compile_description():
    original=successor_description.build()
    normalized=Program(original.inputs,
                       tuple((AND if op==AND_ALU else op,a,b)
                             for op,a,b in original.operations),original.outputs)
    typed,stats=optimize(normalized,WIDTHS,CONSERVATIVE_OUTPUTS)
    fused,fusion=fuse_exclusive_and(typed)
    return fused,dict(full_operations=len(original.operations),
                      typed_operations=len(typed.operations),
                      optimized_operations=len(fused.operations),
                      optimized_sha256=fused.digest(),
                      typed_rewrites=stats['rewrites'],
                      fused_exclusive_cones=fusion['exclusive_cones'])


def build():return compile_description()[0]
