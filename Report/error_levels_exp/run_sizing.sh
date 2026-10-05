#!/bin/bash
# Sizing runs on the patched private copy (errlevels/repo). 4 worker processes at a time.
S=/tmp/claude-1000/-home-ivrl-Ehsan-Projects-GacsCA/48f9b863-47d2-4e83-bc59-bd69b341430f/scratchpad/errlevels
cd $S/repo
export PYTHONPATH=. GACS_BURST=0
OPTS='[{},{"front_k":100},{"window":300,"front_k":100},{"size_max":300,"low":80},{"front_k":100,"size_max":300,"low":80},{"front_k":40}]'
run () { # tag params
  python3 experiments/size_jobs.py --base G16 --params "$2" --skews 1,2,3 --opts "$OPTS" --workers 4 --tag "$1" > $S/logs/size_$1.log 2>&1
}
run q384_g12 '{"margin":58,"q":384}'
run q448_g12 '{"margin":90,"q":448}'
run q384_g9  '{"margin":58,"q":384,"gathers_q":[0,9,18],"E0q":23}'
run q448_g9  '{"margin":90,"q":448,"gathers_q":[0,9,18],"E0q":23}'
run q384_g10 '{"margin":58,"q":384,"gathers_q":[0,10,20],"E0q":25}'
run q512_g9  '{"gathers_q":[0,9,18],"E0q":23}'
run q320_g12 '{"margin":26,"q":320}'
run q320_g9  '{"margin":26,"q":320,"gathers_q":[0,9,18],"E0q":23}'
echo done > $S/logs/sizing_done
