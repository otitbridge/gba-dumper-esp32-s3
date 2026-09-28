from pathlib import Path
import sys,json
sys.path.insert(0,'tools');sys.argv=['reroute_ad6','noop'];import reroute_ad6 as util
import pcbnew as p
w=Path('tmp/ad6-reroute');src=(w/'before.kicad_pcb').read_text()
s=util.without(src,lambda t:util.target(t) and '(net "/MCU_AD6")' in t and '(layer "In2.Cu")' in t)
(w/'manual_base.kicad_pcb').write_text(s)
b=p.LoadBoard(str(w/'manual_base.kicad_pcb'));net=b.FindNet('/MCU_AD6');layers=[p.F_Cu,p.In2_Cu,p.B_Cu];V=lambda x,y:p.VECTOR2I(p.FromMM(x),p.FromMM(y))
path=json.loads((w/'manual_path.json').read_text())
for a,c in zip(path,path[1:]):
 if a[0]!=c[0]:
  assert a[1:]==c[1:];v=p.PCB_VIA(b);v.SetPosition(V(*a[1:]));v.SetViaType(p.VIATYPE_THROUGH);v.SetLayerPair(p.F_Cu,p.B_Cu);v.SetWidth(p.FromMM(.6));v.SetDrill(p.FromMM(.3));v.SetNet(net);b.Add(v)
 else:
  if a[1:]==c[1:]:continue
  t=p.PCB_TRACK(b);t.SetStart(V(*a[1:]));t.SetEnd(V(*c[1:]));t.SetLayer(layers[a[0]]);t.SetWidth(p.FromMM(.25));t.SetNet(net);b.Add(t)
p.SaveBoard(str(w/'candidate.kicad_pcb'),b)
