#!/bin/bash
set -e
cd "$(dirname "$0")"
export CUDA_HOME=/usr/local/cuda
export PATH=$CUDA_HOME/bin:$PATH
rm -rf build && mkdir build && cd build
cmake -DCMAKE_BUILD_TYPE=Release -DCMAKE_CUDA_COMPILER=$CUDA_HOME/bin/nvcc .. > cmake.log
make -j8 2>&1 | grep -E "error|warning: .*gacs|Built target" || true
cp gacs_cuda.cpython-3*.so ..
cd .. && rm -rf build
