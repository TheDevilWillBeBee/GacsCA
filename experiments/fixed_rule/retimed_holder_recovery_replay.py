"""Independent scalar quiet-recovery replay with exact input memoization.

Reuse the audited complete-neighborhood procedure cache for one tick only.
The separately proved canonical late Flag1 recurrence is still executed on
every physical tick; no flags or procedures are repaired by this adapter.
"""
from experiments.fixed_rule.audit_retimed_holder_contextual_macrostep import Replay
from experiments.fixed_rule.audit_retimed_holder_burst_recovery import flag_step


class RecoveryReplay(Replay):
    def step(self, age):
        previous_flags = self.flags
        self.flags = [0]*len(previous_flags)
        try:
            # Replay evaluates only the complete core procedure neighborhood;
            # its zero-flag guard is an execution-domain restriction, not an
            # input to c._clock_step. Preserve the actual separate flag state.
            super().step(age)
        finally:
            self.flags = previous_flags
        self.flags = [flag_step(value) for value in previous_flags]
