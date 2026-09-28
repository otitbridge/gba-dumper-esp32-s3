import pcbnew as p,json
b=p.LoadBoard('hardware/gba_dumper.kicad_pcb');layers=[p.F_Cu,p.In2_Cu,p.B_Cu];out={'segments':[],'pads':[],'vias':[]}
pt=lambda a:[p.ToMM(a.x),p.ToMM(a.y)]
for t in b.GetTracks():
 if t.GetNetname()=='/MCU_AD6':continue
 if isinstance(t,p.PCB_VIA):out['vias'].append([*pt(t.GetPosition()),p.ToMM(t.GetWidth(p.F_Cu))/2])
 elif t.GetLayer() in layers:out['segments'].append([layers.index(t.GetLayer()),*pt(t.GetStart()),*pt(t.GetEnd()),p.ToMM(t.GetWidth())])
for f in b.GetFootprints():
 for pad in f.Pads():
  if pad.GetNetname()=='/MCU_AD6':continue
  bb=pad.GetBoundingBox();out['pads'].append([[i for i,l in enumerate(layers) if pad.IsOnLayer(l)],*[p.ToMM(v) for v in [bb.GetLeft(),bb.GetTop(),bb.GetRight(),bb.GetBottom()]]])
open('tmp/ad6-reroute/obstacles.json','w').write(json.dumps(out))
