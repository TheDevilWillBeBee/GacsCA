"""Ongoing GBC1 generic execution checks; no own-programme claim."""
from dataclasses import asdict, replace
from hashlib import sha256
from itertools import product
from pathlib import Path
import argparse
import json
import time
import compact_completion_rule as b
from compact_full_emitter import emit_helper_test


def source(address):
    return int.from_bytes(sha256(f'GBC1:{address}'.encode()).digest()[:3], 'little') & ((1 << 17) - 1)


def execute(beta, physical=False):
    address = b.PRIMARY_START
    p = b.Packet(p=1)
    writes, history, physical_checks = {}, [], 0
    for tick in range(1, 20000):
        old, old_address = p, address
        address += (1 if old.move == 1 else -1 if old.move == 2 else 0)
        assert 0 <= address < b.Q
        mem = {d: source(address+d) for d in range(-4, 5)}
        p, bit = b.cpu(old, address, mem, beta)
        assert p.mode != b.ERROR, (tick, old)
        if physical:
            for q, s in enumerate(b.SLOTS):
                holder = address-s
                cells = {}
                for x in b.LANES:
                    absolute = holder+x
                    hist = tuple(source(absolute+r) for r in b.SLOTS)
                    heads = tuple(b.pack(old) if absolute+r == old_address else 0 for r in b.SLOTS)
                    cells[x] = b.Cell(addr=absolute % b.Q, age=112*b.Q+tick,
                                     history1=hist, history2=hist, history3=hist,
                                     head=heads, next=tuple(writes.get(absolute+r, 0) for r in b.SLOTS))
                output = b.total_rule(cells, beta)
                assert output.head[q] == b.pack(p)
                assert output.next[q] == (writes.get(address, 0) if bit is None else bit)
                physical_checks += 1
        if bit is not None:
            assert address not in writes
            writes[address] = bit
        history.append((tick, address, b.pack(p), bit))
        if p.mode == b.HALT:
            return {'updates': tick, 'final_packet': asdict(p), 'writes': writes,
                    'trace_sha256': sha256(json.dumps(history).encode()).hexdigest(),
                    'physical_checks': physical_checks}
    raise AssertionError('diagnostic failed to halt')


def span_beta(length, target, lane, kind):
    rows = (('LIT', (lane & 15,)), ('SETFN', ()), ('LIT', (target,)),
            ('SWAP', ()), ('LIT', (length,)), ('READ', (3, 16, kind)), ('HLT', ()))
    bits = tuple(z for op, args in rows for z in b.encode(op, *args))
    return bits + (0,) * (b.Q-len(bits))


def run():
    t0 = time.monotonic()
    indexed = 0
    work = int.from_bytes(sha256(b'GBC2-indexed-work').digest()*2, 'little') & b.WORK_MASK
    for index in range(32):
        get = b.encode('WGET', index)
        set_ = b.encode('WSET', index)
        get += (0,) * (b.Q-len(get))
        set_ += (0,) * (b.Q-len(set_))
        for pointer in (0, 1, 20, 399, 400, 406, 407, 427, b.MASK):
            offset = pointer if index == 31 else 20*index
            old = b.Packet(p=1, a=pointer, b=pointer, work=work)
            got, bit = b.cpu(old, 200, {d: 0 for d in range(-4, 5)}, get)
            assert got.a == (0 if offset >= 407 else (work >> offset) & b.MASK)
            for value in (0, 1, 1 << 19, b.MASK):
                p, bit = b.cpu(replace(old, a=value), 200, {d: 0 for d in range(-4, 5)}, set_)
                mask = b.MASK << offset
                expected = work if offset >= 407 else ((work & ~mask) | (value << offset)) & b.WORK_MASK
                assert p.work == expected and p.a == value and p.b == pointer
                indexed += 1
    # Every possible pending SPAN kind/lane and every length boundary,
    # including adversarial old accumulator bits and invalid indices.
    beta = (0,) * b.Q
    guards = 0
    for kind, lane, length in product(range(4), range(32), range(22)):
        for index in {0, max(0, length-1), length, b.Q-1}:
            limit = 4 if kind == 1 else 6 if kind == 2 else 8
            valid = -limit <= b.signed(lane, 5) <= limit and 1 <= length <= 20 and index < length
            p = b.Packet(p=1, mode=b.SPAN, start=200, a=length, b=b.MASK,
                         index=index, lane=lane, kind=kind)
            out, write = b.cpu(p, 200, {d: source(200+d) for d in range(-4, 5)}, beta)
            assert (out.mode == b.ERROR) == (not valid)
            assert write is None
            guards += 1
    reads = []
    for kind in range(4):
        limit = 4 if kind == 1 else 6 if kind == 2 else 7
        for lane, length in product((-limit, 0, limit), (1, 7, 20)):
            target = b.PRIMARY_START+120+kind
            code = span_beta(length, target, lane, kind)
            result = execute(code, physical=kind == 1 and lane == 0 and length == 20)
            stride = 1 if kind == 0 else 5
            expected = 0
            for k in range(length):
                address = target+k*stride
                mem = {d: source(address+d) for d in range(-4, 5)}
                bit = b.read_vote(mem, lane, address % 5, kind == 1) if kind in (1, 2) else (mem[0] >> (8+lane)) & 1
                expected |= bit << k
            assert result['final_packet']['a'] == expected
            assert result['final_packet']['b'] == expected and not result['writes']
            reads.append({'kind': kind, 'lane': lane, 'length': length, **result})
    writes = []
    for length in (1, 7, 20):
        for value in (0, 1, 0x55555, b.MASK):
            target = b.PRIMARY_START+700
            code, listing, bits = emit_helper_test(value, target, length)
            result = execute(code)
            assert result['writes'] == {target+5*k: value >> k & 1 for k in range(length)}
            writes.append({'length': length, 'value': value, 'programme_bits': bits,
                           'instructions': len(listing), **result})
    fills = []
    for wide, value, length in product(range(2), range(2), (1, 7, 20)):
        target = b.PRIMARY_START+140
        rows = (('LIT', (target,)), ('SWAP', ()), ('LIT', (length,)),
                ('FILL', (wide, value)), ('HLT', ()))
        bits = tuple(z for op, args in rows for z in b.encode(op, *args))
        code = bits+(0,)*(b.Q-len(bits))
        result = execute(code)
        assert result['writes'] == {target+(5 if wide else 1)*k: value for k in range(length)}
        fills.append({'wide': wide, 'value': value, 'length': length, **result})
    return {'passed': True, 'scope': 'generic indexed-Work/pending-span/fill/helper execution only; full emitter unfinished',
            'Q': b.Q, 'U': b.U, 'lambda': b.LAMBDA, 'c': b.ERROR_SEPARATION,
            'radius': 8, 'K': b.FRAME_BITS, 'Head_bits': b.HEAD_BITS,
            'indexed_work_checks': indexed,
            'pending_span_guards': guards, 'span_reads': reads,
            'physical_span_holder_checks': sum(r['physical_checks'] for r in reads),
            'word_writes': writes, 'fills': fills, 'full_own_emitter': False,
            'universal_own_beta_fit': False, 'universal_deadline': False,
            'gray_refutation': False, 'noise_theorem': False, 'shorter_U': False,
            'elapsed_seconds': time.monotonic()-t0}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    result = run()
    args.output.write_text(json.dumps(result, indent=2)+'\n')
    print(json.dumps({k: v for k, v in result.items()
                      if k not in ('span_reads', 'word_writes', 'fills')}, indent=2))
