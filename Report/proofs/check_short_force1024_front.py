#!/usr/bin/env python3
"""SP29 all-raw-word local front uniqueness and ROM bounds.

The unchanged local timing equations are checked against SP29's own
candidate. This is not a physical front invariant or reliability proof.
"""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
import check_distant_epoch1024_front as prior


def main():
    source=Path(prior.__file__).read_text()
    old='import proposed_sparse_distant_epoch1024 as proposed'
    assert source.count(old)==1
    source=source.replace(old,'import proposed_sparse_short_force1024 as proposed').replace('SP28','SP29')
    anchor='        checker_sha256=digest(Path(__file__)),proposal_source_sha256=digest(Path(proposed.__file__)),\n'
    assert source.count(anchor)==1
    source=source.replace(anchor,anchor+
        '        inherited_checker_source_sha256=digest(Path(prior.__file__)),SP28_modified=False,\n')
    namespace=dict(prior.__dict__,prior=prior,__file__=__file__)
    exec(compile(source,str(Path(__file__).resolve()),'exec'),namespace)
    namespace['main']()


if __name__=='__main__':main()
