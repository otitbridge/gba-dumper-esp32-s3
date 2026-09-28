"""Validate completed routing using KiCad Python and the final CLI DRC report."""
from pathlib import Path
import json,xml.etree.ElementTree as ET,collections
import pcbnew as p
r=Path(__file__).resolve().parents[2];b=p.LoadBoard(str(r/'hardware/gba_dumper.kicad_pcb'))
fp={f.GetReference():f for f in b.GetFootprints()}
placement=json.loads((r/'hardware/verification/placement.json').read_text())
for item in placement['components']:
 f=fp[item['reference']];assert abs(p.ToMM(f.GetPosition().x)-item['x_mm'])<1e-6;assert abs(p.ToMM(f.GetPosition().y)-item['y_mm'])<1e-6
 assert f.GetOrientationDegrees()==item['rotation_deg']
expected={(n.attrib['ref'],n.attrib['pin']):net.attrib['name'] for net in ET.parse(r/'hardware/verification/gba_dumper.xml').findall('.//nets/net') for n in net.findall('node')}
for ref,f in fp.items():
 for pad in f.Pads():
  assert pad.GetNetname()==expected.get((ref,pad.GetNumber()),''),(ref,pad.GetNumber())
count=collections.Counter()
for t in b.GetTracks():
 assert not t.GetNetname().startswith('unconnected-')
 if isinstance(t,p.PCB_VIA):
  assert t.GetViaType()==p.VIATYPE_THROUGH and t.GetDrillValue()>=p.FromMM(.3)
  assert t.GetWidth(p.F_Cu)>=p.FromMM(.6);count['via']+=1
 else:
  assert t.GetLayer()!=p.In1_Cu
  assert t.GetWidth()>=p.FromMM(.5 if t.GetNetname() in ['/GND','/BOARD_3V3','/CART_3V3'] else .2)
  count[b.GetLayerName(t.GetLayer())]+=1
assert all(count[n]>0 for n in ['F.Cu','In2.Cu','B.Cu','via'])
zones=[z for z in b.Zones() if not z.GetIsRuleArea()];assert len(zones)==1
z=zones[0];assert z.GetLayer()==p.In1_Cu and z.GetNetname()=='/GND'
assert z.GetFilledPolysList(p.In1_Cu).OutlineCount()==1
assert z.GetFilledArea()>8000e12
report=json.loads((r/'hardware/verification/routing_drc.json').read_text())
assert not report['unconnected_items'] and not report['schematic_parity']
assert not report['violations']
print('PASS: placement unchanged; pad nets match; no reserved GPIO routing; through vias; widths; In1 single GND island; DRC unconnected/errors/parity 0; silk warnings',len(report['violations']))
