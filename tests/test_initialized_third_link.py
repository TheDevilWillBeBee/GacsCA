"""Correct initialization must produce non-aliased top transitions, not just parity."""
from argparse import Namespace
import json

import numpy as np
import pytest

from experiments.cache_bootstrap import cached_initial
from experiments.replay_third_link_completion import initial_top
from experiments.third_link_checkpoint import build
from experiments.third_link_initialized import run
from experiments.verify_third_link_checkpoint import audit
from gacsca.gpu_engine import CleanGraphRunner
from gacsca.hierarchy import encode_state_info, decode_state_info


@pytest.mark.parametrize("R", [3, 5])
def test_full_middle_gpu_period_initialized_cache_nonaliased_top(R):
    _, middle, top = build(R, 11)
    raw = initial_top(top, 11, 1350)
    expected = top.np_engine().step(raw)
    warm = cached_initial(middle, raw)
    cold = middle.np_engine().initial(1, info_bits=encode_state_info(raw, middle.L, middle.p.Q))
    state = {k:np.concatenate((cold[k], warm[k])) for k in warm}
    gpu = middle.gpu_engine()
    runner = CleanGraphRunner(gpu, gpu.to_gpu(state))
    runner.run(middle.p.U)
    decoded = decode_state_info(gpu.info_bits(runner.state).cpu().numpy(), middle.L, middle.p.Q)
    for name in expected:
        np.testing.assert_array_equal(decoded[name][1:2], expected[name], err_msg=name)
    if R == 3:
        # The known false-positive guard: same core, top state and geometry,
        # only the initial caches differ. This fixture must detect the defect.
        assert np.count_nonzero(decoded["trk"][:1] != expected["trk"]) == 8


def test_initialized_third_link_restart_skip_parity_and_independent_audit(tmp_path):
    def args(name, **kw):
        values = dict(R=3, middle_colonies=1, periods=2, stop_after=None,
                      checkpoint_every=1, graph_block=256, seed=1350,
                      certified_skip=False, resume=False, output=tmp_path / name)
        values.update(kw)
        return Namespace(**values)
    run(args("direct"))
    first = run(args("split", certified_skip=True, stop_after=1))
    assert first["status"] == "running" and first["skipped_steps"] > 0
    assert first["identity"]["cache_initialization"] == "input_age_address"
    run(args("split", certified_skip=True, resume=True))
    with np.load(tmp_path / "direct.npz") as a, np.load(tmp_path / "split.npz") as b:
        for key in a.files:
            if key != "_metadata": np.testing.assert_array_equal(a[key], b[key])
        previous = json.loads(str(b["_metadata"]))
    assert run(args("split", certified_skip=True, resume=True)) == previous
    verified = audit(tmp_path / "split.npz")
    assert verified["passed"] and verified["completed_periods"] == 2
    with pytest.raises(ValueError, match="identity"):
        run(args("split", certified_skip=True, resume=True, seed=1351))
