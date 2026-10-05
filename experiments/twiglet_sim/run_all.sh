#!/bin/bash
# usage: run_all.sh <model.xml | file name in models/> <tag> [params.npy] [params_eff.npy]
# Runs run_tests (standing, push, head+arm) + both gait evals on the given model, WITHOUT touching any model or params file.
# The model is passed with TWIGLET_XML; outputs and logs go to out/<tag>/; a summary line is appended to out/sim_summary.txt.
# Defaults: the shipped gaits walk_v3_best.npy / walk_v3_eff_best.npy (= params/walk_v3_best_v334r1.npy / walk_v3_eff_best_v333r1.npy).
set -e
export PYTHONDONTWRITEBYTECODE=1; P=${PYTHON:-python3}; cd "$(dirname "$0")"
[ -n "$1" ] && [ -n "$2" ] || { echo "usage: $0 <model.xml> <tag> [params.npy] [params_eff.npy]"; exit 1; }
export TWIGLET_XML="$1"; export TWIGLET_OUT="out/$2"; mkdir -p "$TWIGLET_OUT"
[ -n "$3" ] && export TWIGLET_PARAMS="$3"; [ -n "$4" ] && export TWIGLET_PARAMS_EFF="$4"
$P run_tests.py v3 > "$TWIGLET_OUT/rt.log" 2>&1
$P walk_eval.py v3 > "$TWIGLET_OUT/we.log" 2>&1
$P walk_eval.py v3 --eff > "$TWIGLET_OUT/wee.log" 2>&1
echo "$2 xml=$1 $(grep '^e ' "$TWIGLET_OUT/rt.log" | cut -c1-60) | $(grep -o 'succ [0-9.]*' "$TWIGLET_OUT/we.log" | tail -1) speed $(grep -o 'speed [0-9.]*' "$TWIGLET_OUT/we.log" | tail -1 | cut -d' ' -f2) | eff $(grep -o 'succ [0-9.]*' "$TWIGLET_OUT/wee.log" | tail -1) speed $(grep -o 'speed [0-9.]*' "$TWIGLET_OUT/wee.log" | tail -1 | cut -d' ' -f2)" | tee -a out/sim_summary.txt
