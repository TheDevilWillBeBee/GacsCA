"""Exact local counterexamples to a proposed malformed-native quotient.

Diagnostic only. Frozen GAW2R, ROM and legal-period proof are unchanged.
Prepared input tapes are not claimed to be reachable physical histories.
Default execution is read-only; --issue writes only this new certificate.
"""
from pathlib import Path
from dataclasses import replace
import hashlib,json,sys,time

S=Path(__file__).resolve().parent
ROOT=S.parents[3]
D=ROOT/'figs/gray_counterexamples/unregistered_gaw_padding_quotient'
sys.path.insert(0,str(S.parent/'unregistered_gaw2'))
import gray_three_gather_gaw2r as k
import gaw2r_compositional_cost as own

def sha(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()

def project(cell):
    widths=(13,20,1,1,1,1)
    return replace(cell,**{name:getattr(cell,name)&((1<<w)-1)
        for name,w in zip(k.NATIVE_NAMES,widths)})

def run():
    inherited_path=ROOT/'figs/gray_counterexamples/unregistered_gaw16/GAW16_standalone_assets.json'
    inherited=json.loads(inherited_path.read_text())
    assert len(inherited['assets_sha256'])==443
    for name,value in inherited['assets_sha256'].items():
        assert sha(ROOT/name)==value,(name,'frozen inherited asset changed')
    rom_path=ROOT/'figs/gray_counterexamples/unregistered_gaw2/GAW2R_rom.json'
    emitted=json.loads(rom_path.read_text())
    assert list(own.ROM.bits)==emitted['bits']
    assert [hex(v) for v in own.ROM.dictionary]==emitted['dictionary']
    for name in ('token_count','used_dictionary','token_bits','early_pc'):
        assert getattr(own.ROM,name)==emitted[name]
    assert (k.Q,k.U,k.WORD,k.PRIMARY_START,k.FRAME_WORDS)==(8192,1048576,100,3848,496)
    cases=[]
    for kind in ('canonical','no_GF_quorum'):
        legal={j:k.Cell(addr=(200+j if kind=='canonical' else 200+17*j)%k.Q,
            age=123,f1=int(kind=='canonical'),info=(7,)*5) for j in range(-8,9)}
        raw=dict(legal);raw[0]=replace(raw[0],addr=8392)
        assert all(project(raw[j])==legal[j] for j in raw)
        assert all(0<=word<=k.MASK for c in raw.values() for word in k.cell_words(c))
        native_raw=k.native_at(raw);native_legal=k.native_at(legal)
        assert native_raw==native_legal==dict(addr=200,age=124,f1=1,f2=0,wf1=0,wf2=0)
        raw_result=k.local_transition(raw,own.ROM)
        legal_result=k.local_transition(legal,own.ROM)
        assert raw_result.info==(0,)*5 and legal_result.info==(7,)*5
        assert project(raw_result)!=legal_result
        output,ticks,head,_=k.execute(own.ROM,k.input_tape(raw),limit=200000)
        actual=[output.get(k.PRIMARY_START+i,0) for i in range(k.FRAME_WORDS)]
        expected=k.cell_words(raw_result)
        different=[i for i,(a,b) in enumerate(zip(actual,expected)) if a!=b]
        assert head.mode==k.HALT
        if kind=='canonical':
            assert ticks==2646 and not different and actual==expected
        else:
            assert ticks==63872 and different==[0,206,207,208,209,210,217,220]
            assert actual[:6]==[8392,124,1,0,0,0]
            assert actual[206:211]==[7]*5
            assert not any(actual[i] for i in range(6,206))
            for side in (-1,1):
                adjusted=[(raw[side*i].addr-side*i)%k.Q for i in range(1,6)]
                assert len(set(adjusted))==5
        cases.append(dict(name=kind,
            prepared_input_only=True,
            raw_neighbourhood_words={str(j):[hex(v) for v in k.cell_words(raw[j])] for j in raw},
            raw_centre_GF=8392,projected_centre_GF=200,
            native_raw=native_raw,native_projected=native_legal,
            raw_local_R_output=[hex(v) for v in expected],
            projected_input_local_R_output=[hex(v) for v in k.cell_words(legal_result)],
            projected_raw_successor_equals_legal_successor=False,
            emitted_raw_output=[hex(v) for v in actual],
            actual_emitted_ticks=ticks,actual_emitted_HALT=True,
            emitted_differs_from_raw_local_R_indices=different,
            no_physical_reachability_or_fault_history_or_reliability_claim=True))
    source_files=(
        'Report/proofs/gray_counterexamples/unregistered_gaw2/gray_three_gather_gaw2r.py',
        'Report/proofs/gray_counterexamples/unregistered_gaw2/build_gray_three_gather_gaw2r.py',
        'Report/proofs/gray_counterexamples/unregistered_gaw2/gaw2r_compositional_cost.py',
        'Report/proofs/gray_counterexamples/unregistered_gaw0/gray_wider_word_gaw0.py',
        'Report/proofs/gray_counterexamples/gray_moving_word_v2.py',
        'Report/proofs/gray_counterexamples/gray_moving_word_kernel.py',
        'Report/proofs/gray_counterexamples/unregistered_gaw13/GAW13_PADDING_PROPOSAL.md',
    )
    return dict(passed=True,
        proof_sha256=sha(S/'PADDING_QUOTIENT_OBSTRUCTION.md'),
        checker_sha256=sha(Path(__file__)),
        inherited_manifest_sha256=sha(inherited_path),inherited_assets_verified=443,
        source_dependencies_sha256={name:sha(ROOT/name) for name in source_files},
        own_ROM_sha256=sha(rom_path),own_listing_sha256=sha(ROOT/'figs/gray_counterexamples/unregistered_gaw2/GAW2R_listing.json'),
        unchanged_rule_Q=8192,unchanged_rule_U=1048576,unchanged_error_separation=104,
        native_padding_projection_quotient_false=True,
        universal_malformed_native_emitter_refinement_false=True,
        legal_native_record_evaluator_or_period_theorem_refuted=False,
        arbitrary_malformed_or_higher_repair_or_iid_theorem_proved=False,
        physical_counterexample_or_Gray_counterexample=False,
        padding_commit_mask_implemented_or_compiled=False,
        active_G17_or_frozen_rule_modified=False,
        cases=cases)

if __name__=='__main__':
    started=time.monotonic();actual=run();path=D/'padding_quotient_certificate.json'
    if '--issue' in sys.argv:
        D.mkdir(parents=True,exist_ok=True)
        assert not path.exists(),'existing certificate must not be overwritten'
        path.write_text(json.dumps(actual,indent=2)+'\n')
    else:
        assert actual==json.loads(path.read_text()),'frozen exact replay differs'
    print(json.dumps(dict(passed=True,readonly='--issue' not in sys.argv,
        prepared_local_cases=2,emitted_ticks=[r['actual_emitted_ticks'] for r in actual['cases']],
        native_padding_projection_quotient_false=True,
        universal_malformed_native_emitter_refinement_false=True,
        legal_record_theorem_or_Gray_or_iid_refutation=False,
        certificate_sha256=sha(path),elapsed_seconds=time.monotonic()-started)),flush=True)
