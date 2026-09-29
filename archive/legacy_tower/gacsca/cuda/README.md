# Archived finite-tower CUDA sources

This directory contains the original finite-tower CUDA build files and source.
It is not used by the active fixed-rule implementation, whose CUDA sources
live alongside its Python modules in `gacsca/fixed_rule/`.

The old compiled extension and notebook checkpoint files that were left in
the active-tree `gacsca/cuda/` after archival are preserved locally under
`figs/legacy_tower/build/gacsca_cuda_residual/`. They are generated artifacts
and are ignored by Git. To reproduce the legacy build at its original paths,
use the pre-cleanup Git checkpoint `bae5fd2` in a separate checkout.
