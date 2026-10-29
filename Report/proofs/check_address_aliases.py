#!/usr/bin/env python3
"""Universal finite checks for phase-correct unused Address normalization.

All raw Address words/constants are checked against actual adder gates.
The 43-tick domination argument is in ROBUSTNESS §7. It is conditional
on correct Address phase, not restoration of a wrong phase or reliability.
"""
from itertools import combinations
import hashlib
import json
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
import numpy as np
from gacsca import candidates
from gacsca.netlist import Net,Compiled,w_add_const_mod


def require(condition,message):
    if not condition:
        raise RuntimeError(message)


def threshold3(words):
    out=0
    for selected in combinations(words,3):
        term=selected[0]
        for word in selected[1:]:
            term &= word
        out |= term
    return out


def main():
    c=candidates.load('G17'); p=c.p
    require(c.digest()=='23a14aab4d3dc4fde5562cf3e26a4536b05456f84e65850fcb3bd95a104d8ceb',
            'candidate changed: re-audit')
    table={}
    raw=np.arange(1<<p.k,dtype=np.int64)
    for value in (*range(1,6),*range(p.Q-5,p.Q)):
        net=Net(); word=[net.input(('a',bit)) for bit in range(p.k)]
        result=w_add_const_mod(net,word,value,p.Q)
        for bit,node in enumerate(result):
            net.set_output(('result',bit),node)
        compiled=Compiled(net)
        actual=compiled.evaluate({name:((raw>>name[1])&1).astype(bool)
                                  for name in compiled.inputs},bool)
        got=sum(actual['result',bit].astype(np.int64)<<bit for bit in range(p.k))
        expected=raw+value
        expected=np.where(expected>=p.Q,expected-p.Q,expected)
        require(np.array_equal(got,expected),('actual adder',value))
        table[value]=got
    adjustments=0
    for address in range(p.Q):
        for offset in (*range(-5,0),*range(1,6)):
            neighbor=(address+offset)%p.Q
            options=[neighbor]
            if neighbor+p.Q < 1<<p.k:
                options.append(neighbor+p.Q)
            for stored in options:
                adjusted=int(table[(-offset)%p.Q][stored])
                require(adjusted%p.Q==address,'phase preservation')
                if offset<0:
                    require(adjusted==address,'left vote canonical')
                else:
                    expect_alias=stored>=p.Q and address+offset<p.Q
                    require(adjusted==address+p.Q*expect_alias,'right alias propagation')
                adjustments+=1
    strip=(1<<128)-1
    steps=[]
    for tick in range(1,44):
        strip=threshold3([strip>>j for j in range(1,6)])
        expected_width=max(0,128-3*tick)
        require(strip==((1<<expected_width)-1),'alias domination strip')
        steps.append(expected_width)
    require(steps[-2]==2 and steps[-1]==0,'43-tick normalization')
    # Full-rule support, safely before any instruction arrival.
    X=np.zeros((c.W,2*p.Q),bool)
    c.set_field(X,'addr',np.tile(np.arange(p.Q),2))
    c.set_field(X,'age',p.age_code(2000))
    alias=np.arange(128)
    word=c.field(X,'addr').copy(); word[alias]+=p.Q
    c.set_field(X,'addr',word)
    C=c.c_backend()
    final=C.unpack(C.run_packed_scalar(C.pack(X),43),X.shape[1])
    require(np.array_equal(c.field(final,'addr'),np.tile(np.arange(p.Q),2)),
            'full-rule support')
    receipt=dict(candidate='G17',**candidates.digests(c),
                 checker_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                 helpers_sha256=hashlib.sha256((ROOT/'gacsca/netlist.py').read_bytes()).hexdigest(),
                 result='proved conditional Address-alias normalization with finite gate checks',
                 actual_adder_inputs_checked=len(raw)*len(table),
                 phase_correct_adjustment_cases=adjustments, maximum_alias_strip_width=128,
                 domination_strip_widths=steps, updates_to_canonical=43,
                 full_rule_C_support=True,
                 hypothesis='initial Address phase is correct everywhere; no Address overwrites for 43 updates',
                 arbitrary_other_fields=True,
                 not_proved=['normalization from arbitrary phases','wrong-phase erosion','all-time reliability'])
    out=ROOT/'figs/robustness/address_alias_certificate.json'
    out.write_text(json.dumps(receipt,indent=2)+'\n')
    print(json.dumps(receipt,indent=2))


if __name__=='__main__':
    main()
