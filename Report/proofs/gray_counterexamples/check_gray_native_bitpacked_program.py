#!/usr/bin/env python3
"""Exact native-prefix code/fit obstruction for the stated GPN0 evaluator."""
from pathlib import Path
import hashlib,json,sys
ROOT=Path(__file__).resolve().parents[3]
sys.path.insert(0,str(ROOT))
import numpy as np
from gacsca import maintenance
import literal_maintenance
import gray_native_bitpacked_program as implementation


def digest(path):return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def info(comp,k,m):
    w=(comp.n_nodes-1).bit_length();header=sum(width for name,width in implementation.HEADER)
    body=len(comp.gates)*(2+2*w);mapping=len(comp.outputs)*w
    return dict(Q=1<<k,U=1<<m,k=k,m=m,native_input_bits=len(comp.inputs),
        native_gates=len(comp.gates),native_output_bits=len(comp.outputs),native_nodes=comp.n_nodes,
        index_width=w,header_bits=header,gate_bits=body,output_map_bits=mapping,
        programme_bits=header+body+mapping,programme_fits_Q=header+body+mapping<=1<<k,
        serial_fetch_fits_fifth_active=header+body+mapping<=8*(1<<k),netlist_sha256=comp.digest)


def main():
    p=implementation;directory=ROOT/'figs/gray_counterexamples';comp=p.native_compiled()
    bits=p.encode(comp);parsed=p.decode(bits)
    assert parsed is not None
    assert parsed['gates']==list(comp.gates)
    assert parsed['outputs']==list(comp.outputs.values())
    baseline=info(comp,13,20)
    assert (len(comp.inputs),len(comp.gates),len(comp.outputs),comp.n_nodes)==(407,2919,35,3328)
    assert len(bits)==baseline['programme_bits']==76389
    assert baseline['gate_bits']+baseline['output_map_bits']==76314
    assert not baseline['programme_fits_Q'] and not baseline['serial_fetch_fits_fifth_active']
    beta=directory/'GPN0_literal_native_beta.bin'
    beta.write_bytes(np.packbits(np.array(bits,np.uint8),bitorder='little').tobytes())
    encoded=directory/'GPN0_literal_native_programme.json'
    encoded.write_text(json.dumps(dict(format='GPN0 little-endian bit-packed SSA, header75bits',
        native_only_not_self_beta=True,bit_length=len(bits),byte_length=len(beta.read_bytes()),
        header=parsed['header'],inputs=comp.inputs,gates=comp.gates,outputs=list(comp.outputs.items()),
        netlist_sha256=comp.digest),separators=(',',':'))+'\n')
    restored=np.unpackbits(np.frombuffer(beta.read_bytes(),np.uint8),bitorder='little')[:len(bits)].tolist()
    assert restored==bits
    # Code/source equivalence follows from the exact decoded structure.
    # Retained random scalar replay is separately measured evidence.
    rng=np.random.default_rng(76389)
    count=128
    inputs=rng.integers(0,2,(count,len(comp.inputs)),dtype=np.uint8)
    actual=[]
    for values in inputs.tolist():
        output,bad=p.evaluate(bits,values)
        assert not bad
        actual.append(output)
    actual=np.array(actual,np.uint8)
    native=comp.evaluate({name:inputs[:,i].astype(bool) for i,name in enumerate(comp.inputs)},bool)
    reference=np.stack([native[name] for name in comp.outputs],axis=1).astype(np.uint8)
    assert np.array_equal(actual,reference)
    asset=directory/'GPN0_native_programme_replays.npz'
    np.savez_compressed(asset,inputs=inputs,decoded_outputs=actual,compiled_outputs=reference)
    malformed=[]
    candidates=[([], 'empty'),(bits[:74],'truncated_header'),(bits[:-1],'truncated_output_map')]
    badmagic=bits.copy();badmagic[0]^=1;candidates.append((badmagic,'wrong_magic'))
    opcode=bits.copy();opcode[75:77]=[1,1];candidates.append((opcode,'reserved_opcode'))
    forward=bits.copy();forward[77:89]=p.number_bits(comp.n_nodes-1,12)
    candidates.append((forward,'forward_reference'))
    for value,name in candidates:
        result,bad=p.evaluate(value,[0]*len(comp.inputs))
        assert bad and result==[0]*35
        malformed.append(dict(name=name,invalid=True,output_zero=True))
    wrong_input,bad=p.evaluate(bits,[0]*(len(comp.inputs)-1))
    assert bad and wrong_input==[0]*35
    malformed.append(dict(name='wrong_input_width',invalid=True,output_zero=True))
    badbit,bad=p.evaluate(bits,[2]+[0]*(len(comp.inputs)-1))
    assert bad and badbit==[0]*35
    malformed.append(dict(name='nonbinary_input',invalid=True,output_zero=True))
    assert p.decode(bits+[0]*7)['consumed_bits']==len(bits)
    corrected_comp=p.native_compiled(builder=maintenance.build)
    corrected_bits=p.encode(corrected_comp)
    corrected=info(corrected_comp,13,20)
    assert len(corrected_bits)==corrected['programme_bits']
    assert not corrected['programme_fits_Q'] and not corrected['serial_fetch_fits_fifth_active']
    powers=[]
    for k in range(13,18):
        c=p.native_compiled(k,k+7);row=info(c,k,k+7)
        assert len(p.encode(c,k,k+7))==row['programme_bits']
        powers.append(row)
    assert [row['Q'] for row in powers if row['programme_fits_Q']]==[131072]
    text=ROOT/'papers_txt/gacs_2001.txt';lines=text.read_text().split('\n')
    title=[i+1 for i,line in enumerate(lines) if 'January 24, 2024 (last printing)' in line]
    assert len(title)==1
    assert 'Canonical simulations' in text.read_text() and 'Primitive variable-period media' in text.read_text()
    pdf=ROOT/'papers/Reliable Cellular Automata with Self-Organization.pdf'
    proof=Path(__file__).with_name('GPN0_PROGRAMME_OBSTRUCTION.md')
    result=dict(name='GPN0 native-prefix exact bit-packed programme/evaluator obstruction',
        baseline=baseline,Q=8192,U=1048576,error_lambda=24,error_separation_c=104,
        original_printed_native_preserved=True,native_only_h1_change=corrected,
        power_of_two_native_prefix_counts=powers,first_tested_power_of_two_native_prefix_fit_Q=131072,
        encoded_literal_native_beta_actual_bits=len(bits),
        exact_decoded_gate_equalities=len(comp.gates),exact_decoded_output_map_equalities=len(comp.outputs),
        all_raw_native_input_programme_equivalence_by_structural_induction=True,
        total_abstract_invalid_programme_input_response_defined=True,
        malformed_case_receipts=malformed,retained_random_replay_vectors=count,
        random_replays_measured_only=True,universal_proof_based_on_random_replays=False,
        independent_native_module_no_cross_module_optimization_premise=True,
        one_fresh_programme_bit_per_tick_serial_fetch_premise=True,
        no_programme_prefetch_before_fifth_stage_premise=True,
        prefix_storage_obstruction_for_this_encoder_proved=True,
        serial_fetch_fifth_stage_obstruction_proved=True,
        native_prefix_header_free_bits=76314,fifth_active_ticks=65536,
        native_prefix_fetch_ticks_lower_bound=76389,fetch_excess_ticks=10853,
        increasing_U_alone_repairs_storage_failure=False,
        existing_paper_asymptotic_bound_is_Q8192_certificate=False,
        gacs_supplied_printed_version='2024-01-24 corrected/strengthened printing',
        gacs_title_page_version_newline=title[0],gray_cited_section_numbers='7.3 and7.4',
        supplied_corresponding_programme_sections='9.1,9.2,9.3; Theorem9.2, Algorithm9.7, Condition9.20',
        source_version_difference_refutes_Gray_citation=False,
        modern_sufficient_bound_transplant_optimistic_C1_K277_maximum_P_bits=11,
        modern_bound_guarantee_failure_is_actual_runtime_lower_bound=False,
        supplied_three_input_interpreter_verbatim_covers_Gray_eleven_inputs=False,
        programme_is_whole_self_beta=False,physical_interpreter_service_or_final_layout_emitted=False,
        physical_whole_rule_defined_on_all_raw_states=False,
        arbitrary_word_loop_or_parallel_evaluator_obstruction_proved=False,
        native_prefix_Q131072_is_full_rule_sufficient_constant=False,
        faithful_Gray_counterexample_or_iid_memory_failure_proved=False,
        faster_U_used=False,active_rule_modified=False,global_reliability_established=False,
        encoder_sha256=digest(p.__file__),checker_sha256=digest(__file__),
        written_proof_sha256=digest(proof),native_netlist_sha256=comp.digest,
        beta_asset_sha256=digest(beta),programme_description_sha256=digest(encoded),
        replay_asset_sha256=digest(asset),literal_module_sha256=digest(literal_maintenance.__file__),
        generated_literal_maintenance_sha256=literal_maintenance.source_sha256(),
        active_maintenance_sha256=digest(ROOT/'gacsca/maintenance.py'),
        netlist_library_sha256=digest(ROOT/'gacsca/netlist.py'),
        gray_text_sha256=digest(ROOT/'papers_txt/gray_readers_guide.txt'),
        gray_pdf_sha256=digest(next((ROOT/'papers').glob('A Reader*'))),
        gacs_text_sha256=digest(text),gacs_pdf_sha256=digest(pdf),
        receipt_dependencies_sha256={name:digest(directory/name) for name in
            ('GT0_raw_gather_certificate.json','Gray_computed_simbit_order_certificate.json')})
    receipt=directory/'GPN0_native_programme_certificate.json'
    receipt.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({k:result[k] for k in ('encoded_literal_native_beta_actual_bits',
        'exact_decoded_gate_equalities','prefix_storage_obstruction_for_this_encoder_proved',
        'serial_fetch_fifth_stage_obstruction_proved','physical_whole_rule_defined_on_all_raw_states')}))


if __name__=='__main__':main()
