"""CPU-only continuous evaluator certificate for the corrected own-F ROM."""
import argparse
import hashlib
import json
from pathlib import Path

from gacsca.fixed_rule import stream28_dual_pass20 as physical
from gacsca.fixed_rule import stream28_dual_projected20 as projected
from gacsca.fixed_rule.gpu_validation import corrected_circuit, description
from experiments.fixed_rule.certify_dual_projection20 import neighborhood
from experiments.fixed_rule.compact8_address_rom import project_all_dual_static
from experiments.fixed_rule.measure_stream28_spatial_capacity import PROJECTED_OUTPUT_FIELDS
from experiments.fixed_rule.replay_compact8_numpy import replay


def run(center=3218,age=0,seed=2026092901):
    with corrected_circuit.corrected_initial_data() as plan:
        rows=neighborhood(center,age,seed)
        words=tuple(word for row in rows for word in physical.encode_cell(row))
        addressed=project_all_dual_static(center,words,True)
        if addressed!=words:raise AssertionError('upper static Address projection differs')
        expected=projected.encode_cell(projected.project(physical.local_step(rows)))
        program=description.build()
        computed=program.evaluate(addressed)
        actual=tuple(computed[i] for i in PROJECTED_OUTPUT_FIELDS)
        if actual!=expected:
            field=next(i for i,(a,b) in enumerate(zip(actual,expected)) if a!=b)
            raise AssertionError(('corrected projected local F',field,
                                  actual[field],expected[field]))
        evaluator=replay(1,center,True,True,words,u20=True)
        if (not evaluator['passed'] or evaluator['description_sha256']!=program.digest()
                or evaluator['projected_output_words_checked']!=119):
            raise AssertionError('corrected circuit physical replay failed')
    return dict(passed=True,center=center,age=age,seed=seed,
                description_sha256=program.digest(),
                input_sha256=hashlib.sha256(b''.join(
                    int(w).to_bytes(8,'little') for w in addressed)).hexdigest(),
                projected_words_checked=119,
                projected_output_sha256=hashlib.sha256(b''.join(
                    int(w).to_bytes(8,'little') for w in actual)).hexdigest(),
                circuit_gate_instances=len(plan['routes'].gate_positions),
                circuit_operand_edges=len(plan['routes'].edges),
                timing=plan['timing'],evaluator=evaluator,
                source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest())


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output',type=Path,required=True)
    args=parser.parse_args()
    if args.output.exists():parser.error('output already exists')
    result=run()
    args.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(result,indent=2))
