#!/usr/bin/env python3
"""Conditional SP30 right-native outputs; physical bridge is not supplied."""
from pathlib import Path
import hashlib,json,sys,time
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from gacsca.netlist import Net,Compiled
import proposed_sparse_signal_reservation1024 as proposed
from check_signal_reservation1024_second_signal import blocked


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    started=time.monotonic();p=proposed.parameters();c=proposed.load_artifact()
    phases={(r['field'],r['bit']):r['address'] for r in proposed.dependency_table(p)}
    strips=((121*p.Q,122*p.Q-512),(136*p.Q-512,136*p.Q));records=[]
    for j in range(136,184):
        class Captured(Net):
            def input(self,key):
                if isinstance(key,tuple) and len(key)==4 and key[0]=='x':
                    _,d,field,bit=key;col=j+d
                    if field in ('addr','age','f1','wf1'):
                        if blocked(strips,j,d,phases[field,bit],p.Q):return 0
                        assert col>=136
                        if field=='addr':return (0 if col<=143 else col%p.Q)>>bit&1
                        if field=='f1':return int(col in (144,145,146))
                        if field=='age':return super().input(('upper_Age',col,bit)) if col<=143 else p.age_code(1)>>bit&1
                        if field=='wf1':return super().input(('upper_WF1',col,bit)) if col<=143 else 0
                return super().input(key)
        n,_=proposed.full_net(p,Captured);outputs={}
        for field in ('addr','age','f1','wf1'):
            bits=[n.outputs['y',field,b] for b in range(dict(c.schema)[field])]
            outputs[field]=sum(v<<b for b,v in enumerate(bits)) if all(v in (0,1) for v in bits) else None
        records.append(dict(colony=j,constant_output_words=outputs,netlist_sha256=Compiled(n).digest))
    r=dict(proposal='SP30',scope='Conditional second-right-native algebraic probe only; no actual physical store/source bridge or third signal',
        checker_sha256=digest(__file__),proposal_source_sha256=digest(proposed.__file__),
        proposed_candidate_sha256=c.digest(),proposed_netlist_sha256=c.comp.digest,
        Q=p.Q,U=p.U,records=records,all_H2_and_other_unmentioned_fields_and_I_free=True,
        physical_actual_output_words_or_third_signal_proved=False,
        numerical_whole_CA_trajectory_used=False,active_G17_modified=False,global_reliability_established=False,
        source_helper_sha256=digest(ROOT/'Report/proofs/check_signal_reservation1024_second_signal.py'),
        second_signal_receipt_sha256=digest(ROOT/'figs/robustness/SP30_second_signal_certificate.json'),
        seconds=time.monotonic()-started)
    (ROOT/'figs/robustness/SP30_second_right_native_probe.json').write_text(json.dumps(r,indent=2)+'\n')
    print(json.dumps(dict(records=[x for x in records if x['colony']<=148],seconds=r['seconds'])))


if __name__=='__main__':main()
