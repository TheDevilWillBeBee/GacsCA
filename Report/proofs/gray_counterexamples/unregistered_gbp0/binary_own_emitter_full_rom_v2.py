"""Complete GBP1R enlarged-ROM diagnostic own-transition emitter UNDER DEVELOPMENT.

The immutable bitcode is counted in full. This source has no total-rule or
host-CPU opcode: helpers use real LDV/LDC, generic Word20 arithmetic and CODE.
An overlong listing is a rejected emission, never an executable own beta.
"""
from binary_own_emitter_rom_v2 import OwnEmitter, Label, ProgrammeOverflow
import binary_own_rule_rom_v2 as b

class FullEmitter(OwnEmitter):
    # Own Work words 0..14 hold the upper metadata (nc in two words).
    # 15/16: changed register index/value; 17/18/19: work patch start/value/
    # width. Word20 is seven flags. Upper work is always fetched from Input.
    M={'p':0,'move':1,'mode':2,'pc':3,'index':4,'buf':5,
       'lane':6,'ret':7,'dst':8,'width':9,'kind':10,'start':11,
       'nclo':12,'nchi':13,'rdst':15,'rval':16,'wstart':17,
       'wval':18,'wwidth':19,'flags':20}
    def __init__(self):
        super().__init__();self.helper_labels={};self.meta_offsets={};o=0
        for f,w in b.META:self.meta_offsets[f]=(o,w);o+=w
    def mg(self,name,d=0):
        self.a.lit(5,self.M[name]);self.a.emit('WGET',d,5)
    def ms(self,name,r=0):
        self.a.lit(5,self.M[name]);self.a.emit('WSET',5,r)
    def ml(self,name,value):self.a.lit(0,value);self.ms(name)
    def flag(self,value):
        self.mg('flags');self.a.lit(5,value);self.a.op('or',0,0,5);self.ms('flags')
    def call(self,name):
        ret=self.a.fresh('return_'+name)
        self.a.emit('LIT',6,Label(ret));self.a.jump('helper_'+name);self.a.label(ret)
    def table(self,d,name,index):
        self.a.lit(5,20);self.a.op('mul',5,5,index)
        self.a.emit('LIT',2,Label('data_'+name));self.a.op('add',5,5,2)
        self.a.emit('CODE',d,5)
    def check_reg(self,r):
        self.less(r,b.REGISTERS,out=2)
        self.a.op('not',2,2,2);self.a.bnz(2,self.fail_label)
    def metadata_load(self):
        self.call('metadata_load')
    def service(self,d=0):
        # Holder-native Address plus declared copy offset, NOT a raw source GF.
        self.nc(3,0,13);self.table(0,'slots',10)
        self.a.op('add',d,0,3);self.a.lit(5,b.Q-1);self.a.op('and',d,d,5)
    def arg(self,offset,width,d=0):
        # R7/R8 are the two real immutable CODE windows, each Word20.
        a=self.a
        if offset>=20:
            a.lit(5,offset-20);a.op('shr',d,8,5)
        else:
            a.lit(5,offset);a.op('shr',d,7,5)
            if offset+width>20:
                a.lit(5,20-offset);a.op('shl',2,8,5);a.op('or',d,d,2)
        a.lit(5,(1<<width)-1);a.op('and',d,d,5)
    def op_args(self,name):
        z=4;out=[]
        for w in b.ARGS[name]:out.append((z,w));z+=w
        return out
    def get_arg(self,name,k,d=0):self.arg(*self.op_args(name)[k],d)
    def validate_args(self,name):
        positions={'HLT':(), 'MOV':(0,1), 'LIT':(0,), 'ALU':(0,1,2),
          'BNZ':(0,), 'JMP':(), 'WGET':(0,1), 'WSET':(0,1), 'NATIVE':(),
          'CGET':(0,1), 'LDV':(0,1,2), 'LDC':(0,1,2), 'LDB':(0,1),
          'ST':(0,1), 'CODE':(0,1), 'JREG':(0,)}[name]
        for k in positions:self.get_arg(name,k,1);self.check_reg(1)
    def reg_value(self,name,k):self.get_arg(name,k,1);self.call('reg_read')
    def changed_reg(self,name,k=0):
        self.ms('rval',0);self.get_arg(name,k,0);self.ms('rdst',0)
    def fail(self):
        self.ml('p',1);self.ml('mode',b.ERROR);self.ml('move',0)
        self.a.jump(self.packet_done)
    def finish_run(self):
        self.less(4,b.CODE_BITS,out=2);self.a.op('not',2,2,2);self.a.bnz(2,self.fail_label)
        self.ms('pc',4);self.ml('mode',b.RUN);self.ml('move',0)
        self.a.jump(self.packet_done)
    def move_to(self,target=1):
        # Uses actual logical output Address; target word remains unchanged.
        self.mov(4,target);self.service(0)
        equal=self.a.fresh('move_equal');left=self.a.fresh('move_left');done=self.a.fresh('move_done')
        self.a.op('eq',2,0,4);self.a.bnz(2,equal)
        self.a.op('lt',2,0,4);self.a.bnz(2,left)
        self.ml('move',2);self.a.jump(done)
        self.a.label(left);self.ml('move',1);self.a.jump(done)
        self.a.label(equal);self.ml('move',0);self.a.label(done)
    def signed_range(self,r,limit):
        valid=self.a.fresh('signed_valid')
        self.less(r,limit+1,out=2);self.a.bnz(2,valid)
        self.less(r,b.MASK-limit+1,out=2);self.a.bnz(2,self.fail_label)
        self.a.label(valid)
    def incoming_source(self):
        # Priority self, left, right and collision failure exactly match incoming.
        a=self.a;self.mov(7,9);a.lit(4,0);a.lit(8,0)
        for delta in (0,-1,1):
            a.lit(5,delta);a.op('add',9,7,5)
            self.read('head',width=3,bit=0);self.mov(3,0)
            a.lit(5,1);a.op('and',0,0,5)
            skip=a.fresh('no_incoming');a.op('not',0,0,0);a.bnz(0,skip)
            a.op('shr',0,3,5)
            if delta==0:
                eligible=a.fresh('self_eligible')
                self.eq(0,0,out=2);a.bnz(2,eligible)
                self.eq(0,3,out=2);a.op('not',2,2,2);a.bnz(2,skip);a.label(eligible)
            else:
                self.eq(0,1 if delta==-1 else 2,out=2)
                a.op('not',2,2,2);a.bnz(2,skip)
            already=a.fresh('already_chosen');a.bnz(4,already);self.mov(8,9);a.label(already)
            a.lit(5,1);a.op('add',4,4,5);a.label(skip)
        none=a.fresh('incoming_none');one=a.fresh('incoming_one')
        a.op('not',2,4,4);a.bnz(2,none)
        self.mov(9,8);self.mov(8,4);self.metadata_load()
        self.eq(8,1,out=2);a.bnz(2,one);a.jump(self.fail_label)
        a.label(none);self.mov(9,7);self.metadata_load();self.flag(16)
        a.jump(self.packet_done);a.label(one)
    def io_body(self):
        a=self.a
        self.mg('kind',1);self.less(1,4,out=2);a.op('not',2,2,2);a.bnz(2,self.fail_label)
        self.mg('dst',1);self.check_reg(1)
        db=a.fresh('io_ldb');valid=a.fresh('io_valid');self.mg('kind',1)
        self.eq(1,b.LDB,out=2);a.bnz(2,db)
        self.mg('width',1);a.op('not',2,1,1);a.bnz(2,self.fail_label)
        self.less(1,21,out=2);a.op('not',2,2,2);a.bnz(2,self.fail_label)
        self.mg('kind',2);store=a.fresh('io_store_valid');self.eq(2,b.STORE,out=3);a.bnz(3,store)
        self.mg('lane',1);self.signed5(1);self.signed_range(1,6)
        a.label(store);self.mg('width',1);self.mg('kind',2)
        notvote=a.fresh('io_not_vote');self.eq(2,b.LDV,out=3);a.op('not',3,3,3);a.bnz(3,notvote)
        a.lit(5,5);a.op('mul',1,1,5);a.label(notvote);self.mov(7,1);a.jump(valid)
        a.label(db);self.mg('width',1);self.eq(1,37,out=2);a.op('not',2,2,2);a.bnz(2,self.fail_label)
        self.mg('lane',1);self.signed5(1);self.signed_range(1,3);a.lit(7,37)
        a.label(valid);self.mg('index',1);a.op('lt',2,1,7);a.op('not',2,2,2);a.bnz(2,self.fail_label)
        # Count R7; target R8; final and current address must both be below Q.
        self.mg('kind',2);self.eq(2,b.STORE,out=3)
        stride=a.fresh('io_stride');targets=a.fresh('io_targets')
        a.bnz(3,stride);a.lit(2,1);a.jump(targets)
        a.label(stride);self.mg('lane',2);a.label(targets)
        a.op('mul',8,1,2);self.mg('start',3);a.op('add',8,8,3)
        a.lit(5,1);a.op('sub',1,7,5);a.op('mul',1,1,2);a.op('add',1,1,3)
        self.less(1,b.Q,out=2);a.op('not',2,2,2);a.bnz(2,self.fail_label)
        self.less(8,b.Q,out=2);a.op('not',2,2,2);a.bnz(2,self.fail_label)
        self.service(0);a.op('eq',2,0,8)
        arrived=a.fresh('io_arrived');a.bnz(2,arrived);self.move_to(8);a.jump(self.packet_done)
        a.label(arrived)
        self.mg('kind',1)
        for kind in range(4):
            self.eq(1,kind,out=2);a.bnz(2,self.io_labels[kind])
        a.jump(self.fail_label)
        # All IO cases return to the same true old-index increment block.
        a.label(self.io_labels[b.STORE]);self.mg('dst',1);self.call('reg_read')
        self.mg('index',1);a.op('shr',0,0,1);a.lit(5,1);a.op('and',0,0,5)
        a.lit(5,3);a.op('shl',0,0,5);a.lit(5,4);a.op('or',0,0,5);self.ms('flags')
        a.jump(self.io_advance)
        a.label(self.io_labels[b.LDB]);self.call('mem_read')
        self.mg('lane',1);self.signed5(1);a.lit(5,3);a.op('add',1,1,5)
        a.op('shr',0,0,1);a.lit(5,2047);a.op('and',0,0,5);self.ms('wval')
        self.mg('index',0);a.lit(5,11);a.op('mul',0,0,5);self.ms('wstart');self.ml('wwidth',11)
        a.jump(self.io_advance)
        a.label(self.io_labels[b.LDC]);self.call('mem_read')
        self.mg('lane',1);self.signed5(1);a.lit(5,8);a.op('add',1,1,5)
        a.op('shr',0,0,1);a.lit(5,1);a.op('and',3,0,5)
        self.mg('dst',1);self.call('reg_read');self.mg('index',1)
        self.patch_bit(0,1,3);self.ms('rval');self.mg('dst');self.ms('rdst')
        a.jump(self.io_advance)
        a.label(self.io_labels[b.LDV]);self.mg('index',0);a.lit(5,5)
        a.op('mod',1,0,5);a.op('div',8,0,5);self.mov(4,1)
        self.table(3,'slots',1);self.mg('lane',1);self.signed5(1)
        a.lit(5,8);a.op('add',1,1,5);a.op('sub',1,1,3);self.mov(3,1)
        self.ms('wstart',3);self.call('mem_read');self.mg('wstart',3)
        a.op('shr',0,0,3);a.lit(5,1);a.op('and',3,0,5);self.ml('wstart',511)
        self.mg('buf',0);self.patch_bit(0,4,3);self.ms('buf')
        self.eq(4,4,out=2);noquorum=a.fresh('io_vote_incomplete');a.op('not',2,2,2);a.bnz(2,noquorum)
        # A five-bit population count is an explicit bounded loop.
        self.mov(3,0);a.lit(4,0);a.lit(1,0);loop=a.fresh('count_bits');a.label(loop)
        a.op('shr',0,3,1);a.lit(5,1);a.op('and',0,0,5);a.op('add',4,4,0);a.op('add',1,1,5)
        self.less(1,5,out=2);a.bnz(2,loop)
        self.less(4,3,out=2);a.op('not',3,2,2)
        self.mg('dst',1);self.call('reg_read');self.patch_bit(0,8,3);self.ms('rval')
        self.mg('dst');self.ms('rdst');self.ml('buf',0);a.label(noquorum)
        a.jump(self.io_advance)
        a.label(self.io_advance);self.mg('index',0);a.lit(5,1);a.op('add',0,0,5);self.ms('index')
        a.op('eq',2,0,7);notfinished=a.fresh('io_not_finished');a.op('not',2,2,2);a.bnz(2,notfinished)
        self.mg('ret',4);self.finish_run()
        a.label(notfinished);self.mg('kind',2);self.eq(2,b.STORE,out=3)
        nostride=a.fresh('io_next_no_stride');targetdone=a.fresh('io_next_target_done')
        a.op('not',3,3,3);a.bnz(3,nostride);self.mg('lane',2);a.op('mul',0,0,2);a.jump(targetdone)
        a.label(nostride);a.label(targetdone);self.mg('start',1);a.op('add',1,1,0)
        self.move_to(1);a.jump(self.packet_done)
    def signed5(self,r):
        nonnegative=self.a.fresh('signed5_nonnegative');self.less(r,16,out=2);self.a.bnz(2,nonnegative)
        self.a.lit(5,32);self.a.op('sub',r,r,5);self.a.label(nonnegative)
    def patch_bit(self,value,index,bit):
        # All three inputs must be distinct from scratch R2/R5.
        self.a.lit(5,1);self.a.op('shl',2,5,index);self.a.op('invert',5,2,2)
        self.a.op('and',value,value,5);self.a.op('shl',bit,bit,index);self.a.op('or',value,value,bit)
    def run_body(self):
        a=self.a;self.mg('pc',1);a.emit('CODE',7,1)
        a.lit(5,20);a.op('add',1,1,5);a.emit('CODE',8,1)
        self.arg(0,4,1);self.table(4,'lengths',1);self.mg('pc',0);a.op('add',4,4,0)
        # Opcode selection preserves code words and the candidate successor PC.
        for name in b.OP_NAMES:self.eq(1,b.OP[name],out=2);a.bnz(2,self.op_labels[name])
        a.jump(self.fail_label)
        for name in b.OP_NAMES:
            a.label(self.op_labels[name]);self.validate_args(name)
            if name=='HLT':self.ml('mode',b.HALT);self.ml('move',0);a.jump(self.packet_done);continue
            if name=='MOV':self.reg_value(name,1);self.changed_reg(name)
            elif name=='LIT':self.get_arg(name,1);self.changed_reg(name)
            elif name=='ALU':
                self.reg_value(name,1);self.ms('wstart');self.reg_value(name,2);self.ms('wval')
                self.get_arg(name,3,3)
                labels=[a.fresh('alu_'+f) for f in b.ALU_NAMES];done=a.fresh('alu_done')
                for k,label in enumerate(labels):self.eq(3,k,out=2);a.bnz(2,label)
                for f,label in zip(b.ALU_NAMES,labels):
                    a.label(label);self.mg('wstart',1);self.mg('wval',2);a.op(f,0,1,2);a.jump(done)
                a.label(done);self.changed_reg(name);self.ml('wstart',511);self.ml('wwidth',0)
            elif name=='BNZ':
                self.reg_value(name,0);done=a.fresh('bnz_untaken');a.op('not',2,0,0);a.bnz(2,done)
                self.get_arg(name,1,4);a.label(done)
            elif name=='JMP':self.get_arg(name,0,4)
            elif name=='JREG':self.reg_value(name,0);self.mov(4,0)
            elif name=='CODE':self.reg_value(name,1);a.emit('CODE',0,0);self.changed_reg(name)
            elif name=='WGET':
                self.reg_value(name,1);self.less(0,21,out=2);a.op('not',2,2,2);a.bnz(2,self.fail_label)
                self.mov(1,0);self.call('work_read');self.changed_reg(name)
            elif name=='WSET':
                self.reg_value(name,0);self.less(0,21,out=2);a.op('not',2,2,2);a.bnz(2,self.fail_label)
                a.lit(5,20);a.op('mul',0,0,5);self.ms('wstart')
                self.reg_value(name,1);self.ms('wval');self.ml('wwidth',20)
            elif name=='NATIVE':self.flag(2)
            elif name=='CGET':
                self.reg_value(name,1);self.mov(1,0)
                zero=a.fresh('cget_zero');hi=a.fresh('cget_hi');done=a.fresh('cget_done')
                self.less(1,37,out=2);a.op('not',2,2,2);a.bnz(2,zero)
                self.less(1,20,out=2);a.op('not',2,2,2);a.bnz(2,hi)
                self.mg('nclo',0);a.op('shr',0,0,1);self.mg('nchi',3)
                a.lit(5,20);a.op('sub',2,5,1);a.op('shl',3,3,2);a.op('or',0,0,3);a.jump(done)
                a.label(hi);a.lit(5,20);a.op('sub',1,1,5);self.mg('nchi',0);a.op('shr',0,0,1);a.jump(done)
                a.label(zero);a.lit(0,0);a.label(done)
                self.get_arg(name,2,1);a.lit(5,1);a.op('shl',2,5,1);a.op('sub',2,2,5);a.op('and',0,0,2)
                self.changed_reg(name)
            else:self.io_enter(name);continue
            self.finish_run()
    def io_enter(self,name):
        a=self.a;self.less(4,b.CODE_BITS,out=2);a.op('not',2,2,2);a.bnz(2,self.fail_label)
        # Validate every entry premise before changing any record or register.
        targetk=0 if name=='LDB' else 1
        self.reg_value(name,targetk);self.less(0,b.Q,out=2);a.op('not',2,2,2);a.bnz(2,self.fail_label)
        self.mov(3,0)
        if name!='ST':
            self.ms('wval',3);self.reg_value(name,1 if name=='LDB' else 2)
            self.signed_range(0,3 if name=='LDB' else 6);self.mov(2,0)
            self.mg('wval',3);self.ml('wval',0)
        else:self.get_arg(name,3,2)
        self.ms('start',3);self.ms('ret',4)
        self.ms('lane',2);self.ml('mode',b.IO);self.ml('index',0);self.ml('buf',0)
        if name=='LDB':self.ml('dst',0);self.ml('width',37);self.ml('kind',b.LDB);self.flag(1)
        else:
            self.get_arg(name,0);self.ms('dst');self.get_arg(name,2 if name=='ST' else 3)
            self.ms('width');self.ml('kind',b.STORE if name=='ST' else b.LDV if name=='LDV' else b.LDC)
            if name!='ST':self.ml('rval',0);self.get_arg(name,0);self.ms('rdst')
        self.mg('start',1);self.move_to(1);a.jump(self.packet_done)
    def head_field(self):
        a=self.a;self.fail_label=a.fresh('packet_fail');self.packet_done=a.fresh('packet_done')
        self.io_advance=a.fresh('io_advance');self.io_labels={i:a.fresh('io_kind_'+str(i)) for i in range(4)}
        self.op_labels={name:a.fresh('opcode_'+name) for name in b.OP_NAMES}
        reset=a.fresh('head_reset');birth=a.fresh('head_birth');collect=a.fresh('head_collect')
        earlymove=a.fresh('head_earlymove');active=a.fresh('head_active')
        self.reset_branch(reset);self.on_age(112*b.Q+1,birth);self.on_age(b.COLLECT,collect)
        self.less(8,b.COLLECT+1);skip=a.fresh('no_earlymove');a.bnz(3,skip)
        self.less(8,b.EVALUATE);a.bnz(3,earlymove);a.label(skip)
        self.less(8,112*b.Q+2);skip=a.fresh('no_active');a.bnz(3,skip)
        self.less(8,120*b.Q);a.bnz(3,active);a.label(skip)
        self.metadata_load();a.jump(self.packet_done)
        a.label(reset);self.ml('flags',16);a.jump(self.packet_done)
        a.label(birth);self.ml('flags',16);self.service(0);self.eq(0,b.PRIMARY_START,out=2)
        notentry=a.fresh('head_not_entry');a.op('not',2,2,2);a.bnz(2,notentry);self.flag(32)
        a.label(notentry);a.jump(self.packet_done)
        a.label(collect);self.metadata_load();self.flag(1);self.service(0)
        self.less(0,b.PRIMARY_START,out=2);a.bnz(2,self.packet_done)
        self.less(0,b.PRIMARY_START+37,out=2);a.op('not',2,2,2);a.bnz(2,self.packet_done)
        a.lit(5,b.PRIMARY_START);a.op('sub',0,0,5);a.lit(5,11);a.op('mul',0,0,5);self.ms('wstart')
        self.call('mem_read');a.lit(5,3);a.op('shr',0,0,5);a.lit(5,2047);a.op('and',0,0,5)
        self.ms('wval');self.ml('wwidth',11);a.jump(self.packet_done)
        a.label(earlymove);self.metadata_load();self.service(0)
        self.less(0,b.PRIMARY_START,out=2);zero=a.fresh('earlymove_zero');a.bnz(2,zero)
        self.less(0,b.COLLECTOR+1,out=2);a.op('not',2,2,2);a.bnz(2,zero)
        self.flag(64);self.service(0);self.eq(0,b.COLLECTOR,out=2)
        notcollector=a.fresh('not_collector');a.op('not',2,2,2);a.bnz(2,notcollector);self.flag(32)
        a.label(notcollector);a.jump(self.packet_done);a.label(zero);self.flag(1);a.jump(self.packet_done)
        a.label(active);self.incoming_source()
        self.mg('move',0);self.eq(0,3,out=2);a.bnz(2,self.fail_label)
        self.mg('mode',0);run=a.fresh('cpu_run');io=a.fresh('cpu_io')
        self.eq(0,b.RUN,out=2);a.bnz(2,run);self.eq(0,b.IO,out=2);a.bnz(2,io)
        self.ml('move',0);a.jump(self.packet_done)
        a.label(io);self.io_body();a.label(run);self.run_body()
        a.label(self.fail_label);self.fail();a.label(self.packet_done);self.packet_output()
        self.reader_native();self.table(9,'slots',10);self.logical_controls()
    def write_head(self,r,width,bitreg=None,bit=0):
        a=self.a
        if bitreg is None:a.lit(5,self.offsets['head'][0]+5*bit)
        else:
            a.lit(5,5);a.op('mul',5,5,bitreg);a.lit(2,self.offsets['head'][0]);a.op('add',5,5,2)
        a.op('add',5,5,10);a.emit('ST',r,5,width,5)
    def packet_output(self):
        a=self.a;fullzero=a.fresh('packet_all_zero');normal=a.fresh('packet_normal');outdone=a.fresh('packet_output_done')
        self.mg('flags',0);a.lit(5,16);a.op('and',2,0,5);a.bnz(2,fullzero);a.jump(normal)
        a.label(fullzero);a.lit(1,0);loop=a.fresh('packet_zero_word');a.label(loop)
        a.lit(0,0);a.lit(5,20);a.op('mul',3,1,5)
        self.less(1,b.HEAD_BITS//20,out=2);tail=a.fresh('packet_zero_tail');a.op('not',2,2,2);a.bnz(2,tail)
        self.write_head(0,20,3);after=a.fresh('packet_zero_after');a.jump(after)
        a.label(tail);self.write_head(0,b.HEAD_BITS%20,3);a.label(after)
        a.lit(5,1);a.op('add',1,1,5);self.less(1,(b.HEAD_BITS+19)//20,out=2);a.bnz(2,loop)
        self.mg('flags',0);a.lit(5,32);a.op('and',0,0,5);a.lit(5,5);a.op('shr',0,0,5)
        self.write_head(0,1,bit=0);a.jump(outdone)
        a.label(normal)
        a.lit(7,0);meta=a.fresh('packet_metadata');a.label(meta)
        a.emit('WGET',0,7);self.table(3,'metadata_offsets',7)
        # Metadata offsets increase strictly. A fixed 20-bit store may
        # overlap the next metadata field; its later store repairs that
        # overlap, and the register pass repairs the final three bits.
        self.write_head(0,20,3)
        a.lit(5,1);a.op('add',7,7,5);self.less(7,14,out=2);a.bnz(2,meta)
        # All eleven register words are fetched from real backup-copy columns.
        a.lit(1,0);loop=a.fresh('packet_register');a.label(loop)
        self.mg('rdst',2);a.op('eq',2,1,2);changed=a.fresh('register_changed');ready=a.fresh('register_ready')
        a.bnz(2,changed);self.call('reg_read');a.jump(ready)
        a.label(changed);self.mg('rval');a.label(ready)
        a.lit(5,20);a.op('mul',3,1,5);a.lit(5,119);a.op('add',3,3,5);self.write_head(0,20,3)
        a.lit(5,1);a.op('add',1,1,5);self.less(1,b.REGISTERS,out=2);a.bnz(2,loop)
        # Work streaming preserves the raw old 407 bits except an explicit
        # clear/early-move/one-field patch, including a patch crossing words.
        a.lit(7,0);loop=a.fresh('packet_work');a.label(loop)
        self.mg('flags',0);a.lit(5,1);a.op('and',2,0,5)
        oldzero=a.fresh('work_zero');oldready=a.fresh('work_ready');a.bnz(2,oldzero)
        a.lit(5,64);a.op('and',2,0,5);fromleft=a.fresh('work_from_left');a.bnz(2,fromleft)
        self.mov(1,7);self.call('work_read');self.mov(8,0);a.jump(oldready)
        a.label(fromleft);self.shift_source(-1);self.mov(1,7);self.call('work_read');self.mov(8,0);self.shift_source(1)
        self.mg('flags',0);a.lit(5,32);a.op('and',2,0,5);noor=a.fresh('work_no_or');a.op('not',2,2,2);a.bnz(2,noor)
        self.mov(1,7);self.call('work_read');a.op('or',8,8,0);a.label(noor);a.jump(oldready)
        a.label(oldzero);a.lit(8,0);a.label(oldready)
        a.lit(4,0);bits=a.fresh('work_patch_bit');a.label(bits)
        a.lit(5,20);a.op('mul',1,7,5);a.op('add',1,1,4)
        self.mg('wstart',2);a.op('lt',3,1,2);skip=a.fresh('work_patch_skip');a.bnz(3,skip)
        self.mg('wwidth',3);a.op('add',3,3,2);a.op('lt',3,1,3);a.op('not',3,3,3);a.bnz(3,skip)
        a.op('sub',1,1,2);self.mg('wval',0);a.op('shr',3,0,1);a.lit(5,1);a.op('and',3,3,5)
        self.patch_bit(8,4,3);a.label(skip)
        a.lit(5,1);a.op('add',4,4,5);self.less(4,20,out=2);a.bnz(2,bits)
        self.mov(0,8);a.lit(5,20);a.op('mul',3,7,5);a.lit(5,b.PACKET_BITS);a.op('add',3,3,5)
        tail=a.fresh('packet_work_tail');self.eq(7,20,out=2);a.bnz(2,tail)
        self.write_head(0,20,3);after=a.fresh('packet_work_after');a.jump(after)
        a.label(tail);self.write_head(0,7,3);a.label(after)
        a.lit(5,1);a.op('add',7,7,5);self.less(7,21,out=2);a.bnz(2,loop)
        # A STORE IO writes exactly one output Next bit, after old-Next stutter.
        self.mg('flags',0);a.lit(5,4);a.op('and',2,0,5)
        no_next=a.fresh('no_next_write');a.op('not',2,2,2);a.bnz(2,no_next)
        a.lit(5,3);a.op('shr',0,0,5);a.lit(5,1);a.op('and',0,0,5);self.output('next')
        a.label(no_next)
        self.mg('flags',0);a.lit(5,2);a.op('and',2,0,5)
        no_native=a.fresh('no_upper_native');a.op('not',2,2,2);a.bnz(2,no_native)
        self.load_head_work();a.emit('NATIVE');self.nc(0,0,20);self.write_head(0,20,bit=82)
        self.nc(0,20,17);self.write_head(0,17,bit=102);a.label(no_native);a.label(outdone)
    def helpers(self):
        a=self.a
        a.label('helper_reg_read');a.lit(2,20);a.op('mul',5,1,2)
        a.lit(2,119);a.op('add',5,5,2);a.lit(2,5);a.op('mul',5,5,2)
        a.lit(2,self.offsets['head'][0]);a.op('add',5,5,2);a.emit('LDV',0,5,9,20);a.emit('JREG',6)
        a.label('helper_work_read');a.lit(2,20);a.op('mul',5,1,2)
        a.lit(2,b.PACKET_BITS);a.op('add',5,5,2);a.lit(2,5);a.op('mul',5,5,2)
        a.lit(2,self.offsets['head'][0]);a.op('add',5,5,2);a.emit('LDV',0,5,9,20)
        self.eq(1,20,out=2);not_tail=a.fresh('work_read_not_tail');a.op('not',2,2,2);a.bnz(2,not_tail)
        a.lit(2,127);a.op('and',0,0,2);a.label(not_tail);a.emit('JREG',6)
        a.label('helper_metadata_load');a.lit(1,0);meta=a.fresh('load_metadata');a.label(meta)
        self.table(3,'metadata_offsets',1);a.lit(5,5);a.op('mul',5,5,3)
        a.lit(2,self.offsets['head'][0]);a.op('add',5,5,2);a.emit('LDV',0,5,9,20)
        self.table(2,'metadata_widths',1);a.lit(5,1);a.op('shl',2,5,2);a.op('sub',2,2,5)
        a.op('and',0,0,2);a.emit('WSET',1,0)
        a.lit(5,1);a.op('add',1,1,5);self.less(1,14,out=2);a.bnz(2,meta)
        for name,value in (('rdst',15),('rval',0),('wstart',511),('wval',0),
                           ('wwidth',0),('flags',0)):self.ml(name,value)
        a.emit('JREG',6)
        a.label('helper_mem_read');self.mov(3,9);self.table(9,'slots',10)
        self.read('history1');self.mov(1,0);self.read('history2');self.mov(2,0);self.read('history3')
        self.mov(9,3)
        a.op('and',3,1,2);a.op('or',1,1,2);a.op('and',0,0,1);a.op('or',0,0,3);a.emit('JREG',6)
    def complete(self):
        a=self.a;self.native_outputs_and_final_workspace()
        # Mandatory raw-self wipe is a computed-output zeroing branch.
        self.nc(4,33,1);a.lit(9,0);a.lit(5,b.PRIMARY_START);a.emit('LDC',0,5,9,13)
        self.nc(1,0,13);a.op('eq',0,0,1);a.op('not',0,0,0);a.op('and',0,0,4)
        wipe=a.fresh('all_sf_wipe');finish=a.fresh('finish_rule');a.bnz(0,wipe)
        a.lit(10,0);copy=a.fresh('copy');a.label(copy);self.table(9,'slots',10);self.logical_controls()
        self.info_field();self.next_field();self.mail_field('mailL');self.mail_field('mailR')
        for g in range(3):self.history_field(g)
        self.courier_field(True);self.courier_field(False);self.head_field()
        a.lit(5,1);a.op('add',10,10,5);self.less(10,5,out=2);a.bnz(2,copy);a.jump(finish)
        a.label(wipe);a.lit(1,37);loop=a.fresh('wipe_word');a.label(loop)
        a.lit(5,b.PRIMARY_START);a.op('add',5,5,1);a.lit(0,0)
        tail=a.fresh('wipe_tail');self.less(1,b.FRAME_BITS-20,out=2);a.op('not',2,2,2);a.bnz(2,tail)
        # All remaining raw SF bits form a contiguous range, not a new opcode.
        a.lit(5,b.PRIMARY_START);a.op('add',5,5,1);a.emit('ST',0,5,20,1)
        a.lit(5,20);a.op('add',1,1,5);a.jump(loop)
        a.label(tail);a.lit(5,b.PRIMARY_START+b.FRAME_BITS-20);a.emit('ST',0,5,20,1)
        a.label(finish);a.emit('HLT');self.helpers()
        a.data('data_slots',[x&b.MASK for x in b.SLOTS]);a.data('data_lengths',[b.LENGTH[i] for i in range(16)])
        a.data('data_metadata_offsets',[self.meta_offsets[f][0]+k for f,w in b.META for k in range(0,w,20)])
        a.data('data_metadata_widths',[min(20,w-k) for f,w in b.META for k in range(0,w,20)])
        return a

if __name__=='__main__':
    asm=FullEmitter().complete();length,labels,rows=asm.listing()
    try:asm.assemble();fits=True;failure=None
    except ProgrammeOverflow as exc:fits=False;failure=exc.args[0]
    print({'scope':'COMPLETE GBP1 emission, semantic equivalence not yet proved',
      'bits':length,'instructions':sum(op!='DATA20' for _,op,_,_ in rows),
      'Q':b.Q,'code_capacity':b.CODE_BITS,'fits':fits,'failure':failure,'own_beta_proved':False,
      'deadline_proved':False})
