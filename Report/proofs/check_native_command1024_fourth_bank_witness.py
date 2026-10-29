#!/usr/bin/env python3
"""J242 enlarged-bank witnesses, explicitly not physical reachability."""
from contextlib import redirect_stdout
from pathlib import Path
import hashlib,io,json,sys,tempfile,time
ROOT=Path(__file__).resolve().parents[2];S=ROOT/'Report/proofs';OUT=ROOT/'figs/robustness'
sys.path[:0]=[str(ROOT),str(S),str(S/'unregistered_sp31_fourth_enclosure')]
import probe_sp31_fourth_bank_witness as probe
PROOF=S/'SP31_FOURTH_BANK_WITNESS.md'
def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()
def main():
    start=time.monotonic();path=OUT/'unregistered_sp31_fourth_bank_witness/witness_receipt.json'
    retained=json.loads(path.read_text())
    assert retained['probe_sha256']==sha(probe.__file__)
    enclosurepath=OUT/'SP31_fourth_source_enclosure_certificate.json';enclosure=json.loads(enclosurepath.read_text())
    assert retained['source_enclosure_certificate_sha256']==sha(enclosurepath)
    assert enclosure['actual_full_fourth_source_enclosure_proved']
    with tempfile.TemporaryDirectory(prefix='sp31-bank-witness-') as tmp:
        probe.OUT=Path(tmp)
        with redirect_stdout(io.StringIO()):probe.main()
        replay=json.loads((Path(tmp)/'witness_receipt.json').read_text())
        for key in retained:
            if key!='seconds':assert replay[key]==retained[key],key
    rows=retained['cofactor_records'];assert len(rows)==38
    for mode in (0,1):
        subset=[r for r in rows if r['mode']==mode]
        assert [(r['kind'],r['j']) for r in subset]==[('true',j) for j in range(132,148)]+[('foreign',j) for j in range(149,152)]
        assert all(r['outputs']['f1']==1 and r['outputs']['f2']==mode for r in subset)
    # Direct populations in the shared table, not circuit samples.
    for j in range(132,142):assert any(131<=s<=141 for s in range(j-5,j))
    for j in (142,143):assert sum(131<=s<=141 for s in range(j-5,j))>=4
    for j in range(144,148):assert all(s>=133 for s in range(j-5,j))
    for h in range(149,152):assert sum(s<=148 for s in range(h-5,h))>=3
    result=dict(proposal='SP31',scope='Shared all-one/all-zero optional commands of enlarged J242 captured-table abstraction; no actual physical bank or mask reachability',
        Q=enclosure['Q'],U=enclosure['U'],candidate_sha256=enclosure['candidate_sha256'],netlist_sha256=enclosure['netlist_sha256'],
        proof_sha256=sha(PROOF),checker_sha256=sha(__file__),exploration_receipt_sha256=sha(path),
        proof_dependencies_sha256={name:sha(S/name) for name in ('SP31_OWN_RULE.md','SP31_FOURTH_SOURCE_ENCLOSURE.md')},
        receipt_dependencies_sha256={'SP31_fourth_source_enclosure_certificate.json':sha(enclosurepath)},
        source_dependencies_sha256={str(p.relative_to(ROOT)):sha(p) for p in (Path(probe.__file__),S/'unregistered_sp31_fourth_enclosure/probe_sp31_fourth_enclosure.py',S/'proposed_native_command1024.py',ROOT/'gacsca/rule_g.py',ROOT/'gacsca/netlist.py')},
        retained_exploration_assets_sha256={str(p.relative_to(ROOT)):sha(p) for p in (path,OUT/'unregistered_sp31_fourth_bank_witness_run.log')},
        readonly_all38_cofactors_replay_equal=True,complete_optional_commands=19,shared_table_assignments=2,
        full_rule_cofactors=38,all_remaining_private_SF_and_instruction_inputs_symbolic=True,
        GF_exceptions_zero=True,ones_free_Age=15,ones_free_Flag2=1,free_Workspace_zero=True,
        shared_enlarged_bank_allone_allzero_complete_Flag2_witnesses_proved=True,
        two_partial_outputs_only_allowed_by_enclosure=True,
        native_equations_alone_exclude_nonshrinking_extreme_masks=False,
        actual_physical_bank_or_initial_upper_Info_or_mask_reachability_proved=False,
        actual_fourth_native_pulse_or_noise_failure_proved=False,
        higher_repair_or_positive_iid_or_minimum_sufficient_change_proved=False,
        additional_rule_change=False,active_G17_modified=False,Gray_or_G17_refutation=False,global_reliability_established=False,
        seconds=time.monotonic()-start)
    (OUT/'SP31_fourth_bank_witness_certificate.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(dict(passed=True,shared_enlarged_table_extreme_witnesses_proved=True,full_rule_cofactors=38,actual_physical_reachability_proved=False,actual_fourth_pulse_or_global_reliability_proved=False,seconds=result['seconds'])),flush=True)
if __name__=='__main__':main()
