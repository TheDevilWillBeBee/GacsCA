"""One depth-independent, compiler-reordered ROM candidate for compact16 F.

No physical rule/alphabet/opcode changes. Its own metadata comes from this ROM.
This candidate is selected by the measured v1 search, not by hierarchy depth.
"""
from functools import lru_cache
from . import compact16_holder_program as original
from . import word_boolean_cuts as cuts,word_dag_order as order
from .compact16_compiler_candidate import Compilation

RESULT_CAPACITY=270


@lru_cache(None)
def proof():
    baseline=original.compiled_description();rewritten,cut_certificate=cuts.optimize(baseline)
    assert cuts.verify(baseline,rewritten,cut_certificate)['complete_outputs']==154
    result,permutation=order.reorder(rewritten,reverse_outputs=True,children='original')
    assert order.verify(rewritten,result,permutation)
    return result,cut_certificate,permutation


@lru_cache(None)
def compilation():return Compilation(proof()[0],RESULT_CAPACITY)


def compiled_description():return proof()[0]
def layout():return compilation().layout()
def base_rom():return compilation().base_rom()


def __getattr__(name):return getattr(original,name)
