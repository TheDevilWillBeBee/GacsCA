import numpy as np
import pytest

from experiments.plot_nested_phase_faults import matrices, plot


def fixture():
    records = []
    for period in (1, 2, 3):
        records.append(dict(period=period, middle_age=10691 + period,
                            rows=[dict(fields=dict(simage=0, simaddr=0), raw_track_copy_errors=0, repaired_track_errors=0),
                                  dict(fields=dict(simage=1, simaddr=1), raw_track_copy_errors=4 if period == 1 else 0, repaired_track_errors=0)],
                            ground=dict(any_state_cells=[0, 1]), conditional_transition=dict(any_state_cells=[0, int(period == 1)]),
                            physical_flag2=[0, 65]))
    return dict(identity=dict(spec=dict(phase="evaluation"), labels=[dict(target="clean", width=0, trial=0),
                dict(target="control", width=21, trial=0)]), records=records)


def test_nested_phase_plot_uses_values_not_counts_of_nonzero_fields(tmp_path):
    data = fixture()
    values = matrices(data)
    np.testing.assert_array_equal(values["Incorrect decoded register values"], [[0, 0, 0], [2, 2, 2]])
    np.testing.assert_array_equal(values["Incorrect raw track copies"], [[0, 0, 0], [4, 0, 0]])
    plot(data, tmp_path / "plot")
    assert (tmp_path / "plot.png").stat().st_size > 10000
    assert (tmp_path / "plot.pdf").stat().st_size > 1000
    with pytest.raises(FileExistsError): plot(data, tmp_path / "plot")
