"""Audit emitted nested opcodes and independent concurrency/scratch barriers."""
import argparse
from collections import Counter
import json
from pathlib import Path

from gacsca.build import make_tower, make_system
from gacsca.interp import INTERPRETABLE, NMAX, NSLOT, slot_of
from experiments.tower_checkpoint import fingerprint


def inventory():
    result = []
    configurations = [
        ("R3", {}),
        ("R5", dict(R=5, D=1, Q0=512, U0=32768, U1=8192)),
        ("Gray", dict(R=5, D=1, Q0=8192, U0=1048576, Q1=8192,
                      U1=1048576, ncol0=8192, schedule="gray")),
    ]
    # The additional four kinds require the explicit inner context; this is
    # an inventory of the current implementation, not constructor bypassing.
    supported = set(INTERPRETABLE) | {"IBC", "ICHAIN", "ILATCH", "IEVAL"}
    for label, kw in configurations:
        middle, top = make_tower(**kw)
        ages = sorted({op.t0 for op in middle.prog.ops})
        peak = max(len(middle.prog.ops_at(a)) for a in ages)
        peak_ages = [a for a in ages if len(middle.prog.ops_at(a)) == peak]
        value_slots = []
        for a in ages:
            ops = middle.prog.ops_at(a)
            for i, op in enumerate(ops):
                if op.kind not in ("CONST", "RESET", "BUSLATCH_INT"):
                    value_slots.append(slot_of(ops, i))
        gray = label == "Gray"
        lower = make_system(Q=8192 if gray else 1024, U=1048576 if gray else 65536,
                            ncol=16, R=middle.T.R, D=middle.prog.D,
                            Qs=middle.p.Q, Us=middle.p.U, Qss=top.p.Q, Uss=top.p.U,
                            with_tracks=True, full_registers=True, nested_controls=True,
                            schedule="gray" if gray else "compressed", prog_up=middle.prog,
                            L_up=middle.L, trickle_up=middle.sched.trickle,
                            regwin_up=middle.sched.reg_window, inner_ctx=middle.sched.ictx)
        deadline = 15 * lower.p.U // 16 if gray else lower.p.U - 1
        diagnostic = dict(excluded_kinds=[], execution_verified=False,
                          physical_Q=lower.p.Q, physical_U=lower.p.U,
                          encoded_bits=lower.L.K, compute_end=lower.sched.compute_end,
                          deadline=deadline, slack=deadline-lower.sched.compute_end,
                          evaluation_slots=sum(o.kind == "IEVAL" for o in lower.prog.ops))
        result.append(dict(name=label, Q=middle.p.Q, U=middle.p.U,
                           instruction_counts=dict(Counter(op.kind for op in middle.prog.ops)),
                           unsupported_emitted_kinds=sorted({op.kind for op in middle.prog.ops} - supported),
                           peak_concurrent=peak, peak_ages=peak_ages,
                           peak_kinds=dict(Counter(op.kind for op in middle.prog.ops_at(peak_ages[0]))),
                           current_instruction_cap=NMAX,
                           largest_nonconstant_resource_slot=max(value_slots), resource_slots=NSLOT,
                           full_compilation=diagnostic))
    return dict(scope="static compiler inventory, not a third-link execution", configurations=result,
                fingerprints=fingerprint())


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    data = inventory()
    with args.output.open("x") as stream:
        json.dump(data, stream, indent=2)
    for item in data["configurations"]:
        print(item["name"], "missing", item["unsupported_emitted_kinds"],
              "concurrency", item["peak_concurrent"], "/", item["current_instruction_cap"],
              "resource slot", item["largest_nonconstant_resource_slot"], "/", item["resource_slots"])


if __name__ == "__main__":
    main()
