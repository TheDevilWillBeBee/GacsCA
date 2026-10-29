"""Read-only replay of the pinned standalone GAW2D/R checkpoint."""
from pathlib import Path
import sys,json,hashlib,time,importlib.util
ROOT=Path(__file__).resolve().parents[4]
D=ROOT/'figs/gray_counterexamples/unregistered_gaw2'
S=Path(__file__).resolve().parent

def sha(p):return hashlib.sha256(Path(p).read_bytes()).hexdigest()

def stable(data):
    if isinstance(data,dict):return {k:stable(v) for k,v in data.items() if k!='elapsed_seconds'}
    if isinstance(data,(list,tuple)):return [stable(v) for v in data]
    return data


def main():
    start=time.monotonic();asset_path=D/'GAW2_standalone_assets_v2.json'
    manifest=json.loads(asset_path.read_text());assets=manifest['assets_sha256']
    for path,expected in assets.items():assert sha(ROOT/path)==expected,('source/receipt mismatch',path)
    certificate=json.loads((D/'GAW2_three_gather_period_certificate.json').read_text())
    assert certificate['proof_sha256']==sha(S/'GAW2_THREE_GATHER_PERIOD.md')
    assert certificate['all_upper_raw_patterns_quantified']==49037
    assert certificate['GAW2R_noiseless_physical_period_proved']
    assert not any(certificate[n] for n in ('own_Q_bit_fit_proved','Gray_refutation_proved','iid_reliability_proved','pure_E0_period_proved','shorter_U_proved','active_rule_modified'))
    import gaw2_compositional_cost as cd
    import gaw2r_compositional_cost as cr
    for tag,cost,name in [('GAW2D',cd,'GAW2_compositional_cost.json'),('GAW2R',cr,'GAW2R_compositional_cost.json')]:
        retained=json.loads((D/name).read_text());actual=[cost.run(clock) for clock in retained['phase_partition'][:-1]]
        assert actual==retained['records']
        assert max(r['tick_bound'] for r in actual)==141557
        if tag=='GAW2R':assert retained['available_ticks']==147455>141557
        # Load the exact same new contract source with the explicit variant.
        saved=sys.argv[:];sys.argv=[str(S/'check_gaw2_contracts.py')]+(['R'] if tag=='GAW2R' else [])
        try:
            spec=importlib.util.spec_from_file_location('contracts_'+tag,S/'check_gaw2_contracts.py')
            checker=importlib.util.module_from_spec(spec);spec.loader.exec_module(checker)
            result=checker.main(write=False)
        finally:sys.argv=saved
        assert stable(result)==stable(json.loads((D/(tag+'_contracts.json')).read_text()))
    import check_gaw2_period as period
    result=period.main(write=False)
    assert stable(result)==stable(json.loads((D/'GAW2_period_contracts.json').read_text()))
    assert result['storage_R']['total_immutable_bits']==270349
    assert result['cached_deadline_failures'][1]['ticks']==137553
    # A replay must leave every registered source/receipt byte unchanged.
    for path,expected in assets.items():assert sha(ROOT/path)==expected,('replay mutation',path)
    print(json.dumps(dict(passed=True,assets_verified=len(assets),new_cost_partitions=2,new_cost_classes=144,
        symbolic_data_instances=1440,symbolic_courier_instances=5760,native_cofactors=49152,
        full_Q_fit=False,Gray_iid_or_shorter_U=False,registered_main_modified=False,
        checkpoint_sha256=sha(asset_path),elapsed_seconds=time.monotonic()-start)))

if __name__=='__main__':main()
