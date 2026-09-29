"""Verify a saved physical light-cone derivation without rerunning its accelerator.

Every leaf update is checked through exhaustive tables generated from complete
native F. Every memoized spacetime-block result is then checked from already
verified subqueries. Initial periodic data is checked independently from RLE.
"""
import argparse
from bisect import bisect_right
import hashlib
import json
from pathlib import Path
import tarfile
import numpy as np
from gacsca.fixed_rule import delivery_rule as f,delivery_native as native

MASK=255;FIRST=1<<16;LAST=1<<17;WORDS=f.Q//8


def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def tables():
    lib=native.library();one={};two={}
    def row(address,c1,c2,rs,ls):
        return tuple(f.Cell(address=(address+j)%f.Q,age=98*f.Q,f1=c1 if j==0 else ((rs>>(j-1))&1 if j>0 else 0),f2=c2 if j==0 else ((ls>>(-j-1))&1 if j<0 else 0)) for j in range(-5,6))
    for available in range(6):
        for current in range(2):
            for bits in range(32):one[available,current,bits]=native.local_step(row(f.Q-1-available,current,0,bits,0),lib).f1
        for current in range(2):
            for flag1 in range(2):
                for bits in range(32):
                    out=native.local_step(row(available,0,current,7 if flag1 else 0,bits),lib)
                    assert out.f1==flag1;two[available,current,flag1,bits]=out.f2
    return one,two


