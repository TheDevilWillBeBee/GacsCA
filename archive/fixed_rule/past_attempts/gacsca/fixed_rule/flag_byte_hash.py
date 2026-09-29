"""Exact memoized physical F1/F2 light cones after Wf cutoff.

Leaves pack eight neighboring physical flag pairs and fixed colony-edge tags.
No simulated controller, upper transition, hierarchy level or rule program is
interpreted by this engine. Every cached block derives from the same radius-five
physical Boolean transition. Initial data is periodic on the actual finite ring.
"""
from bisect import bisect_right
from .flag_hash import Engine as Base
from .delivery_rule import Q,U

BITS=8
MASK=(1<<BITS)-1
FIRST=1<<(2*BITS)
LAST=1<<(2*BITS+1)
WORDS=Q//BITS


def count(planes):
    a,b,c,d,e=planes;s=a^b^c;k=(a&b)|(a&c)|(b&c);l=(s&d)|(s&e)|(d&e)
    return k|l,(k&l)|((s^d^e)&(k|l)),k&l


def leaf_step(left,center,right):
    f,g=center&MASK,(center>>BITS)&MASK;rf=right&MASK;lg=(left>>BITS)&MASK
    rr=[((f>>j)|(rf<<(BITS-j)))&((MASK>>j) if center&LAST else MASK) for j in range(1,6)]
    two,three,_=count(rr);nextf=three|(f&two)
    ll=[((g<<j)|(lg>>(BITS-j)))&MASK for j in range(1,6)]
    inside=[v&(MASK<<j) for j,v in enumerate(ll,1)] if center&FIRST else ll
    eraseinside=MASK
    for j,v in enumerate(ll,1):eraseinside&=v|((1<<j)-1 if center&FIRST else 0)
    _,_,global4=count(ll);_,_,inside4=count(inside)
    on=inside4|(nextf&global4);anyleft=0
    for v in ll:anyleft|=v
    erase=((~nextf)&eraseinside)|(nextf&~anyleft)
    nextg=((g&~erase)|((~g)&on))&MASK
    return (center&(FIRST|LAST))|nextf|(nextg<<BITS)


class Engine(Base):
    def leaf(self,value):
        if not isinstance(value,int) or not 0<=value<1<<(2*BITS+2):raise ValueError('fixed physical pair/tag word required')
        key=(0,value)
        if key not in self.intern:self.intern[key]=len(self.nodes);self.nodes.append((0,value,value))
        return self.intern[key]
    def center(self,node,ticks):
        """Central half after at most quarter-width physical steps."""
        level,left,right=self.nodes[node]
        if level<2 or not isinstance(ticks,int) or not 0<=ticks<=1<<(level-2):raise ValueError('invalid symmetric light cone')
        if not ticks:return self.join(self.nodes[left][2],self.nodes[right][1])
        key=(node,ticks)
        if key in self.cache:return self.cache[key]
        if level==2:
            a,b=self.nodes[left][1:];c,d=self.nodes[right][1:]
            values=[self.nodes[x][1] for x in (a,b,c,d)];self.leaf_evaluations+=2
            out=self.join(self.leaf(leaf_step(*values[:3])),self.leaf(leaf_step(*values[1:])))
        else:
            limit=1<<(level-3);first=min(ticks,limit)
            middle=self.join(self.nodes[left][2],self.nodes[right][1])
            a,b,c=(self.center(part,first) for part in (left,middle,right))
            if ticks<=limit:
                out=self.join(self.join(self.nodes[a][2],self.nodes[b][1]),self.join(self.nodes[b][2],self.nodes[c][1]))
            else:
                rest=ticks-limit;out=self.join(self.center(self.join(a,b),rest),self.center(self.join(b,c),rest))
        self.cache[key]=out;return out
    def periodic_segments(self,segments,level,offset=0):
        ends=tuple(end for end,pattern in segments);patterns=tuple(pattern for end,pattern in segments);period=ends[-1];memo={}
        def build(k,start):
            start%=period;key=(k,start)
            if key in memo:return memo[key]
            i=bisect_right(ends,start)
            if start+(1<<k)<=ends[i]:out=self.periodic(patterns[i],k,start%len(patterns[i]))
            else:
                half=1<<(k-1);out=self.join(build(k-1,start),build(k-1,start+half))
            memo[key]=out;return out
        return build(level,offset)


def segments_from_words(runs,colonies):
    total=colonies*WORDS;rows=[tuple(map(int,row)) for row in runs];previous=0
    for end,a,b in rows:
        if not previous<end<=total//8 or not 0<=a<(1<<64) or not 0<=b<(1<<64):raise ValueError('invalid physical 64-site runs')
        previous=end
    if previous!=total//8:raise ValueError('incomplete physical ring')
    cuts={0,total,*[end*8 for end,a,b in rows]}
    for c in range(colonies):cuts.update((c*WORDS,c*WORDS+1,(c+1)*WORDS-1,(c+1)*WORDS))
    cuts=sorted(cuts);segments=[];i=0
    for start,end in zip(cuts,cuts[1:]):
        while rows[i][0]*8<=start:i+=1
        a,b=rows[i][1:]
        pattern=tuple(((a>>(BITS*j))&MASK)|(((b>>(BITS*j))&MASK)<<BITS) for j in range(8))
        tag=(FIRST if start%WORDS==0 else 0)|(LAST if start%WORDS==WORDS-1 else 0)
        if tag:pattern=(pattern[start%8]|tag,)
        if segments and segments[-1][1]==pattern:segments[-1]=(end,pattern)
        else:segments.append((end,pattern))
    return segments


def evolve(runs,colonies,age,ticks):
    if not isinstance(age,int) or not 98*Q<=age<U or not isinstance(ticks,int) or not 0<=ticks<=U-age:raise ValueError('unforced suffix interval required')
    segments=segments_from_words(runs,colonies);size=colonies*WORDS
    level=max(2,(max(ticks,(size+1)//2)-1).bit_length()+2)
    engine=Engine();quarter=1<<(level-2)
    initial=engine.periodic_segments(segments,level,-quarter)
    final=engine.center(initial,ticks)
    return engine,initial,final
