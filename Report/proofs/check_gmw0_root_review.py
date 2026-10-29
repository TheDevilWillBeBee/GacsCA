#!/usr/bin/env python3
"""Read-only review of GMW0's frozen native-prefix execution assets.

Checks every physical holder at every retained execution tick. These are
finite implementation checks, not an E0 theorem or a self-programme proof.
The accepted universal arguments are the register and copy inductions in
GMW0_PHYSICAL_NATIVE_PROGRAMME.md. Only this review's receipt is written.
"""
from pathlib import Path
import hashlib
import json
import sys
import time

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / "Report/proofs/gray_counterexamples"
DIRECTORY = ROOT / "figs/gray_counterexamples"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(SOURCE))
import gray_moving_word_kernel as kernel
import literal_maintenance
import validate_gray_counterexamples as frozen_validator


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    started = time.monotonic()
    frozen_validator.validate_moving_word_kernel(DIRECTORY, SOURCE)
    dependencies = (
        SOURCE / "gray_moving_word_kernel.py",
        SOURCE / "check_gray_moving_word_kernel.py",
        SOURCE / "GMW0_PHYSICAL_NATIVE_PROGRAMME.md",
        SOURCE / "literal_maintenance.py",
        DIRECTORY / "GMW0_native_programme_certificate.json",
        DIRECTORY / "GMW0_native_beta.bin",
        DIRECTORY / "GMW0_native_listing.json",
        DIRECTORY / "GMW0_native_physical_replays.npz",
    )
    before_hashes = {str(path.relative_to(ROOT)): digest(path)
                     for path in dependencies}
    beta, listing, labels = kernel.native_word_programme()
    positions = []
    holder_counts = [0] * 5
    native_replays = 0
    with np.load(DIRECTORY / "GMW0_native_physical_replays.npz") as retained:
        # Independent scalar comparisons of all retained arbitrary upper inputs.
        for data, result in zip(retained["inputs"], retained["outputs"]):
            cells = {j: dict(zip(("addr", "age", "f1", "f2", "wf1", "wf2"),
                                map(int, data[j + 5]))) for j in range(-5, 6)}
            expected = literal_maintenance.scalar(cells)
            assert result.tolist() == [expected[field]
                                      for field in ("addr", "age", "f1", "f2")]
            native_replays += 1
        cells = {j: dict(zip(("addr", "age", "f1", "f2", "wf1", "wf2"),
                            map(int, retained["inputs"][18, j + 5])))
                 for j in range(-5, 6)}
        tape = kernel.tape_from_native(cells)
        out = {}
        old_position = kernel.ENTRY
        age = 112 * kernel.Q + 1
        for position, raw_before, raw_after, written in zip(
                retained["trace_addresses"], retained["trace_before"],
                retained["trace_after"], retained["trace_writes"]):
            position = int(position)
            old_head = int.from_bytes(raw_before.tobytes(), "little")
            new_head = int.from_bytes(raw_after.tobytes(), "little")
            packet = kernel.unpack(old_head)
            assert position == old_position + {0: 0, 1: 1, 2: -1}[packet.move]
            new_out = dict(out)
            if int(written) >= 0:
                new_out[position] = int(written)
            for holder, slot in enumerate(kernel.SLOTS):
                x = position - slot
                neighbourhood = {
                    j: kernel.Cell(
                        addr=(x + j) % kernel.Q, age=age,
                        heads=tuple(old_head if x + j + s == old_position else 0
                                    for s in kernel.SLOTS),
                        mem=tuple(tape.get(x + j + s, 0) for s in kernel.SLOTS),
                        out=tuple(out.get(x + j + s, 0) for s in kernel.SLOTS))
                    for j in range(-5, 6)}
                actual = kernel.local_transition(neighbourhood, beta)
                expected = kernel.Cell(
                    addr=x % kernel.Q, age=(age + 1) % kernel.U,
                    heads=tuple(new_head if x + s == position else 0
                                for s in kernel.SLOTS),
                    mem=tuple(tape.get(x + s, 0) for s in kernel.SLOTS),
                    out=tuple(new_out.get(x + s, 0) for s in kernel.SLOTS))
                assert actual == expected, (age, position, holder)
                holder_counts[holder] += 1
            positions.append(position)
            old_position, out, age = position, new_out, age + 1
    assert native_replays == 98
    assert holder_counts == [34396] * 5 and age == 951901
    assert len(listing) == 107 and sum(row["bits"] for row in listing) == 2346
    assert 0 <= min(positions) <= max(positions) < kernel.Q
    for path in dependencies:
        assert digest(path) == before_hashes[str(path.relative_to(ROOT))]
    result = dict(
        scope="ROBUSTNESS J162: frozen GMW0 native-prefix review; finite replays only",
        Q=kernel.Q, U=kernel.U, error_lambda=kernel.LAMBDA,
        error_separation_c=kernel.ERROR_SEPARATION,
        programme_bits=2346, programme_instructions=107,
        head_logical_bits=434, physical_frame_bits=2272,
        native_prefix_ticks=34396, fifth_stage_budget=8 * kernel.Q,
        native_scalar_replays=native_replays,
        physical_whole_cell_replays=sum(holder_counts),
        holder_replay_counts=holder_counts,
        all_five_holders_checked_at_every_retained_tick=True,
        replay_is_exhaustive_all_raw_state_proof=False,
        replays_measured_only=True,
        preloaded_input_tape_and_zero_physical_workspace_flag_premises=True,
        own_full_programme_proved=False, continuing_E0_execution_proved=False,
        faithful_Gray_completion_proved=False, iid_memory_failure_proved=False,
        global_reliability_established=False, frozen_dependencies_unchanged=True,
        active_rule_modified=False, checker_sha256=digest(__file__),
        dependency_sha256=before_hashes, wall_seconds=time.monotonic() - started)
    receipt = ROOT / "figs/robustness/GMW0_root_review_certificate.json"
    receipt.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({key: result[key] for key in (
        "native_scalar_replays", "physical_whole_cell_replays",
        "frozen_dependencies_unchanged", "global_reliability_established",
        "wall_seconds")}))


if __name__ == "__main__":
    main()