def audit(stem,output):
    stem,output=Path(stem),Path(output)
    if output.exists():raise FileExistsError('preserve evidence')
    root=Path(__file__).resolve().parents[2];x=json.loads(stem.with_suffix('.json').read_text())
    assert sha(stem.with_suffix('.npz'))==x['artifact_sha256'] and sha(stem.with_suffix('.tar.gz'))==x['archive_sha256']
    with tarfile.open(stem.with_suffix('.tar.gz')) as archive:
        assert set(archive.getnames())==set(x['source_sha256'])
        for name,digest in x['source_sha256'].items():assert sha(root/name)==digest==hashlib.sha256(archive.extractfile(name).read()).hexdigest()
    assert x['rule']==json.loads(json.dumps(f.identity()))
    assert x['start_age']==98*f.Q and 0<x['ticks']<=f.U-98*f.Q
    assert x['final_age']==(x['start_age']+x['ticks'])%f.U
    with np.load(stem.with_suffix('.npz'),allow_pickle=False) as a:
        nodes=a['nodes'];queries=a['queries'];initial=int(a['initial']);final=int(a['final']);runs=a['cutoff_runs']
    assert nodes.shape==(x['nodes'],3) and queries.shape==(x['queries'],3)
    assert sha(x['source_checkpoint'])==x['source_checkpoint_sha256']
    with np.load(x['source_checkpoint'],allow_pickle=False) as a:np.testing.assert_array_equal(a['runs'],runs)
    intern={}
    for i,row in enumerate(nodes):
        level,left,right=map(int,row)
        if level==0:assert left==right and left<1<<18;key=(0,left)
        else:
            assert left<i and right<i and int(nodes[left,0])==int(nodes[right,0])==level-1
            key=(level,left,right)
        assert key not in intern;intern[key]=i
    def join(left,right):
        level=int(nodes[left,0]);assert int(nodes[right,0])==level
        return intern[level+1,left,right]
    def leaf(value):return intern[0,value]
    one,two=tables();leaf_cache={}
    def local(left,center,right):
        key=(left,center,right)
        if key in leaf_cache:return leaf_cache[key]
        assert not(center&FIRST and center&LAST)
        a,b,c=left,center,right
        f1=(a&255)|((b&255)<<8)|((c&255)<<16)
        f2=((a>>8)&255)|(((b>>8)&255)<<8)|(((c>>8)&255)<<16)
        out1=out2=0
        for bit in range(8):
            pos=8+bit;available_r=min(5,7-bit) if b&LAST else 5;available_l=min(5,bit) if b&FIRST else 5
            rs=sum(((f1>>(pos+j))&1)<<(j-1) for j in range(1,6));ls=sum(((f2>>(pos-j))&1)<<(j-1) for j in range(1,6))
            next1=one[available_r,(f1>>pos)&1,rs];next2=two[available_l,(f2>>pos)&1,next1,ls]
            out1|=next1<<bit;out2|=next2<<bit
        value=(b&(FIRST|LAST))|out1|(out2<<8);leaf_cache[key]=value;return value
    checked={}
    for row in queries:
        node,t,out=map(int,row);level,left,right=map(int,nodes[node]);assert level>=2 and 0<t<=1<<(level-2)
        assert (node,t) not in checked
        if level==2:
            a,b=map(int,nodes[left,1:]);c,d=map(int,nodes[right,1:]);values=[int(nodes[v,1]) for v in (a,b,c,d)]
            expected=join(leaf(local(*values[:3])),leaf(local(*values[1:])))
        else:
            limit=1<<(level-3);first=min(t,limit);middle=join(int(nodes[left,2]),int(nodes[right,1]))
            a,b,c=(checked[part,first] for part in (left,middle,right))
            if t<=limit:expected=join(join(int(nodes[a,2]),int(nodes[b,1])),join(int(nodes[b,2]),int(nodes[c,1])))
            else:expected=join(checked[join(a,b),t-limit],checked[join(b,c),t-limit])
        assert out==expected;checked[node,t]=out
    assert checked[initial,x['ticks']]==final
    # Independent constant-byte partition of this actual saved input. Refuse
    # unsupported large nonconstant word repetitions rather than sample them.
    segments=[];begin=0
    for end,a,b in map(lambda row:tuple(map(int,row)),runs):
        values=[((a>>(8*j))&255)|(((b>>(8*j))&255)<<8) for j in range(8)]
        if len(set(values))==1:segments.append((end*8,values[0]))
        else:
            assert end-begin<=1024
            for word in range(begin,end):
                for j,value in enumerate(values):segments.append((word*8+j+1,value))
        begin=end
    period=x['colonies']*WORDS;assert segments[-1][0]==period
    ends=[end for end,value in segments];cuts={0,period,*ends}
    for c in range(x['colonies']):cuts.update((c*WORDS,c*WORDS+1,(c+1)*WORDS-1,(c+1)*WORDS))
    cuts=sorted(cuts);atoms=[]
    for start,end in zip(cuts,cuts[1:]):
        value=segments[bisect_right(ends,start)][1]
        if start%WORDS==0:value|=FIRST
        if start%WORDS==WORDS-1:value|=LAST
        atoms.append((end,value))
    ends=[end for end,value in atoms];uniform_cache={};initial_checked=set()
    def uniform(level,value):
        key=(level,value)
        if key not in uniform_cache:
            uniform_cache[key]=leaf(value) if not level else join(uniform(level-1,value),uniform(level-1,value))
        return uniform_cache[key]
    def verify_initial(node,offset):
        offset%=period;key=(node,offset)
        if key in initial_checked:return
        level,left,right=map(int,nodes[node]);i=bisect_right(ends,offset)
        if offset+(1<<level)<=ends[i]:assert node==uniform(level,atoms[i][1])
        else:
            assert level>0;verify_initial(left,offset);verify_initial(right,offset+(1<<(level-1)))
        initial_checked.add(key)
    level=int(nodes[initial,0]);verify_initial(initial,-(1<<(level-2)))
    counts_cache={}
    def counts(node,n):
        key=(node,n)
        if key in counts_cache:return counts_cache[key]
        level,left,right=map(int,nodes[node])
        if not n:out=(0,0)
        elif not level:out=((left&255).bit_count(),((left>>8)&255).bit_count())
        else:
            half=1<<(level-1);a=counts(left,min(n,half));b=counts(right,max(0,n-half));out=(a[0]+b[0],a[1]+b[1])
        counts_cache[key]=out;return out
    observed=counts(final,period);assert list(observed)==x['flag_counts']
    result=dict(passed=True,verifier_sha256=sha(__file__),source_files=len(x['source_sha256']),physical_ticks=x['ticks'],verified_queries=len(checked),nodes=len(nodes),native_local_table_checks=len(one)+len(two),distinct_verified_leaf_neighborhoods=len(leaf_cache),initial_periodic_subblocks=len(initial_checked),final_flag_counts=observed,artifact_sha256=x['artifact_sha256'],scope='complete saved light-cone derivation checked from native local rule tables; controller composition and forcing-window prefix audited separately')
    output.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2));return result


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('--input',type=Path,required=True);parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args();audit(args.input,args.output)
