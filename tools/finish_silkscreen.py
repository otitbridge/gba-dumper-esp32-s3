"""Finalize WeAct silk only; keep component geometry and all copper unchanged."""
from pathlib import Path
import pcbnew as p
r=Path(__file__).resolve().parents[1];path=r/'hardware/gba_dumper.kicad_pcb';
# Remove obsolete silk using parsed blocks before loading the board.
import sys
sys.argv=['silk','noop']
from reroute_ad6 import without
src=path.read_text()
src=without(src,lambda t:any(t.startswith('(gr_text "'+label+'"') for label in ['NATIVE USB: UNUSED','PC: USB-UART','PC : USB-UART','WEACT ESP32S3-A / N16R2','REMOVE USB FIRST','GBA DUMPER / WEACT','V1 PLACEMENT / UNROUTED','JP1 / JP2 / CARTRIDGE','CARTRIDGE']))
path.write_text(src)
b=p.LoadBoard(str(path))
V=lambda x,y:p.VECTOR2I(p.FromMM(x),p.FromMM(y))
for f in b.GetFootprints():
 for field in f.GetFields():
  if field.GetLayer() in [p.F_SilkS,p.B_SilkS] and field.IsVisible():
   field.SetTextSize(V(max(1,p.ToMM(field.GetTextSize().x)),max(1,p.ToMM(field.GetTextSize().y))))
   field.SetTextThickness(p.FromMM(.15))
existing=set()
for d in b.GetDrawings():
 if isinstance(d,p.PCB_TEXT):
  if d.GetText()=='NORMALLY CLOSED':d.SetText('DEFAULT CLOSED')
  positions={'POWER LINK':(21,43),'DEFAULT CLOSED':(21,45.5),'WR ENABLE':(32,65.5),'DEFAULT OPEN':(32,68)}
  if d.GetLayer()==p.F_SilkS and d.GetText() in positions:d.SetPosition(V(*positions[d.GetText()]))
  if d.GetText()=='PC' and d.GetLayer()==p.F_SilkS:d.SetPosition(V(64,98))
  if d.GetLayer() in [p.F_SilkS,p.B_SilkS]:
   d.SetTextSize(V(max(1,p.ToMM(d.GetTextSize().x)),max(1,p.ToMM(d.GetTextSize().y))))
   d.SetTextThickness(p.FromMM(.15));existing.add(d.GetText())
for s,x,y in [('PC',64,98),('CARTRIDGE',21,40.5),('CARTRIDGE',32,63),('GBA DUMPER / WEACT ESP32S3-A',28,96.5),('S3-WROOM-1-N16R2 / REMOVE USB FIRST',28,98.3)]:
 if s in existing:continue
 t=p.PCB_TEXT(b);t.SetText(s);t.SetPosition(V(x,y));t.SetTextSize(V(1,1));t.SetTextThickness(p.FromMM(.15));t.SetLayer(p.F_SilkS);b.Add(t)
p.SaveBoard(str(path),b)
print('WeAct silkscreen updated')
