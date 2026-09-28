"""Stream every immediate parent of an actual depth-two initializer, bounded RAM."""
import argparse,hashlib,json,resource,time
from pathlib import Path
import numpy as np
from gacsca.fixed_rule import small_holder_stream_initial as stream,small_holder_initial as scalar
from gacsca.fixed_rule import small_holder_rule as f,small_holder_projected as r,small_holder_program as p


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True);args=parser.parse_args();out=Path(args.output)
    if out.exists():raise FileExistsError('preserve evidence')
    start=time.perf_counter();top=(r.Cell(address=321,age=117,s2_head=1,s2_phase=3,s2_rd=321,s2_value=0x123456789ABCDEF0),)
    initial=stream.InitialRing(top);digest=hashlib.sha256();count=checks=0;max_chunk=0
    for rows in initial.chunks(1):
        digest.update(rows.tobytes());max_chunk=max(max_chunk,rows.nbytes)
        for offset in (0,len(rows)-1):
            expected=f.encode_cell(r.lift(scalar.cell_at(top,1,count+offset)))
            np.testing.assert_array_equal(rows[offset],expected);checks+=1
        count+=len(rows)
    assert count==f.Q
    info=[]
    for at in range(0,f.FIELDS,stream.CHUNK):info.extend(initial.raw(1,p.layout().info[at:at+stream.CHUNK])[:,f.COL['s2_data']])
    np.testing.assert_array_equal(info,f.encode_cell(r.lift(top[0])))
    paths=(Path(__file__),Path(stream.__file__),Path(scalar.__file__))
    result=dict(passed=True,encoded_depth=2,parent_rows_streamed=count,raw_words_per_parent=f.FIELDS,raw_bytes_streamed=count*f.FIELDS*8,max_chunk_bytes=max_chunk,scalar_rows_checked=checks,all_top_raw_fields_preserved=True,stream_sha256=digest.hexdigest(),descriptor_sha256=f.self_description().digest(),resources=[initial.resources(d) for d in (1,2,3)],seconds=time.perf_counter()-start,host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,source_sha256={str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in paths},limitation='complete real depth-two parent stream; no full bottom-world allocation or evolving transition in this measurement')
    out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))


if __name__=='__main__':main()
