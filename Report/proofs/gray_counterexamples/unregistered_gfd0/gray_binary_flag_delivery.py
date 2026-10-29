"""GFD0: binary, radius-five, stage-three native-flag delivery component.

The native/control and fifth-write interfaces are not a completed CA.  The
early flag calculation has no port: it is the emitted printed-native circuit
on actual collected raw History columns. No instruction ROM or host transition
callback is read by the component. A whole own beta and hardwirer remain open.
"""
from pathlib import Path
import sys
BASE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE))
import gray_raw_gather as gather
import literal_maintenance as printed
from gacsca import maintenance
from gacsca.netlist import Net, Compiled, at_least, w_eq_const, w_in_range, w_add_const

Q = 8192
U = 128 * Q
LAMBDA = 24
ERROR_SEPARATION = 104
SLOTS = gather.SLOTS
LANES = gather.LANES
NATIVE_SCHEMA = (('addr', 13), ('age', 20), ('f1', 1), ('f2', 1), ('wf1', 1), ('wf2', 1))
NATIVE_TAGS = tuple((field, bit) for field, width in NATIVE_SCHEMA for bit in range(width))
NATIVE_BITS = len(NATIVE_TAGS)
PACK_BITS = NATIVE_BITS * len(LANES)
EXTRA_FIELDS = (('pack', PACK_BITS), ('courierL', 1), ('courierR', 1))
ALL_FIELDS = gather.FIELDS + EXTRA_FIELDS
FRAME_BITS = gather.FRAME_BITS + 5 * (PACK_BITS + 2)
PRIMARY_START = Q // 2 - FRAME_BITS // 2
NATIVE_START = PRIMARY_START
COLLECTOR = NATIVE_START + NATIVE_BITS - 1
COLLECT_START = 69 * Q + 3
EVALUATE = COLLECT_START + NATIVE_BITS
DELIVERY = 80 * Q - 1
LEFT_DESTINATION = 3
RIGHT_DESTINATION = Q - 3


def schema():
    return NATIVE_SCHEMA + tuple((field, 5 * width) for field, width in ALL_FIELDS)


def layout():
    tags = [(field, bit) for field, width in schema() for bit in range(width)]
    assert len(tags) == FRAME_BITS
    return {tag: PRIMARY_START + i for i, tag in enumerate(tags)}


def unpack_bank(word):
    """407 bits: raw field-bit order, each followed by eleven offset lanes."""
    cells = {j: {f: 0 for f, _ in NATIVE_SCHEMA} for j in LANES}
    for k, (field, bit) in enumerate(NATIVE_TAGS):
        for lane, j in enumerate(LANES):
            cells[j][field] |= ((word >> (k * 11 + lane)) & 1) << bit
    return cells


def pack_bank(cells):
    return sum(((cells[j][field] >> bit) & 1) << (k * 11 + lane)
               for k, (field, bit) in enumerate(NATIVE_TAGS)
               for lane, j in enumerate(LANES))


def native_flags_scalar(word, corrected=False):
    cells = unpack_bank(word)
    result = maintenance.maintenance_scalar(cells, Q=Q, U=U) if corrected else printed.scalar(cells)
    return result['f1'], result['f2']


def native_flags_build(n, bits, corrected=False):
    assert len(bits) == PACK_BITS
    cells = {j: {} for j in LANES}
    for j in LANES:
        lane = LANES.index(j)
        for field, width in NATIVE_SCHEMA:
            indices = [NATIVE_TAGS.index((field, b)) * 11 + lane for b in range(width)]
            cells[j][field] = [bits[i] for i in indices] if width > 1 else bits[indices[0]]
    result = (maintenance.build if corrected else printed.build)(n, cells, 13, 20)
    return result['f1'], result['f2']


def native_netlist(corrected=False):
    n = Net()
    bits = [n.input(('bank', b)) for b in range(PACK_BITS)]
    f1, f2 = native_flags_build(n, bits, corrected)
    n.set_output(('f1',), f1)
    n.set_output(('f2',), f2)
    return n


def extra_plan(age, address, slot, field, bit=0):
    """Scalar source descriptor, before the mandatory holder wipe.

    This independent scalar plan is also the finite logical routing contract.
    Native evaluation reads old voted pack at the collector, never current
    host-calculated flag results. A shifted copy uses its logical Address.
    """
    a = (address + slot) % Q
    current = (field, slot, bit)
    if age in {s[0] for s in gather.STAGES}:
        return ('zero',)
    if field == 'pack':
        if age == COLLECT_START:
            k, lane = divmod(bit, 11)
            if a == NATIVE_START + k:
                return ('majority3', *((f'history{g}', slot, lane) for g in (1, 2, 3)))
            return ('zero',)
        if COLLECT_START < age < EVALUATE:
            if a == COLLECTOR:
                return ('or', current, (field, slot - 1, bit))
            if NATIVE_START <= a < COLLECTOR:
                return (field, slot - 1, bit)
            return ('zero',)
        return current
    if age == EVALUATE:
        if a == COLLECTOR:
            return ('native_flag', slot, 2 if field == 'courierL' else 1)
        return ('zero',)
    if EVALUATE < age < 80 * Q:
        if field == 'courierL':
            if a == LEFT_DESTINATION:
                return ('or', current, (field, slot + 1, 0))
            if LEFT_DESTINATION < a <= COLLECTOR:
                return (field, slot + 1, 0)
        else:
            if a == RIGHT_DESTINATION:
                return ('or', current, (field, slot - 1, 0))
            if COLLECTOR <= a < RIGHT_DESTINATION:
                return (field, slot - 1, 0)
        return ('zero',)
    return current


