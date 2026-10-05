import re
f = 'gacsca/rule_g.py'
s = open(f).read()
def rep(a, b, count=1):
    global s
    assert s.count(a) == count, (a, s.count(a))
    s = s.replace(a, b)
rep("SLOTS = (-2, -1, 0, 1, 2)\n",
    "import os\nNC = int(os.environ.get('GACS_COPIES', '5'))      # study patch: 5 adjacent copies or 3 copies at stride 2\n"
    "SLOTS = (-2, -1, 0, 1, 2) if NC == 5 else (-2, 0, 2)\nSI = {s_: i_ for i_, s_ in enumerate(SLOTS)}\n")
rep("sch += [(f, 5 * logical_width(f, p)) for f in fivefold_fields(p)]",
    "sch += [(f, NC * logical_width(f, p)) for f in fivefold_fields(p)]")
rep("return [(s, -(s - 2)) for s in range(5)]", "return [(SI[s], -s) for s in SLOTS]")
rep("def maj5(n, bits):\n    return at_least(n, bits, 3)",
    "def maj5(n, bits):\n    if len(bits) == 3:\n        return maj3(n, *bits)\n    return at_least(n, bits, 3)")
rep("return cell[z][f][(slot + 2) * w + i]", "return cell[z][f][SI[slot] * w + i]")
rep("new = {f: [None] * (5 * logical_width(f, p)) for f in FIVE}", "new = {f: [None] * (NC * logical_width(f, p)) for f in FIVE}")
rep("new[f][(slot + 2) * w + i] = n.AND(keep, vals[f][i])", "new[f][SI[slot] * w + i] = n.AND(keep, vals[f][i])")
rep("new = {f: [None] * (5 * logical_width(f, p)) for f in FRONT}", "new = {f: [None] * (NC * logical_width(f, p)) for f in FRONT}")
rep("new['reg'][(d + 2) * L + i]", "new['reg'][SI[d] * L + i]")
rep("new['pend'][d + 2] = pend", "new['pend'][SI[d]] = pend", 3)
rep("new['pval'][d + 2] = n.AND(pend, alu)", "new['pval'][SI[d]] = n.AND(pend, alu)", 3)
rep("new['pkind'][(d + 2) * p.PK + j] = pkind[j]", "new['pkind'][SI[d] * p.PK + j] = pkind[j]", 3)
open(f, 'w').write(s)
print('patched')
