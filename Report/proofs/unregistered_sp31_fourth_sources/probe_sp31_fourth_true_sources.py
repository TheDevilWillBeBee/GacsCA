#!/usr/bin/env python3
"""Unregistered fourth-source study: actual-table cofactors, not a repair proof.

Unknown outputs are preserved as unknowns. No future tape is supplied and no
automaton source is changed. A written actual-bank/store/capture lift remains
an obligation even if the finite cofactor study succeeds.
"""
from itertools import product
from pathlib import Path
import hashlib,json,sys,time

ROOT=Path(__file__).resolve().parents[3]
PROOFS=ROOT/'Report/proofs'
sys.path[:0]=[str(ROOT),str(PROOFS),str(PROOFS/'unregistered_terminal'),
             str(PROOFS/'unregistered_sp31_third_sources')]
from gacsca.netlist import const_word
from probe_sp30_symbolic_left_absorption import AbsorptionNet
import proposed_native_command1024 as proposed
from probe_sp31_third_true_sources import third_left_value,NATIVE
from check_native_command1024_first_pulse import blocked

OUT=ROOT/'figs/robustness/unregistered_sp31_fourth_sources'
def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def native_word(values):
    if isinstance(values,int):return values if values in (0,1) else None
    return sum(v<<b for b,v in enumerate(values)) if all(v in (0,1) for v in values) else None

def main():
    start=time.monotonic();p=proposed.parameters();candidate=proposed.load_artifact()
    build,_=proposed.proposed_build()
    sourcecert=ROOT/'figs/robustness/SP31_third_source_enclosure_certificate.json'
    pulsecert=ROOT/'figs/robustness/SP31_third_pulse_certificate.json'
    sources=json.loads(sourcecert.read_text());pulse=json.loads(pulsecert.read_text())
    assert sources['actual_full_third_source_enclosure_proved']
    assert pulse['actual_third_native_pulse_proved']
    assert pulse['candidate_sha256']==sources['candidate_sha256']==candidate.digest()
    phases={(r['field'],r['bit']):r['address'] for r in proposed.dependency_table(p)}
    strips=((141*p.Q,142*p.Q-512),(149*p.Q-512,149*p.Q))
    records=[]
    for a,j,q in product(range(2),range(100,141),(0,134,1023)):
        n=AbsorptionNet()
        cells={d:{f:[0 if blocked(strips,j,d,phases[f,b],p.Q) else
                            third_left_value(n,p,j+d,f,b,a,q)
                         for b in range(p.k if f=='addr' else p.m)]
                    if f in ('addr','age') else
                    (0 if blocked(strips,j,d,phases[f,0],p.Q) else
                     third_left_value(n,p,j+d,f,0,a,q))
                  for f in NATIVE} for d in range(-5,9)}
        got=build(n,cells,p.k,p.m,Q=p.Q,nb=p.nb,radix=p.R,
                  pos_bits=p.PB,service_force=0)
        rec=dict(a=a,j=j,q=q)
        for field in ('addr','age_now','age','f1','f2'):
            rec[field]=native_word(got[field])
        records.append(rec)
    # Nonconstant symbolic words are data, not failed histories.
    record=dict(scope='Selected literal maintenance cofactors of the already proved actual third true-capture table; fourth-bank physical lift not supplied',
        Q=p.Q,U=p.U,candidate_sha256=candidate.digest(),
        source_certificate_sha256=sha(sourcecert),pulse_certificate_sha256=sha(pulsecert),
        checker_sha256=sha(__file__),input_table_source_sha256=sha(PROOFS/'unregistered_sp31_third_sources/probe_sp31_third_true_sources.py'),
        selected_native_cofactors=records,selected_cases=len(records),
        actual_third_protected_true_output_banks_proved=False,
        actual_fourth_source_enclosure_or_pulse_proved=False,
        global_reliability_established=False,active_G17_modified=False,
        additional_rule_change=False,seconds=time.monotonic()-start)
    OUT.mkdir(exist_ok=True)
    (OUT/'selected_third_true_native_cofactors.json').write_text(json.dumps(record,indent=2)+'\n')
    print(json.dumps(dict(passed=True,selected_cases=len(records),actual_fourth_source_enclosure_or_pulse_proved=False,seconds=record['seconds'])),flush=True)

if __name__=='__main__':main()
