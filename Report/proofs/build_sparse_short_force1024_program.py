#!/usr/bin/env python3
"""Build explicitly changed isolated SP29; compilation is not reliability."""
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
import build_sparse_distant960_program as prior


def main():
    source=Path(prior.__file__).read_text()
    assert source.count('import proposed_sparse_distant960 as proposed')==1
    source=source.replace('import proposed_sparse_distant960 as proposed',
                          'import proposed_sparse_short_force1024 as proposed')
    source=source.replace('import xor_multiplicity_scheduler as safe',
                          'import fixed_match_wait_scheduler as safe')
    source=source.replace('SP23','SP29')
    source=source.replace('active_G17_modified=False,SP22_modified=False,',
                          'active_G17_modified=False,SP22_modified=False,SP28_modified=False,force_duration=2048,')
    source=source.replace('driver_sha256=digest(Path(__file__)),',
        'driver_sha256=digest(Path(__file__)),inherited_driver_sha256=digest(Path(prior.__file__)),')
    namespace=dict(prior.__dict__,prior=prior,__file__=__file__)
    exec(compile(source,str(Path(__file__).resolve()),'exec'),namespace)
    namespace['main']()


if __name__=='__main__':
    main()
