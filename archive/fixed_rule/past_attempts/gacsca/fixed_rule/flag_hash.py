"""Memoized physical Flag2 spacetime blocks after Flag1 and Wf are zero.

This accelerates the physical radius-five Boolean subsystem, not an encoded
controller or simulated upper transition. A leaf packs 64 adjacent F2 sites and
a fixed first-word boundary tag. Its transition reads only that word and its
left neighbor. Binary tree levels are memoization geometry, NOT CA hierarchy
levels; no physical alphabet, F description or P changes.
"""
from .delivery_rule import Q,U

MASK=(1<<64)-1
FIRST=1<<64
WORDS=Q//64


def leaf_step(left,center):
    value=center&MASK;first=bool(center&FIRST)
    planes=[((value<<j)|(0 if first else ((left&MASK)>>(64-j))))&MASK for j in range(1,6)]
    a,b,c,d,e=planes;ab=a&b;cd=c&d
    four=(ab&cd)|(ab&e&(c|d))|(cd&e&(a|b))
    erase=MASK
    for j,plane in enumerate(planes,1):erase&=plane|((1<<j)-1 if first else 0)
    return (center&FIRST)|(((~value)&four)|(value&~erase))


class Engine:
    """Hash-consed binary physical blocks and certified causal-half updates."""
    def __init__(self):
        self.nodes=[];self.intern={};self.cache={};self.period_cache={};self.leaf_evaluations=0
    def leaf(self,value):
        if not isinstance(value,int) or not 0<=value<1<<65:raise ValueError('finite physical word/tag required')
        key=(0,value)
        if key not in self.intern:self.intern[key]=len(self.nodes);self.nodes.append((0,value,value))
        return self.intern[key]
    def join(self,left,right):
        level=self.nodes[left][0]
        if level!=self.nodes[right][0]:raise ValueError('equal spatial block sizes required')
        key=(level+1,left,right)
        if key not in self.intern:self.intern[key]=len(self.nodes);self.nodes.append(key)
        return self.intern[key]
    def uniform(self,value,level):
        node=self.leaf(value)
        for _ in range(level):node=self.join(node,node)
        return node
    def periodic(self,pattern,level,offset=0):
        pattern=tuple(pattern);offset%=len(pattern);key=(pattern,level,offset)
        if key in self.period_cache:return self.period_cache[key]
        if level==0:node=self.leaf(pattern[offset])
        else:
            half=1<<(level-1);node=self.join(self.periodic(pattern,level-1,offset),self.periodic(pattern,level-1,offset+half))
        self.period_cache[key]=node;return node
    def set(self,node,position,value):
        level,left,right=self.nodes[node]
        if not 0<=position<1<<level:raise ValueError('position outside block')
        if level==0:return self.leaf(value)
        half=1<<(level-1)
        return self.join(self.set(left,position,value),right) if position<half else self.join(left,self.set(right,position-half,value))
    def at(self,node,position):
        level,left,right=self.nodes[node]
        if not 0<=position<1<<level:raise ValueError('position outside block')
        while level:
            half=1<<(level-1);node=left if position<half else right
            if position>=half:position-=half
            level,left,right=self.nodes[node]
        return left
    def half(self,node,ticks):
        """Right spatial half after ticks <= half-width physical transitions.

        Each packed-word output reads only itself and its left neighbor, so the
        supplied left half contains the entire required physical light cone.
        Memoization never substitutes an upper-level transition.
        """
        level,left,right=self.nodes[node]
        if level<1 or not 0<=ticks<=1<<(level-1):raise ValueError('invalid causal-half query')
        if not ticks:return right
        key=(node,ticks)
        if key in self.cache:return self.cache[key]
        if level==1:
            self.leaf_evaluations+=1;out=self.leaf(leaf_step(self.nodes[left][1],self.nodes[right][1]))
        else:
            quarter=1<<(level-2);middle=self.join(self.nodes[left][2],self.nodes[right][1])
            if ticks<=quarter:
                out=self.join(self.half(middle,ticks),self.half(right,ticks))
            else:
                a,b,c=(self.half(part,quarter) for part in (left,middle,right))
                rest=ticks-quarter;out=self.join(self.half(self.join(a,b),rest),self.half(self.join(b,c),rest))
        self.cache[key]=out;return out
    def advance(self,node,ticks):
        if not isinstance(ticks,int) or ticks<0:raise ValueError('nonnegative physical ticks required')
        level=self.nodes[node][0]
        while (1<<level)<ticks:node=self.join(node,self.uniform(0,level));level+=1
        return self.half(self.join(self.uniform(0,level),node),ticks)
