"""GBP1R's concrete Word20 emitter, UNDER DEVELOPMENT, not an own-beta proof.

This backend records exact bits/PC references and refuses Q overflow. The
native/final-source/non-head sections below use only declared CPU opcodes.
The full Head interpreter section is still to be emitted; no prefix is called
the own programme. This file is deliberately not registered/frozen yet.
"""
from dataclasses import dataclass
import binary_own_rule_rom_v2 as b

@dataclass(frozen=True)
class Label:
    name:str

class Assembler:
    def __init__(self):self.items=[];self.counter=0
    def label(self,name):self.items.append(('label',name));return Label(name)
    def fresh(self,stem):self.counter+=1;return f'{stem}_{self.counter}'
    def emit(self,op,*args):
        assert len(args)==len(b.ARGS[op])
        self.items.append(('instruction',op,args))
    def lit(self,r,value):self.emit('LIT',r,value&b.MASK)
    def op(self,fn,d,a,c):self.emit('ALU',d,a,c,b.ALU[fn])
    def jump(self,label):self.emit('JMP',Label(label))
    def bnz(self,r,label):self.emit('BNZ',r,Label(label))
    def data(self,name,words):
        self.items.append(('label',name));self.items.append(('data',tuple(words)))
    def listing(self):
        pc=0;labels={};rows=[]
        for item in self.items:
            if item[0]=='label':
                assert item[1] not in labels;labels[item[1]]=pc
            elif item[0]=='instruction':
                op,args=item[1:];size=4+sum(b.ARGS[op]);rows.append((pc,op,args,size));pc+=size
            else:
                words=item[1];rows.append((pc,'DATA20',words,20*len(words)));pc+=20*len(words)
        return pc,labels,rows
    def assemble(self):
        length,labels,rows=self.listing();bits=[];invalid=[]
        for pc,op,args,size in rows:
            if op=='DATA20':
                bits.extend((word>>i)&1 for word in args for i in range(20));continue
            values=[]
            for arg,width in zip(args,b.ARGS[op]):
                value=labels[arg.name] if isinstance(arg,Label) else arg
                if not 0<=value<1<<width:invalid.append((pc,op,value,width))
                values.append(value&((1<<width)-1))
            bits.extend(b.encode(op,*values))
        assert len(bits)==length
        if length>b.CODE_BITS or invalid:
            raise ProgrammeOverflow({'bits':length,'capacity':b.CODE_BITS,'invalid_references':invalid,
                                     'instructions':sum(op!='DATA20' for _,op,_,_ in rows)})
        return tuple(bits)+(0,)*(b.CODE_BITS-length),labels,rows

class ProgrammeOverflow(Exception):pass

