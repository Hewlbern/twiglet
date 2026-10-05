#!/bin/bash
# mkvar.sh NEW BASE : copy variant files BASE -> NEW (then append edits)
cd "$(dirname "$0")/variants"; for e in py rib.py fuse.py args grid; do [ -f $2.$e ] && cp $2.$e $1.$e; done; true
