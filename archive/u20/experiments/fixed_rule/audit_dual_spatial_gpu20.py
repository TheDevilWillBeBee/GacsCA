"""Compare a complete physical CUDA evaluator period to an independent replay."""
import time

import numpy as np

from gacsca.fixed_rule import spatial_codec8 as codec
from gacsca.fixed_rule import spatial_epoch8 as spatial
from gacsca.fixed_rule import stream28_dual_spatial_gpu20 as gpu


def verify(captured,evolved,events,*,packets=26101,gates=14851,
           wrap_gates=63):
    if len(captured)!=spatial.Q or len(evolved)!=spatial.Q:
        raise ValueError('complete physical evaluator ring required')
    start=time.perf_counter()
    initial=np.array([codec.encode_cell(row) for row in captured],dtype=np.uint64)
    expected=np.array([codec.encode_cell(row) for row in evolved],dtype=np.uint64)
    with gpu.World(initial) as world:
        world.run(spatial.PERIOD)
        actual,device_events,counts=world.read()
        device_bytes=world.device_bytes
    if not np.array_equal(actual,expected):
        failures=np.argwhere(actual!=expected)
        raise AssertionError(('GPU physical evaluator state mismatch',
                              failures[:12].tolist(),len(failures)))
    if sorted(device_events)!=sorted(tuple(map(int,row)) for row in events):
        missing=set(map(tuple,events))-set(device_events)
        excess=set(device_events)-set(map(tuple,events))
        raise AssertionError(('GPU physical output events mismatch',
                              tuple(sorted(missing))[:5],
                              tuple(sorted(excess))[:5]))
    if counts!=(packets,gates+wrap_gates):
        raise AssertionError(('GPU physical event counts mismatch',counts,
                              (packets,gates+wrap_gates)))
    return dict(passed=True,ticks=spatial.PERIOD,sites=spatial.Q,
                output_events=len(device_events),
                packet_deliveries=counts[0],gate_completions=gates,
                next_period_initial_gate_completions=wrap_gates,
                complete_state_equal=True,device_bytes=device_bytes,
                seconds=time.perf_counter()-start)
