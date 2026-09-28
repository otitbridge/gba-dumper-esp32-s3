"""Finish the verified A16 test-point branch and enforce the minimum trace width."""
import pcbnew as p
from pathlib import Path
r=Path(__file__).resolve().parents[1];path=r/'tmp/routing/routed.kicad_pcb'
b=p.LoadBoard(str(path));V=lambda x,y:p.VECTOR2I(p.FromMM(x),p.FromMM(y));net=b.FindNet('/CART_A16_D0')
for t in b.GetTracks():
 if not isinstance(t,p.PCB_VIA) and t.GetWidth()<p.FromMM(.2):t.SetWidth(p.FromMM(.2))
# Keep component positions intact. Connect TP9 to the seeded backside A16 trunk.
t=p.PCB_TRACK(b);t.SetStart(V(94,38));t.SetEnd(V(96.6,38));t.SetWidth(p.FromMM(.25));t.SetLayer(p.F_Cu);t.SetNet(net);b.Add(t)
v=p.PCB_VIA(b);v.SetPosition(V(96.6,38));v.SetWidth(p.FromMM(.6));v.SetDrill(p.FromMM(.3));v.SetViaType(p.VIATYPE_THROUGH);v.SetLayerPair(p.F_Cu,p.B_Cu);v.SetNet(net);b.Add(v)
p.SaveBoard(str(path),b)
