#!/usr/bin/env python3
"""SP29 exact operand/phase audit for the broad coherent Info theorem."""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
import check_distant_epoch1024_encoding_family as prior


def main():
    source=Path(prior.__file__).read_text()
    replacements={
        'import proposed_sparse_distant_epoch1024 as proposed':'import proposed_sparse_short_force1024 as proposed',
        'assert len(listing) == 130974':'assert len(listing) == 130871',
        'assert (direct, histories) == (1368, 17715)':'assert (direct, histories) == (1354, 17684)',
        "proof_file = ROOT/'Report/proofs/SP28_ENCODING_FAMILY.md'":"proof_file = ROOT/'Report/proofs/SP29_OWN_RULE.md'"}
    for old,new in replacements.items():
        assert source.count(old)==1,old
        source=source.replace(old,new)
    source=source.replace('SP28','SP29').replace('E28','E29').replace('J144','J166')
    anchor='        active_G17_modified=False, checker_sha256=digest(Path(__file__)),\n'
    assert source.count(anchor)==1
    source=source.replace(anchor,anchor+
        '        inherited_checker_source_sha256=digest(Path(prior.__file__)),SP28_modified=False,force_duration=2048,\n')
    namespace=dict(prior.__dict__,prior=prior,__file__=__file__)
    exec(compile(source,str(Path(__file__).resolve()),'exec'),namespace)
    namespace['main']()


if __name__=='__main__':main()
