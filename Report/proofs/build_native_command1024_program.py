#!/usr/bin/env python3
"""Compile the explicitly changed SP31 into its own isolated ROM."""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
import build_sparse_distant960_program as inherited


def main():
    source=Path(inherited.__file__).read_text()
    old='import proposed_sparse_distant960 as proposed'
    assert source.count(old)==1
    source=source.replace(old,'import proposed_native_command1024 as proposed')
    source=source.replace('import xor_multiplicity_scheduler as safe','import fixed_match_wait_scheduler as safe')
    source=source.replace('SP23','SP31')
    source=source.replace('active_G17_modified=False,SP22_modified=False,',
        'active_G17_modified=False,SP22_modified=False,SP30_modified=False,native_service_force_removed=True,native_WF2_from_actual_special_Info=True,')
    source=source.replace('driver_sha256=digest(Path(__file__)),',
        'driver_sha256=digest(Path(__file__)),inherited_driver_sha256=digest(Path(inherited.__file__)),')
    namespace=dict(inherited.__dict__,inherited=inherited,__file__=__file__)
    exec(compile(source,str(Path(__file__).resolve()),'exec'),namespace)
    namespace['main']()


if __name__=='__main__':main()
