"""Complete GBC3 encoder variant: tail-merge only virtual continue_pc.

No additional opcode/rule/state/storage change. The full GBC3 initial
emitter is reused; all paths still emit. The shared software block uses
the same countedWork slots. A changed instruction-table diagnostic is
required because the initial code rejectedQ; this is not an own beta.
"""
import complete_branch_emitter as old


def emit_complete_structural_listing():
    assembler,continuation=old.Assembler,old.virtual_continue
    class TailAssembler(assembler):
        def finish(self,require_fit=True):
            self.label('common_virtual_continue')
            continuation(self,old.VPC)
            return super().finish(require_fit)
    def shared_continuation(a,source=old.VPC):
        if source!=old.VPC:
            a.get(source)
            a.put(old.VPC)
        a.branch(0,'common_virtual_continue')
    try:
        old.Assembler=TailAssembler
        old.virtual_continue=shared_continuation
        r=old.emit_complete_structural_listing()
    finally:
        old.Assembler=assembler
        old.virtual_continue=continuation
    r['compiler_change']='one shared continue_pc output tail; same total rule/ISA/407-bit Work'
    r['whole_own_beta']=False
    r['complete_emitted_equivalence_proved']=False
    r['universal_runtime_proved']=False
    return r
