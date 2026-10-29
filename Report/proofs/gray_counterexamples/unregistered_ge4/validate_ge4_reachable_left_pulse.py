#!/usr/bin/env python3
"""Read-only replay of the unregistered conditional GE4 history certificate."""
from pathlib import Path
import hashlib,json,sys,time
SOURCE=Path(__file__).resolve().parent
sys.path.insert(0,str(SOURCE))
import check_ge4_reachable_left_pulse as check


def canonical(value):return json.loads(json.dumps(value,sort_keys=True))


def main():
    started=time.monotonic()
    path=check.DIRECTORY/'GE4_reachable_left_pulse_certificate.json'
    before=path.read_bytes();expected=json.loads(before)
    actual=check.receipt()
    assert canonical(actual)=={k:v for k,v in expected.items() if k!='elapsed_seconds'}
    assert path.read_bytes()==before
    assert actual['results']['sixth_quiet_clock_interval_colonies']==[7,35]
    assert actual['fixed_left_later_widths_assumed'] is False
    assert actual['results']['faithful_Gray_refutation_iid_or_shorter_U_proved'] is False
    print(json.dumps(dict(validated=True,read_only=True,receipt_sha256=hashlib.sha256(before).hexdigest(),
        actual_native_history_proved_conditionally=True,sixth_quiet_clock_interval_colonies=[7,35],
        whole_Gray_iid_or_shorter_U_proved=False,elapsed_seconds=time.monotonic()-started)))


if __name__=='__main__':main()
