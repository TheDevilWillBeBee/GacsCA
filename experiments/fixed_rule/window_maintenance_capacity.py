"""Capacity rejection for a literal circuit concatenation, not an integrated rule."""
import hashlib
import json
from pathlib import Path
from gacsca.fixed_rule import window_rule as computing,window_maintenance as maintenance


def measure():
    # Address is already present. Age and four flags would add 39 state bits.
    added=maintenance.WIDTH-dict(maintenance.SCHEMA)['addr']
    width=computing.WIDTH+added
    gates=len(computing.self_description().gates)+len(maintenance.description().gates)
    # Optimistic workspace: eleven complete raw inputs, both circuit blocks,
    # two complete output banks and a guard. No mail/reconstruction instructions
    # are included in this lower bound on computation-window length.
    memory=2+11*width+gates+2*width+1
    minimum_window=memory+gates+1
    # Between consecutive gate fetches, a memory operand requires at least one
    # full reflected traversal. This bound omits extra visits and all other work.
    minimum_ticks=2*minimum_window*(gates-1)
    sources=('gacsca/fixed_rule/window_maintenance.py','gacsca/fixed_rule/window_rule.py',
             'gacsca/fixed_rule/maintenance.py','gacsca/level0_spec.py','gacsca/params.py',
             'tests/fixed_rule/test_window_maintenance.py',__file__)
    root=Path(__file__).resolve().parents[2]
    hashes={str(Path(name).resolve().relative_to(root)):hashlib.sha256(Path(name).read_bytes()).hexdigest() for name in sources}
    return dict(scope='rejected naive unshared NAND concatenation; not a compiled full simulator or lower bound on other evaluators',
                Q=maintenance.Q,gray_period=maintenance.U,maintenance_schema=maintenance.SCHEMA,
                maintenance_gates=len(maintenance.description().gates),maintenance_digest=maintenance.description().digest(),
                assumed_raw_state_bits=width,unshared_gate_count=gates,optimistic_memory_cells=memory,
                optimistic_window_cells=minimum_window,gate_traversal_tick_lower_bound=minimum_ticks,
                gray_active_update_ticks=8*maintenance.Q,fails_current_update_budget=minimum_ticks>8*maintenance.Q,
                exceeds_current_uint16_rom_constants=minimum_window>65536,
                omitted=['mail routing to five colonies','three retrieval rounds','stage clock and reset',
                         'spatial redundancy','extra coupling gates','clock evolution in padding representation'],
                source_sha256=hashes)


if __name__=='__main__':
    target=Path('figs/fixed_rule/window_maintenance_capacity_v1.json')
    with target.open('x') as out:json.dump(measure(),out,indent=2);out.write('\n')
    print(json.dumps({k:v for k,v in measure().items() if k!='source_sha256'},indent=2))
