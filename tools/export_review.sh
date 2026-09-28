#!/bin/bash
# Export current WeAct review images, never manufacturing files.
set -eu
cd "$(dirname "$0")/.."
: "${KICAD_CLI:=/Applications/KiCad/KiCad.app/Contents/MacOS/kicad-cli}"
mkdir -p output/schematic output/pcb
"$KICAD_CLI" sch export svg -o output/schematic/ hardware/gba_dumper.kicad_sch
"$KICAD_CLI" pcb export svg --layers F.Cu,F.Silkscreen,Edge.Cuts,Dwgs.User --mode-single --page-size-mode 2 --exclude-drawing-sheet -o output/pcb/placement.svg hardware/gba_dumper.kicad_pcb
# Include daughterboard overhang in the review viewport; PCB outline remains 100 mm.
python3 - <<'PYVIEW'
from pathlib import Path
import re
p=Path('output/pcb/placement.svg');s=p.read_text()
s=re.sub(r'width="[^"]+mm" height="[^"]+mm" viewBox="[^"]+"', 'width="104mm" height="108mm" viewBox="-2 -2 104 108"', s, count=1)
p.write_text(s)
for p in [Path('output/pcb/placement.svg'),Path('output/schematic/gba_dumper.svg')]:
 p.write_text('\n'.join(line.rstrip() for line in p.read_text().splitlines())+'\n')
PYVIEW
# Optional PNG rasterization: Node + sharp (set NODE_PATH to installed modules).
if [ -n "${REVIEW_NODE:-}" ]; then
 "$REVIEW_NODE" - <<'JS'
const sharp = require('sharp');
(async () => {
 await sharp('output/pcb/placement.svg',{density:300}).resize({width:1800}).png().toFile('output/pcb/placement.png');
 await sharp('output/schematic/gba_dumper.svg',{density:144}).resize({width:4200}).png().toFile('output/schematic/gba_dumper.png');
})().catch(e => { console.error(e); process.exit(1); });
JS
fi
