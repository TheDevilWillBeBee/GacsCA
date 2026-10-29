#!/usr/bin/env python3
"""SP18 source core with a one-tick Age offset in the shifted reference.

Use the retained SP18 source-core driver with an explicitly different
left reference. Evolve that periodic reference by one actual own-rule
step before t=0. Its entire state is operational, including its mail/
workspace. This is still a finite driven measurement, not an eroder proof.
"""
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
import check_sparse_epoch448_source_core as prior


def main():
    source=Path(prior.__file__).read_text()
    source=source.replace("default=20", "default=4")
    source=source.replace("stem = 'SP18_epoch_source_core'", "stem = 'SP18_epoch_GF_Age_source_core'")
    source=source.replace("np.savez_compressed(input_asset, top=top, upper=upper, initial_packed=initial,\n"
        "                        core_begin=begin, core_tau=tau)", "pass # saved after actual one-tick reference advancement")
    old="    sim.set_state(initial, t=0)\n    del initial"
    new="""    sim.set_state(initial, t=0)
    sim.run(1)
    initial[1]=sim.state()[1]
    sim.set_state(initial, t=0)
    np.savez_compressed(input_asset,top=top,upper=augmented(candidate,top),
        initial_packed=initial,core_begin=begin,core_tau=tau,left_reference_clock_offset=1)
    del initial"""
    assert source.count(old)==1
    source=source.replace(old,new)
    source=source.replace("driver_sha256=digest(Path(__file__)),",
        "driver_sha256=digest(Path(__file__)), "
        "inherited_driver_sha256=digest(Path(prior.__file__)),")
    source=source.replace("left_reference_phase_shift=-1,",
        "left_reference_phase_shift=-1,left_reference_clock_offset=1,"
        "initial_shifted_reference_full_rule_steps=1,")
    namespace=dict(prior.__dict__,prior=prior,__file__=__file__)
    exec(compile(source,str(Path(__file__).resolve()),'exec'),namespace)
    namespace['main']()


if __name__=='__main__':
    main()
