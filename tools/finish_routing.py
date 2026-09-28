"""Enforce WeAct routing widths without moving components or modifying silk."""
from pathlib import Path
import pcbnew as p
r=Path(__file__).resolve().parents[1];path=r/'tmp/weact-routing/routed.kicad_pcb'
b=p.LoadBoard(str(path));count=0
for t in b.GetTracks():
 if isinstance(t,p.PCB_VIA): continue
 minimum=p.FromMM(.5 if t.GetNetname() in ['/GND','/BOARD_3V3','/CART_3V3'] else .2)
 if t.GetWidth()<minimum:t.SetWidth(minimum);count+=1
p.SaveBoard(str(path),b)
print('Width corrections:',count)
