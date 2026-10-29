#!/usr/bin/env python3
"""J208 universal local zero-GF identity; conditional gather-prefix contract."""
from pathlib import Path
import hashlib,json,sys,time
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from gacsca.netlist import Net,Compiled
import proposed_sparse_signal_reservation1024 as proposed
from check_signal_reservation1024_second_signal import blocked


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def main():
    start=time.monotonic();p=proposed.parameters();c=proposed.load_artifact();parent=ROOT/'figs/robustness'
    stencil=(*range(-37,-22),*range(-17,6));assert len(stencil)==38
    zeroed=set()
    class ZeroGF(Net):
        def input(self,key):
            if isinstance(key,tuple) and len(key)==4 and key[0]=='x' and key[2]=='addr' and key[1] in stencil:
                zeroed.add(key);return 0
            return super().input(key)
    n,_=proposed.full_net(p,ZeroGF)
    assert zeroed=={('x',d,'addr',b) for d in stencil for b in range(10)}
    equalities=0
    for field,value in (('addr',0),('f1',1),('wf1',0)):
        for b in range(dict(c.schema)[field]):
            assert n.outputs['y',field,b]==((value>>b)&1);equalities+=1
    assert equalities==12
    assert all(n.outputs['y','age',b] not in (0,1) for b in range(p.m))
    assert n.outputs['y','f2',0] not in (0,1)
    routes=0
    for distance in range(37):
        for d in stencil:
            for phase in range(59,69):
                for slot in proposed.SLOTS:
                    assert blocked(((-512,0),),distance,d,phase+slot,p.Q)==(distance+d<0)
                    routes+=1
    assert routes==70300
    own=json.loads((parent/'SP30_encoded_certificate.json').read_text())
    prior=json.loads((parent/'SP30_seventh_signal_certificate.json').read_text())
    assert own['proposed_candidate_sha256']==prior['proposed_candidate_sha256']==c.digest()
    assert own['complete_encoded_noiseless_and_all_period_E0_simulation_proved']
    records={r['colony']:r for r in prior['sixth_native_source_cofactor_records']}
    for j in range(104,121):assert records[j]['constant_output_words']['addr']==0
    recovered={(r['colony'],r['normal_phase']) for r in prior['recovered_GF_F1_primary_records']}
    assert {(j,phase) for j in range(98,104) for phase in range(59,69)}<=recovered
    for j in range(104,116):
        assert records[j]['constant_output_words']==dict(addr=0,age=None,f1=1,wf1=0)
    seventh_flags={r['colony']:r['Flag1_constant'] for r in prior['seventh_Flag1_cofactors']}
    assert all(seventh_flags[j]==1 for j in range(98,116))
    sources=('Report/proofs/proposed_distant_native448.py','Report/proofs/check_signal_reservation1024_second_signal.py',
        'Report/proofs/SP30_OWN_RULE.md','Report/proofs/SP30_SEVENTH_SIGNAL.md','gacsca/netlist.py','gacsca/rule_g.py')
    receipt=dict(proposal='SP30',scope='J208 complete local Age-independent zero-GF identity and conditional actual gather-prefix contract; all-period premise supply/general eroder/higher/iid open',
        Q=p.Q,U=p.U,T_wf=p.T_wf,checker_sha256=digest(__file__),written_proof_sha256=digest(ROOT/'Report/proofs/SP30_ZERO_GF_PREFIX.md'),
        proposal_source_sha256=digest(proposed.__file__),proposed_candidate_sha256=c.digest(),proposed_netlist_sha256=c.comp.digest,
        source_dependencies_sha256={name:digest(ROOT/name) for name in sources},
        receipt_dependencies_sha256={name:digest(parent/name) for name in ('SP30_encoded_certificate.json','SP30_seventh_signal_certificate.json')},
        preliminary_probe_log_sha256=digest(parent/'SP30_zero_GF_local_cofactor_unregistered.log'),
        raw_GF_zero_stencil=list(stencil),fixed_GF_input_bits=380,constant_output_bit_equalities=12,
        cofactored_complete_netlist_sha256=Compiled(n).digest,
        native_output_words=dict(addr=0,f1=1,wf1=0),Age_and_Flag2_output_not_fixed=True,
        all_unmentioned_raw_fields_private_flags_Age_and_instruction_inputs_free=True,
        unused_or_legal_Age_words_all_covered=True,shared_GF_selector_assumption_used=False,
        universal_complete_local_identity_proved=True,
        exact_stride8_route_checks=70300,all_integer_Q_translations_and_receiver_distances_covered=True,
        conditional_zero_GF_prefix_gather_and_own_programme_contract_proved=True,
        actual_source_holders_strip_correct_gather_programme_and_store_premises_explicit=True,
        actual_seventh_source_prefix_consistent_with_prior_certificate=True,
        all_period_source_or_strip_or_gather_or_control_premises_supplied=False,
        left_signal_or_complete_eighth_or_permanent_glider_or_general_eroder_or_full_data_proved=False,
        higher_error_map_or_positive_iid_epsilon_or_globally_minimal_change_proved=False,
        numerical_payload_samples_used=False,additional_rule_programme_layout_or_constant_change=False,
        active_G17_or_frozen_SP30_modified=False,global_reliability_established=False,seconds=time.monotonic()-start)
    (parent/'SP30_zero_GF_prefix_certificate.json').write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps({key:receipt[key] for key in ('universal_complete_local_identity_proved',
        'fixed_GF_input_bits','constant_output_bit_equalities','exact_stride8_route_checks',
        'conditional_zero_GF_prefix_gather_and_own_programme_contract_proved',
        'all_period_source_or_strip_or_gather_or_control_premises_supplied','seconds','global_reliability_established')}),flush=True)


if __name__=='__main__':main()
