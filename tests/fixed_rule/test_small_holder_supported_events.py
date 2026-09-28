import unittest
from unittest.mock import patch
import random
import test_small_holder_register_events as base
from gacsca.fixed_rule import small_holder_supported_events as supported
from gacsca.fixed_rule import small_holder_register_events as registers
from gacsca.fixed_rule import small_holder_core as c

# Run the existing event/checkpoint/rejection cases against this new backend.
class SupportedEvents(base.RegisterEvents):
    def setUp(self):
        self.swap=patch.object(base,'fast',supported)
        self.swap.start();self.addCleanup(self.swap.stop)

    def test_input_support_is_complete_and_other_words_irrelevant(self):
        used=set(supported.support());self.assertEqual(len(used),70)
        rng=random.Random(914)
        p=registers.event_program()
        for _ in range(30):
            words=[rng.getrandbits(w) for _ in range(11) for _,w in c.SCHEMA]
            changed=[x if i in used else rng.getrandbits(64) for i,x in enumerate(words)]
            self.assertEqual(p.evaluate(words),p.evaluate(changed))
        self.assertEqual(supported.input_source().count('in['),70)

if __name__=='__main__':unittest.main()
