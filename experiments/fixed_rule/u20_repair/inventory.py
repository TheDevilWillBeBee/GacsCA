"""Static-input catalog and source identity inventory for the U20 candidate."""
import argparse
import hashlib
import json
from pathlib import Path

from gacsca.fixed_rule import spatial_codec8
from gacsca.fixed_rule import stream28_compact_layout as layout_module
from gacsca.fixed_rule import stream28_dual_holder_rule20 as holder
from gacsca.fixed_rule import stream28_dual_pass20 as physical
from gacsca.fixed_rule import stream28_spatial_overlay20 as late
from gacsca.fixed_rule.u20_repair.corrected_circuit import corrected_initial_data
from experiments.fixed_rule.build_compact8_circuit import static_plan


SOURCES = (
    'gacsca/fixed_rule/stream28_dual_pass20.py',
    'gacsca/fixed_rule/stream28_dual_pass_optimized20.py',
    'gacsca/fixed_rule/stream28_dual_core_clock_description20.py',
    'gacsca/fixed_rule/stream28_dual_native20.py',
    'gacsca/fixed_rule/stream28_dual_dense_gpu20.cu',
    'gacsca/fixed_rule/gpu_validation/description.py',
    'gacsca/fixed_rule/gpu_validation/dense_corrected.cu',
    'experiments/fixed_rule/compact8_address_rom.py',
    'experiments/fixed_rule/build_compact8_circuit.py',
    'experiments/fixed_rule/stream28_compact_routes.py',
    'experiments/fixed_rule/schedule_compact_operands.py',
)


def catalog(root):
    with corrected_initial_data():
        plan=static_plan(True,True)
        layout=layout_module.build()
        source_by_wire={wire:site for site,wire in plan['raw_sources'].items()}
        entries=[]
        for wire in layout.static_inputs:
            neighbor,field=divmod(wire,physical.FIELDS)
            if field<holder.FIELDS:
                field_name=holder.SCHEMA[field][0]
                table='holder_static_fields'
                local_index=field
            else:
                local_index=field-holder.FIELDS
                field_name=f'spatial_raw_{local_index}'
                table='corrected_spatial_ROM'
            entries.append(dict(wire=wire,neighbor_index=neighbor,
                                upper_address_offset=neighbor-7,
                                upper_field_index=field,upper_field_name=field_name,
                                lower_ROM_row_address='(upper_address + upper_address_offset) % 8192',
                                lower_ROM_field_index=local_index,
                                lower_ROM_table=table,
                                lower_SOURCE_site=source_by_wire.get(wire),
                                first_read_old_age=physical.EARLY_CAPTURE_AGE,
                                last_read_old_age=late.CAPTURE_AGE))
    return dict(rule_sha256=hashlib.sha256((root/SOURCES[0]).read_bytes()).hexdigest(),
                source_sha256={p:hashlib.sha256((root/p).read_bytes()).hexdigest()
                               for p in SOURCES},
                static_words=len(entries),
                physically_sourced=sum(e['lower_SOURCE_site'] is not None for e in entries),
                compiler_pruned=[e['wire'] for e in entries if e['lower_SOURCE_site'] is None],
                entries=entries)


if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    if args.output.exists():raise FileExistsError(args.output)
    root=Path(__file__).resolve().parents[3]
    result=catalog(root)
    args.output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n')
    print(json.dumps({key:value for key,value in result.items() if key!='entries'},
                     indent=2,sort_keys=True))
