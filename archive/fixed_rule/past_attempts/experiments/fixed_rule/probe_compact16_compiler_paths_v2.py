"""Representative physical full-raw path checks for the isolated ROM candidate."""
import json
from pathlib import Path
import time
from types import FunctionType
from gacsca.fixed_rule import compact16_holder_compiler_program as p,compact16_holder_core as c
from experiments.fixed_rule import certify_compact16_holder_instruction_paths as ordinary
from experiments.fixed_rule import certify_compact16_holder_meta_paths as meta
from experiments.fixed_rule import certify_compact16_holder_dispatch_paths as dispatch
from experiments.fixed_rule.run_compact16_holder_streamed_depth2 import sha


def bind(fn):
    namespace=dict(fn.__globals__);namespace['p']=p
    result=FunctionType(fn.__code__,namespace,fn.__name__,fn.__defaults__,fn.__closure__)
    result.__kwdefaults__=fn.__kwdefaults__
    return result


class Ordinary(ordinary.InstructionPath):__init__=bind(ordinary.InstructionPath.__init__)
class Meta(meta.MetaPath):__init__=bind(meta.MetaPath.__init__)
class Dispatch(dispatch.DispatchPath):__init__=bind(dispatch.DispatchPath.__init__)


def main():
    fig=Path('figs/fixed_rule');out=fig/'compact16_compiler_paths_v2.json'
    if out.exists():raise FileExistsError(out)
    started=time.perf_counter();g=p.layout();rom=bind(meta.verify_rom)();kinds={}
    for pc,op in enumerate(g.instructions):kinds.setdefault(op.kind,pc)
    picks=[kinds[k] for k in (c.LIT,c.ADD,c.NAND,c.EQ,c.SHR,c.LT,c.SEND,c.LOAD,c.HALT,c.IF_THIRD) if k in kinds]
    picks.extend([len(g.instructions)-2,next(pc for pc,op in enumerate(g.instructions) if op.kind==c.NAND and pc>g.stage_ranges[4][0])])
    ordinary_rows=[Ordinary(pc,third=(g.stage_ranges[4][0]<=pc<g.stage_ranges[4][1] and g.instructions[pc].kind==c.IF_THIRD)).check() for pc in dict.fromkeys(picks)]
    meta_pc=kinds[c.META]
    metadata=[Meta(meta_pc,(a,a)).check() for a in (len(p.base_rom())-1,len(p.base_rom())+37,f.Q-1)]
    dispatched=[]
    for start,pc in ((0,g.entries[0]),(g.memory_count+1,g.entries[0]+1),(0,g.entries[4])):
        if start<=g.memory_count+pc:dispatched.append(Dispatch(start,pc).check())
    result=dict(passed=True,ROM=rom,ordinary=ordinary_rows,META=metadata,dispatch=dispatched,
                physical_descriptor_sha256=p.original.f.self_description().digest(),
                source_sha256={str(Path(__file__)):sha(__file__)},seconds=time.perf_counter()-started,
                scope='Representative complete raw local-event paths for this own-ROM candidate, including ordinary ALU, SEND, LOAD, halt, META endpoint/fallback, and dispatch. Interior META hit needs separate proof; the existing probe Affine.word helper does not accept negative query coefficient. Not exhaustive new-ROM path composition or full physical period execution.')
    with out.open('x') as stream:stream.write(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:v for k,v in result.items() if k not in ('ordinary','META','dispatch')},indent=2))


if __name__=='__main__':main()
