#!/bin/bash
# run_variant.sh <variant name>  (variants/<name>.py): Blender edit -> Blender build -> fusion (v3.30 attachment) -> photo measure
set -e; cd "$(dirname "$0")"; V=$1; B=${BLENDER:-blender}; P=${PYTHON:-python3}; export PYTHONDONTWRITEBYTECODE=1
mkdir -p var; $B -b base_wig_v330.blend -P edit_locks_v333.py -- --variant variants/$V.py --save var/$V.blend $(cat variants/$V.grid 2>/dev/null) 2>&1 | grep -E "EDIT_OK|Error|error" || true
$B -b -P build_ribbon_v334.py -- --from-blend var/$V.blend $( [ -f variants/$V.rib.py ] && echo --ovr variants/$V.rib.py ) --out var/locks_$V.stl --blend var/${V}_built.blend $(cat variants/$V.args 2>/dev/null) 2>&1 | grep -E "WIG_OK|Error|error" | cut -c1-200
cd ..; FUSE_OVR=$( [ -f blender/variants/$V.fuse.py ] && echo blender/variants/$V.fuse.py ) $P fuse_v333.py blender/var/locks_$V.stl $V 2>&1 | grep -E "^\{|Error" | cut -c1-900
$P measure/measure_v333.py $V out/wig_$V.stl --lit 2>&1 | grep -E "^$V|Error" | cut -c1-200
echo DONE $V
