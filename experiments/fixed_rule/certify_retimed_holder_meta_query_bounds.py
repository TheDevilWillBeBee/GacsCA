"""Discharge the valid-15-bit-query premise along every symbolic ROM path.

Instrument the diagnostic timed/batch proof; no physical execution is replaced.
Known-bit masks overapproximate each word, including descriptor-computed Address.
"""
import argparse
import hashlib
import json
from pathlib import Path
import resource
import time
from unittest.mock import patch

from gacsca.fixed_rule import retimed_holder_rule as f, retimed_holder_core as c
from gacsca.fixed_rule.wordcode import NAND, ADD, SHR, EQ, LT, MASK
from experiments.fixed_rule import certify_retimed_holder_timed_dataflow as timed
from experiments.fixed_rule.audit_small_holder_position_events import sha


class KnownBits:
    """Conservative structural width for this symbolic vocabulary.

    The full-description equivalence checker already handles variable, not,
    modular-add and Boolean nodes. Its structural bound is independent of the
    optimizer's possible-bit masks. No query is masked or modified here.
    """
    def __init__(self,terms):self.terms=terms
    def valid_query(self,query):
        ones=(1<<self.terms.width(query))-1
        assert ones<f.Q,('META query exceeds certified Address domain',ones)
        return ones


def prove(schedule_doc):
    original=timed.batch.Terms.lookup;checkers={};calls=0;maximum=0;selectors=set()
    def checked(terms,address,selector):
        nonlocal calls,maximum
        checker=checkers.setdefault(terms,KnownBits(terms))
        maximum=max(maximum,checker.valid_query(address));calls+=1;selectors.add(selector)
        return original(terms,address,selector)
    with patch.object(timed.batch.Terms,'lookup',checked):result=timed.prove(schedule_doc)
    assert selectors==set(range(7))
    return dict(passed=True,checked_lookup_calls=calls,selectors=sorted(selectors),
                maximum_possible_query_mask=maximum,certified_query_bits=15,
                includes_input_regeneration_and_computed_output_regeneration=True,
                timed_Dataflow_result=result)


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--schedule',required=True);parser.add_argument('--timed',required=True);parser.add_argument('--output',required=True)
    args=parser.parse_args();out=Path(args.output)
    if out.exists():raise FileExistsError('preserve evidence')
    start=time.perf_counter();schedule_doc=json.loads(Path(args.schedule).read_text());previous=json.loads(Path(args.timed).read_text())
    for doc in (schedule_doc,previous):
        assert doc['passed']
        for source,wanted in doc['source_sha256'].items():assert sha(source)==wanted,source
    assert previous['schedule_sha256']==sha(args.schedule)
    result=prove(schedule_doc);replay=json.loads(json.dumps(result.pop('timed_Dataflow_result')))
    assert all(previous[key]==value for key,value in replay.items()),'instrumentation changed timed result'
    result.update(descriptor_sha256=f.self_description().digest(),input_sha256={str(path):sha(path) for path in (args.schedule,args.timed)},
                  source_sha256={str(path):sha(path) for path in (Path(__file__),Path(timed.__file__),Path(timed.batch.__file__))},
                  seconds=time.perf_counter()-start,host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                  limitation='Discharges the query-width premise in the symbolic instruction trajectory. Physical META refinements and the complete period induction remain separate proof dependencies.')
    out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2),flush=True)


if __name__=='__main__':main()
