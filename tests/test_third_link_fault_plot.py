"""Recovery censoring and visualization use actual observation times."""
import numpy as np

from experiments.plot_third_link_faults import recovery_interval, summarize, render


def test_sampled_sustained_recovery_not_first_accidental_zero():
    times = np.array([10, 11, 14, 18])
    assert recovery_interval(times, np.array([1, 0, 1, 0]), 10) == [4, 8]
    assert recovery_interval(times, np.array([1, 0, 0, 1]), 10) is None
    assert recovery_interval(times, np.zeros(4), 10) == [0, 0]
    assert recovery_interval(times, np.zeros(4), 20) is None


def test_fault_summary_and_all_figures(tmp_path):
    times = [16, 17, 18, 31, 32, 33, 47, 64]
    labels = [dict(phase="clean", width=0), dict(phase="early", width=1), dict(phase="late", width=1)]
    samples = [dict(step=t, bad_structure=[0, int(t == 17), int(t in (31, 32))],
                    flag1=[0, 0, 0], flag2=[0, int(t >= 17), int(t >= 31)]) for t in times]
    commits = [dict(period=i, ground=dict(structural_cells=[0, 0, 0], middle_info_bits=[0, 0, 0],
                                         any_state_cells=[0, 0, int(i == 1)]),
                    conditional_transition=dict(any_state_cells=[0, 0, 0])) for i in (1, 2)]
    meta = dict(identity=dict(labels=labels, U=32, Q=64, physical_cells=256), samples=samples, commits=commits)
    rows = summarize(meta)
    assert rows[0]["sampled_structure_recovery_intervals"] == [[0, 1]]
    assert rows[1]["sampled_structure_recovery_intervals"] == [[1, 2]]
    assert rows[0]["final_flag2"] == [1] and rows[0]["final_info_bit_errors"] == [0]
    assert render(meta, np.zeros((len(times), 3, 16)), tmp_path / "test") == rows
    for kind in ("recovery", "decoded", "space_time"):
        for ext in ("png", "pdf"):
            assert (tmp_path / f"test_{kind}.{ext}").stat().st_size > 0
