"""Exhaustive canonical unforced flag tables from the complete native rule."""
from . import delivery_rule as f,delivery_native as native


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

