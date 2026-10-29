"""GBC6 shared continuation and terminating header blocks.

No extra rule/ISA/storage resource: this encoder rewrites exact listed
instruction sequences only when no interior label is removed. The
generic counted CALL/RETURN and field-access rule is the GBC6 baseline.
Every raw branch is still emitted; exact Q rejections remain retained.
"""
import complete_branch_emitter as old


def emit_complete_structural_listing():
    original_assembler,original_continue=old.Assembler,old.virtual_continue
    accounting={}
    class SharedAssembler(original_assembler):
        def finish(self,require_fit=True):
            self.label('common_virtual_continue')
            original_continue(self,old.VPC)
            pattern=[('SWAP',()),('WGET',(old.QCOL//20,)),
                     ('ALUI',(old.b.ALU['add'],old.HEAD_BASE)),
                     ('SWAP',()),('PUTWORD',(6,1)),('BR',(0,'cpu_next'))]
            oldrows=self.rows;oldmarks=dict(self.marks);rows=[];mapping={};removed=0;i=0
            while i<len(oldrows):
                mapping[i]=len(rows)
                match=oldrows[i:i+len(pattern)]==pattern
                internal=any(i<index<i+len(pattern) for index in oldmarks.values())
                if match and not internal:
                    rows.append(('BR',(0,'common_virtual_header')))
                    i+=len(pattern);removed+=1
                else:
                    rows.append(oldrows[i]);i+=1
            mapping[len(oldrows)]=len(rows)
            self.rows=rows;self.marks={name:mapping[index] for name,index in oldmarks.items()}
            self.label('common_virtual_header')
            old.head_write(self,0,6)
            self.branch(0,'cpu_next')
            accounting.update(header_blocks_merged=removed,
                              premerge_instructions=len(oldrows),
                              postmerge_instructions=len(self.rows))
            return super().finish(require_fit)
    def shared_continue(a,source=old.VPC):
        if source!=old.VPC:
            a.get(source);a.put(old.VPC)
        a.branch(0,'common_virtual_continue')
    try:
        old.Assembler=SharedAssembler;old.virtual_continue=shared_continue
        r=old.emit_complete_structural_listing()
    finally:
        old.Assembler=original_assembler;old.virtual_continue=original_continue
    r['compiler_change']='shared continuation plus exact terminating header tails; same GBC6 rule'
    r['shared_control_accounting']=accounting
    return r
