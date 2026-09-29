"""Direct packed initialization must equal the established NumPy encoding."""
import numpy as np
import pytest
import torch

from gacsca.build import make_system


@pytest.mark.parametrize("R,D,width", [(3, 3, 16), (5, 1, 16), (5, 1, 20)])
def test_packed_initial_exact_numpy_parity(R, D, width):
    s = make_system(Q=256, U=16384, ncol=2, R=R, D=D, Qs=16, Us=2048)
    gpu = s.gpu_engine(register_bits=width)
    bits = np.random.default_rng(921).integers(0, 2, (3, s.p.L), dtype=np.uint8)
    for info in (None, bits):
        expected = gpu.to_gpu(s.np_engine().initial(3, info_bits=info))
        torch.testing.assert_close(gpu.initial(3, info), expected, rtol=0, atol=0)
    with pytest.raises(ValueError, match="binary"):
        gpu.initial(3, np.full_like(bits, 2))
    with pytest.raises(ValueError, match="positive"):
        gpu.initial(0)
