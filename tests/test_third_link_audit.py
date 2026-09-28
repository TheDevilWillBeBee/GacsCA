"""Independent packed decoder catches a majority flip but not a lone holder error."""
import numpy as np
import pytest

from experiments.third_link_checkpoint import build
from experiments.verify_third_link_checkpoint import decode_packed_info
from gacsca.hierarchy import encode_state_info


@pytest.mark.parametrize("R", [3, 5])
def test_third_link_independent_decoder_and_copy_faults(R):
    outer, middle, _ = build(R, 1)
    expected = middle.np_engine().initial(1)
    expected["simage"][:] = 65535
    expected["simaddr"][:] = 43210
    physical = outer.np_engine().initial(1, info_bits=encode_state_info(expected, outer.L, outer.p.Q))
    packed = outer.gpu_engine().to_gpu(physical).cpu().numpy()
    actual, count, disagreements = decode_packed_info(packed, outer, middle)
    assert count == middle.p.L * outer.L.K and disagreements == 0
    for name in expected: np.testing.assert_array_equal(actual[name], expected[name], err_msg=name)
    position, words = outer.L.b0, (outer.T.NT + 31) // 32
    for r in range(R // 2 + 1):
        packed[0, (position - (r - R // 2)) % outer.p.L, 5 + r * words] ^= 1
        actual, _, disagreements = decode_packed_info(packed, outer, middle)
        if r < R // 2:
            for name in expected: np.testing.assert_array_equal(actual[name], expected[name], err_msg=name)
            assert disagreements == r + 1
        else:
            assert actual["addr"][0, 0] == (expected["addr"][0, 0] ^ 1)
            assert disagreements == R // 2
