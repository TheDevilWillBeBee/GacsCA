#!/usr/bin/env python3
"""One SP22 periodic startup core with a pristine initial dependency shield.

Use nine actual level-2 native words GF -4..4 and zero other fields,
two further encodings, and one evolving-reference shifted core. Their
unused Info positions make this finite block compatible with an intact
phase-zero hierarchy. The entire first-period central cone lies in it.
Backend observations remain measured, not an iid counterexample.
"""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
import check_backward_fitted448_periodic_core as prior


def main():
    source=Path(prior.__file__).read_text()
    old="    cells=p.Q*p.Q;center=(p.Q//2)*p.Q;begin=center+1;tau=p.T_wf-8\n    top=np.zeros((candidate.W,1),dtype=bool)"
    new="""    cells=9*p.Q*p.Q;center=(4*p.Q+p.Q//2)*p.Q;begin=center+1;tau=p.T_wf-8
    top=np.zeros((candidate.W,9),dtype=bool)
    candidate.set_field(top,'addr',np.arange(-4,5)%p.Q)
    assert min(center-16*p.Q,cells-center-16*p.Q)>12*p.U
    # Each of these nine level-2 cells has five unused Info positions.
    primaries=set(proposed.layout(p).tolist())|{p.lo,p.hi-1}
    for address in np.arange(-4,5)%p.Q:
        assert all((int(address)+slot)%p.Q not in primaries for slot in range(-2,3))"""
    assert source.count(old)==1
    source=source.replace(old,new)
    source=source.replace('observer.sim(execution,1,p.Q)','observer.sim(execution,1,9*p.Q)')
    source=source.replace('observer.sim(execution,len(CASES)+1,p.Q)',
                          'observer.sim(execution,len(CASES)+1,9*p.Q)')
    source=source.replace("stem='SP22_periodic_startup_core'","stem='SP22_shielded_startup_core'")
    source=source.replace("default=2)","default=1)")
    source=source.replace('driver_sha256=digest(Path(__file__)),',
        "driver_sha256=digest(Path(__file__)),inherited_driver_sha256=digest(Path(prior.__file__)),")
    source=source.replace('initial_pristine_infinite_hierarchy=False,',
        "initial_pristine_infinite_hierarchy=False,initial_central_context_has_pristine_hierarchy_extension=True,\n"
        "        pristine_initial_dependency_shield_radius=12*p.U,\n"
        "        full_first_period_central_cone_inside_pristine_initial_context=True,")
    source=source.replace('six finite actual periodic own-ROM startup cores;',
        'one finite actual periodic own-ROM startup core with a pristine first-period central dependency shield;')
    namespace=dict(prior.__dict__,prior=prior,__file__=__file__)
    exec(compile(source,str(Path(__file__).resolve()),'exec'),namespace)
    namespace['CASES']=[prior.CASES[0]]
    namespace['main']()


if __name__=='__main__':
    main()
