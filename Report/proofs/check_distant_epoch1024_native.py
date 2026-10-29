#!/usr/bin/env python3
"""SP28 native-only transfer of J125/J126, at explicitly changed parameters."""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
import check_distant960_native as prior


def main():
    source=Path(prior.__file__).read_text()
    replacements={
        'import proposed_sparse_distant960 as proposed':'import proposed_sparse_distant_epoch1024 as proposed',
        'latest==23641<p.E0==24192':'latest==25217<p.E0==25984',
        "['Q']==965":"['Q']==1029",
        "['POSITION_BITS']==10":"['POSITION_BITS']==11",
        'frame_size=965,frame_position_bits=10':'frame_size=1029,frame_position_bits=11',
        'actual30 GF/Age wiring identities':'actual29 GF/Age wiring identities'}
    for old,new in replacements.items():
        assert source.count(old)==1,old
        source=source.replace(old,new)
    source=source.replace('SP23','SP28')
    source=source.replace('checker_sha256=digest(Path(__file__)),',
        'checker_sha256=digest(Path(__file__)),inherited_checker_sha256=digest(Path(prior.__file__)),')
    namespace=dict(prior.__dict__,prior=prior,__file__=__file__)
    exec(compile(source,str(Path(__file__).resolve()),'exec'),namespace)
    namespace['main']()


if __name__=='__main__':main()
