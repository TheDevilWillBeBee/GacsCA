#!/usr/bin/env python3
"""All-raw front/ROM interfaces for the separate SP30 own rule."""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
import check_distant_epoch1024_front as prior


def main():
    source=Path(prior.__file__).read_text()
    old='import proposed_sparse_distant_epoch1024 as proposed';assert source.count(old)==1
    source=source.replace(old,'import proposed_sparse_signal_reservation1024 as proposed').replace('SP28','SP30')
    anchor='        checker_sha256=digest(Path(__file__)),proposal_source_sha256=digest(Path(proposed.__file__)),\n'
    assert source.count(anchor)==1
    source=source.replace(anchor,anchor+'        inherited_checker_source_sha256=digest(Path(prior.__file__)),SP29_modified=False,\n')
    namespace=dict(prior.__dict__,prior=prior,__file__=__file__)
    exec(compile(source,str(Path(__file__).resolve()),'exec'),namespace);namespace['main']()


if __name__=='__main__':main()
