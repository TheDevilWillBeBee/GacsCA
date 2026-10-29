#!/usr/bin/env python3
"""Exact corrected-native geometry closure with all flags free.

Canonical Address and a common Age are invariant under noiseless updates,
independently of all Flag1/Flag2/Workspace flag inputs. This justifies
stopping an error-free campaign once its whole geometry agrees.
"""
from pathlib import Path
import hashlib,json,sys,time
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
from gacsca import maintenance
from gacsca.netlist import Net,const_word,w_add_const
import corrected_native_rule as native


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    started=time.monotonic()
    p=native.ParamsNative()
    for phase in range(p.Q):
        n=Net()
        age=[n.input(('common_age',i)) for i in range(p.m)]
        cells={j:dict(addr=const_word((phase+j)%p.Q,p.k),age=age,
                **{field:n.input(('arbitrary_flag',j,field)) for field in ('f1','f2','wf1','wf2')})
               for j in range(-5,6)}
        out=maintenance.build(n,cells,p.k,p.m)
        assert out['addr'] == const_word(phase,p.k)
        assert out['age_now'] == age
        assert out['age'] == w_add_const(n,age,1)
    result=dict(Q=p.Q,U=p.U,checker_sha256=digest(__file__),
        active_maintenance_sha256=digest(ROOT/'gacsca/maintenance.py'),
        corrected_native_source_sha256=digest(native.__file__),
        phases_checked=p.Q,symbolic_common_clock_bits=p.m,
        independent_symbolic_flag_bits=44,
        canonical_geometry_noiseless_invariant_proved=True,
        workspace_zero_required=False,full_simulation_rule_required=False,
        iid_unreliability_proved=False,elapsed_seconds=time.monotonic()-started)
    (ROOT/'figs/gray_counterexamples/native_geometry_invariant_certificate.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))


if __name__=='__main__':
    main()
