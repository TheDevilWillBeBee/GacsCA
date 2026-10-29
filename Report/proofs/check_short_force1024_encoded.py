#!/usr/bin/env python3
"""SP29 complete-start E0 interfaces; physical proof in SP29_OWN_RULE.md."""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
import check_distant_epoch1024_encoded as prior


def main():
    source=Path(prior.__file__).read_text()
    old='import proposed_sparse_distant_epoch1024 as proposed'
    assert source.count(old)==1
    source=source.replace(old,'import proposed_sparse_short_force1024 as proposed').replace('SP28','SP29')
    anchor='        checker_sha256=digest(Path(__file__)),proposal_source_sha256=digest(Path(proposed.__file__)),\n'
    assert source.count(anchor)==1
    source=source.replace(anchor,anchor+
        '        inherited_checker_source_sha256=digest(Path(prior.__file__)),SP28_modified=False,force_duration=2048,\n'
        '        written_proof_sha256=digest(ROOT/"Report/proofs/SP29_OWN_RULE.md"),\n')
    source=source.replace("proof='ROBUSTNESS J138; explicit SP29 epoch/NPe changes with J135 corrected fast-window induction'",
        "proof='ROBUSTNESS J166 / SP29_OWN_RULE.md; own programme and shortened force, J125/J135/J138 physical induction with verified interfaces'")
    namespace=dict(prior.__dict__,prior=prior,__file__=__file__)
    exec(compile(source,str(Path(__file__).resolve()),'exec'),namespace)
    namespace['main']()


if __name__=='__main__':main()
