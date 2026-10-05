#!/bin/bash
# build and test the recommended variant: Q 384, margin 58, gathers 10Q apart
S=/tmp/claude-1000/-home-ivrl-Ehsan-Projects-GacsCA/48f9b863-47d2-4e83-bc59-bd69b341430f/scratchpad/errlevels
cd $S/repo
export GACS_BURST=0 PYTHONPATH=.
python3 ../build_variant.py V_q384_g10 > $S/logs/build_V_q384_g10.log 2>&1
python3 experiments/run_g_period.py --candidate V_q384_g10 --colonies 12 --periods 3 --seed 0 --threads 4 > $S/logs/period_V_q384_g10_random.log 2>&1
python3 experiments/run_g_period.py --candidate V_q384_g10 --colonies 16 --periods 3 --seed 1 --threads 4 --coherent > $S/logs/period_V_q384_g10_coherent.log 2>&1
for m in random invert; do python3 experiments/level0_one_tick.py --candidate V_q384_g10 --trials 6000 --times 300 --healthy --mode $m --seed 2 --tag V_q384_g10_${m}_6000 >> $S/logs/level0_V_q384_g10.log 2>&1; done
python3 ../burst_cpu.py --candidate V_q384_g10 --widths 72,200 --places edge,edgeR,edgeL,mid --workers 4 > $S/logs/burst_V_q384_g10.log 2>&1
python3 ../burst_cpu.py --candidate V_q384_g10 --mode shift --widths 72,200 --places edge,reachL,in10,mid --workers 4 --tag V_q384_g10_shift > $S/logs/burst_V_q384_g10_shift.log 2>&1
echo done > $S/logs/g10_done
