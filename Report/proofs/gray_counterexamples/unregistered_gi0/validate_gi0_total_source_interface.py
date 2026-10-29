#!/usr/bin/env python3
"""Read-only replay of GI0; never rewrites any accepted receipt or source."""
from pathlib import Path
import hashlib,json,sys,time
sys.path.insert(0,str(Path(__file__).resolve().parent))
import check_gi0_total_source_interface as check


def normalize(value):return json.loads(json.dumps(value,sort_keys=True))


def main():
    start=time.monotonic();path=check.DIRECTORY/'GI0_total_source_interface_certificate.json'
    before=path.read_bytes();expected=json.loads(before);actual=check.receipt()
    assert normalize(actual)=={k:v for k,v in expected.items() if k!='elapsed_seconds'}
    assert path.read_bytes()==before
    assert actual['results']['smallest_contiguous_interval_hull_for_this_projection']==[-7,8]
    assert actual['results']['all_Gray_completions_or_Gacs_nonexistence_proved'] is False
    print(json.dumps(dict(read_only=True,validated=True,receipt_sha256=hashlib.sha256(before).hexdigest(),
        smallest_projection_interval_hull=[-7,8],whole_Gray_iid_or_faster_U_result=False,
        elapsed_seconds=time.monotonic()-start)))


if __name__=='__main__':main()
