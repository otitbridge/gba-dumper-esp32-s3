"""Render actual manufacturing exports with Gerbonara 1.6.3."""
from pathlib import Path
from gerbonara import LayerStack, GerberFile
root = Path(__file__).resolve().parents[1] / 'output/fabrication_review'
stack = LayerStack.open(root / 'gerbers')
for side in ('top', 'bottom'):
    (root / f'review/gerber_{side}.svg').write_text(str(stack.to_pretty_svg(side=side)))
silk = GerberFile.open(root / 'gerbers/gba_dumper-F_Silkscreen.gto')
(root / 'review/gerber_silk_qr.svg').write_text(str(silk.to_svg(fg='white', bg='#163b2b', force_bounds=((0,-100),(100,0)))))
