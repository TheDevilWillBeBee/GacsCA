import numpy as np

from experiments.cache_bootstrap import cached_initial
from experiments.replay_third_link_completion import initial_top
from experiments.third_link_checkpoint import build
from gacsca.hierarchy import encode_state_info, decode_state_info
from gacsca.engine_np import repair


def test_compressed_cached_initial_preserves_encoded_state_and_supplies_input_controls():
    _, middle, top = build(3, 11)
    raw = initial_top(top, 11, 1350)
    saved = {k:v.copy() for k,v in raw.items()}
    warm = cached_initial(middle, raw)
    cold = middle.np_engine().initial(1, info_bits=encode_state_info(raw, middle.L, middle.p.Q))
    for name in warm:
        if name not in ("simage", "simaddr"):
            np.testing.assert_array_equal(warm[name], cold[name])
    np.testing.assert_array_equal(warm["simage"], np.repeat(raw["age"], 256, axis=1))
    np.testing.assert_array_equal(warm["simaddr"], np.repeat(raw["addr"], 256, axis=1))
    decoded = decode_state_info(repair(warm["trk"])[..., middle.T["INFO"]], middle.L, middle.p.Q)
    for name in raw:
        np.testing.assert_array_equal(raw[name], saved[name])
        np.testing.assert_array_equal(decoded[name], raw[name])
