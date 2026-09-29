"""Run the identical complete-checkpoint harness with supported-input events.

Backend injection selects an execution representation once, independently of
encoded depth. The unchanged physical ROM and transition remain the reference.
"""
from unittest.mock import patch
from experiments.fixed_rule import small_holder_register_periods as harness
from gacsca.fixed_rule import small_holder_supported_events as supported

if __name__=='__main__':
    with patch.object(harness,'gpu',supported):
        harness.main()
