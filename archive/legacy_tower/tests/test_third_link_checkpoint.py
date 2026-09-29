"""Exact physical restart and certified-skip parity for the finite third link."""
from argparse import Namespace
import json
import numpy as np
import pytest

from experiments.third_link_checkpoint import run, build


def arguments(path, **changes):
    args = Namespace(R=3, middle_colonies=1, periods=2, stop_after=None,
                     checkpoint_every=1, graph_block=256, seed=1350,
                     certified_skip=False, resume=False, output=path)
    for k,v in changes.items(): setattr(args, k, v)
    return args


def contents(path):
    with np.load(path.with_suffix(".npz"), allow_pickle=False) as data:
        return json.loads(str(data["_metadata"])), {k:data[k].copy() for k in data.files if k != "_metadata"}


def test_third_link_restart_and_certified_skip_are_bit_exact(tmp_path):
    outer, middle, top = build(3, 1)
    assert all(s.L.full_registers for s in (outer, middle, top))
    direct_path, resumed_path = tmp_path / "direct", tmp_path / "resumed"
    direct = run(arguments(direct_path))
    first = run(arguments(resumed_path, certified_skip=True, stop_after=1))
    assert first["completed_periods"] == 1 and first["status"] == "running"
    assert first["certificates"] > 0 and first["skipped_steps"] > 0
    resumed = run(arguments(resumed_path, certified_skip=True, resume=True))
    assert direct["status"] == resumed["status"] == "complete"
    assert direct["physical_steps"] == resumed["physical_steps"] == 2 * 16384
    assert direct["top_checks"] == resumed["top_checks"] == []
    assert direct["top_neighborhood_aliasing"] and not direct["whole_top_colonies"]
    _, a = contents(direct_path)
    before, b = contents(resumed_path)
    assert a.keys() == b.keys()
    for name in a: np.testing.assert_array_equal(a[name], b[name], err_msg=name)
    run(arguments(resumed_path, certified_skip=True, resume=True))
    after, _ = contents(resumed_path)
    assert before == after  # completed resume does not run or rewrite data
    with pytest.raises(FileExistsError): run(arguments(direct_path))
    with pytest.raises(ValueError, match="identity mismatch"):
        run(arguments(resumed_path, certified_skip=True, resume=True, seed=1351))


@pytest.mark.parametrize("R,n", [(3, 0), (5, 65), (7, 1)])
def test_third_link_checkpoint_rejects_invalid_geometry(R, n):
    with pytest.raises(ValueError): build(R, n)


@pytest.mark.parametrize("R", [3, 5])
def test_full_alphabet_middle_period_matches_direct_top_transition(R):
    from gacsca.gpu_engine import CleanGraphRunner
    from gacsca.hierarchy import encode_state_info, decode_state_info
    outer, middle, top = build(R, 1)
    raw = {k:v[:, :1].copy() for k,v in top.np_engine().initial(1).items()}
    raw["addr"][:] = 5
    raw["age"][:] = next(o.t0 for o in top.prog.ops if o.kind == "BITOP")
    raw["simage"][:] = 65535
    raw["simaddr"][:] = 43210
    raw["trk"][:] = np.random.default_rng(1360 + R).integers(0, 2, raw["trk"].shape, dtype=np.uint8)
    expected = top.np_engine().step(raw)
    state = middle.np_engine().initial(1, info_bits=encode_state_info(raw, middle.L, middle.p.Q))
    gpu = middle.gpu_engine()
    runner = CleanGraphRunner(gpu, gpu.to_gpu(state))
    runner.run(middle.p.U)
    decoded = decode_state_info(gpu.info_bits(runner.state).cpu().numpy(), middle.L, middle.p.Q)
    for name in expected: np.testing.assert_array_equal(decoded[name], expected[name], err_msg=name)
