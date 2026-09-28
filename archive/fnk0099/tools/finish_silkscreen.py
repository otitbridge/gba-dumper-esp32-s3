"""Finalize silk text without moving components, pads, holes or routing."""
from pathlib import Path
import pcbnew as p
r=Path(__file__).resolve().parents[1];path=r/'hardware/gba_dumper.kicad_pcb';b=p.LoadBoard(str(path))
V=lambda x,y:p.VECTOR2I(p.FromMM(x),p.FromMM(y))
for f in b.GetFootprints():
 for field in f.GetFields():
  if field.GetLayer() in [p.F_SilkS,p.B_SilkS] and field.IsVisible():
   field.SetTextSize(V(max(1,p.ToMM(field.GetTextSize().x)),max(1,p.ToMM(field.GetTextSize().y))))
   field.SetTextThickness(p.FromMM(.15))
 if f.GetReference() in ['H1','H2']:f.Reference().SetPosition(V(p.ToMM(f.GetPosition().x),9.8))
drawings=list(b.GetDrawings())
existing=set()
for d in drawings:
 if isinstance(d,p.PCB_TEXT):
  if d.GetText() in ['V1 PLACEMENT / UNROUTED','REMOVE USB FIRST','DO NOT CONNECT - GBA BUS','Native USB label position TBD']:
   b.Remove(d);continue
  if d.GetLayer()==p.F_SilkS:existing.add(d.GetText())
  if d.GetLayer() in [p.F_SilkS,p.B_SilkS]:
   d.SetTextSize(V(max(1,p.ToMM(d.GetTextSize().x)),max(1,p.ToMM(d.GetTextSize().y))))
   d.SetTextThickness(p.FromMM(.15))
  else:
   replacements={'FNK0099 ENVELOPE TBD':'FNK0099 / USER CONFIRMED','ANTENNA RESERVATION - VERIFY':'ANTENNA KEEP OUT','USB ACCESS / VERIFY BOARD OUTLINE':'USB ACCESS / USER CONFIRMED'}
   if d.GetText() in replacements:d.SetText(replacements[d.GetText()])
def text(s,x,y):
 # Idempotent addition.
 if s in existing:return
 existing.add(s)
 t=p.PCB_TEXT(b);t.SetText(s);t.SetPosition(V(x,y));t.SetTextSize(V(1,1));t.SetTextThickness(p.FromMM(.15));t.SetLayer(p.F_SilkS);b.Add(t)
text('NATIVE USB',25,50)
text('DO NOT CONNECT - GBA BUS',25,52.5)
text('REMOVE USB FIRST',25,55)
text('JP1 / JP2 / CARTRIDGE',25,57.5)
text('DEFAULT OPEN',32,65.5)
text('NORMALLY CLOSED',21,45.5)
text('GBA DIRECT V1',24,98)
p.SaveBoard(str(path),b)
print('Updated silk text; placement and routing unchanged')
