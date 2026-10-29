"""Counted generic native software. No native/full-rule ISA operation.

Every input is a real READ of the17-record lower packed bank. Intermediates
use actual old voted Out20 words at explicit within-colony coordinates.
"""
import controller as c
import layout as l

RAM_BASE=l.P+l.CHUNKS+16
RAM={'RG':0,'LG':1,'RA':2,'LA':3,'RAE':4,'C1':5,'C2':6,'F1':7,'F2':9}


class Assembly:
    def __init__(self):self.rows=[];self.labels={}
    def mark(self,name):
        assert name not in self.labels;self.labels[name]=len(self.rows)
    def e(self,name,*args):self.rows.append((name,*args))
    def lit(self,r,v):self.e('LIT',r,v.bit_length(),v)
    def alu(self,fn,dst,a,b):self.e('ALU',c.ALU_NAMES.index(fn),dst,a,b)
    def cp(self,dst,src):self.alu('copy',dst,src,src)
    def br(self,cond,a,b,to):self.e('BR',cond,a,b,to)
    def jump(self,to):self.br(0,0,0,to)
    def call(self,to):self.e('CALL',to)
    def compile(self):
        at=[0]
        for row in self.rows:
            vals=tuple(0 if isinstance(v,str) else v for v in row[1:])
            at.append(at[-1]+len(c.encode(row[0],*vals)))
        labels={name:at[row] for name,row in self.labels.items()}
        resolved=[]
        for row in self.rows:
            resolved.append((row[0],*(labels[v] if isinstance(v,str) else v for v in row[1:])))
        # A failed size/fetch must be reported before silently truncating PC.
        invalid=[dict(row=i,pc=at[i],target=v) for i,row in enumerate(resolved)
                 for v in ([row[-1]] if row[0] in ('BR','CALL') else []) if v>=c.Q]
        beta=tuple(b for row in resolved for b in c.encode(*row)) if not invalid else None
        return dict(rows=resolved,labels=labels,positions=at,beta=beta,
                    bits=at[-1],invalid_targets=invalid)


def descriptor(base,width,adjust=False):
    assert 0<=base<4096 and 0<=width<=20
    return base|(width<<12)|(int(adjust)<<17)


def helpers(a):
    a.mark('RAW')
    a.lit(7,4095);a.alu('and',0,4,7)
    a.lit(7,20);a.alu('div',0,0,7)
    a.lit(7,l.P+2);a.alu('add',0,0,7);a.e('MOVE',0)
    a.lit(7,4095);a.alu('and',6,4,7)
    a.lit(7,20);a.alu('mod',6,6,7)
    a.lit(7,12);a.alu('shr',7,4,7)
    a.lit(0,31);a.alu('and',7,7,0)
    a.e('READ',0,5,6,7,0,0)
    a.lit(7,1<<17);a.alu('and',7,4,7);a.br(1,7,7,'RAW_DONE')
    a.lit(7,8);a.alu('sub',6,5,7);a.alu('sub',0,0,6)
    a.lit(7,c.Q-1);a.alu('and',0,0,7)
    a.mark('RAW_DONE');a.e('RET')

    # Four loop-control/native registers R1..R4 survive each RAM helper.
    # LOAD5 also preserves R0, for comparing a RAW result against a cache.
    for label,kind,dst in (('RAMLOAD','READ',0),('RAMLOAD5','READ',5),('RAMSTORE','WRITE',0)):
        a.mark(label);a.lit(6,RAM_BASE+2);a.alu('add',5,5,6);a.e('MOVE',5)
        a.lit(6,0);a.lit(7,20)
        if kind=='READ':a.e('READ',dst,6,6,7,0,1)
        else:a.e('WRITE',0,6,7,0)
        a.e('RET')

    a.mark('Q5')
    # Link13 in bits6..18, candidate index in0..2, match count in3..5.
    # RAW preserves this real Word20 register across every nested call.
    a.e('GETHEAD',3,4);a.lit(7,6);a.alu('shl',3,3,7)
    a.mark('Q5_CANDIDATE');a.lit(7,7);a.alu('and',6,3,7);a.alu('add',5,1,6)
    a.call('RAW');a.cp(2,0);a.cp(5,1)
    a.mark('Q5_TEST');a.call('RAW');a.alu('eq',6,0,2)
    a.lit(7,3);a.alu('shl',6,6,7);a.alu('add',3,3,6)
    a.lit(7,1);a.alu('add',5,5,7)
    a.lit(7,5);a.alu('add',6,1,7);a.br(5,5,6,'Q5_TEST')
    a.lit(7,3);a.alu('shr',6,3,7);a.lit(7,7);a.alu('and',6,6,7)
    a.lit(7,3);a.br(6,7,6,'Q5_FOUND')
    a.lit(7,c.MASK^56);a.alu('and',3,3,7)
    a.lit(7,1);a.alu('add',3,3,7)
    a.lit(7,7);a.alu('and',6,3,7);a.lit(7,5);a.br(5,6,7,'Q5_CANDIDATE')
    a.lit(5,8);a.call('RAW');a.lit(6,0);a.jump('Q5_RETURN')
    a.mark('Q5_FOUND');a.cp(0,2);a.lit(6,1)
    a.mark('Q5_RETURN');a.lit(7,6);a.alu('shr',7,3,7);a.e('SETHEAD',7,4);a.e('RET')


