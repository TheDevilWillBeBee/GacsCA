# Discrepancies and underspecified rules (running log)

| # | Topic | Gray | Masumori | Resolution here |
|---|---|---|---|---|
| D1 | Address adjustment in votes (Gray p.22) | add (x-y) mod Q | "cannot be used, x,y unknown"; use (addr_y - i_y) | Identical: y = x+i so x-y = -i. Gray's rule is fine; Masumori's rewrite is the same rule. |
| D2 | Flag2 cond (iii) uses *computed* Age | computed Age | replaced by current Age ("circular") | Not circular: (iii) applies only when C(x) does not exist, and then the Age vote is taken in L(x) regardless of Flag2. Implemented Gray's version (`Variant.gray`), Masumori's as `Variant.masumori`. |
| D3 | Flag1 cond (ii) | >=3 sites in R(x) & C(x) | >=3 sites in R(x) | Both implemented; Gray default. Masumori variant is measurably less robust (threshold 0.38 vs 0.40, see level0 report). |
| D4 | Workspace.Flag1 cond (iii): SimBit at site (x-A(x))+(Q-3) "inaccessible" | as stated | claims unreachable (example with A(x)=2) | Masumori's example violates cond (i) (A(x) in [Q-5,Q-1]); under (i) the site is within +-2 of x, inside the range-5 neighbourhood. Gray's rule is implementable as written. Same for Workspace.Flag2 (site x-A(x)+3, offset in [-1,3]). |
| D5 | Majority "clear majority" | keep current value if no clear majority | unknown | >=3 of 5 (strict); `plurality` variant available. |
| D6 | Age increment when vote has no majority | ambiguous | always increments | always increment (a cell always advances its clock). |
| D7 | Noise "error rate" | per-cell per-step replacement prob. eps | "cells destroyed according to error rate"; recovery reported up to 0.5-0.6 | Standard model implemented; measured threshold ~0.40 (Q=271). Masumori's Fig 7B (dense hits, instant recovery) is inconsistent with per-cell eps=0.5 under this rule; their exact protocol is unknown. |
| D8 | Flag2 rule (a): "no site in L(x)&C(x) has Flag2 = 0" | as stated | copied | Implemented literally. Note: a partial Flag2 block inside a healthy colony (Flag1=0) cannot erode from its left end (cell a keeps 1 because cell a-1 is 0); it clears only when the whole colony is covered or when Flag1=1 (rule (b)). Flagged for study in the trickle-down experiments. |
