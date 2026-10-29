"""GBC5 scratch-free reader specialization, unchanged GBC4 total rule.

This is a software encoder change only. All captured input accesses are
the existing real READ-SPAN primitive; no state, opcode or table is added.
The complete rejected listing is not an issued Q-bit own programme.
"""
from pathlib import Path
import sys

INHERITED = Path(__file__).resolve().parents[1] / 'unregistered_gbc4'
sys.path.insert(0, str(INHERITED))
import complete_branch_emitter as e
import shared_control_emitter as shared
b = e.b


def reader_body(a, width):
    """B=Head bit offset; q=Work100; Fn=signed logical centre.

    A/B are scratch. No Work word, NC, Fn, or output tape is modified.
    Entry and return use the declared counted bank1 CALL/RETURN.
    """
    assert 1 <= width <= 20
    a.label('scratch_free_head_read_' + str(width))
    a.emit('SWAP')
    a.immediate('mul', 5)
    a.immediate('add', e.HEAD_BASE)
    a.emit('SWAP')
    a.get(e.QCOL)
    a.emit('ALU', b.ALU['add'])
    a.emit('SWAP')
    a.literal(width)
    a.emit('READ', 3, 16, 1)
    a.emit('RETURN', 1)


def emit_component(q, centre, offset, width):
    assert 0 <= q < 5 and -4 <= centre <= 4
    assert 0 <= offset and offset + width <= b.HEAD_BITS
    a = e.Assembler()
    a.literal(q); a.put(e.QCOL)
    a.literal(centre & 15); a.emit('SETFN')
    a.literal(offset); a.emit('SWAP')
    a.call('scratch_free_head_read_' + str(width), 380)
    a.emit('HLT')
    reader_body(a, width)
    return a.finish()


def emit_complete_structural_listing():
    old_read, old_helper = e.head_read, e.shared_head_read_helper
    old_assembler = e.Assembler
    widths, callers, captured = set(), [], {}

    class CapturingAssembler(old_assembler):
        def finish(self, require_fit=True):
            captured['rows'] = list(self.rows)
            captured['marks'] = dict(self.marks)
            return super().finish(require_fit)

    def scratch_free_read(a, offset, width, destination=None, centre=None):
        assert 0 <= offset < 1024 and 1 <= width <= 20
        assert offset + width <= b.HEAD_BITS
        ident = len(callers)
        start_label = 'gbc5_reader_start_' + str(ident)
        call_label = 'gbc5_reader_call_' + str(ident)
        end_label = 'gbc5_reader_end_' + str(ident)
        a.label(start_label)
        if centre is None:
            a.get(e.CENTRE)
        else:
            a.literal(centre & 15)
        a.emit('SETFN')
        a.literal(offset); a.emit('SWAP')
        target = 'scratch_free_head_read_' + str(width)
        a.label(call_label)
        a.call(target, e.COPY_RETURN)
        if destination is not None:
            a.put(destination)
        a.label(end_label)
        widths.add(width)
        callers.append({'start_label': start_label, 'call_label': call_label,
                        'end_label': end_label, 'offset': offset,
                        'width': width, 'destination': destination,
                        'centre': centre, 'target': target})

    def helpers(a):
        for width in sorted(widths):
            reader_body(a, width)

    try:
        e.Assembler = CapturingAssembler
        e.head_read, e.shared_head_read_helper = scratch_free_read, helpers
        out = shared.emit_complete_structural_listing()
    finally:
        e.Assembler = old_assembler
        e.head_read, e.shared_head_read_helper = old_read, old_helper
    out['compiler_change'] = 'width-specialized scratch-free Head readers; unchanged GBC4 total rule'
    out['reader_widths'] = sorted(widths)
    out['reader_callers'] = callers
    out['symbolic_rows'] = captured['rows']
    out['symbolic_marks'] = captured['marks']
    return out


if __name__ == '__main__':
    import argparse, json
    p = argparse.ArgumentParser(); p.add_argument('--output', type=Path, required=True)
    a = p.parse_args(); out = emit_complete_structural_listing()
    a.output.write_text(json.dumps(out, indent=2) + '\n')
    print(json.dumps({k: out[k] for k in ('programme_bits', 'instructions',
                                        'Q_fit', 'reader_widths')}, indent=2))
