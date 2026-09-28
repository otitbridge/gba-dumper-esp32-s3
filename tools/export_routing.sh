#!/bin/bash
# Review images only. Does not alter existing silk or create manufacturing data.
set -eu
cd "$(dirname "$0")/.."
: "${KICAD_CLI:=/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli}"
mkdir -p output/pcb/routed
"$KICAD_CLI" pcb export svg --layers F.Cu,In2.Cu,B.Cu,F.Silkscreen,Edge.Cuts --mode-single --page-size-mode 2 --exclude-drawing-sheet -o output/pcb/routed/routing_overview.svg hardware/gba_dumper.kicad_pcb
"$KICAD_CLI" pcb export svg --layers In1.Cu,Edge.Cuts --mode-single --page-size-mode 2 --exclude-drawing-sheet -o output/pcb/routed/ground_plane.svg hardware/gba_dumper.kicad_pcb
python3 - <<'PY'
from pathlib import Path
for p in Path('output/pcb/routed').glob('*.svg'):
 p.write_text('\n'.join(t.rstrip() for t in p.read_text().splitlines())+'\n')
PY
if [ -n "${REVIEW_NODE:-}" ]; then
 "$REVIEW_NODE" - <<'JS'
const sharp=require('sharp');
(async()=>{for(const n of ['routing_overview','ground_plane']) await sharp(`output/pcb/routed/${n}.svg`,{density:180}).resize({width:2000}).png().toFile(`output/pcb/routed/${n}.png`);})().catch(e=>{console.error(e);process.exit(1);});
JS
fi