def build(n, cells, address, age, flag1, wipe, writes, corrected=False):
    """A total finite binary transducer; every data read is at radius <=5.

    Native computed controls and five late-store pairs are explicit integration
    interfaces. Flag1/Flag2 early results are NOT interfaces. They are evaluated
    from the physical voted pack in this graph. The zero-Workspace-before96Q
    restriction needed for the clean native prefix is outside this transducer.
    """
    widths = dict(ALL_FIELDS)
    cache = {}

    def value(logical, field, bit=0):
        key = logical, field, bit
        if key not in cache:
            cache[key] = at_least(n, [cells[logical - s][field][i * widths[field] + bit]
                                     for i, s in enumerate(SLOTS)], 3)
        return cache[key]

    eq = lambda t: w_eq_const(n, age, t)
    reset = n.any(eq(s[0]) for s in gather.STAGES)
    collect = n.AND(w_in_range(n, age, COLLECT_START + 1, EVALUATE), n.NOT(reset))
    delivering = w_in_range(n, age, EVALUATE + 1, 80 * Q)
    upper_flags = {}

    def flags(logical):
        if logical not in upper_flags:
            upper_flags[logical] = native_flags_build(
                n, [value(logical, 'pack', b) for b in range(PACK_BITS)], corrected)
        return upper_flags[logical]

    # GT0's other fields retain their actual previously emitted equations.
    # The old early ports are replaced below only on their exact special writes.
    base_cells = {j: {f: cells[j][f] for f, _ in gather.FIELDS} for j in cells}
    result = gather.build(n, base_cells, address, age, flag1, wipe, 0, 0, writes)
    for slot in SLOTS:
        a = w_add_const(n, address, slot % Q)
        at_collector = w_eq_const(n, a, COLLECTOR)
        for b in range(PACK_BITS):
            k, lane = divmod(b, 11)
            current = value(slot, 'pack', b)
            seed = n.AND(w_eq_const(n, a, NATIVE_START + k), at_least(n,
                [value(slot, f'history{g}', lane) for g in (1, 2, 3)], 2))
            incoming = value(slot - 1, 'pack', b)
            moving_value = n.MUX(at_collector, n.OR(current, incoming),
                n.MUX(w_in_range(n, a, NATIVE_START, COLLECTOR), incoming, 0))
            v = n.MUX(reset, 0, n.MUX(eq(COLLECT_START), seed,
                n.MUX(collect, moving_value, current)))
            result['pack', slot, b] = n.AND(v, n.NOT(wipe))
        for field, destination, direction, which in (
                ('courierL', LEFT_DESTINATION, 1, 1),
                ('courierR', RIGHT_DESTINATION, -1, 0)):
            current = value(slot, field)
            incoming = value(slot + direction, field)
            at_destination = w_eq_const(n, a, destination)
            eligible = w_in_range(n, a, min(destination, COLLECTOR), max(destination, COLLECTOR) + 1)
            if eq(EVALUATE) == 0 or at_collector == 0:
                seeded = 0
            else:
                seeded = n.AND(at_collector, flags(slot)[which])
            moving_value = n.MUX(at_destination, n.OR(current, incoming),
                n.MUX(eligible, incoming, 0))
            v = n.MUX(reset, 0, n.MUX(eq(EVALUATE), seeded,
                n.MUX(delivering, moving_value, current)))
            result[field, slot, 0] = n.AND(v, n.NOT(wipe))
        # At each backup holder the exact logical target reads its own courier
        # vote. No global/shared early-result port or head-centre lookup occurs.
        special = n.MUX(w_eq_const(n, a, LEFT_DESTINATION), value(slot, 'courierL'),
            n.MUX(w_eq_const(n, a, RIGHT_DESTINATION), value(slot, 'courierR'),
                  value(slot, 'simbit')))
        result['simbit', slot, 0] = n.MUX(eq(DELIVERY),
            n.AND(special, n.NOT(wipe)), result['simbit', slot, 0])
    return result


def netlist(corrected=False, internal_native=False):
    n = Net()
    cells = {j: {field: [n.input(('x', j, field, bit)) for bit in range(5 * width)]
                 for field, width in ALL_FIELDS} for j in range(-5, 6)}
    native_result = None
    if internal_native:
        raw = {j: {field: ([n.input(('native', j, field, bit)) for bit in range(width)]
                  if width > 1 else n.input(('native', j, field, 0)))
                  for field, width in NATIVE_SCHEMA} for j in range(-5, 6)}
        native_result = (maintenance.build if corrected else printed.build)(n, raw, 13, 20)
        address, age, f1 = (native_result[field] for field in ('addr', 'age', 'f1'))
        same = n.all(n.NOT(n.XOR(a, b)) for a, b in zip(address, raw[0]['addr']))
        wipe = n.AND(f1, n.NOT(same))
    else:
        address = [n.input(('computed_address', b)) for b in range(13)]
        age = [n.input(('computed_age', b)) for b in range(20)]
        f1 = n.input(('computed_flag1',))
        wipe = n.input(('native_wipe',))
    writes = {s: (n.input(('write_enable', s)), n.input(('write_value', s))) for s in SLOTS}
    outputs = build(n, cells, address, age, f1, wipe, writes, corrected)
    for name, node in outputs.items():
        n.set_output(('y',) + name, node)
    if internal_native:
        for field in ('addr', 'age'):
            for bit, node in enumerate(native_result[field]):
                n.set_output(('native_output', field, bit), node)
        for field in ('f1', 'f2'):
            n.set_output(('native_output', field, 0), native_result[field])
        pulse = w_in_range(n, age, 96 * Q, 98 * Q)
        for field in ('wf1', 'wf2'):
            port = n.input(('late_workspace_port', field))
            n.set_output(('native_output', field, 0), n.AND(port, n.AND(pulse, n.NOT(wipe))))
    return n
