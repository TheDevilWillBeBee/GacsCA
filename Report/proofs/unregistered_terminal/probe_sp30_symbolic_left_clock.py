#!/usr/bin/env python3
"""Prepared left-capture cofactors with a shared arbitrary raw clock.

No physical history, all-period supply, permanent island or noisy result.
"""
from pathlib import Path
import hashlib,json,sys,time
ROOT=Path(__file__).resolve().parents[3];sys.path.insert(0,str(ROOT));sys.path.insert(0,str(ROOT/'Report/proofs'))
from gacsca.netlist import Net,Compiled
import proposed_sparse_signal_reservation1024 as proposed
from check_signal_reservation1024_second_signal import blocked


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    start=time.monotonic();p=proposed.parameters();c=proposed.load_artifact()
    phases={(r['field'],r['bit']):r['address'] for r in proposed.dependency_table(p)}
    records=[]
    for K in (0,1,2,3,4,5,6,92,1022,1023,1024):
        strips=(((K-1)*p.Q,K*p.Q-512),)
        for back in range(2,7):
            j=K-back
            class Captured(Net):
                def input(self,key):
                    if isinstance(key,tuple) and len(key)==4 and key[0]=='x':
                        _,d,f,b=key;col=j+d
                        if f in ('addr','age','f1','wf1'):
                            if blocked(strips,j,d,phases[f,b],p.Q):return 0
                            assert col<=K-2
                            if f=='addr':return ((col%p.Q)>>b)&1
                            if f=='f1':return 0
                            if col==K-2:return super().input(('edge_'+f,b))
                            return super().input(('common_age',b)) if f=='age' else 0
                    return super().input(key)
            n,_=proposed.full_net(p,Captured);bits={};words={}
            for f in ('addr','age','f1','wf1'):
                nodes=[n.outputs['y',f,b] for b in range(dict(c.schema)[f])]
                bits[f]=[v if v in (0,1) else None for v in nodes]
                words[f]=sum(v<<b for b,v in enumerate(nodes)) if all(v in (0,1) for v in nodes) else None
            records.append(dict(K=K,receiver=j,offset_from_K=-back,constant_output_bits=bits,
                constant_output_words=words,netlist_sha256=Compiled(n).digest))
            print(json.dumps(dict(K=K,receiver=j,words=words)),flush=True)
    out=ROOT/'figs/robustness/unregistered_symbolic_left_clock';out.mkdir(exist_ok=True)
    receipt=dict(scope='Prepared left capture cofactors, arbitrary shared raw Age and free edge Age/WF1; physical all-period premises unproved',
        Q=p.Q,U=p.U,T_wf=p.T_wf,checker_sha256=digest(__file__),proposal_source_sha256=digest(proposed.__file__),
        proposed_candidate_sha256=c.digest(),proposed_netlist_sha256=c.comp.digest,
        route_primitive_sha256=digest(ROOT/'Report/proofs/check_signal_reservation1024_second_signal.py'),
        records=records,unmentioned_H2_Info_private_fields_and_instructions_free=True,
        actual_all_period_source_or_signal_supply_or_permanent_defect_or_eroder_proved=False,
        higher_error_map_or_positive_iid_or_new_reliability_proved=False,
        additional_rule_programme_layout_or_constant_change=False,active_G17_or_frozen_SP30_modified=False,
        global_reliability_established=False,seconds=time.monotonic()-start)
    (out/'receipt.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(dict(seconds=receipt['seconds'],scope=receipt['scope'],global_reliability_established=False)),flush=True)


if __name__=='__main__':main()
