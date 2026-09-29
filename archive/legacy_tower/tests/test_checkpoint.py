import numpy as np
import pytest

from gacsca.checkpoint import save_checkpoint, load_checkpoint
from gacsca.build import make_tower
from gacsca.hierarchy import encode_info, encode_state_info, decode_state_info


def test_checkpoint_roundtrip_and_identity(tmp_path):
    path = tmp_path / "checkpoint.npz"
    meta = dict(identity={"source": "test", "R": 5}, steps=2**40 + 3)
    arrays = dict(physical=np.arange(48, dtype=np.uint32).reshape(2, 3, 8))
    save_checkpoint(path, meta, arrays)
    loaded, state = load_checkpoint(path, meta["identity"])
    assert loaded == meta
    np.testing.assert_array_equal(state["physical"], arrays["physical"])
    with pytest.raises(ValueError, match="identity mismatch"):
        load_checkpoint(path, {"source": "changed", "R": 5})
    with pytest.raises(ValueError, match="numeric"):
        save_checkpoint(path, meta, dict(physical=np.array([object()])))
    assert load_checkpoint(path, meta["identity"])[0] == meta


def test_failed_atomic_replace_preserves_checkpoint(tmp_path, monkeypatch):
    path = tmp_path / "checkpoint.npz"
    meta = dict(identity="run", steps=1)
    save_checkpoint(path, meta, dict(x=np.arange(5)))
    def fail(*a):
        raise OSError("injected replace failure")
    monkeypatch.setattr("gacsca.checkpoint.os.replace", fail)
    with pytest.raises(OSError, match="injected"):
        save_checkpoint(path, dict(identity="run", steps=2), dict(x=np.arange(8)))
    assert load_checkpoint(path, "run")[0] == meta
    assert list(tmp_path.iterdir()) == [path]


@pytest.mark.parametrize("R", [3, 5])
def test_vector_encoding_preserves_raw_copies_and_matches_scalar(R):
    kw = dict(R=5, D=1, Q0=512, U0=32768, U1=8192) if R == 5 else {}
    lower, upper = make_tower(**kw)
    S = upper.np_engine().initial(2)
    rng = np.random.default_rng(39)
    for name, (_, width) in lower.L.fields.items():
        S[name.lower()] = rng.integers(0, 1 << width, S["addr"].shape, dtype=np.int32)
    S["trk"] = rng.integers(0, 2, S["trk"].shape, dtype=np.uint8)
    bits = encode_state_info(S, lower.L, lower.p.Q)
    for b in range(2):
        cells = [dict({k: int(v[b, i]) for k, v in S.items() if k != "trk"}, tracks=S["trk"][b, i])
                 for i in range(S["addr"].shape[1])]
        np.testing.assert_array_equal(bits[b], encode_info(cells, lower.L, lower.p.Q))
    decoded = decode_state_info(bits, lower.L, lower.p.Q)
    for k in S:
        np.testing.assert_array_equal(decoded[k], S[k])
    S["age"][0, 0] = 1 << lower.L.fields["AGE"][1]
    with pytest.raises(ValueError, match="out-of-range"):
        encode_state_info(S, lower.L, lower.p.Q)
