"""Isolated literal transcription of Gray pp.20--22, Q8192/U1048576.

Unlike the repository's candidate-B module, the Flag2 1->0 clause (a)
requires that no left in-colony cell has Flag2 zero. This preserves the
printed predicate; it is not an endorsement of that predicate's intent.
"""
import hashlib
import inspect
from gacsca import maintenance

Q = 8192
U = 128 * Q
K = 13
M = 20
LAMBDA = 24
ERROR_SEPARATION = 104


def generated_source():
    source = inspect.getsource(maintenance.build)
    old = "n.AND(n.NOT(f1), n.NOT(at_least(n, left_inside, 2)))"
    new = "n.AND(n.NOT(f1), n.all(n.OR(n.NOT(inside[j]), cells[j]['f2']) for j in range(-1, -6, -1)))"
    assert source.count(old) == 1
    return source.replace(old, new)


def build(n, cells, k=K, m=M, **options):
    namespace = dict(maintenance.__dict__)
    source = generated_source()
    exec(compile(source, '<literal Gray Flag2 maintenance>', 'exec'), namespace)
    return namespace['build'](n, cells, k, m, **options)


def source_sha256():
    return hashlib.sha256(generated_source().encode()).hexdigest()


def scalar(cells, Q=Q, U=U):
    """Independent integer reading of the printed rule, not circuit replay."""
    c = cells[0]

    def majority(values, default):
        for value in values:
            if values.count(value) >= 3:
                return value, True
        return default, False

    adjusted = {j: (cells[j]['addr'] - j) % Q for j in range(-5, 6) if j}
    right_addr, exists = majority([adjusted[j] for j in range(1, 6)], c['addr'])
    inside = {j: exists and 0 <= right_addr + j < Q for j in range(-5, 6)}
    right_age, age_exists = majority([cells[j]['age'] for j in range(1, 6)], c['age'])
    left_age, _ = majority([cells[j]['age'] for j in range(-1, -6, -1)], c['age'])
    inconsistency = (not exists or not age_exists or
        sum(inside[j] and cells[j]['addr'] != (right_addr + j) % Q for j in range(-1, -6, -1)) >= 3 or
        sum(inside[j] and cells[j]['age'] != right_age for j in range(-1, -6, -1)) >= 3)
    right_flag1 = sum(inside[j] and cells[j]['f1'] for j in range(1, 6))
    workspace1 = sum(inside[j] and cells[j]['wf1'] for j in range(-5, 6)) >= 3
    flag1 = int(inconsistency or workspace1 or right_flag1 >= 3 or (c['f1'] and right_flag1 >= 2))
    source3 = not exists and (left_age + 1) % 16 == 0
    source4 = sum(inside[j] and cells[j]['wf2'] for j in range(-5, 6)) >= 3
    left = [cells[j]['f2'] for j in range(-1, -6, -1)]
    turn_on = (sum(inside[j] and cells[j]['f2'] for j in range(-1, -6, -1)) >= 4 or
        (flag1 and sum(left) >= 4) or source3 or source4)
    # Gray p.21: no site in L(x) intersect C(x) has Flag2 equal to zero.
    no_left_zero = all(not inside[j] or cells[j]['f2'] for j in range(-1, -6, -1))
    erase = (not flag1 and no_left_zero) or (flag1 and not any(left))
    flag2 = int(source3 or source4 or not erase) if c['f2'] else int(turn_on)
    left_addr, _ = majority([adjusted[j] for j in range(-1, -6, -1)], c['addr'])
    vote_right = exists and (not flag1 or flag2)
    age_now = right_age if vote_right else left_age
    return dict(addr=right_addr if vote_right else left_addr,
                age_now=age_now, age=(age_now + 1) % U, f1=flag1, f2=flag2)
