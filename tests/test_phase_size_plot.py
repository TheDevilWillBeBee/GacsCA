import numpy as np
import pytest

from experiments.plot_phase_size import wilson


def test_wilson_edges_and_symmetry():
    lo, hi = wilson([0, 5, 10], [10, 10, 10])
    assert lo[0] == pytest.approx(0)
    assert hi[-1] == pytest.approx(1)
    np.testing.assert_allclose(lo, 1 - hi[::-1], atol=1e-15)
    assert lo[1] < .5 < hi[1]
    with pytest.raises(ValueError):
        wilson(1, 0)
