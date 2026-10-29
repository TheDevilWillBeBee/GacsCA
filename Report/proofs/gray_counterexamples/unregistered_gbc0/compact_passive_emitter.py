"""Actual Q-bit GBC0 programme for the COMPLETE passive Age123 slice.

This is NOT an all-raw own programme.  The quantified upper family has
canonical GF, common Age123, zero native flags/Workspace, and arbitrary
raw simulation fields (all five copies, without coherence). The active
lower interpreter uses real READ/PUSH/NATIVE/NCGET/WRITE/STREAM.
"""
import compact_stream_rule as b

def emitted_map(cells):
    """Mathematical comparison map delta, never called by the CPU/ISA.

    The actual emitted programme computes delta on all declared upper
    binary words. delta agrees with F_beta only on the stated passive
    clock family. It is not silently installed as the physical rule.
    """
    native=b.native_at(cells,0)
    fields={}
    for name,width in b.FIELDS:
        shift=1 if name=='mailL' else -1 if name=='mailR' else 0
        fields[name]=tuple(b.voted(cells,s+shift,name)&((1<<width)-1) for s in b.SLOTS)
    return b.Cell(**native,wf1=0,wf2=0,**fields)

class Assembler:
    def __init__(self):self.rows=[];self.labels={}
    def label(self,name):
        assert name not in self.labels
        self.labels[name]=sum(len(b.encode(op,*(0 if isinstance(v,str) else v for v in args)))
                              for op,args in self.rows)
    def emit(self,name,*args):self.rows.append((name,args))
    def literal(self,value):self.emit('LIT',value)
    def swap(self):self.emit('SWAP')
    def immediate(self,fn,value):self.emit('ALUI',b.ALU[fn],value)
    def branch(self,cond,label):self.emit('BR',cond,label)
    def finish(self):
        bits=[];listing=[]
        for name,args in self.rows:
            values=tuple(self.labels[v] if isinstance(v,str) else v for v in args)
            encoded=b.encode(name,*values)
            listing.append((len(bits),name,values,len(encoded)))
            bits.extend(encoded)
        if len(bits)>b.CODE_BITS:
            raise ValueError(('rejected programme exceeds Q',len(bits),b.CODE_BITS))
        return tuple(bits+[0]*(b.CODE_BITS-len(bits))),listing,len(bits)

def emit_passive():
    a=Assembler();P=b.PRIMARY_START
    # Scan native raw bit columns in descending order, appending each
    # eleven-lane window into Work. No scratch is hidden in that buffer.
    a.literal(P+36);a.swap()
    a.label('native_input')
    a.emit('READ',b.READ_WORD,0)
    a.immediate('shr',3);a.emit('PUSH',11)
    a.emit('SELF',0);a.immediate('eq',P);a.branch(2,'native_loaded')
    a.emit('SELF',0);a.immediate('sub',1);a.swap();a.branch(0,'native_input')
    a.label('native_loaded');a.emit('NATIVE')
    a.literal(P);a.swap()
    a.label('native_output')
    a.swap();a.immediate('sub',P);a.swap();a.emit('NCGET')
    a.immediate('and',1);a.swap();a.immediate('add',P);a.swap();a.emit('WRITE')
    a.emit('SELF',0);a.immediate('eq',P+34);a.branch(2,'native_done')
    a.emit('SELF',0);a.immediate('add',1);a.swap();a.branch(0,'native_output')
    a.label('native_done')
    for target in (P+35,P+36):
        a.literal(target);a.swap();a.literal(0);a.emit('WRITE')
    # All simulation-structure raw columns are written. Mail shifts are
    # the actual upper first-gather shifts at computed Age124; all other
    # upper fields stutter at that phase. STREAM still votes every bit.
    for field,width in b.FIELDS:
        start,count=b.offsets()[field]
        centre=1 if field=='mailL' else -1 if field=='mailR' else 0
        a.literal(start);a.swap();a.literal(count)
        a.emit('STREAM',1,0,centre&31)
    a.emit('HLT')
    return a.finish()

if __name__=='__main__':
    import json
    beta,listing,length=emit_passive()
    print(json.dumps({'Q':b.Q,'U':b.U,'lambda':b.LAMBDA,'c':b.ERROR_SEPARATION,
                      'programme_bits':length,'instructions':len(listing),
                      'Head_bits':b.HEAD_BITS,'K':b.FRAME_BITS,'2K':2*b.FRAME_BITS,
                      'labels_scope':'complete passive Age123 slice only',
                      'full_own_beta':False},indent=2))
