#!/usr/bin/env python3
"""Read-only provenance, complete emission and124 prepared execution replay.

Does not recertify the interrupted cost analysis as a successful theorem.
Does not modify main checkpoint or active rule.
"""
from pathlib import Path
import hashlib,json,time
import gray_wider_word_gaw0 as k
import build_gray_wider_word_gaw0 as b
from check_gray_wider_word_gaw0 import instance
ROOT=Path(__file__).resolve().parents[4]
D=ROOT/'figs/gray_counterexamples/unregistered_gaw0'

def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def main():
    start=time.monotonic();manifest=json.loads((D/'GAW0_standalone_assets.json').read_text())
    for path,expected in manifest['assets_sha256'].items():assert digest(ROOT/path)==expected,path
    cert=json.loads((D/'GAW0_complete_emission_certificate.json').read_text())
    for name,sha in cert['sources_sha256'].items():assert digest(Path(__file__).parent/name)==sha,name
    for name,sha in cert['assets_sha256'].items():assert digest(D/name)==sha,name
    raw,list0,lab0,errors=b.programme().assemble()
    assert raw.token_count==1979 and raw.token_count*9==17811 and raw.used_dictionary==605
    assert errors==[{'dictionary_overflow':605}]
    rom,listing,labels=instance();expected=json.loads((D/'GAW0D_rom.json').read_text())
    assert list(rom.bits)==expected['bits'] and [hex(v) for v in rom.dictionary]==expected['dictionary']
    assert rom.token_bits==10 and len(rom.bits)==32768 and len(rom.dictionary)==1024
    assert rom.token_count*rom.token_bits==19790
    assert dict(instructions=listing,labels=labels)==json.loads((D/'GAW0D_listing.json').read_text())
    for row in listing:
        operands=tuple(v&((1<<w)-1) for v,w in zip(row['operands'],k.ARGS[row['opcode']]))
        assert k.decode(k.beta_word(rom,row['address']))==(row['opcode'],operands)
    records=json.loads((D/'GAW0D_prepared_replays.json').read_text());assert len(records)==124
    for record in records:
        cells={j:k.cell_from_words([int(v,16) for v in record['inputs'][j+8]]) for j in range(-8,9)}
        computed=k.cell_words(k.local_transition(cells,rom))
        assert [hex(v) for v in computed]==record['expected'],record['name']
        out,ticks,last,trace=k.execute(rom,k.input_tape(cells),limit=300000,record=True)
        actual=[out.get(k.PRIMARY_START+i,0) for i in range(k.FRAME_WORDS)]
        assert actual==computed and ticks==record['ticks'] and last.mode==k.HALT,record['name']
        assert min(t[0] for t in trace)==record['min_head_address']
        assert max(t[0] for t in trace)==record['max_head_address']
    assert max(r['ticks'] for r in records)==53747<65535
    assert cert['all_raw_own_programme_equivalence_proved'] is False
    assert cert['full_noiseless_period_or_Gray_faithfulness_or_iid_or_shorter_U'] is False
    print(json.dumps(dict(status='passed',hashed_assets=len(manifest['assets_sha256']),prepared_replays=len(records),
        tokens=1979,Q_fit=False,total_DIAGNOSTIC_immutable_capacity_bits=135168,measured_max_ticks=53747,
        universal_deadline_or_Gray_or_iid=False,elapsed_seconds=time.monotonic()-start)))

if __name__=='__main__':main()
