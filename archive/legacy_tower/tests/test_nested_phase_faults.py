"""Phase/field placement and exact restart of the new physical experiment."""
from argparse import Namespace
import json

import numpy as np
import pytest

from experiments import nested_phase_faults as experiment
from experiments import analyze_nested_phase_faults as analysis
from experiments.third_link_checkpoint import build


@pytest.mark.parametrize("phase", ["evaluation", "rollover"])
def test_nested_phase_faults_target_actual_destination_and_encoded_fields(phase):
    outer, middle, top = build(3, 11)
    spec = experiment.phase_spec(outer, middle, top, phase, 11)
    assert spec["top_cell"] == 5
    assert spec["opcode"]["kind"] == "BITOP" and spec["opcode_index"] == 2
    assert spec["age"] == (10691 if phase == "evaluation" else 16382)
    assert spec["middle_holder"] == 5 * 256 + 85
    for target in ("info", "hold"):
        bit = spec["centers"][target] - outer.L.b0 - outer.L.track_base
        assert divmod(bit, middle.T.R) == (middle.T[target.upper()], 1)
    bit = spec["centers"]["control"] - outer.L.b0
    offset, width = outer.L.fields["SIMAGE"]
    assert offset <= bit < offset + width
    labels, boxes = experiment.scenarios(outer, spec, [1, 21], 2)
    assert len(labels) == 13 and len(boxes) == 12
    for b in boxes:
        b.validate(len(labels), outer.p.L)
        assert b.left // outer.p.Q == (b.right - 1) // outer.p.Q == spec["middle_holder"]
        assert b.start == outer.p.U - 2 and b.stop == outer.p.U - 1
        assert b.right - b.left == labels[b.batch]["width"]
    with pytest.raises(ValueError): experiment.scenarios(outer, spec, [256], 1)
    with pytest.raises(ValueError): experiment.scenarios(outer, spec, [21, 21], 1)
    with pytest.raises(ValueError): experiment.phase_spec(outer, middle, top, "evaluation", 1)


def test_phase_preparation_is_cpu_evolution_not_clock_relabeling():
    _, middle, top = build(3, 11)
    a = experiment.prepare(middle, top, 11, 1350, 1)
    b = experiment.prepare(middle, top, 11, 1350, 2)
    expected = middle.np_engine().step(a)
    for name in b: np.testing.assert_array_equal(b[name], expected[name])
    assert np.all(b["age"] == 2)


def test_evaluation_gate_rejects_cold_controls_and_checks_target_index():
    outer, middle, top = build(3, 11)
    spec = experiment.phase_spec(outer, middle, top, "evaluation", 11, 8)
    assert spec["middle_holder"] == 2133
    cold = middle.np_engine().initial(1)
    cold["age"][:] = spec["age"]
    with pytest.raises(ValueError, match="intended BITOP"):
        experiment.validate_evaluation(middle, top, cold, spec)
    with pytest.raises(ValueError, match="outside top ring"):
        experiment.phase_spec(outer, middle, top, "evaluation", 11, 11)


def test_nested_phase_checkpoint_restart_and_retained_boundaries(tmp_path, monkeypatch):
    # Short initialization fixture isolates runner/restart mechanics. The actual
    # phase/topology selection is covered above, not claimed by this fixture.
    outer, middle, top = build(3, 1)
    spec = dict(phase="fixture", age=0, middle_holder=85,
                centers=dict(control=42, info=67, hold=148))
    monkeypatch.setattr(experiment, "build", lambda *a: (outer, middle, top))
    monkeypatch.setattr(analysis, "build", lambda *a: (outer, middle, top))
    monkeypatch.setattr(experiment, "phase_spec", lambda *a: spec)
    def args(name, resume=False, stop=None):
        return Namespace(output=tmp_path / name, phase="evaluation", top_cells=1,
                         widths=[21], trials=1, periods=2, chunk=16384,
                         seed=1400, initialization_seed=1350, stop_after=stop, resume=resume)
    direct = experiment.run(args("direct"))
    partial = experiment.run(args("split", stop=1))
    assert partial["status"] == "running" and partial["steps"] == outer.p.U
    resumed = experiment.run(args("split", resume=True))
    assert direct["status"] == resumed["status"] == "complete"
    assert direct["commits"] == resumed["commits"]
    assert experiment.run(args("split", resume=True)) == resumed
    with np.load(tmp_path / "direct.npz") as a, np.load(tmp_path / "split.npz") as b:
        for key in a.files:
            if key != "_metadata": np.testing.assert_array_equal(a[key], b[key])
    for period in (1, 2):
        with np.load(tmp_path / f"split_boundary{period}.npz") as data:
            meta = json.loads(str(data["_metadata"]))
            assert meta["steps"] == period * outer.p.U
            assert "initial_trk" in data and "previous_trk" in data
    with pytest.raises(FileExistsError): experiment.run(args("split"))
    bad = args("split", resume=True)
    bad.seed += 1
    with pytest.raises(ValueError, match="identity"): experiment.run(bad)
    result = analysis.analyze(tmp_path / "split")
    assert result["passed"] and result["independently_decoded_boundaries"] == 2


def test_phase_analysis_distinguishes_unprotected_controls_from_track_repair():
    _, middle, _ = build(3, 1)
    ground = middle.np_engine().initial(1)
    state = {k:np.repeat(v, 3, axis=0) for k,v in ground.items()}
    state["simage"][1, 17] ^= 16
    state["trk"][2, 19, middle.T["HOLD"], 1] ^= 1
    rows = analysis.error_details(state, ground, middle)
    assert rows[0]["damaged_holders"] == []
    assert rows[1]["fields"]["simage"] == 1 and rows[1]["damaged_holders"] == [17]
    assert rows[1]["raw_track_copy_errors"] == rows[1]["repaired_track_errors"] == 0
    assert rows[2]["raw_track_copy_errors"] == 1 and rows[2]["damaged_holders"] == [19]
    assert rows[2]["repaired_hold_errors"] == rows[2]["repaired_info_errors"] == 0
