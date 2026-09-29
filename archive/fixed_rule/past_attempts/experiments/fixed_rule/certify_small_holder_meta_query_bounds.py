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

from gacsca.fixed_rule import small_holder_rule as f, small_holder_core as c
from gacsca.fixed_rule.wordcode import NAND, ADD, SHR, EQ, LT, MASK
from experiments.fixed_rule import certify_small_holder_timed_dataflow as timed
from experiments.fixed_rule.audit_small_holder_position_events import sha


class KnownBits:
    def __init__(self,terms):self.terms=terms;self.masks=[]
    def at(self,term):
        while len(self.masks)<=term:
            node=self.terms.nodes[len(self.masks)];kind=node[0]
            if kind=='const':ones=node[1];zeros=MASK^ones
            elif kind=='input':ones=(1<<node[3])-1;zeros=MASK
            elif kind=='rom':ones=(1<<dict(c.SCHEMA)[c.STATIC[node[2]]])-1;zeros=MASK
            elif kind=='op':
                op,a,b=node[1:];ao,az=self.masks[a];bo,bz=self.masks[b]
                if op==NAND:ones=az|bz;zeros=ao&bo
                elif op in (EQ,LT):ones=1;zeros=MASK
                elif op==ADD:
                    top=ao+bo;ones=MASK if top>MASK else (1<<top.bit_length())-1;zeros=MASK
                elif op==SHR:
                    value=self.terms.value(b)
                    ones=(0 if value>=64 else ao>>value) if value is not None else (1<<ao.bit_length())-1
                    zeros=MASK
                else:raise AssertionError(('unknown word operation',op))
            else:raise AssertionError(('unknown symbolic node',node))
            self.masks.append((ones,zeros))
        return self.masks[term]

    def valid_query(self,query):
        ones,_=self.at(query)
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
