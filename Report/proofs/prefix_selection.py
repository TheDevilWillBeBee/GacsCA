"""EXPLICIT SP3 maintenance change: Flag2 no longer overrides Flag1's vote.

The quiet-majority diagnostic and all flag predicates remain those of SP2.
Only vote_right changes from exists AND (NOT f1 OR f2) to exists AND NOT f1.
This module does not modify G17, SP1, SP2, CURRENT or their helper globals.
Its full own-ROM instance is defined separately in proposed_sparse_prefix.
"""
from gacsca import maintenance
import check_quiet_majority_proposal as diagnostic
from check_right_barrier import dominant_majority

OLD = "    vote_right = n.AND(exists, n.OR(n.NOT(f1), f2))"
NEW = "    vote_right = n.AND(exists, n.NOT(f1))"


def proposed_build(symbolic=False):
    _, source = diagnostic.proposed_build(symbolic=symbolic)
    assert source.count(OLD) == 1
    source = source.replace(OLD, NEW)
    namespace = dict(maintenance.__dict__)
    if symbolic:
        namespace["majority_word"] = dominant_majority
    exec(compile(source, "<SP3: no Flag2 geometry override; explicit change>", "exec"), namespace)
    return namespace["build"], source
