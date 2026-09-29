"""Describe retained raw computation damage without claiming macrostep failure."""
import json
from pathlib import Path
import numpy as np
from gacsca.fixed_rule import compact16_holder_rule as f
from experiments.fixed_rule.audit_compact16_holder_dense_noise import restore
from experiments.fixed_rule.run_compact16_holder_streamed_depth2 import sha


def heads(raw):
    return [dict(position=int(pos),phase=int(raw[pos,f.COL['s2_phase']]),pc=int(raw[pos,f.COL['s2_pc']]))
            for pos in np.flatnonzero(raw[:,f.COL['s2_head']])]


def main():
    source=Path('figs/fixed_rule/compact16_holder_dense_noise_v1.json')
    output=Path('figs/fixed_rule/compact16_holder_dense_noise_diagnosis_v1.json')
    if output.exists():raise FileExistsError(output)
    doc=json.loads(source.read_text());assert doc['passed'] and sha(doc['artifact'])==doc['artifact_sha256']
    rows=[]
    with np.load(doc['artifact'],allow_pickle=False) as z:
        healthy=z['healthy_512'];expected=heads(healthy)
        for case in range(8):
            raw=restore(z,case,512);fields=doc['trials'][case]['trace'][-1]['different_fields']
            assert all(name not in fields for name in ('address','age'))
            rows.append(dict(case=case,primary_Data_positions=np.flatnonzero(raw[:,f.COL['s2_data']]!=healthy[:,f.COL['s2_data']]).tolist(),
                             actual_primary_heads=heads(raw),different_Flag1_sites=fields.get('f1',0),different_Flag2_sites=fields.get('f2',0),
                             different_Signal_words=fields.get('signal',0)))
    result=dict(passed=True,reference=str(source),reference_sha256=sha(source),healthy_primary_heads=expected,cases=rows,
                source_sha256={str(Path(__file__)):sha(__file__)},
                scope='Exact primary controller/Data diagnostics at a nonterminal physical clock. No final decoded macrostep or permanent-failure claim.')
    with output.open('x') as out:out.write(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result))


if __name__=='__main__':main()
