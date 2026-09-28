"""Compose the local certificates into a spatially distributed pulse theorem."""
import argparse,itertools,json,time
from pathlib import Path
from gacsca.fixed_rule import retimed_holder_rule as f,retimed_holder_projected as r
from experiments.fixed_rule.run_retimed_holder_streamed_repair import sha


def compose():
    root=Path('figs/fixed_rule');gp=root/'retimed_holder_two_site_geometry_v1.json';sp=root/'retimed_holder_two_tick_repair_v2.json'
    geometry=json.loads(gp.read_text());structural=json.loads(sp.read_text())
    for receipt in (geometry,structural):
        assert receipt['passed'] and receipt['descriptor_sha256']==f.self_description().digest()
        for source,digest in receipt['source_sha256'].items():assert sha(source)==digest,source
    assert geometry['complete_position_cover']
    assert {tuple(x['defect_positions']) for x in geometry['cases']}==set(itertools.combinations(range(-5,6),2))
    assert len(geometry['cases'])==55
    for row in geometry['cases']:
        assert row['passed'] and row['independent_bits']==148 and row['checked_raw_outputs']==['address','age','f1','f2']
        assert row['descriptor_sha256']==f.self_description().digest()
        assert all(-5<=offset<=5 and name in ('address','age','f1','f2','w2_wf1','w2_wf2') for offset,name in row['support'])
    assert structural['geometry_certificate_sha256']==sha(gp)
    assert structural['complete_procedure_cut_replayed'] and structural['unrestricted_logical_procedure_words'] and structural['no_head_count_assumption']
    static={name for name,_ in f.STATIC};procedure={f's{k}_{name}' for k in range(5) for name,_ in f.PROCEDURE};other=set(structural['all_mutable_nonprocedure_fields_equal'])
    assert len(static)==49 and len(procedure)==90 and len(other)==15
    assert static|procedure|other=={name for name,_ in f.SCHEMA} and not (static&procedure or static&other or procedure&other)
    assert set(structural['healthy_output_coherent_procedure_fields'])=={name for name,_ in f.PROCEDURE}
    assert r.SCHEMA==f.SCHEMA[len(f.STATIC):] and len(r.SCHEMA)==105
    assert f.NEIGHBORHOOD==tuple(range(-7,8)) and f.OFFSETS==tuple(range(-2,3))
    assert geometry['all_healthy_addresses']==f.Q and geometry['all_healthy_ages']==structural['all_legal_ages']==f.U
    return dict(passed=True,descriptor_sha256=f.self_description().digest(),geometry_radius=5,geometry_window_cells=11,procedure_and_Signal_vote_window_cells=5,maximum_fault_sites_per_geometry_window=2,total_fault_site_count_unrestricted=True,physical_mutable_words=105,complete_reconstructed_raw_words=154,all_clock_ages=f.U,all_addresses=f.Q,first_tick_geometry_Signal_Wf_equal_everywhere=True,first_tick_procedure_defects_confined_to_original_fault_sites=True,healthy_first_tick_procedure_output_coherent=True,second_tick_all_physical_fields_equal=True,proof_inputs={str(gp):sha(gp),str(sp):sha(sp)},hypotheses=['infinite line or periodic ring of size divisible by Q','canonical Addresses and uniform Age in [0,U)','healthy primary Flag1/Flag2 and all Wf copies zero','healthy procedures are coherent fivefold copies, with arbitrary typed logical Data/head/controller/mail words','healthy Signals are coherent fivefold bit copies','the faulty input differs only by arbitrary G-state replacements at a site set having at most two sites in every interval of eleven consecutive sites','no further transition faults during the two repair ticks'],theorem='Under the stated hypotheses, G^2(damaged)=G^2(healthy) as complete physical configurations. The number and values of faults may be arbitrary subject to the local spatial condition.',composition='Every radius-five geometry computation sees at most two replacements and therefore repairs. Each five-input procedure/Signal majority sees at most two bad copies. Checked descriptor cuts make all nonprocedure outputs equal and confine procedure discrepancies to original faulty holders. The healthy output procedures are coherent without a head-count restriction. On the next tick every five-copy vote repairs those remaining discrepancies, and the complete-output cut gives equality. Fixed G projection restores all metadata from the already equal Address.',limitation='A conditional isolated spatial-pulse theorem, not arbitrary forcing-phase recovery, continuous stochastic noise, a threshold, hierarchical amplification or robust-cap repair.')


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--output',required=True);args=parser.parse_args();out=Path(args.output)
    if out.exists():raise FileExistsError(out)
    started=time.perf_counter();result=compose();result.update(seconds=time.perf_counter()-started,source_sha256={str(Path(__file__)):sha(__file__)})
    out.write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))

if __name__=='__main__':main()
