#!/usr/bin/env python3
"""Universal abstract SP27 verifier, adapted from the retained SP22 checker.

The build did not record a transport hash; the actual regenerated compiled
circuit and profile are instead pinned to the candidate/build identities.
The checker records its own transport helper hash. No physical repair or
all-time reliability follows from this abstract programme certificate.
"""
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
import check_sparse_backward_fitted448_schedule as prior


def main():
    source=Path(prior.__file__).read_text()
    import_line='import proposed_sparse_backward_fitted448 as proposed'
    assert source.count(import_line)==1
    source=source.replace(import_line,'import proposed_sparse_distant_transport1024 as proposed')
    line='    require(build["transport_checker_sha256"] == digest(ROOT / "Report/proofs/check_fast_mail_proposal.py"), "transport source changed")\n'
    assert source.count(line)==1
    source=source.replace(line,'')
    source=source.replace('SP22','SP27').replace('history_ranks_checked=12','history_ranks_checked=64')
    # The retained generic checker tests clocks through distance12.
    # Expand actual capture events as well as the history-rank loop.
    anchor='    source = inspect.getsource(transport.fixed_capture_certificate)\n'
    assert source.count(anchor)==1
    source=source.replace(anchor,anchor+
        '    source = source.replace("for off in range(1, 13)", "for off in range(1, max(abs(o) for r in table for o in r[\\\"offsets\\\"]) + 1)")\n')
    source=source.replace("inherited_checker_source_sha256=digest(ROOT/'Report/proofs/check_sparse_epoch448_schedule.py')",
        "inherited_checker_source_sha256=digest(ROOT/'Report/proofs/check_sparse_backward_fitted448_schedule.py')")
    namespace=dict(prior.__dict__,prior=prior,__file__=__file__)
    exec(compile(source,str(Path(__file__).resolve()),'exec'),namespace)
    namespace['main']()


if __name__=='__main__':main()
