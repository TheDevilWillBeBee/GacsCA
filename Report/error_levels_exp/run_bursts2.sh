#!/bin/bash
# second batch of CPU burst experiments (4 workers); waits for the first variant run to finish
S=/tmp/claude-1000/-home-ivrl-Ehsan-Projects-GacsCA/48f9b863-47d2-4e83-bc59-bd69b341430f/scratchpad/errlevels
cd $S/repo
export GACS_BURST=0 PYTHONPATH=.
until [ -f $S/results/burst_V_q384_g9.json ]; do sleep 5; done
python3 ../burst_cpu.py --candidate V_q384_g9 --mode shift --widths 72,200 --places edge,edgeR,edgeL,mid --workers 4 --tag V_q384_g9_shift > $S/logs/burst_V_q384_g9_shift.log 2>&1
python3 ../burst_cpu.py --candidate G16 --mode shift --widths 72,200 --places edge,mid --workers 4 --tag G16_shift > $S/logs/burst_G16_shift.log 2>&1
python3 ../burst_cpu.py --candidate V_q384_g12 --widths 72,200 --places edge,edgeR,edgeL,mid --workers 4 > $S/logs/burst_V_q384_g12.log 2>&1
python3 ../burst_cpu.py --candidate V_q384_g9 --mode copy --widths 72,200 --places edge,edgeR,edgeL,mid --workers 4 --tag V_q384_g9_copy > $S/logs/burst_V_q384_g9_copy.log 2>&1
python3 experiments/size_jobs.py --base G16 --params '{"margin":58,"q":384,"gathers_q":[0,8,16],"E0q":21}' --skews 1,2,3 --opts '[{},{"front_k":100},{"window":300,"front_k":100},{"size_max":300,"low":80},{"front_k":100,"size_max":300,"low":80},{"front_k":40}]' --workers 4 --tag q384_g8 > $S/logs/size_q384_g8.log 2>&1
echo done > $S/logs/bursts2_done
