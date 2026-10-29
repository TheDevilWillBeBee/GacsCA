#!/usr/bin/env python3
"""SP31 canonical native interfaces; pure-E0 scope only.

The written induction supplies the quantified time statement. The
cofactors and complete legal increment table certify its local steps.
"""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
import check_distant960_native as prior


def main():
    source=Path(prior.__file__).read_text()
    replacements={
        'import proposed_sparse_distant960 as proposed':'import proposed_native_command1024 as proposed',
        "service_force=n.any([service['service_force'],epoch['force'],pressure['signal']])":"service_force=0",
        'latest==23641<p.E0==24192':'latest==25217<p.E0==25984',
        "['Q']==965":"['Q']==1029","['POSITION_BITS']==10":"['POSITION_BITS']==11",
        'frame_size=965,frame_position_bits=10':'frame_size=1029,frame_position_bits=11',
        'actual30 GF/Age wiring identities':'actual29 GF/Age wiring identities',
        'error_set_E0_union_actual_real1_required=True':'errors_restricted_to_actual_global_E0=True',
        'all_time_computed_GF_Age_under_E0_plus_real1_proved=True':'all_time_computed_GF_Age_under_pure_E0_proved=True',
        "scope='J125 geometry/vote/native induction applies to SP23 changed constants with actual29 GF/Age wiring identities; no own programme/data/higher-error theorem'":"scope='SP31 actual29 GF/Age wiring with service_force0; canonical/common native induction under pure global E0; no damaged-input or higher-error theorem'"}
    for old,new in replacements.items():
        assert source.count(old)==1,old;source=source.replace(old,new)
    source=source.replace('SP23','SP31')
    anchor='checker_sha256=digest(Path(__file__)),';assert source.count(anchor)==1
    source=source.replace(anchor,anchor+'inherited_checker_sha256=digest(Path(prior.__file__)),SP30_modified=False,force_duration=2048,')
    namespace=dict(prior.__dict__,prior=prior,__file__=__file__)
    exec(compile(source,str(Path(__file__).resolve()),'exec'),namespace);namespace['main']()


if __name__=='__main__':main()
