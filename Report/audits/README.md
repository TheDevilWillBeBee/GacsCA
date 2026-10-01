# Independent audits

Two independent agents audited this work. They were given the prompt
[`docs/prompts/DESIGN_OPTIMIZATION_AUDIT_PROMPT.md`](../../docs/prompts/DESIGN_OPTIMIZATION_AUDIT_PROMPT.md):
the first part for the first audit, and the appended section for the second.
Each could edit only its own files.

| | scope | report | response |
|---|---|---|---|
| First audit (2026-09-30) | R1 → G13/G14, at commit `7caedb2` | [AUDIT.md](AUDIT.md) | REPORT §25 |
| Second audit (2026-10-01) | `7caedb2` → `b3cdabe`: §§24–26, G15, the three-level hybrid | [AUDIT2.md](AUDIT2.md) | REPORT §27 |

- **Scripts.** The auditors' scripts are in `scripts/round1/` and
  `scripts/round2/`, and the outputs they cite are in `logs/round1/` and
  `logs/round2/`.
- **Paths.** The audit files are kept as their authors wrote them, so they
  refer to the layout of the time:

  | then | now |
  |---|---|
  | `gacsca/fixed_rule/design_optimization/` | `gacsca/` |
  | `experiments/fixed_rule/design_optimization/` | `experiments/` |
  | `tests/fixed_rule/design_optimization/` | `tests/` |
  | `Report/fixed_rule/design_optimization/` | `Report/` |
  | `figs/fixed_rule/design_optimization/` | `figs/` |
  | `experiments/fixed_rule/design_optimization_audit/` | `Report/audits/scripts/` |
  | `figs/fixed_rule/design_optimization_audit/` | `Report/audits/logs/` |

  Running a script today needs those module paths changed: in Python,
  `gacsca.fixed_rule.design_optimization` becomes `gacsca`.
