"""Isolated scheduler workaround: do not flatten XORs with repeated leaves.

The active jobsched.py is unchanged. Its multi-front folding tracks leaf
presence as a set, so a flattened XOR multiset is unsafe. Leaving such a
tree binary preserves its original Boolean operations and multiplicities.
All generated programs still require the universal output verifier.
"""
import hashlib
import inspect
from gacsca import jobsched


def engine(p, comp, layout, **options):
    source = inspect.getsource(jobsched.Dag)
    old = '            if len(leaves) < 3:'
    new = '            if len(leaves) < 3 or (op == M_XOR and len(set(leaves)) != len(leaves)):'
    assert source.count(old) == 1
    source = source.replace(old,new)
    namespace = dict(jobsched.__dict__)
    exec(compile(source,'<isolated XOR multiplicity scheduler>', 'exec'),namespace)
    exec(compile(inspect.getsource(jobsched.Engine),'<same engine with isolated safe DAG>', 'exec'),namespace)
    return namespace['Engine'](p,comp,layout,**options),hashlib.sha256(source.encode()).hexdigest()