def load(a,name,alternate=False):
    a.lit(5,RAM[name]);a.call('RAMLOAD5' if alternate else 'RAMLOAD')


def store(a,name):
    a.lit(5,RAM[name]);a.call('RAMSTORE')


def extract(a,source,shift,dst=0):
    if shift:a.lit(7,shift);a.alu('shr',dst,source,7)
    else:a.cp(dst,source)
    a.lit(7,15);a.alu('and',dst,dst,7)


def threshold(a,source,shift,n,dst=0):
    extract(a,source,shift,dst);a.lit(7,n);a.alu('le',dst,7,dst)


def set_loop_desc(a,base,width,adjust=False):
    a.lit(7,1<<18);a.alu('and',4,4,7)
    a.lit(7,descriptor(base,width,adjust));a.alu('or',4,4,7)
    a.lit(6,3);a.alu('add',5,3,6);a.call('RAW')


def counter_inside(a,reg,shift):
    a.lit(7,18);a.alu('shr',6,4,7);a.alu('and',0,0,6)
    if shift:a.lit(7,shift);a.alu('shl',0,0,7)
    a.alu('add',reg,reg,0)


def native_program(printed=False):
    a=Assembly()
    for field,side,dest in ((0,9,'RG'),(0,3,'LG'),(13,9,'RA'),(13,3,'LA')):
        a.lit(4,descriptor(field,13 if field==0 else 20,field==0))
        a.lit(1,side);a.call('Q5')
        if dest=='RG':a.lit(7,13);a.alu('shl',6,6,7);a.alu('or',0,0,6)
        if dest=='RA':a.cp(1,6)
        store(a,dest)
        if dest=='RA':a.cp(0,1);store(a,'RAE')
    a.lit(1,0);a.lit(2,0);a.lit(3,0)
    a.mark('CELL')
    a.lit(6,3);a.alu('add',5,3,6)
    load(a,'RG')
    a.lit(7,c.Q-1);a.alu('and',6,0,7)
    # RAMLOAD changes R5; recover lane before the signed-range calculation.
    a.lit(7,3);a.alu('add',5,3,7)
    a.alu('add',6,6,5);a.lit(7,8);a.alu('sub',6,6,7)
    a.lit(7,c.Q);a.alu('lt',6,6,7)
    a.lit(7,13);a.alu('shr',0,0,7);a.alu('and',6,6,0)
    a.lit(7,18);a.alu('shl',4,6,7)
    a.lit(7,5);a.br(6,7,3,'LEFT_DONE')
    a.lit(7,12);a.alu('shl',6,6,7);a.alu('add',2,2,6)
    set_loop_desc(a,0,13,True);load(a,'RG',True)
    a.lit(7,c.Q-1);a.alu('and',5,5,7);a.alu('ne',0,0,5)
    counter_inside(a,1,0)
    set_loop_desc(a,13,20);load(a,'RA',True);a.alu('ne',0,0,5)
    counter_inside(a,1,4)
    set_loop_desc(a,34,1)
    a.lit(7,4);a.alu('shl',6,0,7);a.alu('add',2,2,6)
    counter_inside(a,2,8)
    a.mark('LEFT_DONE');a.lit(7,5);a.br(6,3,7,'RIGHT_DONE')
    set_loop_desc(a,33,1);counter_inside(a,1,8)
    a.mark('RIGHT_DONE')
    set_loop_desc(a,35,1);counter_inside(a,1,12)
    set_loop_desc(a,36,1);counter_inside(a,2,0)
    a.lit(7,1);a.alu('add',3,3,7);a.lit(7,11);a.br(5,3,7,'CELL')
    a.cp(0,1);store(a,'C1');a.cp(0,2);store(a,'C2')

    a.lit(4,descriptor(33,1));a.lit(5,8);a.call('RAW');a.cp(3,0)
    load(a,'C1');a.cp(1,0)
    load(a,'RG');a.lit(7,13);a.alu('shr',0,0,7);a.lit(7,0);a.alu('eq',2,0,7)
    load(a,'RAE');a.lit(7,0);a.alu('eq',0,0,7);a.alu('or',2,2,0)
    for shift in (0,4,12,8):threshold(a,1,shift,3);a.alu('or',2,2,0)
    threshold(a,1,8,2);a.alu('and',0,0,3);a.alu('or',2,2,0)
    a.cp(0,2);store(a,'F1')
    load(a,'RG');a.lit(7,13);a.alu('shr',0,0,7);a.lit(7,0);a.alu('eq',1,0,7)
    load(a,'LA');a.lit(7,1);a.alu('add',0,0,7);a.lit(7,15);a.alu('and',0,0,7)
    a.lit(7,0);a.alu('eq',0,0,7);a.alu('and',1,1,0)
    load(a,'C2');a.cp(3,0);threshold(a,3,0,3);a.alu('or',1,1,0)
    load(a,'F1');a.cp(2,0)
    a.lit(4,descriptor(34,1));a.lit(5,8);a.call('RAW');a.br(1,0,0,'TURNON')
    a.br(2,2,2,'FLAGGED_KEEP')
    extract(a,3,8)
    if printed:extract(a,3,12,6);a.alu('eq',0,0,6)
    else:a.lit(7,1);a.alu('le',0,0,7)
    a.jump('KEEP_END')
    a.mark('FLAGGED_KEEP');extract(a,3,4);a.lit(7,0);a.alu('eq',0,0,7)
    a.mark('KEEP_END');a.lit(7,0);a.alu('eq',0,0,7);a.alu('or',0,0,1);a.jump('F2_DONE')
    a.mark('TURNON');threshold(a,3,8,4);threshold(a,3,4,4,6)
    a.alu('and',6,6,2);a.alu('or',0,0,6);a.alu('or',0,0,1)
    a.mark('F2_DONE');store(a,'F2')
    load(a,'F1');a.lit(7,0);a.alu('eq',1,0,7)
    load(a,'F2');a.alu('or',1,1,0)
    load(a,'RG');a.lit(7,13);a.alu('shr',0,0,7);a.alu('and',1,1,0)
    a.lit(5,RAM['LG']);a.alu('sub',5,5,1);a.call('RAMLOAD')
    a.lit(7,c.Q-1);a.alu('and',3,0,7)
    a.lit(5,RAM['LA']);a.alu('sub',5,5,1);a.call('RAMLOAD')
    a.lit(7,1);a.alu('add',4,0,7)
    for src,base,width in ((3,0,13),(4,13,20)):
        a.lit(5,l.P+base//20+2);a.e('MOVE',5)
        a.lit(6,base%20);a.lit(7,width);a.e('WRITE',src,6,7,0)
    for name,base in (('F1',33),('F2',34)):
        load(a,name);a.lit(5,l.P+base//20+2);a.e('MOVE',5)
        a.lit(6,base%20);a.lit(7,1);a.e('WRITE',0,6,7,0)
    a.e('HALT');helpers(a)
    out=a.compile();out['printed_Flag2']=printed
    out['RAM_BASE']=RAM_BASE;out['RAM_words']=RAM
    return out
