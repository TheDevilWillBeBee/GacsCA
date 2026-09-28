"""Isolated construction-time layout experiments; no evolving interpreter.

Reuses the sealed compiler functions with private globals, never module mutation.
The result is an ordinary fixed ROM. This helper has no hierarchy-depth input.
"""
from functools import lru_cache
from types import FunctionType
from . import compact16_holder_program as base


class Compilation:
    def __init__(self,description,capacity=320):
        self.description=description;self.capacity=capacity
        self.compiled_description=lambda:description
        original=base.layout.__wrapped__
        namespace=dict(original.__globals__)
        namespace.update(compiled_description=self.compiled_description,RESULT_CAPACITY=capacity)
        self.layout=lru_cache(None)(FunctionType(original.__code__,namespace,original.__name__,original.__defaults__,original.__closure__))
        original=base.base_rom.__wrapped__;namespace=dict(original.__globals__);namespace['layout']=self.layout
        self.base_rom=lru_cache(None)(FunctionType(original.__code__,namespace,original.__name__,original.__defaults__,original.__closure__))
    def __getattr__(self,name):return getattr(base,name)


def cost(compilation):
    g=compilation.layout()
    ticks=sum(g.schedule(*phase)[0] for phase in g.stage_ranges)+g.schedule(*g.delivery_range)[0]
    return dict(core_cells=g.computation_cells,memory_cells=g.memory_count,instructions=len(g.instructions),controller_path_ticks=ticks,
                capacity=compilation.capacity,description_sha256=compilation.description.digest())
