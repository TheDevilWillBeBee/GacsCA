"""Hash-consed Boolean netlists with word helpers.

Node 0 is constant 0 and node 1 is constant 1. Inputs follow, then gates.
Gates are two-input AND, OR or XOR; NOT x is XOR(x, 1). Local algebraic
simplification and hash-consing keep the netlist canonical enough that the
gate count is a meaningful size measure, but no rewrite changes a function.
"""
import hashlib
import numpy as np

AND, OR, XOR = 0, 1, 2
OPNAMES = ('AND', 'OR', 'XOR')


class Net:
    def __init__(self):
        self.kind = ['C0', 'C1']          # 'C0','C1','IN','G'
        self.gate = [None, None]          # (op, a, b) for gates
        self.input_names = []             # names in input order
        self.input_node = {}              # name -> node
        self.table = {}                   # (op, a, b) -> node
        self.outputs = {}                 # name -> node

    # ------------------------------------------------------------ building
    def input(self, name):
        if name in self.input_node:
            return self.input_node[name]
        node = len(self.kind)
        self.kind.append('IN')
        self.gate.append(None)
        self.input_names.append(name)
        self.input_node[name] = node
        return node

    def _negated(self, x):
        g = self.gate[x]
        if g is not None and g[0] == XOR and g[1] == 1:
            return g[2]
        return None

    def op(self, op, a, b):
        if a > b:
            a, b = b, a
        if op == AND:
            if a == 0: return 0
            if a == 1: return b
            if a == b: return a
            if self._negated(a) == b or self._negated(b) == a: return 0
        elif op == OR:
            if a == 0: return b
            if a == 1: return 1
            if a == b: return a
            if self._negated(a) == b or self._negated(b) == a: return 1
        elif op == XOR:
            if a == 0: return b
            if a == b: return 0
            if a == 1:
                inner = self._negated(b)
                if inner is not None: return inner
            if self._negated(a) == b or self._negated(b) == a: return 1
        else:
            raise ValueError(op)
        key = (op, a, b)
        node = self.table.get(key)
        if node is None:
            node = len(self.kind)
            self.kind.append('G')
            self.gate.append(key)
            self.table[key] = node
        return node

    def AND(self, a, b): return self.op(AND, a, b)
    def OR(self, a, b): return self.op(OR, a, b)
    def XOR(self, a, b): return self.op(XOR, a, b)
    def NOT(self, a): return self.op(XOR, a, 1)
    def ANDN(self, a, b): return self.AND(a, self.NOT(b))

    def MUX(self, s, a, b):
        """s ? a : b."""
        if a == b: return a
        if s == 1: return a
        if s == 0: return b
        return self.XOR(b, self.AND(s, self.XOR(a, b)))

    def all(self, bits):
        bits = list(bits)
        if not bits: return 1
        while len(bits) > 1:
            nxt = [self.AND(bits[i], bits[i+1]) for i in range(0, len(bits) - 1, 2)]
            if len(bits) % 2: nxt.append(bits[-1])
            bits = nxt
        return bits[0]

    def any(self, bits):
        bits = list(bits)
        if not bits: return 0
        while len(bits) > 1:
            nxt = [self.OR(bits[i], bits[i+1]) for i in range(0, len(bits) - 1, 2)]
            if len(bits) % 2: nxt.append(bits[-1])
            bits = nxt
        return bits[0]

    def set_output(self, name, node):
        if name in self.outputs:
            raise ValueError(f'duplicate output {name}')
        self.outputs[name] = node

    # ------------------------------------------------------------ analysis
    def live_nodes(self):
        """Nodes reachable from outputs (topologically ordered)."""
        seen = bytearray(len(self.kind))
        stack = list(self.outputs.values())
        while stack:
            n = stack.pop()
            if seen[n]: continue
            seen[n] = 1
            g = self.gate[n]
            if g is not None:
                stack.append(g[1]); stack.append(g[2])
        return [n for n in range(len(self.kind)) if seen[n]]

    def gate_count(self):
        return sum(1 for n in self.live_nodes() if self.kind[n] == 'G')

    def used_inputs(self):
        return [self.input_names[i] for i, n in enumerate(self.input_node[x] for x in self.input_names)
                if n in set(self.live_nodes())]

    def depth(self):
        d = [0] * len(self.kind)
        for n in self.live_nodes():
            g = self.gate[n]
            if g is not None:
                d[n] = 1 + max(d[g[1]], d[g[2]])
        return max((d[o] for o in self.outputs.values()), default=0)

    def compact(self):
        """Return (inputs, gates, outputs) over live nodes with dense ids.

        Dense ids: 0, 1 constants; then all declared inputs (in declaration
        order, used or not); then live gates in topological order.
        """
        live = self.live_nodes()
        remap = {0: 0, 1: 1}
        for i, name in enumerate(self.input_names):
            remap[self.input_node[name]] = 2 + i
        gates = []
        nxt = 2 + len(self.input_names)
        for n in live:
            if self.kind[n] == 'G':
                op, a, b = self.gate[n]
                remap[n] = nxt
                nxt += 1
                gates.append((op, remap[a], remap[b]))
        outputs = {name: remap[node] for name, node in self.outputs.items()}
        return list(self.input_names), gates, outputs

    def digest(self):
        inputs, gates, outputs = self.compact()
        h = hashlib.sha256()
        h.update(repr(inputs).encode())
        h.update(np.asarray(gates, dtype=np.int64).tobytes())
        h.update(repr(sorted(outputs.items())).encode())
        return h.hexdigest()


