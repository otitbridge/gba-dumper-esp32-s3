"""Check that manufacturing settings and DRC outcomes remain explicit."""
from pathlib import Path
import json,collections
r=Path(__file__).resolve().parents[2]
p=json.loads((r/'hardware/gba_dumper.kicad_pro').read_text())
ds=p['board']['design_settings']; rules=ds['rules']
for key,want in {'min_clearance':.2,'min_track_width':.2,'min_copper_edge_clearance':.5,'min_hole_clearance':.35,'min_hole_to_hole':.45,'min_through_hole_diameter':.3,'min_via_diameter':.6,'min_via_annular_width':.15,'min_silk_clearance':.15,'min_text_height':1,'min_text_thickness':.15}.items(): assert rules[key]==want,key
assert not ds['drc_exclusions']
assert ds['rule_severities']['unconnected_items']=='error'
classes={c['name']:c for c in p['net_settings']['classes']}
assert classes['POWER_3V3']['track_width']==.8
assert classes['GBA_SIGNAL']['track_width']==.25
patterns={c['pattern']:c['netclass'] for c in p['net_settings']['netclass_patterns']}
assert all(patterns['/'+n]=='POWER_3V3' for n in ['BOARD_3V3','CART_3V3','GND'])
routed=(r/'hardware/verification/routing_drc.json').exists()
report=json.loads((r/('hardware/verification/routing_drc.json' if routed else 'hardware/verification/placement_drc.json')).read_text())
assert not [v for v in report['violations'] if v['severity']=='error']
assert all(v['type'] in {'text_height','text_thickness'} for v in report['violations'])
assert len(report['unconnected_items'])==(0 if routed else 90)
print('PASS: manufacturing settings and class assignments; no exclusions; DRC non-connectivity errors 0; outstanding silk warnings:',dict(collections.Counter(v['type'] for v in report['violations'])))

# Verify actual schematic net names match routing patterns, including the root sheet slash.
import fnmatch, xml.etree.ElementTree as ET
for net in ET.parse(r/'hardware/verification/gba_dumper.xml').findall('.//nets/net'):
 name=net.attrib['name']
 if not name.startswith('unconnected-'):
  matches=[c for pattern,c in patterns.items() if fnmatch.fnmatchcase(name,pattern)]
  assert len(matches)==1,(name,matches)
