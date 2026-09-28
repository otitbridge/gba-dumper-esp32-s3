#!/bin/bash
# Review only: no Gerber, drill or placement output.
set -eu
cd "$(dirname "$0")/.."
: "${KICAD_CLI:=/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli}"
mkdir -p output/pcb/final_review
"$KICAD_CLI" pcb export svg --layers F.Silkscreen,F.Mask,Edge.Cuts --mode-single --page-size-mode 2 --exclude-drawing-sheet -o output/pcb/final_review/front_silk.svg hardware/gba_dumper.kicad_pcb
python3 - <<'PY'
from pathlib import Path
p=Path('output/pcb/final_review/front_silk.svg')
s=p.read_text().replace('#F2EDA1','#14213D').replace('#D864FF','#9CA3AF').replace('#D0D2CD','#475569')
p.write_text('\n'.join(l.rstrip() for l in s.splitlines())+'\n')
PY
if [ -n "${REVIEW_NODE:-}" ]; then
 "$REVIEW_NODE" - <<'JS'
require('sharp')('output/pcb/final_review/front_silk.svg').resize(2000,2000).flatten({background:'white'}).png().toFile('output/pcb/final_review/front_silk.png');
JS
fi
