"""Packet induction replay plus checks of the actual CPU transport helpers.

The BDD proves the finite-coordinate flight identity. The compiled helper audit
bridges to the C++ representation on the reported exhaustive/source and sampled
target/time classes; it is not a proof of the entire event executor.
"""
import argparse
import ctypes
import hashlib
import inspect
import json
from pathlib import Path
import resource
import subprocess
import time

from gacsca.fixed_rule import retimed_holder_cpu_gather as backend
from gacsca.fixed_rule import retimed_holder_core as c, retimed_holder_rule as f
from gacsca.fixed_rule import small_holder_core as old_c
from experiments.fixed_rule import prove_small_holder_packet_flight as flight
from experiments.fixed_rule.audit_small_holder_position_events import sha


WRAPPER = r'''
extern "C" int audit_transport(uint64_t *count){
 *count=0;
 const uint64_t targets[]={1,5,Q-5,Q-1,8,8+4*8*INFO_WORDS,8+4*14*INFO_WORDS};
 for(uint64_t n: {UINT64_C(1),UINT64_C(15)})
 for(uint64_t a=0;a<Q;++a)for(uint64_t target:targets)
 for(uint64_t track=0;track<2;++track)for(uint64_t hops=0;hops<8;++hops){
  uint64_t pos=(n-1)*Q+a,birth=UINT64_C(1234567890);
  Packet packet{birth,pos,track,target,UINT64_C(0xdeadbeef),hops};
  // Reflect left travel into the rightward coordinates of the BDD proof.
  uint64_t source=track?a:Q-1-a,dest=track?target:Q-1-target;
  uint64_t hit_coordinate=hops*Q+dest;
  uint64_t hit=hit_coordinate>source?hit_coordinate-source:UINT64_MAX;
  uint64_t drop=(hops+1)*Q-source;
  if(hit_distance(packet)!=hit||drop_distance(packet)!=drop)return -1;
  if(lifetime(packet)!=std::min(hit,drop))return -2;
  uint64_t end=std::min(hit,drop),size=n*Q;
  const uint64_t times[]={0,1,end-1,end,end+1,7*Q+17};
  for(uint64_t elapsed:times){
   uint64_t pos_expected=track?(pos+elapsed)%size:(pos+((elapsed/size)+1)*size-elapsed)%size;
   if(moved(packet,elapsed,size)!=pos_expected)return -3;
   Packet shifted=packet;shifted.pos=pos_expected;shifted.birth+=elapsed;
   if(line(shifted,size)!=line(packet,size))return -4;
   ++*count;
  }
 }
 return 0;
}
'''


def compiled_check(text, label):
    digest = hashlib.sha256(text.encode()).hexdigest()[:20]
    directory = Path('figs/fixed_rule/build') / ('cpu_transport_audit_'+digest)
    directory.mkdir(parents=True, exist_ok=True)
    source, target = directory/'audit.cpp', directory/'audit.so'
    if source.exists():
        assert source.read_text() == text
    else:
        source.write_text(text)
    if not target.exists():
        with (directory/'build.log').open('w') as log:
            subprocess.run(['c++', '-O2', '-std=c++17', '-shared', '-fPIC', str(source), '-o', str(target)],
                           stdout=log, stderr=subprocess.STDOUT, check=True)
    lib = ctypes.CDLL(str(target.resolve()))
    lib.audit_transport.argtypes = [ctypes.POINTER(ctypes.c_uint64)]
    lib.audit_transport.restype = ctypes.c_int
    count = ctypes.c_uint64()
    result = lib.audit_transport(ctypes.byref(count))
    return dict(label=label, result=result, checked_time_cases=count.value,
                generated_source=str(source), generated_source_sha256=sha(source))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', required=True)
    args = parser.parse_args()
    out = Path(args.output)
    if out.exists():
        raise FileExistsError('preserve evidence')
    started = time.perf_counter()
    assert f.Q == flight.f.Q == 32768
    assert inspect.getsource(c.receive) == inspect.getsource(old_c.receive)
    induction = [flight.prove_case(hops) for hops in range(8)]
    source = backend.source()+WRAPPER
    actual = compiled_check(source, 'actual CPU helpers')
    assert actual['result'] == 0, actual
    mutations = []
    for old, new, label in (
        ('return distance>0?', 'return distance>=0?', 'zero-distance premature hit'),
        ('p.pos%Q+1:Q-p.pos%Q', 'p.pos%Q:Q-p.pos%Q', 'left-edge early drop'),
    ):
        assert source.count(old) == 1
        result = compiled_check(source.replace(old, new), label)
        assert result['result'] != 0, ('mutation escaped', label)
        mutations.append(result)
    files = [Path(__file__), Path(backend.__file__), Path(backend.__file__).with_suffix('.cpp'),
             Path(c.__file__), Path(old_c.__file__), Path(flight.__file__), Path(flight.BDD.__module__.replace('.', '/')+'.py')]
    # BoundedBDD is declared in the flight module; also bind its underlying BDD.
    files.append(Path('gacsca/fixed_rule/word_bdd.py'))
    result = dict(passed=True, induction=induction, actual_helpers=actual, rejected_mutations=mutations,
                  identical_receive_source=True, source_sha256={str(path):sha(path) for path in files},
                  seconds=time.perf_counter()-started, host_max_rss_kib=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                  scope='Exact BDD rightward flight induction for all 15-bit source/target coordinates and 19-bit elapsed values, hops 0..7; left by reflection. Actual C++ helper check covers every source coordinate, both tracks, all hops, seven targets, rings of 1/15 colonies, and six endpoint/time probes.',
                  separate_obligations=['local raw-mail factorization and legal-clock transfer',
                                        'guarded MEM targets and controller noninterference',
                                        'birth collision exclusion and actual delivery ordering',
                                        'whole event-backend equivalence remains conditional on its domain'])
    out.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps(result, indent=2), flush=True)


if __name__ == '__main__':
    main()
