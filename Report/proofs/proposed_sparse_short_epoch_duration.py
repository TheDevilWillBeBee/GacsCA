"""EXPLICIT unincorporated short-force-window revisions of SP28.

Only the global RF force-window duration changes. Birth remains at T_wf.
All packet, code, pressure and private equations are retained. This is a
full Boolean transition with free instruction inputs, not a candidate:
no matching own programme or reliability theorem is provided.
G17 and all accepted earlier proposal sources are unchanged.
"""
from types import FunctionType, SimpleNamespace
import proposed_sparse_distant_epoch1024 as baseline
from proposed_sparse_epoch_duration_family import epoch_helper


def full_net(p, duration, net_class=None):
    if not isinstance(duration, int) or not 0 <= duration <= 3*p.Q:
        raise ValueError('isolated short duration must be an integer in [0,3Q]')
    old_previous = baseline.previous
    starter = SimpleNamespace(**dict(old_previous.base.starter.__dict__,
                                     epoch=epoch_helper(duration)))
    base = SimpleNamespace(**dict(old_previous.base.__dict__, starter=starter))
    previous = SimpleNamespace(**dict(old_previous.__dict__, base=base))
    legacy = baseline.legacy
    namespace = dict(legacy.__dict__, schema=baseline.schema, width=baseline.width,
                     previous=previous, dependency_table=baseline.dependency_table,
                     service_build=baseline.service_build,
                     generated_source=baseline.generated_source)
    fn = legacy.full_net
    build = FunctionType(fn.__code__, namespace, fn.__name__, fn.__defaults__)
    return build(p) if net_class is None else build(p, net_class)
