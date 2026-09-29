"""Run one complete encoded physical evaluator period on the A100.

All gates, routes, packets, and dynamic registers advance by the fixed CUDA
radius-one rule. This returns device-computed output events to Holder callers;
the host does not evaluate the encoded own-rule DAG.
"""
import time

import numpy as np

from gacsca.fixed_rule import spatial_codec8 as codec
from gacsca.fixed_rule import spatial_epoch8 as spatial
from gacsca.fixed_rule import stream28_dual_spatial_gpu20 as gpu


def run(captured):
    if len(captured)!=spatial.Q:
        raise ValueError('complete physical evaluator ring required')
    started=time.perf_counter()
    raw=np.array([codec.encode_cell(row) for row in captured],dtype=np.uint64)
    with gpu.World(raw) as world:
        world.run(spatial.PERIOD-1)
        _,_,before_wrap=world.read()
        world.run(1)
        actual,events,counts=world.read()
        device_bytes=world.device_bytes
    if np.any(actual[:,266]):
        raise AssertionError('physical GPU evaluator collision')
    if len(events)!=119 or len({site for _,site,_ in events})!=119:
        raise AssertionError(('GPU evaluator output event coverage',len(events)))
    if ((counts[0],before_wrap[1],counts[1]-before_wrap[1])!=
            (26101,14851,63)):
        raise AssertionError(('GPU evaluator physical event counts',
                              counts,before_wrap))
    evolved=tuple(codec.decode_cell(row.tolist()) for row in actual)
    result=dict(passed=True,ticks_evolved=spatial.PERIOD,
                physical_site_ticks=spatial.Q*spatial.PERIOD,
                physical_output_events=events,
                packet_deliveries=[counts[0]],
                gate_completions=[before_wrap[1]],
                next_period_initial_gate_completions=(
                    counts[1]-before_wrap[1]),
                output_events=len(events),
                device_bytes=device_bytes,
                seconds=time.perf_counter()-started,
                backend='fixed physical CUDA spatial local rule')
    return result,evolved,{}
