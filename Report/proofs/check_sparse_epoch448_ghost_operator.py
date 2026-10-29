#!/usr/bin/env python3
"""Measured NumPy/CUDA check of SP18's explicitly driven halo operator.

Reuse the SP14 finite operator comparison, with SP18's own netlist/ROM and
new receipt names. Neither comparison is a universal backend certificate.
"""
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
import check_sparse_framed448_ghost_operator as prior
import proposed_sparse_epoch448 as proposed


def main():
    source = Path(prior.__file__).read_text().replace('SP14', 'SP18')
    source = source.replace("checker_sha256=digest(Path(__file__)),",
        "checker_sha256=digest(Path(__file__)), "
        "inherited_checker_sha256=digest(Path(prior.__file__)),")
    namespace = dict(prior.__dict__, proposed=proposed, prior=prior, __file__=__file__)
    exec(compile(source, str(Path(__file__).resolve()), 'exec'), namespace)
    namespace['proposed'] = proposed
    namespace['main']()


if __name__ == '__main__':
    main()
