"""Isolated scheduler fix: ready lookup keys may wait for fixed MP.

Retain the XOR-multiplicity workaround and every instruction/visit rule.
Only the six-pass inactivity rejection is deferred while lookup keys are
ready and the requested fixed match pass has not arrived. A stalled run
after that pass still rejects. Every built programme requires universal
symbolic verification. Active jobsched.py and previous helpers unchanged.
"""
import hashlib,inspect,textwrap
from gacsca import jobsched
import xor_multiplicity_scheduler as previous


def engine(p,comp,layout,**options):
    instance,dag_sha=previous.engine(p,comp,layout,**options)
    source=textwrap.dedent(inspect.getsource(jobsched.Engine.run))
    old='        if self.T - max(f.last_act for f in self.fronts) > 6 * PL:\n'
    new=('        wait_for_match = (not self.post_match and self.fixed_MP is not None\n'
         '                          and self.keys_left == 0 and pg < self.fixed_MP)\n'
         '        if self.T - max(f.last_act for f in self.fronts) > 6 * PL and not wait_for_match:\n')
    assert source.count(old)==1
    source=source.replace(old,new)
    namespace=dict(instance.run.__globals__)
    exec(compile(source,'<isolated fixed-match wait; active scheduler unchanged>','exec'),namespace)
    patched=type('FixedMatchWaitEngine',(instance.__class__,),{'run':namespace['run']})
    instance.__class__=patched
    return instance,hashlib.sha256((dag_sha+'\n'+source).encode()).hexdigest()