# ---------------------------------------------------------------- evaluation
class Compiled:
    """Dense straight-line form used by the NumPy and C evaluators."""

    def __init__(self, net):
        self.inputs, self.gates, self.outputs = net.compact()
        self.index = {name: 2 + i for i, name in enumerate(self.inputs)}
        self.n_nodes = 2 + len(self.inputs) + len(self.gates)
        self.digest = net.digest()

    def evaluate(self, values, dtype=np.uint64):
        """values: dict input-name -> array (bit-packed words or 0/1 ints).

        Missing inputs are an error. Returns dict output-name -> array.
        """
        first = next(iter(values.values()))
        shape = np.shape(first)
        if dtype is bool or dtype is np.bool_:
            ones = np.ones(shape, dtype=bool)
        else:
            ones = np.full(shape, np.iinfo(dtype).max, dtype=dtype)
        zeros = np.zeros(shape, dtype=dtype)
        node = [zeros, ones]
        for name in self.inputs:
            if name not in values:
                raise KeyError(f'missing input {name}')
            node.append(np.asarray(values[name], dtype=dtype))
        for op, a, b in self.gates:
            x, y = node[a], node[b]
            node.append(x & y if op == AND else (x | y if op == OR else x ^ y))
        return {name: node[i] for name, i in self.outputs.items()}

    def evaluate_scalar(self, values):
        """Plain Python evaluation on 0/1 ints (independent of NumPy)."""
        node = [0, 1]
        for name in self.inputs:
            node.append(int(values[name]) & 1)
        for op, a, b in self.gates:
            x, y = node[a], node[b]
            node.append(x & y if op == AND else (x | y if op == OR else x ^ y))
        return {name: node[i] for name, i in self.outputs.items()}


# ---------------------------------------------------------------- word helpers
def const_word(value, width):
    return [(value >> i) & 1 for i in range(width)]


def w_eq(n, a, b):
    assert len(a) == len(b)
    return n.NOT(n.any(n.XOR(x, y) for x, y in zip(a, b)))


def w_eq_const(n, a, value):
    bits = []
    for i, x in enumerate(a):
        bits.append(x if (value >> i) & 1 else n.NOT(x))
    if value >> len(a):
        return 0
    return n.all(bits)


def w_mux(n, s, a, b):
    return [n.MUX(s, x, y) for x, y in zip(a, b)]


def w_add_const(n, a, value):
    """(a + value) mod 2^len(a)."""
    out, carry = [], 0
    for i, x in enumerate(a):
        c = (value >> i) & 1
        if c:
            out.append(n.NOT(n.XOR(x, carry)))
            carry = n.OR(x, carry)
        else:
            out.append(n.XOR(x, carry))
            carry = n.AND(x, carry)
    return out


