from functools import lru_cache
import unittest

from gacsca.fixed_rule import retimed_holder_rule as f,retimed_holder_program as p
from gacsca.fixed_rule.wordcode import Program,ADD,EQ,LT,NAND,SHR
from experiments.fixed_rule.certify_retimed_holder_colony_cut import certify
from experiments.fixed_rule.certify_small_holder_clock_mail_factorization import ClockTerms
from experiments.fixed_rule.retimed_holder_symbolic_bits import BitDependencies


class ColonyCut(unittest.TestCase):
    def test_complete_actual_descriptor_all_clock_values(self):
        result=certify()
        self.assertEqual(result['complete_raw_output_words'],22*f.FIELDS)
        self.assertEqual(result['all_legal_ages'],f.U)
        self.assertGreater(result['raw_controller_outputs_checked'],0)
        self.assertEqual(result['Signal_output_bits_checked'],110)

    def test_mail_cannot_be_silently_allowed(self):
        with self.assertRaisesRegex(AssertionError,'crosses colony ownership'):
            certify(allow_mail=True)

    def test_unconfined_controllers_break_the_cut(self):
        with self.assertRaisesRegex(AssertionError,'crosses colony ownership'):
            certify(restrict_controllers=False)

    def test_cross_boundary_Data_mutant_rejected(self):
        original=f.self_description();outputs=list(original.outputs)
        outputs[f.COL['s2_data']]=6*f.FIELDS+f.COL['s2_data']
        mutant=Program(original.inputs,original.operations,tuple(outputs))
        with self.assertRaisesRegex(AssertionError,'crosses colony ownership'):
            certify(description=mutant)

    def test_bit_dependencies_are_conservative_under_carries_and_shifts(self):
        t=ClockTerms(p.base_rom());x=t.variable('x',3);y=t.variable('y',3)
        dep=BitDependencies(t,{x:0,y:1});mask=(1<<64)-1
        expressions=[t.op(ADD,x,y),t.op(ADD,x,x),t.op(SHR,x,y),
                     t.op(SHR,t.op(ADD,x,x),t.const(4)),
                     t.bor(t.op(ADD,x,x),t.const(16)),t.modular_add(x,-1,3),
                     t.op(EQ,x,y),t.op(LT,x,y),t.op(ADD,t.inv(t.op(EQ,x,y)),t.const(1))]
        def evaluate(word,a,b):
            @lru_cache(None)
            def visit(w):
                node=t.nodes[w]
                if node[0]=='const':return node[1]
                if node[0]=='variable':return {'x':a,'y':b}[node[1]]
                if node[0]=='not':return (~visit(node[1]))&mask
                if node[0]=='modadd':return (visit(node[1])+node[2])&((1<<node[3])-1)
                kind,left,right=node[1:];u,v=visit(left),visit(right)
                if kind==ADD:return (u+v)&mask
                if kind==NAND:return (~(u&v))&mask
                if kind==SHR:return u>>v if v<64 else 0
                if kind==EQ:return int(u==v)
                if kind==LT:return int(u<v)
                raise AssertionError(kind)
            return visit(word)
        for word in expressions:
            values=[[evaluate(word,a,b) for b in range(8)] for a in range(8)]
            for bit in (*range(9),63):
                known,owners=dep.bit(word,bit)
                actual=[[value>>bit&1 for value in row] for row in values]
                if known is not None:
                    self.assertTrue(all(value==known for row in actual for value in row))
                if any(len({actual[a][b] for a in range(8)})>1 for b in range(8)):
                    self.assertIn(0,owners)
                if any(len(set(row))>1 for row in actual):self.assertIn(1,owners)


if __name__=='__main__':unittest.main()
