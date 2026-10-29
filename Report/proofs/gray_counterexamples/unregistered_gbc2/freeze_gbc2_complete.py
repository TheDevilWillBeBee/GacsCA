"""Register this isolated complete-encoder rejection, not main reports."""
from pathlib import Path
from hashlib import sha256
import json

ROOT=Path(__file__).resolve().parents[4]
S=ROOT/'Report/proofs/gray_counterexamples/unregistered_gbc2'
D=ROOT/'figs/gray_counterexamples/unregistered_gbc2'

def run():
    old=json.loads((ROOT/'figs/gray_counterexamples/unregistered_gbc0/GBC0_manifest.json').read_text())
    inherited={k:v for k,v in old['assets'].items() if k.startswith('gacsca/')
               or k=='Report/GRAY_COUNTEREXAMPLES.md'}
    for k,v in inherited.items():assert sha256((ROOT/k).read_bytes()).hexdigest()==v,k
    files=list(S.glob('*.py'))+list(S.glob('*.md'))
    files += [p for p in D.iterdir() if p.is_file() and p.suffix in ('.json','.log')
              and p.name not in ('GBC2_complete_manifest.json',)
              and not p.name.startswith(('GBC2_readonly_','GBC2_freeze_'))]
    # The unfrozen earlierGBC1 rejection/prefix is historical evidence,
    # with exact source hashes retained, not inherited proof authority.
    S1=ROOT/'Report/proofs/gray_counterexamples/unregistered_gbc1'
    D1=ROOT/'figs/gray_counterexamples/unregistered_gbc1'
    files+=list(S1.glob('*.py'))+list(D1.glob('*.json'))+list(D1.glob('*.log'))
    assets={str(p.relative_to(ROOT)):sha256(p.read_bytes()).hexdigest() for p in files}
    assets.update(inherited)
    out={'scope':{'frozen':True,'name':'GBC2 complete specified encoder rejection and selected separate-code diagnostics',
                 'Q':8192,'U':1048576,'lambda':24,'c':104,'radius':8,
                 'K':3087,'Head_bits':553,'Work_bits':407,
                 'initial_complete_bits':48705,'initial_instructions':3645,
                 'initial_out_of_Q_references':383,
                 'tail_merged_bits':42727,'tail_merged_instructions':3229,
                 'tail_merged_out_of_Q_references':350,
                 'complete_structural_branches':True,
                 'selected_complete_cases':90,'universal_complete_equivalence':False,
                 'separate_code_completion_updates':126614,
                 'separate_code_cutoff_updates':65534,
                 'separate_code_cutoff_wrong_raw_bits':12,
                 'cutoff_changed_field':'Head.pc only; Info agrees',
                 'physical_errors':[],'prepared_lower_execution':True,
                 'physical_period':False,'whole_own_beta':False,
                 'universal_deadline':False,'U128Q_impossible':False,
                 'intact_recursive_start':False,'gray_counterexample':False,
                 'iid_failure':False,'shorter_U':False,'active_rule_modified':False},
         'assets':assets,'provenance':'First complete rejection and all measured diagnostic inputs are retained. Wide-PC instruction-table dispatch and targetCODE are explicitly separate; not an issued own programme.',
         'validator_command':'python3 Report/proofs/gray_counterexamples/unregistered_gbc2/validate_gbc2_complete.py --output /tmp/GBC2_parent_readonly_validation.json'}
    (D/'GBC2_complete_manifest.json').write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({'assets':len(assets),'manifest_sha256':sha256((D/'GBC2_complete_manifest.json').read_bytes()).hexdigest(),'scope':out['scope']},indent=2))

if __name__=='__main__':run()
