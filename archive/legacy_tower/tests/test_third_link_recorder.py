"""Recorder sampling/resume contract, without sleeping or consuming the GPU."""
from argparse import Namespace
import numpy as np
import pytest

from experiments import record_third_link as recorder
from gacsca.checkpoint import load_checkpoint


def frame(period, status="running", R=3):
    return (dict(identity=dict(R=R, fingerprints={}), status=status),
            dict(period=np.array(period), physical_steps=np.array(period * 16384),
                 decoded_mismatches=np.array(0), middle_addr=np.arange(4),
                 middle_trk=np.full((4, 2, 3), period % 2, np.uint8)), ["INFO", "HOLD"])


def args(tmp_path, resume=False):
    return Namespace(input=tmp_path / "source.npz", output=tmp_path / "trace",
                     interval=0.01, idle_timeout=1, resume=resume)


def test_recorder_preserves_irregular_samples_and_completed_resume(tmp_path, monkeypatch):
    frames = iter([frame(64), frame(192, "complete")])
    monkeypatch.setattr(recorder, "sample", lambda _:next(frames))
    monkeypatch.setattr(recorder.time, "sleep", lambda _:None)
    meta = recorder.run(args(tmp_path))
    assert meta["status"] == "complete" and meta["first_available_period"] == 64
    stored, data = load_checkpoint(tmp_path / "trace.npz", meta["identity"])
    np.testing.assert_array_equal(data["period"], [64, 192])  # no invented samples 0 or 128
    assert data["middle_trk"].shape == (2, 4, 2, 3)
    monkeypatch.setattr(recorder, "sample", lambda _:frame(192, "complete"))
    assert recorder.run(args(tmp_path, resume=True)) == stored
    with pytest.raises(FileExistsError): recorder.run(args(tmp_path))


@pytest.mark.parametrize("fault", ["identity", "backward"])
def test_recorder_rejects_changed_source_or_backward_progress(tmp_path, monkeypatch, fault):
    second = frame(192, R=5) if fault == "identity" else frame(32)
    frames = iter([frame(64), second])
    monkeypatch.setattr(recorder, "sample", lambda _:next(frames))
    monkeypatch.setattr(recorder.time, "sleep", lambda _:None)
    with pytest.raises(ValueError, match="identity changed|moved backward"):
        recorder.run(args(tmp_path))