class OwnEmitter:
    # R10 is copy q; R9 is the selected logical centre; R8 is computed Age;
    # R7 is logical Address; R4 is reader Flag1. Leaf I/O uses R0 and R5.
    def __init__(self):self.a=Assembler();self.offsets=b.offsets()
    def mov(self,d,s):self.a.emit('MOV',d,s)
    def load_native(self,centre=9):
        self.a.lit(5,b.PRIMARY_START);self.a.emit('LDB',5,centre);self.a.emit('NATIVE')
    def reader_native(self):
        self.a.lit(3,0);self.load_native(3)
    def nc(self,d,offset,width):
        self.a.lit(5,offset);self.a.emit('CGET',d,5,width)
    def store_native(self,r,offset,width):
        self.a.lit(5,b.PRIMARY_START+offset);self.a.emit('ST',r,5,width,1)
    def read(self,field,d=0,width=None,centre=9,bit=0):
        width=dict(b.FIELDS)[field] if width is None else width
        assert 1<=width<=20
        self.a.lit(5,self.offsets[field][0]+5*bit)
        self.a.emit('LDV',d,5,centre,width)
    def output(self,field,r=0,width=None,bit=0):
        width=dict(b.FIELDS)[field] if width is None else width
        assert 1<=width<=20
        self.a.lit(5,self.offsets[field][0]+5*bit)
        self.a.op('add',5,5,10);self.a.emit('ST',r,5,width,5)
    def eq(self,r,value,out=3):
        self.a.lit(5,value);self.a.op('eq',out,r,5)
    def less(self,r,value,out=3):
        self.a.lit(5,value);self.a.op('lt',out,r,5)
    def on_age(self,value,label):self.eq(8,value);self.a.bnz(3,label)
    def reset_branch(self,label,stages=None):
        for value in b.RESET if stages is None else stages:self.on_age(value,label)
    def shift_source(self,delta):
        self.a.lit(5,delta);self.a.op('add',9,9,5)
    def load_head_work(self):
        # Native only: the actual old voted 407-bit work is loaded, not a
        # selected future command. Source R9 survives every load/operation.
        self.a.lit(1,0);loop=self.a.fresh('work_load');end=self.a.fresh('work_done')
        self.a.label(loop)
        self.a.lit(2,100);self.a.op('mul',5,1,2)
        self.a.lit(2,self.offsets['head'][0]+5*b.PACKET_BITS);self.a.op('add',5,5,2)
        self.a.emit('LDV',0,5,9,20)
        self.a.lit(2,20);self.a.op('eq',3,1,2)
        tail=self.a.fresh('work_not_tail');self.a.op('not',3,3,3);self.a.bnz(3,tail)
        self.a.lit(2,127);self.a.op('and',0,0,2);self.a.label(tail)
        self.a.emit('WSET',1,0)
        self.a.lit(2,1);self.a.op('add',1,1,2)
        self.a.lit(2,21);self.a.op('lt',3,1,2);self.a.bnz(3,loop);self.a.label(end)
    def native_outputs_and_final_workspace(self):
        a=self.a;self.reader_native()
        for offset,width in ((0,13),(13,20),(33,1),(34,1)):
            self.nc(0,offset,width);self.store_native(0,offset,width)
        # Save the reader's wipe before a source-native call overwrites nc.
        self.nc(4,33,1);a.lit(9,0)
        a.lit(5,b.PRIMARY_START);a.emit('LDC',0,5,9,13)
        self.nc(1,0,13);a.op('eq',0,0,1);a.op('not',0,0,0);a.op('and',2,0,4)
        no_source=a.fresh('workspace_zero');workspace_done=a.fresh('workspace_done')
        a.bnz(2,no_source)
        self.nc(8,13,20)
        self.less(8,96*b.Q);a.bnz(3,no_source)
        self.less(8,98*b.Q);a.op('not',3,3,3);a.bnz(3,no_source)
        # Final-source helper returns one Info bit, clobbering nc but no
        # return register. It is inlined twice; each route has true input17.
        right_zero=a.fresh('right_source_zero');right_done=a.fresh('right_source_done')
        self.nc(7,0,13);self.less(7,b.Q-5);a.bnz(3,right_zero)
        a.lit(9,b.Q-3);a.op('sub',9,9,7);self.final_source()
        self.store_native(0,35,1);a.jump(right_done)
        a.label(right_zero);a.lit(0,0);self.store_native(0,35,1)
        a.label(right_done);self.reader_native();self.nc(4,33,1);self.nc(7,0,13)
        left_zero=a.fresh('left_source_zero');left_done=a.fresh('left_source_done')
        a.bnz(4,left_zero);self.less(7,5);a.op('not',3,3,3);a.bnz(3,left_zero)
        a.lit(9,3);a.op('sub',9,9,7);self.final_source()
        self.store_native(0,36,1);a.jump(left_done)
        a.label(left_zero);a.lit(0,0);self.store_native(0,36,1)
        a.label(left_done);a.jump(workspace_done)
        a.label(no_source);a.lit(0,0)
        self.store_native(0,35,1);self.store_native(0,36,1)
        a.label(workspace_done);self.reader_native()
    def final_source(self):
        # Exact all-raw final computed source: commit precedes Workspace read;
        # mandatory wipe belongs to the source, not the reader. No silence or
        # common-upper-clock assumption appears here.
        a=self.a;self.load_native();self.nc(7,0,13);self.nc(8,13,20);self.nc(4,33,1)
        self.read('info');self.mov(3,0)
        commit=a.fresh('source_commit');delivery=a.fresh('source_delivery');selected=a.fresh('source_selected')
        self.eq(8,0,out=2);a.bnz(2,commit)
        self.eq(8,b.DELIVERY,out=2);a.bnz(2,delivery);a.jump(selected)
        a.label(commit);self.read('next');self.mov(3,0);a.jump(selected)
        a.label(delivery)
        left=a.fresh('source_left');right=a.fresh('source_right')
        self.eq(7,3,out=2);a.bnz(2,left);self.eq(7,b.Q-3,out=2);a.bnz(2,right);a.jump(selected)
        a.label(left);self.read('courierL');self.mov(3,0);a.jump(selected)
        a.label(right);self.read('courierR');self.mov(3,0)
        a.label(selected)
        a.lit(5,b.PRIMARY_START);a.emit('LDC',0,5,9,13)
        a.op('eq',0,0,7);a.op('not',0,0,0);a.op('and',0,0,4)
        clean=a.fresh('source_not_wiped');a.op('not',0,0,0);a.bnz(0,clean);a.lit(3,0)
        a.label(clean);self.mov(0,3)
    def logical_controls(self):
        self.nc(7,0,13);self.nc(8,13,20);self.nc(4,33,1)
        self.a.op('add',7,7,9);self.a.lit(5,b.Q-1);self.a.op('and',7,7,5)
    def info_field(self):
        a=self.a;self.read('info');done=a.fresh('info_done');commit=a.fresh('info_commit')
        self.on_age(0,commit)
        special=a.fresh('info_special');self.eq(8,b.DELIVERY);a.bnz(3,special);a.jump(done)
        a.label(commit);self.read('next');a.jump(done)
        a.label(special);left=a.fresh('info_left');right=a.fresh('info_right')
        self.eq(7,3);a.bnz(3,left);self.eq(7,b.Q-3);a.bnz(3,right);a.jump(done)
        a.label(left);self.read('courierL');a.jump(done)
        a.label(right);self.read('courierR');a.label(done);self.output('info')
    def next_field(self):
        a=self.a;self.read('next');zero=a.fresh('next_zero');done=a.fresh('next_done')
        self.reset_branch(zero);a.jump(done);a.label(zero);a.lit(0,0);a.label(done);self.output('next')
    def mail_field(self,field):
        a=self.a;self.read(field);zero=a.fresh(field+'_zero');load=a.fresh(field+'_load')
        move=a.fresh(field+'_move');mask=a.fresh(field+'_mask');done=a.fresh(field+'_done')
        self.reset_branch(zero)
        for t in (1,32*b.Q+1,64*b.Q+1):self.on_age(t,load)
        for g in range(3):
            skip=a.fresh('mail_interval_skip');self.less(8,32*g*b.Q);a.bnz(3,skip)
            self.less(8,(32*g+16)*b.Q);a.bnz(3,move);a.label(skip)
        a.jump(mask);a.label(load);self.read('info');a.jump(mask)
        a.label(move);delta=1 if field=='mailL' else -1
        self.shift_source(delta);self.read(field);self.shift_source(-delta);a.jump(mask)
        a.label(zero);a.lit(0,0);a.label(mask);a.bnz(4,zero if False else done+'_zero')
        a.jump(done);a.label(done+'_zero');a.lit(0,0);a.label(done);self.output(field)
    def history_field(self,g):
        a=self.a;field='history'+str(g+1);self.read(field);self.mov(1,0)
        zero=a.fresh('history_zero');done=a.fresh('history_done');loop=a.fresh('history_lane')
        self.reset_branch(zero,(32*k*b.Q for k in range(g+1)))
        a.lit(2,0);a.label(loop)
        # R2 lane b, R3 signed offset; bit events use only true old Mail/Info.
        a.lit(5,8);a.op('sub',3,2,5)
        centre=a.fresh('history_centre');left=a.fresh('history_left');event=a.fresh('history_event')
        self.eq(2,8,out=0);a.bnz(0,centre)
        self.less(2,8,out=0);a.bnz(0,left)
        a.lit(5,b.Q);a.op('mul',0,3,5);a.lit(5,32*g*b.Q+2);a.op('add',0,0,5);a.jump(event)
        a.label(left);a.lit(5,0);a.op('sub',0,5,3);a.lit(5,b.Q);a.op('mul',0,0,5)
        a.lit(5,32*g*b.Q+2);a.op('add',0,0,5);a.jump(event)
        a.label(centre);a.lit(0,32*g*b.Q+1)
        a.label(event);a.op('eq',0,0,8)
        skip=a.fresh('history_skip');a.op('not',0,0,0);a.bnz(0,skip)
        source_centre=a.fresh('history_read_centre');source_left=a.fresh('history_read_left');source_done=a.fresh('history_source_done')
        self.eq(2,8,out=0);a.bnz(0,source_centre);self.less(2,8,out=0);a.bnz(0,source_left)
        self.read('mailL');a.jump(source_done)
        a.label(source_left);self.read('mailR');a.jump(source_done)
        a.label(source_centre);self.read('info');a.label(source_done)
        a.lit(5,1);a.op('shl',5,5,2);a.op('invert',3,5,5);a.op('and',1,1,3)
        a.op('shl',0,0,2);a.op('or',1,1,0)
        a.label(skip);a.lit(5,1);a.op('add',2,2,5);self.less(2,17,out=0);a.bnz(0,loop)
        self.mov(0,1);a.jump(done);a.label(zero);a.lit(0,0);a.label(done);self.output(field)
    def courier_field(self,left):
        a=self.a;field='courierL' if left else 'courierR';dest=3 if left else b.Q-3
        self.read(field);self.mov(1,0)
        zero=a.fresh('courier_zero');eval_=a.fresh('courier_evaluate');done=a.fresh('courier_done')
        self.reset_branch(zero);self.on_age(b.EVALUATE,eval_)
        self.less(8,b.EVALUATE+1);a.bnz(3,done)
        self.less(8,80*b.Q);a.op('not',3,3,3);a.bnz(3,done)
        self.less(7,min(dest,b.COLLECTOR));a.bnz(3,zero)
        self.less(7,max(dest,b.COLLECTOR)+1);a.op('not',3,3,3);a.bnz(3,zero)
        delta=1 if left else -1;self.shift_source(delta);self.read(field);self.shift_source(-delta)
        not_dest=a.fresh('courier_not_destination');self.eq(7,dest);a.op('not',3,3,3);a.bnz(3,not_dest)
        a.op('or',0,0,1);a.label(not_dest);a.jump(done)
        a.label(eval_);self.eq(7,b.COLLECTOR);a.op('not',3,3,3);a.bnz(3,zero)
        self.load_head_work();a.emit('NATIVE');self.nc(0,34 if left else 33,1);a.jump(done)
        a.label(zero);a.lit(0,0);a.label(done);self.output(field)
        self.reader_native();self.logical_controls()

    def prefix(self):
        """Emitted sections, NOT a full own programme or equivalence proof."""
        self.native_outputs_and_final_workspace()
        # This explicit first-copy prefix restores its offset after the
        # final-source calculations. A full emitter needs a five-copy loop.
        self.a.lit(9,0);self.a.lit(10,0)
        self.logical_controls();self.info_field();self.next_field()
        self.mail_field('mailL');self.mail_field('mailR')
        for g in range(3):self.history_field(g)
        self.courier_field(True);self.courier_field(False)
        self.a.emit('HLT')
        return self.a

if __name__=='__main__':
    emitter=OwnEmitter();asm=emitter.prefix();length,labels,rows=asm.listing()
    print({'scope':'INCOMPLETE native+one-copy non-head prefix',
           'bits':length,'instructions':len(rows),'head_kernel':'not yet emitted',
           'own_beta_proved':False,'deadline_proved':False})
