"""Run with KiCad bundled Python after generate_placement.py and pcb drc."""
from pathlib import Path
import json,xml.etree.ElementTree as ET
import pcbnew as p
r=Path(__file__).resolve().parents[2]
b=p.LoadBoard(str(r/'hardware/gba_dumper.kicad_pcb'))
fp={f.GetReference():f for f in b.GetFootprints()}
x=ET.parse(r/'hardware/verification/gba_dumper.xml')
comps={c.attrib['ref']:c for c in x.findall('.//components/comp')}
assert set(fp)==set(comps)|{'H1','H2','H3','H4'}
assert b.GetCopperLayerCount()==4
routed=bool(len(b.GetTracks()))
if not routed: assert all(z.GetIsRuleArea() for z in b.Zones())
bb=b.GetBoardEdgesBoundingBox()
assert abs(p.ToMM(bb.GetWidth())-100)<.2 and abs(p.ToMM(bb.GetHeight())-100)<.2
for ref,c in comps.items():
 assert fp[ref].GetFPID().GetLibItemName()==c.findtext('footprint').split(':')[1]
 assert c.findtext('tstamps') in fp[ref].GetPath().AsString()
expected={(i.attrib['ref'],i.attrib['pin']):n.attrib['name'] for n in x.findall('.//nets/net') for i in n.findall('node')}
for ref,f in fp.items():
 for pad in f.Pads():
  key=(ref,pad.GetNumber())
  if key in expected: assert pad.GetNetname()==expected[key],key
  else: assert not pad.GetNetname(),key
  if pad.GetAttribute()!=p.PAD_ATTRIB_NPTH:
   bounds=pad.GetBoundingBox()
   for cx,cy in [(5,5),(95,5),(5,95),(95,95)]:
    assert not (p.ToMM(bounds.GetLeft())<cx+4 and p.ToMM(bounds.GetRight())>cx-4 and p.ToMM(bounds.GetTop())<cy+4 and p.ToMM(bounds.GetBottom())>cy-4),(key,cx,cy)
assert abs(p.ToMM(fp['J2'].GetPosition().x-fp['J1'].GetPosition().x)-27.94)<1e-6
assert fp['J1'].GetPosition().y==fp['J2'].GetPosition().y
for ref in ['J1','J2']:
 assert fp[ref].GetOrientationDegrees()==0
 assert abs(p.ToMM(fp[ref].FindPadByNumber('22').GetPosition().y-fp[ref].FindPadByNumber('1').GetPosition().y)-53.34)<1e-6
for ref in ['H1','H2','H3','H4']:
 pad=list(fp[ref].Pads())[0]
 assert pad.GetAttribute()==p.PAD_ATTRIB_NPTH and abs(p.ToMM(pad.GetDrillSize().x)-3.2)<1e-6
report=json.loads((r/('hardware/verification/routing_drc.json' if routed else 'hardware/verification/placement_drc.json')).read_text())
assert not report['violations']
assert not report.get('schematic_parity', [])
assert (len(report['unconnected_items'])==0) if routed else (len(report['unconnected_items'])>0)
print(f'PASS: 52 schematic footprints + 4 NPTH holes; all pad nets and UUIDs; 100mm outline; 4 layers; 27.94mm socket spacing; screw copper clearance; DRC errors 0 / unrouted {len(report["unconnected_items"])}')
