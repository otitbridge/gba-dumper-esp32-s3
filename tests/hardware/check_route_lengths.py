"""Exercise T-junction/via path accounting and check saved comparison provenance."""
from pathlib import Path
import importlib.util,json,hashlib,math
import pcbnew as p
r=Path(__file__).resolve().parents[2]
spec=importlib.util.spec_from_file_location('compare',r/'tools/compare_routing.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
b=p.BOARD();b.SetCopperLayerCount(4);n=p.NETINFO_ITEM(b,'/TEST');b.Add(n)
v=lambda x,y:p.VECTOR2I(p.FromMM(x),p.FromMM(y))
for a,c,layer in [((0,0),(10,0),p.F_Cu),((5,0),(5,5),p.F_Cu),((10,0),(10,10),p.B_Cu)]:
 t=p.PCB_TRACK(b);t.SetStart(v(*a));t.SetEnd(v(*c));t.SetLayer(layer);t.SetWidth(p.FromMM(.25));t.SetNet(n);b.Add(t)
via=p.PCB_VIA(b);via.SetPosition(v(10,0));via.SetViaType(p.VIATYPE_THROUGH);via.SetLayerPair(p.F_Cu,p.B_Cu);via.SetWidth(p.FromMM(.6));via.SetDrill(p.FromMM(.3));via.SetNet(n);b.Add(via)
for ref,x,y,layer in [('S',0,0,p.F_Cu),('E',10,10,p.B_Cu),('T',5,5,p.F_Cu)]:
 f=p.FOOTPRINT(b);f.SetReference(ref);b.Add(f);pad=p.PAD(f);pad.SetNumber('1');pad.SetAttribute(p.PAD_ATTRIB_SMD);pad.SetShape(p.PAD_SHAPE_CIRCLE);pad.SetSize(v(.6,.6));pad.SetPosition(v(x,y));ls=p.LSET();ls.AddLayer(layer);pad.SetLayerSet(ls);pad.SetNet(n);f.Add(pad)
g=m.graph(b,'/TEST')
assert math.isclose(m.shortest(g,('pad','S','1'),('pad','E','1')),20,abs_tol=1e-6)
assert math.isclose(m.shortest(g,('pad','S','1'),('pad','T','1')),10,abs_tol=1e-6)
x=json.loads((r/'hardware/verification/routing_comparison.json').read_text())
for name in ['fnk0099','weact']:
 d=x[name];assert hashlib.sha256((r/d['source']).read_bytes()).hexdigest()==d['sha256']
 assert math.isclose(sum(d['net_track_mm'].values()),d['track_total_mm'],abs_tol=1e-6)
 assert len(d['signal_paths'])==28
assert len(x['signals'])==28
assert math.isclose(x['fnk0099']['track_total_mm'],3017.07,abs_tol=.01)
print('PASS: T-junction split, via transition, stub exclusion, source hashes, 28 signal comparisons, baseline total')
