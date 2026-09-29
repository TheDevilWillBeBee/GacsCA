"""Exact small-cut NAND resynthesis for a fixed complete word descriptor.

Only bitwise NAND cones are rewritten. Arithmetic, comparison and input wires
are opaque leaves, so each eight-row truth table proves all 64 output bits for
arbitrary words. This is construction-time compilation, never CA evolution.
"""
from functools import lru_cache
from .wordcode import Builder, Program, LIT, NAND, MASK
from .word_prune import prune
from .word_allocation import last_uses


@lru_cache(None)
def templates():
    # A small formula library, not a claim of globally minimum NAND circuits.
    best={0xAA:(0,0),0xCC:(0,1),0xF0:(0,2),0:(1,3),255:(1,4)}
    changed=True
    while changed:
        changed=False;items=list(best.items())
        for a,(ca,ta) in items:
            for b,(cb,tb) in items:
                if a>b:continue
                truth=255^(a&b);cost=ca+1 if a==b else ca+cb+1
                if truth not in best or cost<best[truth][0]:
                    best[truth]=(cost,(ta,tb));changed=True
    assert len(best)==256
    return {truth:tree for truth,(_,tree) in best.items()}


def table(tree):
    if isinstance(tree,int):return (0xAA,0xCC,0xF0,0,255)[tree]
    return 255^(table(tree[0])&table(tree[1]))


def optimize(program,*,max_cuts=12,max_depth=5):
    if not 1<=max_cuts<=32 or not 1<=max_depth<=8:raise ValueError('bounded cuts/depth required')
    library=templates();assert all(table(t)==truth for truth,t in library.items())
    b=Builder(program.inputs);mapping=list(range(program.inputs));proofs=[]
    last=last_uses(program);rejected_shared=0

    def live_count(roots):
        seen=set();pending=list(roots)
        while pending:
            w=pending.pop()
            if w<b.inputs or w in seen:continue
            seen.add(w);kind,x,y=b.operations[w-b.inputs]
            if kind!=LIT:pending.extend((x,y))
        return len(seen)

    def is_nand(w):return w>=b.inputs and b.operations[w-b.inputs][0]==NAND

    @lru_cache(None)
    def cuts(w,depth):
        result={(w,)}
        if depth and is_nand(w):
            _,a,c=b.operations[w-b.inputs]
            for x in cuts(a,depth-1):
                for y in cuts(c,depth-1):
                    merged=tuple(sorted(set(x+y)))
                    if len(merged)<=3:result.add(merged)
        # Favor deep cuts (smaller wire numbers), retaining the trivial cut.
        others=sorted(result-{(w,)},key=lambda x:(sum(x),len(x),x))[:max_cuts-1]
        return ((w,),*others)

    def truth_and_nodes(w,leaves):
        memo=dict(zip(leaves,(0xAA,0xCC,0xF0)));nodes=set()
        def visit(v):
            if v in memo:return memo[v]
            if not is_nand(v):raise AssertionError('cut misses non-NAND leaf')
            _,a,c=b.operations[v-b.inputs];nodes.add(v)
            memo[v]=255^(visit(a)&visit(c));return memo[v]
        return visit(w),nodes

    def emit(tree,leaves):
        if isinstance(tree,int):
            if tree<3:
                assert tree<len(leaves),'unused truth-table variable leaked into formula'
                return leaves[tree]
            return b.const(0 if tree==3 else MASK)
        a=emit(tree[0],leaves);c=emit(tree[1],leaves)
        return b.nand(a,c)

    for index,(op,a,c) in enumerate(program.operations):
        wire=b.const(a) if op==LIT else b.op(op,mapping[a],mapping[c])
        if op==NAND:
            choice=None
            for leaves in cuts(wire,max_depth)[1:]:
                truth,nodes=truth_and_nodes(wire,leaves);tree=library[truth]
                # Count distinct new gates rather than formula-tree occurrences.
                gates=set()
                def count(t):
                    if isinstance(t,int):return
                    gates.add(t);count(t[0]);count(t[1])
                count(tree)
                gain=len(nodes)-len(gates)
                if gain>0 and (choice is None or gain>choice[0]):choice=(gain,leaves,truth,tree)
            if choice is not None:
                gain,leaves,truth,tree=choice;new=emit(tree,leaves)
                if new!=wire:
                    roots={mapped for old,mapped in enumerate(mapping) if last[old]>index}
                    if live_count((*roots,new))<live_count((*roots,wire)):
                        proofs.append(dict(old=wire,new=new,leaves=leaves,truth=truth))
                        wire=new
                    else:rejected_shared+=1
        mapping.append(wire)
    expanded=b.finish(tuple(mapping[w] for w in program.outputs));result=prune(expanded)
    return result,dict(original=program,expanded=expanded,mapping=tuple(mapping),rewrites=tuple(proofs),
                       original_operations=len(program.operations),optimized_operations=len(result.operations),
                       rejected_shared=rejected_shared,
                       original_sha256=program.digest(),optimized_sha256=result.digest())


def verify(program,result,certificate):
    """Independent Boolean enumeration and per-operation induction.

    Checks every output mapping, not just the rewritten subexpressions. No
    assumption about controller activity, clocks, geometry or input widths.
    """
    expanded=certificate['expanded'];mapping=certificate['mapping']
    assert expanded.inputs==program.inputs and len(mapping)==program.wires
    assert tuple(mapping[:program.inputs])==tuple(range(program.inputs))
    rewrites={entry['old']:entry for entry in certificate['rewrites']}
    keys={(op,a,c):expanded.inputs+i for i,(op,a,c) in enumerate(expanded.operations)}
    for i,(op,a,c) in enumerate(program.operations):
        aa,cc=(a,c) if op==LIT else (mapping[a],mapping[c])
        from .wordcode import ADD, EQ
        if op in (NAND,ADD,EQ) and aa>cc:aa,cc=cc,aa
        # Builder folds operations whose two inputs are literal constants.
        if op!=LIT and aa>=expanded.inputs and cc>=expanded.inputs:
            oa,va,_=expanded.operations[aa-expanded.inputs];oc,vc,_=expanded.operations[cc-expanded.inputs]
            if oa==oc==LIT:
                from .wordcode import arithmetic
                key=(LIT,arithmetic(op,va,vc),0)
            else:key=(op,aa,cc)
        else:key=(op,aa,cc)
        old=keys[key];new=mapping[program.inputs+i]
        if old==new:continue
        entry=rewrites[old];assert entry['new']==new
        leaves=entry['leaves'];assert 1<=len(leaves)<=3
        for assignment in range(1<<len(leaves)):
            memo={leaf:(assignment>>j)&1 for j,leaf in enumerate(leaves)}
            def bit(w):
                if w in memo:return memo[w]
                assert w>=expanded.inputs
                kind,x,y=expanded.operations[w-expanded.inputs]
                if kind==LIT:
                    assert x in (0,MASK);answer=int(x==MASK)
                else:
                    assert kind==NAND;answer=1-(bit(x)&bit(y))
                memo[w]=answer;return answer
            assert bit(old)==((entry['truth']>>assignment)&1),'incorrect recorded NAND truth table'
            assert bit(old)==bit(new),'incorrect NAND cut rewrite'
    assert expanded.outputs==tuple(mapping[w] for w in program.outputs)
    assert prune(expanded)==result
    return dict(complete_outputs=len(result.outputs),rewrites=len(certificate['rewrites']),arbitrary_64bit_inputs=True)
