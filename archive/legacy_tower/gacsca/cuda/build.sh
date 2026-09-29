#!/bin/bash
set -euo pipefail
cd "$(dirname "$0")"
gacs_cuda_root="${CUDA_HOME:-/usr/local/cuda}"
gacs_build_dir="$(mktemp -d "${TMPDIR:-/tmp}/gacsca-cuda.XXXXXX")"
cmake -S . -B "$gacs_build_dir" -DCMAKE_BUILD_TYPE=Release \
    -DCMAKE_CUDA_COMPILER="$gacs_cuda_root/bin/nvcc"
cmake --build "$gacs_build_dir" -j 8
gacs_ext_suffix="$(python -c 'import sysconfig; print(sysconfig.get_config_var("EXT_SUFFIX"))')"
cp "$gacs_build_dir/gacs_cuda$gacs_ext_suffix" "gacs_cuda.new$gacs_ext_suffix"
mv "gacs_cuda.new$gacs_ext_suffix" "gacs_cuda$gacs_ext_suffix"
printf 'Built CUDA module; build files retained in %s\n' "$gacs_build_dir"
