"""Finite NAND descriptions. Compilation is initialization, never physical evolution."""
from dataclasses import dataclass
import hashlib
import json


@dataclass(frozen=True)
class Circuit:
    inputs: int
    gates: tuple
    outputs: tuple

    @property
    def wires(self):
        return 2 + self.inputs + len(self.gates)

    def digest(self):
        return hashlib.sha256(json.dumps((self.inputs, self.gates, self.outputs),
                                        separators=(',', ':')).encode()).hexdigest()

    def evaluate(self, bits):
        """Diagnostic oracle only. Physical execution lives in machine.py/native.c."""
        if len(bits) != self.inputs or any(b not in (0, 1) for b in bits):
            raise ValueError('incorrect binary input')
        values = [0, 1, *bits]
        for a, b in self.gates:
            values.append(1 - (values[a] & values[b]))
        return tuple(values[i] for i in self.outputs)


class Builder:
    def __init__(self, inputs):
        self.inputs = inputs
        self.gates = []
        self.memo = {}

    def nand(self, a, b):
        if a == 0 or b == 0:
            return 1
        if a == b == 1:
            return 0
        key = tuple(sorted((a, b)))
        if key not in self.memo:
            self.memo[key] = 2 + self.inputs + len(self.gates)
            self.gates.append(key)
        return self.memo[key]

    def inv(self, a):
        return self.nand(a, a)

    def both(self, a, b):
        return self.inv(self.nand(a, b))

    def either(self, a, b):
        return self.nand(self.inv(a), self.inv(b))

    def xor(self, a, b):
        x = self.nand(a, b)
        return self.nand(self.nand(a, x), self.nand(b, x))

    def mux(self, condition, yes, no):
        if yes == no:
            return yes
        return self.nand(self.nand(condition, yes), self.nand(self.inv(condition), no))

    def select(self, condition, yes, no):
        return tuple(self.mux(condition, a, b) for a, b in zip(yes, no))

    def const(self, value, width):
        return tuple((value >> i) & 1 for i in range(width))

    def eq(self, a, b):
        out = 1
        for x, y in zip(a, b):
            out = self.both(out, self.inv(self.xor(x, y)))
        return out

    def increment(self, a):
        carry, out = 1, []
        for x in a:
            out.append(self.xor(x, carry))
            carry = self.both(x, carry)
        return tuple(out)

    def finish(self, outputs):
        return Circuit(self.inputs, tuple(self.gates), tuple(outputs))
