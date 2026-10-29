#!/usr/bin/env python3
"""Reuse the audited universal G17 abstract checker for GR0's own ROM.

The execution/identity/capture/courier checks apply to the isolated GR0
schedule. This deliberately does not claim its adapted simulation protocol
is Gray's five-stage protocol.
"""
from pathlib import Path
import hashlib
import inspect
import json
import sys
from types import SimpleNamespace
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
sys.path.insert(0,str(ROOT/'Report/proofs'))
import check_g17_schedule as inherited
import gray_scale_rule as proposed


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    output = ROOT/'figs/gray_counterexamples'
    build = json.loads((output/'GR0_program_build.json').read_text())
    assert build['build_complete']
    assert build['proposal_sha256'] == digest(proposed.__file__)
    assert build['asset_sha256'] == digest(output/'GR0_program.npz')
    assert build['listing_sha256'] == digest(output/'GR0_program_listing.json')
    listing = json.loads((output/'GR0_program_listing.json').read_text())
    candidate = proposed.load_artifact()
    assert candidate.digest() == build['candidate_sha256']
    source = inspect.getsource(inherited.main)
    replacements = {
        'c = candidates.load("G17")': 'c = proposed.load_artifact()',
        '''    require(c.digest() == "23a14aab4d3dc4fde5562cf3e26a4536b05456f84e65850fcb3bd95a104d8ceb",
            "G17 identity changed: re-audit before changing this verifier")''':
        '    require(c.digest() == build["candidate_sha256"], "GR0 candidate identity")',
        '''    eng = jobsched.Engine(p, comp, c.layout, MP=p.MP,
                          **candidates.RECIPES["G17"]["compile"]["jobs"])
    eng.run()''':
        '    eng = SimpleNamespace(prog=SimpleNamespace(listing=listing))',
        'candidate="G17"': 'candidate="GR0"',
        'ROOT / "figs/robustness/symbolic_schedule.json"':
        'ROOT / "figs/gray_counterexamples/GR0_symbolic_schedule.json"',
    }
    for old,new in replacements.items():
        assert source.count(old) == 1, old
        source = source.replace(old,new)
    namespace = dict(inherited.__dict__)
    namespace.update(ROOT=ROOT, __file__=__file__, proposed=proposed, listing=listing,
                     build=build, SimpleNamespace=SimpleNamespace)
    exec(compile(source,'<GR0 universal own-schedule checker>', 'exec'),namespace)
    namespace['main']()
    receipt_path = output/'GR0_symbolic_schedule.json'
    receipt = json.loads(receipt_path.read_text())
    receipt.update(proposal_sha256=digest(proposed.__file__),
        inherited_checker_sha256=digest(inherited.__file__),
        generated_checker_sha256=hashlib.sha256(source.encode()).hexdigest(),
        own_programme_verified=True, gray_verbatim_simulation=False,
        global_reliability_established=False)
    receipt_path.write_text(json.dumps(receipt,indent=2)+'\n')


if __name__ == '__main__':
    main()
