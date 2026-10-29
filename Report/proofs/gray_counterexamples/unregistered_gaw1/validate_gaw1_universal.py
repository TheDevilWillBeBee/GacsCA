#!/usr/bin/env python3
"""Read-only replay of universal prepared contracts/cost and exact storage trials.

No new cell execution samples; no old/main checkpoint mutation.
"""
from pathlib import Path
import json,hashlib,time
import gaw1_compositional_cost as cost
import check_gaw1_contracts as contracts
import gaw1_lossless_code as raw
import gaw1_phrase_code as phrase
import gaw1_relocation_code as relocation
ROOT=Path(__file__).resolve().parents[4]
D=ROOT/'figs/gray_counterexamples/unregistered_gaw1'


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    start=time.monotonic();manifest=json.loads((D/'GAW1_standalone_assets.json').read_text())
    for rel,sha in manifest['assets_sha256'].items():assert digest(ROOT/rel)==sha,rel
    cert=json.loads((D/'GAW1_universal_prepared_certificate.json').read_text())
    data=json.loads((D/'GAW1_compositional_cost.json').read_text())
    fresh=contracts.main(write=False);old=json.loads((D/'GAW1_contracts.json').read_text())
    assert json.loads(json.dumps(fresh['checks']))==old['checks'] and fresh['sources_sha256']==old['sources_sha256']
    for record in data['records']:assert cost.run(record['clock'])==record
    assert len(data['records'])==62 and data['maximum_ticks']==58973<=65535
    assert max(r['tick_bound'] for r in data['records'])==58973
    words=[cost.k.beta_word(cost.ROM,i) for i in range(cost.ROM.token_count)]
    formats={}
    for tag,module,expected in (('lossless',raw,12780),('phrase',phrase,18078),('relocation',relocation,10871)):
        saved=json.loads((D/('GAW1_'+tag+'_code.json')).read_text())
        dictionary=[int(v,16) for v in saved['dictionary']]
        assert len(dictionary)==512 and len(saved['bits'])==expected>8192
        assert module.decode(saved['bits'],dictionary)==words
        bits,newdictionary,steps=module.compress(words)
        assert bits==saved['bits'] and newdictionary==dictionary
        formats[tag]=expected
    assert cert['universal_prepared_upper_raw_semantics_proved'] is True
    assert cert['universal_prepared_deadline_proved'] is True
    assert cert['alphabet_all_bit_patterns_quantified']==22537
    assert cert['lower_execution_preparations_remain_assumptions'] is True
    assert cert['whole_period_or_noise_or_Gray_or_shorter_U_proved'] is False
    assert cert['own_Q_bit_fit_proved'] is False and cert['active_rule_modified'] is False
    assert cert['proof_sha256']==digest(ROOT/'Report/proofs/gray_counterexamples/unregistered_gaw1/GAW1_UNIVERSAL_PREPARED_EVALUATOR.md')
    print(json.dumps(dict(status='passed',hashed_assets=len(manifest['assets_sha256']),upper_alphabet_bits=22537,
        phase_classes=62,maximum_updates=58973,late_available=65535,late_slack=6562,
        exact_complete_emission_words=len(words),dictionary512_format_bits=formats,
        Q_fit_or_full_period_or_Gray_or_iid=False,no_new_samples=True,elapsed_seconds=time.monotonic()-start)))

if __name__=='__main__':main()
