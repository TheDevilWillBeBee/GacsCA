"""GBC2 full-own-emitter work; not yet a complete beta.

The executable helpers below are generic physical routines. No helper
evaluates a host transition or bypasses READ/WRITE travel. This file is
intentionally marked incomplete until all stage/CPU/source paths exist.
"""
import compact_completion_rule as b

COMPLETE_OWN_EMITTER = False
# Counted software locations inside the existing 407-bit mutable Work.
VALUE, ADDRESS, LENGTH, RETURN = 300, 320, 340, 360
assert RETURN + 20 <= b.WORK_BITS


class Assembler:
    def __init__(self):
        self.rows = []
        self.marks = {}

    def label(self, name):
        assert name not in self.marks
        self.marks[name] = len(self.rows)

    def emit(self, name, *args):
        self.rows.append((name, args))

    def literal(self, value):
        self.emit('LIT', value)

    def immediate(self, name, value):
        self.emit('ALUI', b.ALU[name], value)

    def get(self, offset):
        assert offset % 20 == 0 and 0 <= offset < 407
        self.emit('WGET', offset//20)

    def put(self, offset):
        # Preserve A, replacing precisely this counted 20-bit Work word.
        assert offset % 20 == 0 and 0 <= offset < 407
        self.emit('WSET', offset//20)

    def branch(self, condition, target):
        self.emit('BR', condition, target)

    def call(self, target, slot=RETURN):
        """One-deep generic software call; return storage is counted.

        SELF reads the real opcode PC. The addition is the exact length
        of this emitted block, avoiding variable-length label literals.
        The helper may not overwrite Work[RETURN:RETURN+20].
        """
        fixed = len(b.encode('SELF', 1)) + len(b.encode('WSET', slot//20)) + len(b.encode('BR', 0, 0))
        delta = next(d for d in range(256)
                     if d == fixed + len(b.encode('ALUI', b.ALU['add'], d)))
        before = len(self.rows)
        self.emit('SELF', 1)
        self.immediate('add', delta)
        self.put(slot)
        self.branch(0, target)
        assert sum(len(b.encode(op, *(0 if isinstance(x, str) else x for x in args)))
                   for op, args in self.rows[before:]) == delta

    def finish(self, require_fit=True):
        starts = []
        address = 0
        for name, args in self.rows:
            starts.append(address)
            address += len(b.encode(name, *(0 if isinstance(x, str) else x for x in args)))
        labels = {name: starts[index] for name, index in self.marks.items()}
        if require_fit and address > b.CODE_BITS:
            raise ValueError(('specified GBC1 emission exceeds Q', address, b.CODE_BITS))
        bits, listing = [], []
        for name, args in self.rows:
            values = tuple(labels[x] if isinstance(x, str) else x for x in args)
            encoded = b.encode(name, *values)
            listing.append((len(bits), name, values, len(encoded)))
            bits.extend(encoded)
        return tuple(bits + [0] * max(0, b.CODE_BITS - len(bits))), listing, address


def write_word_helper(a):
    """Write low LENGTH bits of VALUE at ADDRESS, stride five.

    Caller premises: 1<=LENGTH<=20 and the whole target span is in [0,Q).
    All real I/O issue, travel, consume and return ticks are retained.
    No prepared invariant is asserted for arbitrary corrupt helper entry.
    Such entries still have total underlying local ISA semantics.
    """
    a.label('write_word')
    a.get(VALUE)
    a.immediate('and', 1)
    a.emit('SWAP')
    a.get(ADDRESS)
    a.emit('SWAP')
    a.emit('WRITE')
    a.get(VALUE)
    a.immediate('shr', 1)
    a.put(VALUE)
    a.get(ADDRESS)
    a.immediate('add', 5)
    a.put(ADDRESS)
    a.get(LENGTH)
    a.immediate('sub', 1)
    a.put(LENGTH)
    a.branch(2, 'write_word')
    a.get(RETURN)
    a.emit('JMP')


def emit_helper_test(value, target, length):
    """Actual generic routine diagnostic, explicitly not an own beta."""
    assert 0 <= value <= b.MASK and 1 <= length <= 20
    assert 0 <= target and target + 5 * (length - 1) < b.Q
    a = Assembler()
    for offset, v in ((VALUE, value), (ADDRESS, target), (LENGTH, length)):
        a.literal(v)
        a.put(offset)
    a.call('write_word')
    a.emit('HLT')
    write_word_helper(a)
    return a.finish()


# Early-stage compiler context, all contained in the same 407-bit Work.
T, GF, FLAG1, RAWGF = 0, 20, 40, 80
COPY, STAGE, HISTORY_BASE, DISTANCE = 100, 120, 140, 160
SOURCE, DESTINATION, COPY_RETURN = 180, 200, 380
assert COPY_RETURN + 20 <= b.WORK_BITS


def constant_store(a, offset, value):
    a.literal(value)
    a.put(offset)


def emit_native_and_context(a):
    """Actual eleven-lane input loop; central native outputs and context."""
    P = b.PRIMARY_START
    a.literal(P+36)
    a.emit('SWAP')
    a.label('native_input')
    a.emit('READ', b.READ_WORD, 0)
    a.immediate('shr', 3)
    a.emit('PUSH', 11)
    a.emit('SELF', 0)
    a.immediate('eq', P)
    a.branch(2, 'native_loaded')
    a.emit('SELF', 0)
    a.immediate('sub', 1)
    a.emit('SWAP')
    a.branch(0, 'native_input')
    a.label('native_loaded')
    a.emit('NATIVE')
    a.literal(P)
    a.emit('SWAP')
    a.label('native_output')
    a.emit('SWAP')
    a.immediate('sub', P)
    a.emit('SWAP')
    a.emit('NCGET')
    a.immediate('and', 1)
    a.emit('SWAP')
    a.immediate('add', P)
    a.emit('SWAP')
    a.emit('WRITE')
    a.emit('SELF', 0)
    a.immediate('eq', P+34)
    a.branch(2, 'native_done')
    a.emit('SELF', 0)
    a.immediate('add', 1)
    a.emit('SWAP')
    a.branch(0, 'native_output')
    a.label('native_done')
    for target in (P+35, P+36):
        a.literal(target)
        a.emit('SWAP')
        a.literal(0)
        a.emit('WRITE')
    for offset, bit, mask in ((T, 13, b.MASK), (GF, 0, b.Q-1), (FLAG1, 33, 1)):
        a.literal(bit)
        a.emit('SWAP')
        a.emit('NCGET')
        a.immediate('and', mask)
        a.put(offset)


def stream_field(a, field, centre=0):
    start, count = b.offsets()[field]
    a.literal(start)
    a.emit('SWAP')
    a.literal(count)
    a.emit('STREAM', 1, 0, centre & 31)


def fill_field(a, field):
    start, count = b.offsets()[field]
    a.literal(start)
    a.emit('SWAP')
    a.literal(count)
    a.emit('FILL', 0, 0)


def copy_group_helper(a):
    """Voted five-copy one-bit source group to a different output group."""
    a.label('copy_group')
    constant_store(a, COPY, 0)
    a.label('copy_loop')
    a.get(COPY)
    a.emit('SWAP')
    a.get(SOURCE)
    a.emit('ALU', b.ALU['add'])
    a.emit('SWAP')
    a.literal(1)
    a.emit('READ', 3, 0, 1)
    a.put(VALUE)
    a.get(COPY)
    a.emit('SWAP')
    a.get(DESTINATION)
    a.emit('ALU', b.ALU['add'])
    a.put(ADDRESS)
    constant_store(a, LENGTH, 1)
    a.call('write_word')
    a.get(COPY)
    a.immediate('add', 1)
    a.put(COPY)
    a.immediate('lt', 5)
    a.branch(2, 'copy_loop')
    a.get(COPY_RETURN)
    a.emit('JMP')


def copy_fixed_group(a, source, destination):
    constant_store(a, SOURCE, source)
    constant_store(a, DESTINATION, destination)
    a.call('copy_group', COPY_RETURN)


def emit_early_stage_programme():
    """Actual early-stage correction beta, not the complete own emitter.

    It covers every raw upper input whose computed native Age lies in
    [0,72Q+2]. Later early collection/courier/Workspace/CPU stages are
    explicitly unfinished, with a separate unsupported HLT path.
    """
    a = Assembler()
    emit_native_and_context(a)
    a.get(T)
    a.immediate('lt', b.COLLECT)
    a.branch(2, 'early_supported')
    a.emit('HLT')
    a.label('early_supported')
    # The raw-GF wipe is computed before any SF write. Native padding is
    # absent in this binary alphabet; all input GF13 values remain raw.
    a.literal(b.PRIMARY_START)
    a.emit('SWAP')
    a.literal(13)
    a.emit('READ', 3, 0, 0)
    a.put(RAWGF)
    a.get(GF)
    a.emit('SWAP')
    a.get(RAWGF)
    a.emit('ALU', b.ALU['eq'])
    a.branch(2, 'no_wipe')
    a.get(FLAG1)
    a.branch(2, 'wipe_all')
    a.label('no_wipe')
    for field, _ in b.FIELDS:
        stream_field(a, field)
    # Reset private outputs; at age0 commit old Next into Info first.
    for age in (0, 32*b.Q, 64*b.Q):
        a.get(T)
        a.immediate('eq', age)
        a.branch(2, 'private_reset')
    a.branch(0, 'after_private_reset')
    a.label('private_reset')
    for field in ('head', 'next', 'courierL', 'courierR'):
        fill_field(a, field)
    a.get(T)
    a.branch(2, 'after_private_reset')
    copy_fixed_group(a, b.offsets()['next'][0], b.offsets()['info'][0])
    a.label('after_private_reset')
    # Mail reset/Flag1 erasure precedes loads and movements.
    a.get(FLAG1)
    a.branch(2, 'mail_zero')
    for age in (0, 32*b.Q, 64*b.Q):
        a.get(T)
        a.immediate('eq', age)
        a.branch(2, 'mail_zero')
    for age in (1, 32*b.Q+1, 64*b.Q+1):
        a.get(T)
        a.immediate('eq', age)
        a.branch(2, 'mail_load')
    a.get(T)
    a.immediate('mod', 32*b.Q)
    a.immediate('lt', 16*b.Q)
    a.branch(2, 'mail_shift')
    a.branch(0, 'mail_done')
    a.label('mail_zero')
    fill_field(a, 'mailL')
    fill_field(a, 'mailR')
    a.branch(0, 'mail_done')
    a.label('mail_load')
    copy_fixed_group(a, b.offsets()['info'][0], b.offsets()['mailL'][0])
    copy_fixed_group(a, b.offsets()['info'][0], b.offsets()['mailR'][0])
    a.branch(0, 'mail_done')
    a.label('mail_shift')
    stream_field(a, 'mailL', 1)
    stream_field(a, 'mailR', -1)
    a.label('mail_done')
    constant_store(a, STAGE, 0)
    a.label('history_stage')
    # stage base is 32*stage*Q; retain it in DISTANCE temporarily.
    a.get(STAGE)
    a.immediate('mul', 32*b.Q)
    a.put(DISTANCE)
    a.get(STAGE)
    a.immediate('mul', 85)
    a.immediate('add', b.offsets()['history1'][0])
    a.put(HISTORY_BASE)
    # Bank g resets at ages 0,32Q,...,32gQ.
    a.get(DISTANCE)
    a.emit('SWAP')
    a.get(T)
    a.emit('ALU', b.ALU['lt'])
    a.branch(2, 'history_reset_mod')
    a.get(T)
    a.emit('SWAP')
    a.get(DISTANCE)
    a.emit('ALU', b.ALU['eq'])
    a.branch(2, 'history_reset_mod')
    a.branch(0, 'history_capture')
    a.label('history_reset_mod')
    a.get(T)
    a.immediate('mod', 32*b.Q)
    a.branch(2, 'history_capture')
    a.get(HISTORY_BASE)
    a.emit('SWAP')
    a.literal(85)
    a.emit('FILL', 0, 0)
    a.branch(0, 'history_next')
    a.label('history_capture')
    a.get(DISTANCE)
    a.immediate('add', 1)
    a.emit('SWAP')
    a.get(T)
    a.emit('ALU', b.ALU['eq'])
    a.branch(2, 'history_center')
    a.get(DISTANCE)
    a.immediate('add', 2)
    a.emit('SWAP')
    a.get(T)
    a.emit('ALU', b.ALU['sub'])
    a.put(DISTANCE)
    a.immediate('mod', b.Q)
    a.branch(2, 'history_next')
    a.get(DISTANCE)
    a.immediate('div', b.Q)
    a.put(DISTANCE)
    a.branch(1, 'history_next')
    a.immediate('lt', 9)
    a.branch(1, 'history_next')
    # The two symmetric lanes capture different OLD Mail fields.
    constant_store(a, SOURCE, b.offsets()['mailL'][0])
    a.get(DISTANCE)
    a.immediate('add', 8)
    a.immediate('mul', 5)
    a.emit('SWAP')
    a.get(HISTORY_BASE)
    a.emit('ALU', b.ALU['add'])
    a.put(DESTINATION)
    a.call('copy_group', COPY_RETURN)
    constant_store(a, SOURCE, b.offsets()['mailR'][0])
    a.get(DISTANCE)
    a.emit('SWAP')
    a.literal(8)
    a.emit('ALU', b.ALU['sub'])
    a.immediate('mul', 5)
    a.emit('SWAP')
    a.get(HISTORY_BASE)
    a.emit('ALU', b.ALU['add'])
    a.put(DESTINATION)
    a.call('copy_group', COPY_RETURN)
    a.branch(0, 'history_next')
    a.label('history_center')
    constant_store(a, SOURCE, b.offsets()['info'][0])
    a.get(HISTORY_BASE)
    a.immediate('add', 40)
    a.put(DESTINATION)
    a.call('copy_group', COPY_RETURN)
    a.label('history_next')
    a.get(STAGE)
    a.immediate('add', 1)
    a.put(STAGE)
    a.immediate('lt', 3)
    a.branch(2, 'history_stage')
    a.emit('HLT')
    a.label('wipe_all')
    start = b.PRIMARY_START+37
    a.literal(start)
    a.emit('SWAP')
    a.literal(b.FRAME_BITS-37)
    a.emit('FILL', 0, 0)
    a.emit('HLT')
    copy_group_helper(a)
    write_word_helper(a)
    return a.finish()
