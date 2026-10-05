#!/bin/bash
# fuse_measure.sh <variant>: fusion + photo measure only (after a manual Blender build of blender/var/locks_<V>.stl)
set -e; cd "$(dirname "$0")/.."; V=$1; P=${PYTHON:-python3}; export PYTHONDONTWRITEBYTECODE=1
FUSE_OVR=$( [ -f blender/variants/$V.fuse.py ] && echo blender/variants/$V.fuse.py ) $P fuse_v333.py blender/var/locks_$V.stl $V 2>&1 | grep -E "Error" | cut -c1-900 || true
$P measure/measure_v333.py $V out/wig_$V.stl --lit 2>&1 | grep -E "^$V|Error" | cut -c1-200
