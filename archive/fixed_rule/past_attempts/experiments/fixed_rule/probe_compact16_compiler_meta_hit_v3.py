"""Check interior own-ROM META hits with exact singleton query addresses.

A local affine adapter evaluates negative query coefficients only when the query
is a known singleton. It does not assert the full interval theorem.
"""
import json
from pathlib import Path
import time
from types import FunctionType
from gacsca.fixed_rule import compact16_holder_compiler_program as p
from experiments.fixed_rule import certify_compact16_holder_meta_paths as old
from experiments.fixed_rule.run_compact16_holder_streamed_depth2 import sha


class Affine(old.Affine):
    def __eq__(self,other):return isinstance(other,old.Affine) and self.q==other.q and self.k==other.k
    __hash__=old.Affine.__hash__
    def __add__(self,other):
        value=super().__add__(other);return Affine(value.q,value.k)
    def __sub__(self,other):
        value=super().__sub__(other);return Affine(value.q,value.k)
    def times(self,factor):
        value=super().times(factor);return Affine(value.q,value.k)
    def word(self,terms,query):
        value=terms.value(query)
        if value is not None:return terms.const(self.q*value+self.k)
        return super().word(terms,query)


def bind(fn):
    namespace=dict(fn.__globals__);namespace.update(p=p,Affine=Affine)
    result=FunctionType(fn.__code__,namespace,fn.__name__,fn.__defaults__,fn.__closure__)
    result.__kwdefaults__=fn.__kwdefaults__
    return result


class Meta(old.MetaPath):
    __init__=bind(old.MetaPath.__init__)
    event=bind(old.MetaPath.event)
    check=bind(old.MetaPath.check)
    left_return=bind(old.MetaPath.left_return)


def main():
    root=Path('figs/fixed_rule');out=root/'compact16_compiler_meta_hit_v3.json'
    if out.exists():raise FileExistsError(out)
    started=time.perf_counter();g=p.layout();L=len(p.base_rom())
    pc=next(i for i,op in enumerate(g.instructions) if op.kind==9)
    rows=[Meta(pc,(address,address)).check() for address in (1,g.memory_count-1,g.memory_count)]
    result=dict(passed=True,query_addresses=[1,g.memory_count-1,g.memory_count],
                paths=rows,ROM_sha256=sha(root/'compact16_compiler_rom_v2.json'),
                source_sha256={str(Path(__file__)):sha(__file__)},seconds=time.perf_counter()-started,
                scope='Exact singleton-query interior META path identities for a representative instruction. Negative affine query coefficient is evaluated only for a known singleton. The existing strict affine endpoint equalities reject some mathematically equal singleton bounds; only successful addresses are claimed. Not a full interval or all-META path certificate.')
    with out.open('x') as stream:stream.write(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k!='paths'},indent=2))


if __name__=='__main__':main()
