"""Fully counted proposed raw fields; not a whole-rule implementation."""
Q=8192;U=128*Q
NATIVE=(('GF',13),('Age',20),('Flag1',1),('Flag2',1),('WF1',1),('WF2',1))
SF=(('Info',1),('Mailbox',4),('History',51),('Mem',340),('InputTag',14),
    ('Out',20),('OutputTag',14),('Scratch',20),('Couriers',2),('Head',204))
NATIVE_OFFSETS={};SF_OFFSETS={};at=0
for name,n in NATIVE:NATIVE_OFFSETS[name]=at;at+=n
assert at==37
for name,n in SF:SF_OFFSETS[name]=at;at+=5*n
K=at;P=Q//2-K//2;CHUNKS=(K+19)//20
assert (K,P,CHUNKS)==(3387,2403,170)
assert SF_OFFSETS['Head']==2367
HEAD_REG0_BIT=44
REG0_BASE=SF_OFFSETS['Head']+5*HEAD_REG0_BIT
assert REG0_BASE==2587

def sf_bit(name,bit,slot):
    assert name in SF_OFFSETS and 0<=slot<5
    width=dict(SF)[name];assert 0<=bit<width
    return SF_OFFSETS[name]+5*bit+slot

def upper_SF_word(records,centre,name,bit,count):
    S=(0,-2,-1,1,2);INV=(0,4,3,2,1)
    out=0
    for i in range(count):
        values=[(records[centre+S[h]]>>sf_bit(name,bit+i,INV[h]))&1 for h in range(5)]
        out|=int(sum(values)>=3)<<i
    return out

def bank_container(records,chunk):
    """The actual17-lane binary-record bank after coherent packing.

    The records are arbitrary raw K-bit values, including incoherent
    upper SF copies. No expected logical SF word is inserted into this bank.
    """
    result=0
    for lane in range(17):
        record=records[lane-8]
        for bit in range(20):
            i=20*chunk+bit
            result|=(((record>>i)&1) if i<K else 0)<<(20*lane+bit)
    return result
