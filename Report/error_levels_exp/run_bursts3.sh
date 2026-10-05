#!/bin/bash
# third batch: which bursts take two colonies when the values are adversarial (a shifted block)?
S=/tmp/claude-1000/-home-ivrl-Ehsan-Projects-GacsCA/48f9b863-47d2-4e83-bc59-bd69b341430f/scratchpad/errlevels
cd $S/repo
export GACS_BURST=0 PYTHONPATH=.
until [ -f $S/logs/bursts2_done ]; do sleep 5; done
PH=gather2_mid,eval_early,match_pass,final_prog,commit
python3 ../burst_cpu.py --candidate G16 --mode shift --widths 72,150,200 --places reachL,leftm,in10 --phases $PH --workers 4 --tag G16_shift_reach > $S/logs/burst_G16_shift_reach.log 2>&1
python3 ../burst_cpu.py --candidate V_q384_g9 --mode shift --widths 40,72,200 --places reachL,leftm,in10 --phases $PH --workers 4 --tag V_q384_g9_shift_reach > $S/logs/burst_V_q384_g9_shift_reach.log 2>&1
python3 ../burst_cpu.py --candidate G16 --mode random --widths 150,200 --places reachL --phases $PH --workers 4 --tag G16_random_reach > $S/logs/burst_G16_random_reach.log 2>&1
echo done > $S/logs/bursts3_done