def w_add_const_mod(n, a, value, modulus):
    """(a + value) mod `modulus` for a in [0, modulus), value in [0, modulus).
    For a power-of-two modulus equal to 2^len(a) this is exactly w_add_const
    (same gates). Inputs a >= modulus give a deterministic but unspecified
    result."""
    width = len(a)
    value %= modulus
    if modulus == (1 << width):
        return w_add_const(n, a, value)
    s = w_add_const(n, list(a) + [0], value)                    # width+1 bits, no overflow
    ge = n.NOT(w_ult_const(n, s, modulus))
    wrapped = w_add_const(n, s, (1 << (width + 1)) - modulus)  # s - modulus
    return w_mux(n, ge, wrapped, s)[:width]


def w_sub_from_const(n, value, a):
    """(value - a) mod 2^len(a)."""
    return w_add_const(n, [n.NOT(x) for x in a], (value + 1) % (1 << len(a)))


def mixed_age_increment(n, age, k, Q, nb):
    """Age stored as (position in the low k bits, block in the high bits),
    position in [0, Q), block in [0, nb): the packed value of tick t is
    (t // Q) << k | (t % Q). Returns the packed value of t + 1 mod nb*Q."""
    pos, blk = list(age[:k]), list(age[k:])
    last = w_eq_const(n, pos, Q - 1)
    pos_n = w_mux(n, last, [0] * k, w_add_const(n, pos, 1))
    blk_inc = w_mux(n, w_eq_const(n, blk, nb - 1), [0] * len(blk), w_add_const(n, blk, 1))
    blk_n = w_mux(n, last, blk_inc, blk)
    return pos_n + blk_n


def w_add(n, a, b):
    out, carry = [], 0
    for x, y in zip(a, b):
        t = n.XOR(x, y)
        out.append(n.XOR(t, carry))
        carry = n.OR(n.AND(x, y), n.AND(t, carry))
    return out


def w_ult_const(n, a, value):
    """a < value (unsigned), value may exceed the width."""
    width = len(a)
    if value >= (1 << width):
        return 1
    if value <= 0:
        return 0
    # a < value  <=>  not (a >= value); compute a >= value by MSB-first scan
    lt = 0
    eq = 1
    for i in reversed(range(width)):
        x = a[i]
        c = (value >> i) & 1
        if c:
            lt = n.OR(lt, n.AND(eq, n.NOT(x)))
            eq = n.AND(eq, x)
        else:
            eq = n.AND(eq, n.NOT(x))
    return lt


def w_in_range(n, a, lo, hi):
    """lo <= a < hi."""
    return n.AND(n.NOT(w_ult_const(n, a, lo)), w_ult_const(n, a, hi))


def popcount(n, bits):
    """Binary popcount (LSB first) using full adders."""
    counts = [[b] for b in bits]  # each entry is a word
    words = [c for c in counts]
    while len(words) > 1:
        nxt = []
        for i in range(0, len(words) - 1, 2):
            a, b = words[i], words[i+1]
            width = max(len(a), len(b)) + 1
            a = a + [0] * (width - len(a))
            b = b + [0] * (width - len(b))
            nxt.append(w_add(n, a, b))
        if len(words) % 2:
            nxt.append(words[-1])
        words = nxt
    return words[0] if words else [0]


def at_least(n, bits, threshold):
    """Threshold function by the pruned dynamic program c[j] = (>= j so far)."""
    bits = list(bits)
    total = len(bits)
    if threshold <= 0:
        return 1
    if threshold > total:
        return 0
    if threshold == 1:
        return n.any(bits)
    if threshold == total:
        return n.all(bits)
    c = {0: 1}
    for i, x in enumerate(bits, 1):
        lo = max(0, threshold - (total - i))
        hi = min(i, threshold)
        nxt = {}
        for j in range(lo, hi + 1):
            keep = c.get(j, 0) if j <= i - 1 else 0
            if j == 0:
                nxt[j] = 1
                continue
            add = n.AND(x, c.get(j - 1, 0)) if j - 1 <= i - 1 else 0
            nxt[j] = n.OR(keep, add)
        c = nxt
    return c[threshold]


def majority_word(n, words, default):
    """Gray/candidate-B majority: the value occurring >= 3 times among five.

    Returns (value, exists); value is `default` when no such value exists.
    """
    assert len(words) == 5
    # When some value occurs >= 3 times it equals the bitwise majority.
    bitwise = [at_least(n, [w[i] for w in words], 3) for i in range(len(default))]
    exists = at_least(n, [w_eq(n, w, bitwise) for w in words], 3)
    return w_mux(n, exists, bitwise, default), exists
