"""Literal certificate for the shared early/final 8Q local successor."""
import argparse
from dataclasses import replace
import hashlib
import json
from pathlib import Path
import random
import resource
import time

from gacsca.fixed_rule import spatial_epoch8 as spatial
from gacsca.fixed_rule import stream28_dual_pass20 as physical
from gacsca.fixed_rule import stream28_dual_pass_description20 as full
from gacsca.fixed_rule import stream28_dual_pass_optimized20 as optimized
from gacsca.fixed_rule import stream28_dual_holder_rule20 as holder
from gacsca.fixed_rule import stream28_dual_compact_vote20 as vote


def neighborhood(site,age,source=0,output=False,value=0):
    rows=[]
    for offset in physical.NEIGHBORHOOD:
        address=(site+offset)%physical.Q
        raw=holder.Cell(address=address,age=age,
                        **{f's{k}_data':source for k in range(5)})
        evaluator=spatial.Cell(address=address,
                    kind=spatial.OUTPUT if output and offset==0 else
                         spatial.SOURCE if not output and offset==0 else
                         spatial.INERT)
        if output and offset==1:
            evaluator=replace(evaluator,
                              mail=spatial.Packet(1,site,0,3,value))
        rows.append(physical.Cell(raw,evaluator))
    return tuple(rows)


def check():
    started=time.perf_counter()
    rng=random.Random(2026092908)
    original=full.build()
    simplified=optimized.build()
    assert (original.inputs,len(original.outputs))==(
        15*physical.FIELDS,physical.FIELDS)
    counts={'early_capture':0,'early_flag':0,'early_nonflag':0,
            'early_gate':0,'old_vote':0,'late_run':0,'outside':0,
            'head_trigger':0}

    def verify(rows,label):
        want=physical.encode_cell(physical.local_step(rows))
        words=tuple(word for cell in rows for word in
                    physical.encode_cell(cell))
        for name,program in (('full',original),('optimized',simplified)):
            got=program.evaluate(words)
            if got!=want:
                mismatch=next((i,a,b) for i,(a,b) in
                              enumerate(zip(got,want)) if a!=b)
                raise AssertionError((label,name,mismatch))
        counts[label]+=1

    for _ in range(12):
        site=rng.randrange(physical.Q)
        verify(neighborhood(site,physical.EARLY_CAPTURE_AGE,
                            source=rng.getrandbits(64)), 'early_capture')
        for target in physical.EARLY_FLAG_HOLD_ADDRESSES:
            verify(neighborhood(target,
                                physical.EARLY_RUN_START+rng.randrange(1,100),
                                source=7,output=True,
                                value=rng.getrandbits(64)), 'early_flag')
        verify(neighborhood(2497,physical.EARLY_RUN_START+
                            rng.randrange(1,100),source=7,output=True,
                            value=rng.getrandbits(64)), 'early_nonflag')
        tick=rng.randrange(1,spatial.PERIOD-1)
        rows=list(neighborhood(site,physical.EARLY_RUN_START+tick))
        gate=spatial.GateSpec(1,spatial.OUTPUT_OPCODE[1])
        rows[7]=replace(rows[7],evaluator=replace(rows[7].evaluator,
                        kind=spatial.GATE,age=tick,active_slot=1,
                        gates=(gate,spatial.GateSpec(1,14),
                               spatial.EMPTY_GATE),ready=3,
                        arg0=rng.getrandbits(64),
                        arg1=rng.getrandbits(64)))
        verify(tuple(rows),'early_gate')
        verify(neighborhood(site,holder.VOTE_AGES[0]),'old_vote')
        verify(neighborhood(site,physical.EARLY_RUN_STOP),'outside')
        rows=list(neighborhood(site,physical.EARLY_RUN_STOP))
        center=rows[7]
        rows[7]=physical.Cell(replace(center.holder,p3_first=1),
                              center.evaluator)
        verify(tuple(rows),'head_trigger')
        verify(neighborhood(site,holder.RESET_AGES[4]+2,
                            source=3,output=True,
                            value=rng.getrandbits(64)),'late_run')
    return dict(passed=True,literal_cases=sum(counts.values()),
                case_counts=counts,full_operations=len(original.operations),
                optimized_operations=len(simplified.operations),
                optimized_description_sha256=simplified.digest(),
                physical_source_sha256=hashlib.sha256(
                    Path(physical.__file__).read_bytes()).hexdigest(),
                max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                seconds=time.perf_counter()-started,
                limitation='Local exact F only; the short holder SEND ROM is '
                           'separately audited, while the full physical '
                           'U-period and decoded macrosteps are missing.')


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path)
    args=parser.parse_args()
    result=check()
    result['source_sha256']=hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    print(json.dumps(result,indent=2))
    if args.output:
        if args.output.exists():raise FileExistsError(args.output)
        args.output.write_text(json.dumps(result,indent=2)+'\n')
