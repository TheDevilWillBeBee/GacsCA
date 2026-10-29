"""GR0: isolated Gray-scale experimental completion, NOT Gray verbatim.

Q8192/U128Q, lambda24/c104 and literal Gray native maintenance. The
five-front evaluator, streaming captures and early evaluation are explicit
simulation-protocol adaptations. A failure of that protocol cannot be
attributed to Gray without a separate faithfulness proof.
"""
from dataclasses import dataclass
from functools import lru_cache
import hashlib
import inspect
from pathlib import Path
import sys
from types import SimpleNamespace
import numpy as np
from gacsca import rule_g, compiler, machine
from gacsca.netlist import Compiled
import literal_maintenance

for _name in ('OFFSETS', 'LANE_OFFSETS', 'schema', 'width', 'source_names',
              'info_copies', 'flag_store_cells', 'reserved_cells', 'work_range'):
    globals()[_name] = getattr(rule_g, _name)


@dataclass(frozen=True)
class ParamsGrayScale(rule_g.ParamsG):
    @property
    def T_wf(self):
        # The published interval begins at3U/4, independently of the early
        # programme's special-procedure time.
        return 3 * self.U // 4

    def fam(self):
        return sys.modules[__name__]


def parameters():
    return ParamsGrayScale(k=13, m=20, L=64, S=4, NP=100, NPe=20, MP=85,
        E0q=70, gathers_q=(0,32,64), q=8192, nb=256,
        margin=2058, burst=200, clear_ws=True, computed_front=True,
        five_front=True, compact_front=True, mux_front=True, confined=True,
        fronts=5, delta=5, stage_wipe=True,
        skew=(-5,-4,-3,-2,-1,1,2,3,4,5)).check()


def generated_source():
    return inspect.getsource(rule_g.build)


def build(p):
    namespace = dict(rule_g.__dict__)
    namespace['maintenance'] = SimpleNamespace(build=literal_maintenance.build)
    exec(compile(generated_source(), '<isolated Gray-scale full rule>', 'exec'), namespace)
    return namespace['build'](p)


@lru_cache(maxsize=2)
def cached(p):
    net = build(p)
    return net, Compiled(net)


def layout(p):
    return compiler.end_aware_layout(p, cached(p)[1])


def load_artifact():
    root = Path(__file__).resolve().parents[3]
    saved = np.load(root/'figs/gray_counterexamples/GR0_program.npz')
    p = parameters()
    return machine.Candidate(p, saved['rom'], saved['layout'])


def metadata():
    p = parameters()
    _, comp = cached(p)
    return dict(Q=p.Q, U=p.U, width=width(p), radius=5, gates=len(comp.gates),
        netlist_sha256=comp.digest, literal_maintenance_sha256=literal_maintenance.source_sha256(),
        generated_rule_source_sha256=hashlib.sha256(generated_source().encode()).hexdigest(),
        lambda_value=24, error_separation_c=104,
        own_programme_verified=False, gray_verbatim_simulation=False,
        explicit_adaptations=['Five-front evaluator and packed half-colony sweep.',
            'Third stream is voted into two retained histories.',
            'Early evaluation starts at70Q rather than only in the fifth stage.',
            'Special flag copy at80Q and Workspace pulse at96Q.',
            'Mailbox movement and register transport continue during published rest intervals.',
            'Stage wipes are repository stage_wipe equations, not all Gray stage boundaries.'])
